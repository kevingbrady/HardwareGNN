from pathlib import Path
from multiprocessing import Lock
from src.graph_builder.TCLGraphBuilder import TCLGraph
from typing import Any
import numpy as np
import h5py
import zlib
import pickle

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

    def __init__(self, filename, num_entries):

        self.data = np.empty(num_entries, dtype=self.schema)
        self.num_entries = num_entries
        self.filename = filename
        self.filepath = f'{Path.cwd()}/processed/{filename}.h5'

        with h5py.File(self.filepath, 'a') as h5file:
            h5file.require_dataset('circuit_graph', (num_entries,), dtype=self.schema)

    def get(self, idx):
        data = h5py.File(self.filepath, 'r', swmr=True)
        return self.deserialize(data['circuit_graph'][idx])

    def update(self, idx, graph, data_directory):

        with self.write_lock:
            with h5py.File(self.filepath, 'r+') as h5file:
                dataset = h5file['circuit_graph']
                dataset[idx] = self.serialize(graph, data_directory)

    @staticmethod
    def compress_graph(graph: TCLGraph):
        return zlib.compress(pickle.dumps(graph))

    @staticmethod
    def serialize(graph: TCLGraph, data_directory: str):
        return np.frombuffer(h5Store.compress_graph(graph), dtype=np.uint8), len(graph.netlist), len(graph.connections), data_directory

    @staticmethod
    def deserialize(row: tuple[Any, int, int, str]) -> tuple[TCLGraph, int, int, str]:

        graph = row[0].tobytes()
        nodes = row[1]
        edges = row[2]
        data_directory = row[3]

        return pickle.loads(zlib.decompress(graph)), nodes, edges, data_directory

    def print_entries(self):
        with h5py.File(self.filepath, 'r') as h5file:
            dataset = h5file['circuit_graph']
            for row in dataset:
                print(row)