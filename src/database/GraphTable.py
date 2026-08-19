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

    def get_pos_weight(self):
        with self.connect() as conn:
            pos_weight = 0
            query = f'SELECT SUM(trojan_cell_count), SUM(nodes) FROM {self.table_name}'
            trojan_cells, total_cells = conn.execute_query(query)[0]
            if trojan_cells and total_cells:
                pos_weight = total_cells / max(trojan_cells, 1)
            #print(trojan_cells, total_cells, pos_weight)
            return pos_weight

    @staticmethod
    def serialize(graph: Data, filepath: str) -> dict:
        serialized_graph = zlib.compress(pickle.dumps(graph))
        serialized_pyg_graph = zlib.compress(pickle.dumps(graph.to_pyg()))

        return {
            'graph': serialized_graph,
            'pyg_graph': serialized_pyg_graph,
            'nodes': len(graph.netlist),
            'edges': len(graph.connections),
            'trojan_cell_count': len(graph.get_trojan_cells()),
            'data_directory': filepath
        }

    @staticmethod
    def deserialize(row: tuple[Any, Any, int, int, int, str]) -> Any:
        #print(row[0][0])
        return pickle.loads(zlib.decompress(row[0][1]))