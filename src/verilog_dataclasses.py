from dataclasses import dataclass, asdict, astuple, fields, field
from pyosys.libyosys import PortDir
from typing import ClassVar, Dict


@dataclass
class FileInfo:
    filepath: str=''
    filename: str=''
    module: str=''
    lines: tuple[float, float]=(0.0, 0.0)

    def __repr__(self):
        return f'{asdict(self)}'

@dataclass
class Port:
    _port_name_map: ClassVar[Dict[str, int]] = {}
    name: str
    type: str

    def __post_init__(self):
        if self.name not in self._port_name_map:
            self._port_name_map[self.name] = len(self._port_name_map)

    def get_port_as_int(self):
        return self._port_name_map[self.name]

    def __hash__(self):
        return hash(astuple(self))

    def __repr__(self):
        return f'Port({asdict(self)})'


@dataclass
class Cell:

    _cell_type_map: ClassVar[Dict[str, int]] = {}

    idx: int
    name: str
    types: dict
    ports: list[Port]
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
            if key not in self._cell_type_map:
                self._cell_type_map[key] = len(self._cell_type_map)

    def get_type_embedding(self):
        pass

    def __eq__(self, other):
        if not isinstance(other, Cell):
            return NotImplemented
        return asdict(self) == asdict(other)

    def __hash__(self):
        return hash((self.idx, self.name, self.type))

    def __repr__(self):
        return f'Cell({asdict(self)})'


@dataclass
class Wire:
    src: int
    dst: int
    src_port: int
    dst_port: int
    fan_in: int
    fan_out: int
    width: int=1
    file_info: FileInfo=field(default_factory=FileInfo)

    def __hash__(self):
        return hash(astuple(self))

    def __repr__(self):
        return f'Wire({asdict(self)})'
