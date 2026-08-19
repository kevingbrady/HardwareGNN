from dataclasses import dataclass, asdict, astuple, fields, field
from src.database.EmbeddingTable import EmbeddingTable
from typing import ClassVar
from pathlib import Path

import numpy as np
import re

@dataclass
class Port:
    _embedding_table: ClassVar[EmbeddingTable] = EmbeddingTable(table_name='PortEmbeddingTable', db_name='VerilogGNN',
                                          db_path=f'{Path.cwd()}/processed/', clear_table=False)

    _idx = int
    name: str
    type: str

    def __post_init__(self):
        self._embedding_table.enter_value(self.name)
        self._idx = self._embedding_table.get_rowid(self.name)

    def __hash__(self):
        # Native tuples are much faster and safer than astuple() here
        return hash((self.name, self.type))

    def __repr__(self):
        # Manual string formatting avoids the asdict() evaluation bug
        return f"Port({{'name': '{self.name}', 'type': '{self.type}'}})"

    def get_index(self):
        return self._idx

    def get_base_name(self) -> tuple[str, float]:
        match = re.search(r'_(\d+)$', self.name)
        if match:
            idx = float(match.group(1))
            base_name = self.name[:match.start()]
            return base_name, idx
        else:
            return self.name, -1.0

    @staticmethod
    def get_total_port_types():
        return Port._embedding_table.get_table_length()


@dataclass
class Cell:

    _embedding_table: ClassVar[EmbeddingTable] = EmbeddingTable(table_name='CellTypeEmbeddingTable', db_name='VerilogGNN',
                                      db_path=f'{Path.cwd()}/processed/', clear_table=False)
    _type_ids = []
    _type_counts = []

    idx: int
    name: str
    module: str
    types: dict
    ports: dict[str, Port]
    internal_power: float
    switching_power: float
    leakage_power: float
    total_power: float
    max_delay: float
    max_slew: float
    area: float
    label: int = 0

    def __post_init__(self):
        for key in self.types.keys():
            self._embedding_table.enter_value(key)

        self._type_ids = self._embedding_table.get_rowids_for_values(list(self.types.keys()))
        self._type_counts = [x for x in self.types.values()]

    def get_port(self, port_name):
        return self.ports.get(port_name, None)

    def get_type_ids(self):
        return self._type_ids

    def get_type_counts_vector(self):
        #return [np.log1p(x) for x in self.types.values()]
        return self._type_counts

    @staticmethod
    def get_total_cell_types():
        return Cell._embedding_table.get_table_length()

    def __eq__(self, other):
        if not isinstance(other, Cell):
            return NotImplemented
        return asdict(self) == asdict(other)

    def __hash__(self):
        return hash((self.idx, self.name, self.type))

    def __repr__(self):
        return f'Cell({asdict(self)})'


@dataclass
class Net:
    src: int
    dst: int
    src_port: Port
    dst_port: Port
    fan_in: int = 0
    fan_out: int = 0
    width: int=1

    def __hash__(self):
        return hash(astuple(self))

    def __repr__(self):
        return f'Net({asdict(self)})'
