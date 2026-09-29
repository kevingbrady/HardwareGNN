from src.database.DatabaseTable import DatabaseTable
from torch_geometric.data import Data
from typing import Any

import zlib
import pickle


class GraphTable(DatabaseTable):

    table_columns = {
        'graph': 'BLOB',
        'pyg_graph': 'BLOB',
        'nodes': 'INT',
        'edges': 'INT',
        'trojan_cell_count': 'INT',
        'data_directory': 'TEXT'
    }

    def __init__(self, db_name: str, db_path: str, table_name: str, clear_table=True):
        super().__init__(db_name, table_name, db_path, self.table_columns)

        self.create_table(self.table_name, self.table_columns, clear_table)

    def get(self, idx):
        return self.deserialize(self.select(condition=f"rowid = {idx}"))

    @staticmethod
    def serialize(graph: Data, filepath: str) -> list:
        serialized_graph = zlib.compress(pickle.dumps(graph))
        serialized_pyg_graph = zlib.compress(pickle.dumps(graph.to_pyg()))

        return [
            serialized_graph,
            serialized_pyg_graph,
            len(graph.netlist),
            len(graph.connections),
            len(graph.get_trojan_cells()),
            filepath
        ]

    @staticmethod
    def deserialize(row: tuple[Any, Any, int, int, int, str]) -> Any:
        return pickle.loads(zlib.decompress(row[0][1]))