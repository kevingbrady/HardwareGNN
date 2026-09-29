from dataclasses import dataclass, asdict, astuple
from src.graph_builder.AutoSaveDict import AutoSaveDict
from typing import ClassVar
from pathlib import Path

@dataclass
class Port:
    classes: ClassVar[list]  = [
        "Clocks",
        "Asynchronous Controls/Resets",
        "Sequential Core State Blocks",
        "Outputs",
        "Standard Combinational Logic Input",
        "MUX Control Selects / Gating Enables",
        "Design-for-Test (DFT) Scan Chains"
    ]

    name: str
    type: str
    is_clk: bool
    is_invert: bool
    class_idx: int = -1

    def __init__(self, name, type, is_clk, is_invert, cell_types=None):

        self.name = name
        self.type = type
        self.is_clk = is_clk
        self.is_invert = is_invert
        self.is_sequential = False

        self.class_idx = self.infer_class_from_structure(cell_types)

    def get_class(self):
        return self.classes[self.class_idx]

    def infer_class_from_structure(self, cell_types):

        if self.type == "output":
            # Clock Tree Root Drivers (e.g., outputs of clock gates/buffers)
            if self.is_clk:
                return 0   # CLASS 0: Clocks

            # Standard functional logic gate drivers
            return 3  # CLASS 3: Outputs

        else:

            # Sequential Clock Load pins (e.g., CP/CLK inputs on Flip-Flops)
            if self.is_clk:
                return 0  # CLASS 0: Clocks

            # Top-level module primary inputs or unmapped black box pins
            if not cell_types:
                return 4  # CLASS 4: Standard Combinational Logic Input Fallback

                # Pre-lower the macro keys to optimize CPU execution cycles
            cell_macros_string = "_".join(cell_types.keys()).lower()

            # --- SKY130 ADAPTIVE CELL CLASSIFICATION MATCHING ---
            # Identifies Sky130 sequential forms: 'dfx', 'dfr', 'dfs', 'dfb', 'dl' (latches)
            self.is_sequential = any(x in cell_macros_string for x in ["dfx", "dfr", "dfs", "dfb", "dlx", "dlclk"])

            # CLASS 1: Asynchronous Controls / Resets
            # Catches explicit asynchronous clear/set pins on sequential elements
            if self.is_sequential and any(x in cell_macros_string for x in ["rst", "res", "clr", "set"]):
                if self.is_invert:
                    return 1

            # CLASS 6: Design-for-Test (DFT) Scan Chains
            # Matches 'sdf' scan-multiplexed register cells uniquely
            if "sdf" in cell_macros_string:
                return 6

            # CLASS 2: Sequential Core State Blocks
            if self.is_sequential:
                return 2

            # CLASS 5: MUX Control Selects / Gating Enables
            # Captures 'mux' blocks and clock-gating blocks ('clkgated', 'cg')
            if any(x in cell_macros_string for x in ["mux", "gate", "clkp", "clkgn"]):
                return 5

            # CLASS 4: Standard Combinational Logic Input Fallback
            return 4

    def __hash__(self):
        # Native tuples are much faster and safer than astuple() here
        return hash((self.name, self.type))

    def __repr__(self):
        # Manual string formatting avoids the asdict() evaluation bug
        return f"Port({{'name': '{self.name}', 'type': '{self.type}', class: '{self.get_class()}'}})"



@dataclass
class Cell:

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

    _all_cell_types: ClassVar = AutoSaveDict(f'{Path.cwd()}/metadata/cell_types_map.json')
    _type_ids = []
    _type_counts = []

    def __post_init__(self):
        for key in self.types.keys():
            if key not in Cell._all_cell_types:
                Cell._all_cell_types[key] = len(Cell._all_cell_types)

        self._type_ids = [self._all_cell_types[x] for x in list(self.types.keys())]
        self._type_counts = [x for x in self.types.values()]

    def get_port(self, port_name):
        return self.ports.get(port_name, None)

    def get_type_ids(self):
        return self._type_ids

    def get_type_counts_vector(self):
        return self._type_counts

    @staticmethod
    def get_total_cell_types():
        return len(Cell._all_cell_types)

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
    net_type: int
    src_port: Port
    dst_port: Port
    fan_in: int = 0
    fan_out: int = 0
    width: int=1

    def __hash__(self):
        return hash(astuple(self))

    def __repr__(self):
        return f'Net({asdict(self)})'
