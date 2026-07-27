from pathlib import Path
from src.TCLGraphBuilder import TCLGraph
from src.h5Storage import h5Store
from src.utils import pretty_time_delta
from src.errors import *
from multiprocessing import Manager, Lock
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import re
import time


print_lock = Lock()

class VerilogGraphDataset:
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

    def __init__(self, data_directory):
        super(VerilogGraphDataset, self).__init__()

        run_list = [str(f) for f in Path(data_directory).glob('*') if str(f) not in self.ignore_dirs]
        run_list.sort(key=self.sort_key)

        self.dataset = h5Store(len(run_list))

        #run_list = [x for x in run_list if run_list.index(x) == 38]
        #run_list = [x for x in run_list if 'PIC16F84-T200' in x]

        print(run_list)
        dataset_processing_start = time.time()

        with ProcessPoolExecutor(max_tasks_per_child=1) as pool:
            for idx, circuit_dir in enumerate(run_list):
                future = pool.submit(self.run_single_circuit, circuit_dir)
                bound_callback = partial(self.design_output_handler, circuit_dir, idx)
                future.add_done_callback(bound_callback)

        print(f'Finished processing TrustHub dataset in {pretty_time_delta(time.time() - dataset_processing_start)} ')
        #self.dataset.print_entries()

    def design_output_handler(self, input_directory, dataset_idx, future):

        try:
            circuit_graph = future.result()

            if circuit_graph:
                circuit_graph.builder_end_time = time.time()

                with print_lock:
                    print(f'[COMPLETED] {input_directory} [{pretty_time_delta(circuit_graph.builder_end_time - circuit_graph.builder_start_time)}]')
                    print('\t', circuit_graph.get_trojan_cells())
                    print('\t', 'Nodes: ', len(circuit_graph.netlist), 'Edges: ', len(circuit_graph.connections))

            self.dataset.update(
                dataset_idx,
                circuit_graph,
                input_directory
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


