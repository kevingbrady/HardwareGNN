from dataclasses import dataclass, asdict, astuple, fields, field
from pyosys.libyosys import PortDir
from typing import Dict, Any

@dataclass
class Cell:
    idx: int
    name: str
    type: str
    filename: str
    module: str
    cell_lineno: tuple[float, float]
    fan_in: int
    fan_out: int
    label: int

    def __eq__(self, other):
        if not isinstance(other, Cell):
            return NotImplemented
        return asdict(self) == asdict(other)

    def __hash__(self):
        return hash(astuple(self))

    def to_dict(self):
        return asdict(self)


@dataclass
class Port:
    name: str
    type: str
    direction: PortDir

    '''def __init__(self, name: str, direction: PortDir, port_gate_role_map: dict):
        
        self.name = name
        self.direction = direction

        if port_gate_role_map and self.name in port_gate_role_map:
            self.type = port_gate_role_map[self.name]
        else:
            self.type= f"Generic Native Port [{"Input" if self.direction== PortDir.PD_INPUT else "Output"}]"'''

    def __hash__(self):
        return hash(astuple(self))

    def to_dict(self):
        return {'name': self.name, 'type': self.type}


@dataclass
class Wire:
    name: str
    width: int
    wire_lineno: tuple[float, float]

    def __hash__(self):
        return hash(astuple(self))



@dataclass
class Bit(Wire):
    name: str
    width: int
    wire_lineno: tuple[float, float]
    offset: int
    port: Port
    cell: Cell

    @classmethod
    def from_wire(cls, wire:Wire, offset: int, port:Port, cell:Cell):
        return cls(**wire.__dict__, offset=offset, port=port, cell=cell)

    def __repr__(self):
        return f'Bit(name={self.name},width={self.width},wire_lineno={self.wire_lineno},offset={self.offset},port={type(self.port)},cell={type(self.cell)})'


@dataclass
class Signal:
    src: Bit
    dst: Bit
    wire: Wire

    def __eq__(self, other):
        if not isinstance(other, Bit):
            return NotImplemented
        return asdict(self) == asdict(other)

    def __hash__(self):
        return hash(astuple(self))