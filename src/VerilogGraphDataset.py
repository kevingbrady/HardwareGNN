import multiprocessing
from pathlib import Path
from src.graph_builder.TCLGraphBuilder import TCLGraph
from src.database.GraphTable import GraphTable
from src.utils import pretty_time_delta
from src.graph_builder.errors import *
from torch.utils.data import Dataset
from multiprocessing import Lock
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import re
import time
import os

print_lock = Lock()

class VerilogGraphDataset(Dataset):
    ignore_dirs = ['/home/kgb/PycharmProjects/HardwareGNN/data/decompressed/AES-T2200',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/decompressed/memctrl-T100',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/decompressed/MultPyramid-T100',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/decompressed/MultPyramid-T200',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/decompressed/b19-T300',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/decompressed/b19-T400',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/decompressed/b19-T500',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/decompressed/BasicRSA-T100',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/decompressed/BasicRSA-T200',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/decompressed/BasicRSA-T300',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/decompressed/BasicRSA-T400']

    def __init__(self, data_directory, build_dataset=False):
        super(VerilogGraphDataset, self).__init__()

        run_list = [str(f) for f in Path(data_directory).glob('*') if str(f) not in self.ignore_dirs]
        run_list.sort(key=self.sort_key)

        #run_list = [x for x in run_list if run_list.index(x) == 38]
        self.pos_weight = 0

        if build_dataset:
            self.graph_table = GraphTable(table_name='GraphTable', db_name='VerilogGNN',
                                          db_path=f'{Path.cwd()}/processed/')
            self.build_verilog_dataset(run_list)

        else:
            self.graph_table = GraphTable(table_name='GraphTable', db_name='VerilogGNN',
                                          db_path=f'{Path.cwd()}/processed/', clear_table=False)

        self.length = self.graph_table.get_table_length()
        self.pos_weight = self.graph_table.get_pos_weight()


    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        graph = self.graph_table.get(idx)
        return graph.to_pyg()


    def build_verilog_dataset(self, run_list):

        print(run_list)
        dataset_processing_start = time.time()

        with ProcessPoolExecutor(max_tasks_per_child=1) as pool:
            for idx, circuit_dir in enumerate(run_list):
                self.graph_table.insert(data=['', 0, 0, 0, circuit_dir])

                future = pool.submit(self.run_single_circuit, circuit_dir)
                bound_callback = partial(self.design_output_handler, circuit_dir, idx)
                future.add_done_callback(bound_callback)

        print(f'Finished processing TrustHub dataset in {pretty_time_delta(time.time() - dataset_processing_start)} ')

    def design_output_handler(self, input_directory, dataset_idx, future):
        try:
            circuit_graph = future.result()

            if circuit_graph:
                circuit_graph.builder_end_time = time.time()

                with print_lock:
                    print(
                        f'[COMPLETED] {input_directory} [{pretty_time_delta(circuit_graph.builder_end_time - circuit_graph.builder_start_time)}]')

                self.graph_table.update(
                    data=GraphTable.serialize(circuit_graph, input_directory),
                    condition=f'rowid = {dataset_idx+1}'
                )

        except (YosysSynthesisError, TCLError) as exc:
            with print_lock:
                print(f"[ERROR] Directory {input_directory} failed to build circuit graph : {exc}", flush=True)

    @staticmethod
    def run_single_circuit(data_dir):

        for inst in Path(data_dir).glob('*'):
            if inst.name == 'src':

                circuit_files_dir = inst.absolute()
                troj_text_file_cells = []
                clean_cells = []

                for circuit_dir in inst.glob('*'):

                    if circuit_dir.name == 'TjFree':
                        # All files and modules are named the same in these directories
                        # for circuits and their malicious equivalents
                        # so ignore them for getting clean cell names
                        if all(sub not in data_dir for sub in ['PIC16F84', 'MC8051', 'RS232']):
                            clean_circuit = TCLGraph(circuit_dir.absolute())
                            clean_cells = clean_circuit.get_cells_only()

                    elif circuit_dir.name == 'TjIn':
                        circuit_files_dir = circuit_dir.absolute()

                    elif circuit_dir.name == '180nm':
                        circuit_files_dir = circuit_dir.absolute()
                        with open(f'{circuit_dir.absolute()}/troj_modules.txt', 'r') as file:
                            troj_text_file_cells = [line.strip() for line in file]

                trojan_circuit = TCLGraph(circuit_files_dir)

                if trojan_circuit.input_files:

                    trojan_circuit.low_level_design_pass()

                    if 'AES-' in data_dir:
                        if clean_circuit.top_module != trojan_circuit.top_module:
                            clean_cells = [str(x).replace('aes_128/', 'top/AES/') for x in clean_cells]
                            clean_cells.append('top/AES')

                    if 'wb_conmax-T200' in data_dir or 'wb_conmax-T300' in data_dir:
                        clean_cells.remove('wb_conmax_top/rf')

                    for cell in trojan_circuit.netlist:
                        instance_name = cell.name.rpartition('/')[2]
                        if instance_name in troj_text_file_cells:
                            cell.label = 1
                        elif cell.name not in clean_cells:
                            cell.label = 1

                    return trojan_circuit

        return None

    @staticmethod
    def sort_key(path):
        filename = path.split('/')[-1]
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', filename)]

    def __repr__(self):
        return f"VerilogGraphDataset({self.length})"
