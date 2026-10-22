from pathlib import Path
from src.graph_builder.TCLGraphBuilder import TCLGraph
from src.database.GraphTable import GraphTable
from src.utils import pretty_time_delta, get_dir_size
from src.graph_builder.errors import *
from torch.utils.data import Dataset
from torch_geometric.data import Batch
from multiprocessing import Lock
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import re
import time
import os
import torch

print_lock = Lock()


class CleanGraphDataset(Dataset):
    ignore_dirs = ['/home/kgb/PycharmProjects/HardwareGNN/data/TrustHub/AES-T2200',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/TrustHub/memctrl-T100',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/TrustHub/MultPyramid-T100',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/TrustHub/MultPyramid-T200',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/TrustHub/b19-T300',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/TrustHub/b19-T400',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/TrustHub/b19-T500',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/TrustHub/BasicRSA-T100',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/TrustHub/BasicRSA-T200',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/TrustHub/BasicRSA-T300',
                   '/home/kgb/PycharmProjects/HardwareGNN/data/TrustHub/BasicRSA-T400']

    def __init__(self, data_directory, transform=None, build_dataset=False):
        super(CleanGraphDataset, self).__init__()

        self.transform = transform
        # run_list = [str(f) for f in Path(data_directory).glob('*') if str(f) not in self.ignore_dirs]
        data_directories = [item for item in Path(data_directory).iterdir() if item.is_dir()]
        run_list = [
            str(item)
            for data_dir in data_directories
            for item in Path(data_dir).iterdir()
            if item.is_dir() and item.name not in self.ignore_dirs
        ]

        #run_list = [run_list[132050]]
        run_list = [x for x in run_list if x.__contains__('AES-T300')]

        # run_list.sort(key=self.sort_key)

        # run_list = [x for x in run_list if run_list.index(x) == 3]

        if build_dataset:
            self.clean_graphs = GraphTable(table_name='CleanGraphs', db_name='VerilogGNN',
                                           db_path=f'{Path.cwd()}/processed/')
            self.run_single_circuit(run_list[0])
            #self.build_verilog_dataset(run_list)

        else:
            self.clean_graphs = GraphTable(table_name='CleanGraphs', db_name='VerilogGNN',
                                           db_path=f'{Path.cwd()}/processed/', clear_table=False)

        self.length = self.clean_graphs.get_table_length()

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        # full_graph, pyg_graph, nodes, edges, trojan_nodes, filename = self.clean_graphs.get(idx + 1)
        pyg_graph = self.clean_graphs.get(idx + 1, select_index=1)

        if self.transform:
            pyg_graph = self.transform(pyg_graph)

        return pyg_graph

    def get_full_graph(self, idx):
        full_graph = self.clean_graphs.get(idx + 1, select_index=0)
        return full_graph

    def build_verilog_dataset(self, run_list):

        #print(run_list)
        dataset_processing_start = time.time()

        with ProcessPoolExecutor(max_tasks_per_child=1) as pool:
            for circuit_dir in run_list:    #sorted(run_list, key=lambda f: get_dir_size(f), reverse=True):
                future = pool.submit(self.run_single_circuit, circuit_dir)
                bound_callback = partial(self.design_output_handler, circuit_dir)
                future.add_done_callback(bound_callback)

        print(f'Finished processing Trojan dataset in {pretty_time_delta(time.time() - dataset_processing_start)} ')

    def design_output_handler(self, input_directory, future):
        try:
            circuit_graph = future.result()

            if circuit_graph:
                circuit_graph.builder_end_time = time.time()
                with print_lock:
                    print(
                        f'[COMPLETED] {input_directory} [{pretty_time_delta(circuit_graph.builder_end_time - circuit_graph.builder_start_time)}]')

                self.clean_graphs.insert(
                    data=GraphTable.serialize(circuit_graph, input_directory)
                )

        except (YosysSynthesisError, TCLError) as exc:
            with print_lock:
                print(f"[ERROR] Directory {input_directory} failed to build circuit graph : {exc}", flush=True)

    def run_single_circuit(self, data_dir):

        base_dir = Path(data_dir)
        nested_target = base_dir / "src" / "TjFree"

        active_dir = nested_target if nested_target.is_dir() else base_dir
        print(active_dir.absolute())
        circuit = TCLGraph(active_dir.absolute())
        circuit.low_level_design_pass()
        circuit.compute_logic_depth()
        cells = [cell for name, cell in circuit.netlist.items()][:150]
        print(*cells, sep='\n')
        return circuit


    @staticmethod
    def sort_key(path):
        filename = path.split('/')[-1]
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', filename)]


    def __repr__(self):
        return f"CleanGraphDataset({self.length})"
