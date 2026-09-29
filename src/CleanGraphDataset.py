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

    def __init__(self, data_directory, transform=None, build_dataset=False):
        super(CleanGraphDataset, self).__init__()

        self.transform = transform
        run_list = [str(f) for f in Path(data_directory).glob('*') if str(f) not in self.ignore_dirs]
        run_list.sort(key=self.sort_key)

        if build_dataset:
            self.clean_graphs = GraphTable(table_name='CleanGraphs', db_name='VerilogGNN',
                                           db_path=f'{Path.cwd()}/processed/')
            self.build_verilog_dataset(run_list)

        else:
            self.clean_graphs = GraphTable(table_name='CleanGraphs', db_name='VerilogGNN',
                                           db_path=f'{Path.cwd()}/processed/', clear_table=False)

        self.length = self.clean_graphs.get_table_length()


    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        graph = self.clean_graphs.get(idx + 1)

        if self.transform:
            graph = self.transform(graph)

        return graph

    def get_combined_subset(self, indices):
        return Batch.from_data_list([self[x] for x in indices])

    def build_verilog_dataset(self, run_list):

        print(run_list)
        dataset_processing_start = time.time()

        with ProcessPoolExecutor(max_tasks_per_child=1) as pool:

            for idx, circuit_dir in enumerate(sorted(run_list, key=lambda f: get_dir_size(f), reverse=True)):
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

        for inst in Path(data_dir).glob('*'):
            if inst.name == 'src':
                for circuit_dir in inst.glob('*'):
                    if circuit_dir.name == 'TjFree':
                        circuit = TCLGraph(circuit_dir.absolute())
                        circuit.low_level_design_pass()
                        return circuit

        return None

    @staticmethod
    def sort_key(path):
        filename = path.split('/')[-1]
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', filename)]

    def __repr__(self):
        return f"CleanGraphDataset({self.length})"
