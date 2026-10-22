from dataclasses import dataclass, asdict, astuple, field
from src.graph_builder.AutoSaveDict import AutoSaveDict
from typing import ClassVar
from pathlib import Path

import re

_RESET_PATTERN = re.compile(r'\b(rst|res|clr|set|clear|reset)\b|.*(rst|res|clr|set|clear|reset).*', re.IGNORECASE)
_SEQ_DATA_PATTERN = re.compile(r'^(d|din|d_in|da|db|data_in|data)(\d*|\[\d+\])?$', re.IGNORECASE)
_SCAN_PATTERN = re.compile(r'\b(si|se|scan|test_si|test_se)\b|.*(scan).*', re.IGNORECASE)
_MUX_PATTERN = re.compile(r'\b(sel|en|gate|mux_sel|enable)\b|.*(sel|en|gate).*', re.IGNORECASE)


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

    def __init__(self, name, type, is_clk, is_invert, parent_cell=None):

        self.name = name
        self.type = type
        self.is_clk = is_clk
        self.is_invert = is_invert
        self.is_sequential = False

        self.class_idx = self.infer_class_from_structure(parent_cell)

    def get_class(self):
        return self.classes[self.class_idx]

    def infer_class_from_structure(self, parent_cell=None):

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
            if not parent_cell or not parent_cell.types:
                return 4  # CLASS 4: Standard Combinational Logic Input Fallback

            # Match your variations (din_2, DIN_2, data_in[0], etc.) cleanly
            is_reset_pin = bool(_RESET_PATTERN.match(self.name))
            is_seq_data_pin = bool(_SEQ_DATA_PATTERN.match(self.name))
            is_scan_pin = bool(_SCAN_PATTERN.match(self.name))
            is_mux_control = bool(_MUX_PATTERN.match(self.name))

            if parent_cell.combinational_density > 0.85:
                if is_seq_data_pin and len(self.name) == 1 and parent_cell.sequential_density > 0:
                    self.is_sequential = True
                    return 2
                return 4


            # CLASS 1: Asynchronous Controls / Resets
            # Catches explicit asynchronous clear/set pins on sequential elements
            if parent_cell.sequential_density > 0.5:
                self.is_sequential = True
                if is_reset_pin:
                    return 1  # CLASS 1: Asynchronous Controls / Resets
                if is_scan_pin:
                    return 6   # CLASS 6: DFT Scan Chains
                if is_seq_data_pin:
                    return 2

            if is_mux_control and any(x in "".join(parent_cell.types.keys()).lower() for x in ["mux", "gate"]):
                return 5  # Class 5: MUX Control Selects / Gating Enables
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
    power: dict = field(default_factory=lambda: {'internal_power': 0.0, 'switching_power': 0.0, 'leakage_power': 0.0, 'total_power': 0.0})
    timing: dict = field(default_factory=lambda: {'max_delay': 0.0, 'max_slew': 0.0})
    fanout: dict = field(default_factory=lambda: {'sum': 0, 'max': 0, 'mean': 0.0})
    fanin: dict = field(default_factory=lambda: {'sum': 0, 'max': 0, 'mean': 0.0})
    width_metrics: dict = field(default_factory=lambda: {'in_width_sum': 0.0, 'in_width_mean': 0.0, 'out_width_sum': 0.0, 'out_width_mean': 0.0})
    area: float = 0.0
    total_sinks: int = 0
    total_drivers: int = 0
    in_degree: int = 0
    internal_cell_count: int = 0
    sequential_density: float = 0.0
    combinational_density: float = 0.0
    is_hybrid: int = 0
    logic_depth: int = 0
    label: int = 0

    _all_cell_types: ClassVar = AutoSaveDict(f'/home/kgb/PycharmProjects/HardwareGNN/metadata/cell_types_map.json')
    _type_ids = []
    _type_counts = []

    def __post_init__(self):
        for key in self.types.keys():
            if key not in Cell._all_cell_types:
                Cell._all_cell_types[key] = len(Cell._all_cell_types)

        self._type_ids = [self._all_cell_types[x] for x in list(self.types.keys())]
        self._type_counts = [x for x in self.types.values()]
        self.get_cell_type_metrics()

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

        if key == "total_drivers":
            if self.total_drivers > 0:
                self.fanin['mean'] = self.fanin['sum'] / self.total_drivers
                self.width_metrics['in_width_mean'] = self.width_metrics['in_width_sum'] / self.total_drivers

        if key == "total_sinks":
            if self.total_sinks > 0:
                self.fanout['mean'] = self.fanout['sum'] / self.total_sinks
                self.width_metrics['out_width_mean'] = self.width_metrics['out_width_sum'] / self.total_sinks

    def get_port(self, port_name):
        return self.ports.get(port_name, None)

    def get_type_ids(self):
        return self._type_ids

    def get_type_counts_vector(self):
        return self._type_counts

    def get_fanin_metrics(self):
        return self.fanin

    def get_fanout_metrics(self):
        return self.fanout

    def get_width_metrics(self):
        return self.width_metrics

    def get_cell_type_metrics(self):
        seq_pattern = re.compile(r'__(df|edf|dl)[a-z0-9_]+')

        self.internal_cell_count = sum(self.types.values())
        if self.internal_cell_count == 0:
            return

        sequential_count = sum(count for cell_type, count in self.types.items() if seq_pattern.search((cell_type)))
        combinational_count = self.internal_cell_count - sequential_count

        self.sequential_density = sequential_count / self.internal_cell_count
        self.combinational_density = combinational_count / self.internal_cell_count
        self.is_hybrid = 1 if (sequential_count > 0 and combinational_count > 0) else 0

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
    driver: tuple[int, str]
    sink: tuple[int, str]
    src_port: Port
    dst_port: Port
    fan_in: int = 0
    fan_out: int = 0
    driver_fanout_to_sink_fanin_ratio: float = 0.0
    width: int = 0

    def __hash__(self):
        return hash(astuple(self))

    def __repr__(self):
        return f'Net({asdict(self)})'
