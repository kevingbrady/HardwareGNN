from pathlib import Path
from src.TCLGraphBuilder import TCLGraphBuilder
from src.h5Storage import h5Store
from src.utils import pretty_time_delta
from src.errors import *
from multiprocessing import Manager, Lock
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import re
import time
import numpy as np

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

        run_list = [x for x in run_list if run_list.index(x) == 3]
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
            nodes = 0
            edges = 0

            circuit_graph, trojan_modules = future.result()

            if circuit_graph:
                circuit_graph.builder_end_time = time.time()
                nodes = len(circuit_graph.netlist)
                edges = len(circuit_graph.connections)

                with print_lock:
                    #[print(cell) for cell in circuit_graph.netlist]
                    print(f'[COMPLETED] {input_directory} [{pretty_time_delta(circuit_graph.builder_end_time - circuit_graph.builder_start_time)}]')
                    print('\t', trojan_modules)
                    print('\t', 'Nodes: ', len(circuit_graph.netlist), 'Edges: ', len(circuit_graph.connections))

            self.dataset.update(
                dataset_idx,
                np.array([], dtype=np.uint8),
                nodes,
                edges,
                input_directory
            )

        except (YosysSynthesisError, TCLError) as exc:
            with print_lock:
                print(f"[ERROR] Directory {input_directory} failed to build circuit graph : {exc}", flush=True)

    def run_single_circuit(self, circuit_dir):
        for inst in Path(circuit_dir).glob('*'):
            if inst.name == 'src':

                clean_circuit_modules = []
                circuit_files_dir = inst.absolute()

                for circuit_dir in inst.glob('*'):

                    if circuit_dir.name == 'TjFree':

                        clean_circuit_modules = TCLGraphBuilder(circuit_dir.absolute()).get_modules()

                    elif circuit_dir.name in ('TjIn', '180nm'):
                        circuit_files_dir = circuit_dir.absolute()

                trojan_circuit = TCLGraphBuilder(circuit_files_dir)

                if trojan_circuit.input_files:
                    trojan_modules = [x for x in trojan_circuit.modules if
                                      clean_circuit_modules != [] and (x != 'top' and x not in clean_circuit_modules)]
                    trojan_circuit.low_level_design_pass()

                    return trojan_circuit, trojan_modules

        return None, []

    def sort_key(self, path):
        # Extract the value after the last slash
        filename = path.split('/')[-1]

        # Split the filename into text chunks and numeric chunks
        # Non-digits are treated as text; digits are converted to integers
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', filename)]
