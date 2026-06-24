from dataclasses import dataclass, asdict, astuple, fields, field
from pyosys.libyosys import PortDir
from typing import TypedDict, Dict, Any


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
    idx: int
    name: str
    type: str
    size: int
    direction: PortDir

    def __hash__(self):
        return hash(astuple(self))

    def __repr__(self):
        return f'Port({asdict(self)})'


@dataclass
class Cell:
    idx: int
    name: str
    type: str
    ports: list[Port]
    fan_in: int
    fan_out: int
    label: int = 0
    max_wire_width: int=0
    trigger_like_cell: bool = False
    drives_module_output: bool = False
    is_combinational_gate: bool = False
    is_steering_element: bool = False
    file_info: FileInfo=field(default_factory=FileInfo)

    def __post_init__(self):
        self.is_combinational_gate = self.type in ["$_AND_", "$_OR_", "$_XOR_", "$_XNOR_", "$_NAND_", "$_NOR_", "$_NOT_"]
        self.is_steering_element = "MUX" in self.type

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
    name: str
    width: int=1
    output_wire:bool=False
    reads_control_or_slices:bool=False
    file_info: FileInfo=field(default_factory=FileInfo)

    def __hash__(self):
        return hash(astuple(self))

    def __repr__(self):
        return f'Wire({asdict(self)})'

@dataclass
class Bit:
    name: str
    offset: int
    cell_idx: int
    port_idx: int
    wire: str

    @staticmethod
    def from_wire(wire:Wire, offset: int, cell_idx:int, port_idx:int):
        return Bit(name=wire.name + '[' + str(offset) + ']', offset=offset, cell_idx=cell_idx, port_idx=port_idx, wire=wire.name)

    def __hash__(self):
        return hash(astuple(self))

    def __repr__(self):
        return f'Bit({asdict(self)})'


@dataclass
class Signal:
    wire: str
    delay: float

    def __eq__(self, other):
        if not isinstance(other, Signal):
            return NotImplemented
        return asdict(self) == asdict(other)

    def __hash__(self):
        return hash(astuple(self))

    def __repr__(self):
        return f'Signal({asdict(self)})'
