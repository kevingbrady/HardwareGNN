from pathlib import Path
from multiprocessing import Lock
import numpy as np
import h5py

string_vl_type = h5py.string_dtype(encoding="utf-8")
blob_vl_type = h5py.vlen_dtype(np.dtype("uint8"))

class h5Store:

    schema = np.dtype([
        ("graph", blob_vl_type),
        ("nodes", "i8"),
        ("edges", "i8"),
        ("data_directory", string_vl_type)
    ])

    write_lock = Lock()

    def __init__(self, num_entries):
        self.data = np.empty(num_entries, dtype=self.schema)

        self.filename = f'{Path.cwd()}/TrustHubGraphDataset.h5'
        with h5py.File(self.filename, 'w') as h5file:
            dataset = h5file.create_dataset('circuit_graph', (num_entries,), dtype=self.schema)

    def update(self, idx, graph, nodes, edges, filename):

        with self.write_lock:
            with h5py.File(self.filename, 'r+') as h5file:
                dataset = h5file['circuit_graph']
                dataset[idx] = (graph, nodes, edges, filename)

    def print_entries(self):
        with h5py.File(self.filename, 'r') as h5file:
            dataset = h5file['circuit_graph']
            for row in dataset:
                print(row)