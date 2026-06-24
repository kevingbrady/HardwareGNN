from pyosys.libyosys import PortDir, SigSpec
from torch.utils.data import Dataset
from torch_geometric.data import Data
from pyosys import libyosys as yosys
from pathlib import Path
from src.utils import compact_dir, output_manager
from src.cell_mappings import GATE_ROLE_MAP, CUSTOM_MODULE_ROLE_MAP, CONST_STATE_MAP
from src.verilog_dataclasses import Cell, Port, Wire, Bit, Signal, FileInfo
import pprint
import subprocess

liberty_file_path = '/usr/local/share/pdk/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_100C_1v80.lib'


# liberty_file_path = '/usr/local/share/pdk/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v'

class HardwareFileDataset(Dataset):

    def __init__(self, data_dir):
        super(HardwareFileDataset, self).__init__()

        self.silent = True
        self.top_module = None
        self.num_cells = 0

        self.netlist: list[Cell] = []  # Nodes
        self.signal_map: dict[tuple[Bit, Bit], Signal] = {}  # Edges

        self.bit_wire_map = {
            Wire(name='GND'): {PortDir.PD_INPUT: [], PortDir.PD_OUTPUT: []},
            Wire(name='VCC'): {PortDir.PD_INPUT: [], PortDir.PD_OUTPUT: []},
            Wire(name='UNCONNECTED_X'): {PortDir.PD_INPUT: [], PortDir.PD_OUTPUT: []},
            Wire(name='UNCONNECTED_Z'): {PortDir.PD_INPUT: [], PortDir.PD_OUTPUT: []},
            Wire(name='DONT_CARE_MARKER'): {PortDir.PD_INPUT: [], PortDir.PD_OUTPUT: []},
            Wire(name='INTERNAL_PASS_MARKER'): {PortDir.PD_INPUT: [], PortDir.PD_OUTPUT: []}
        }

        self.design = self.extract_behavioral_design(data_dir)

        self.high_level_design_pass()  # Get connections of each bit/port/cell
        self.build_signal_map()        # Condense each bit-bit connection into summarized port-port connection with cell info
        self.low_level_design_pass()  # Flatten netlist to get power/timing/area info for each cell/ bit-bit connection

    def extract_behavioral_design(self, data_dir):

        with output_manager(silent=self.silent):
            yosys.yosys_setup()
            design = yosys.Design()

            for file in Path(data_dir).rglob("*"):

                if file.suffix in ('.v', '.vhd'):
                    filepath = str(file.absolute())
                    if not filepath.__contains__('test'):
                        design.run_pass(f'read_verilog {filepath}')

            design.run_pass(f'hierarchy -auto-top')
            design.run_pass(f'proc')

            yosys.run_pass(f'design -push-copy', design)

        return design

    def low_level_design_pass(self):

        # Flattens netlist to be able to be run with sta to get low level power, timing, and area info
        with output_manager(silent=self.silent):
            yosys.run_pass(f'design -pop', self.design)
            self.top_module = self.design.top_module()
            self.design.run_pass('keep_hierarchy')
            # Fine RTL Synthesis coarse pass
            #self.design.run_pass(f'synth -top {self.top_module.name.str()} -run fine')
            #self.design.run_pass(f'splitnets -ports')

            self.design.run_pass('fsm')
            self.design.run_pass('memory')
            self.design.run_pass('opt')
            self.design.run_pass('techmap')
            self.design.run_pass('simplemap')
            self.design.run_pass('opt')

            # Map sequential cells (Flip-Flops) using the Liberty file
            self.design.run_pass(f'dfflibmap -liberty {liberty_file_path}')
            self.design.run_pass('opt_clean')

            #  Map combinational logic using ABC and the Liberty file
            self.design.run_pass(f'abc -liberty {liberty_file_path}')
            self.design.run_pass(f'clean')

            self.design.run_pass(f'write_verilog -norename {Path.cwd()}/__temp_netlist.v')

            tcl_args = f"""
                set ::top_module "{self.top_module.name.str().replace('\\', '')}"
                set ::liberty_file "{liberty_file_path}"
                set ::working_dir "{Path.cwd()}"
    
                source "{Path.cwd()}/metadata/get_power_timing_area_cell_data.tcl"
                #source "{Path.cwd()}/metadata/bit_signal_map.tcl"
                exit
            """
            result = subprocess.run(['sta', '-no_init'], input=tcl_args, capture_output=True, text=True, check=True)

        #print('Output: ', result.stdout.strip())
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write(result.stdout.strip())


    def high_level_design_pass(self):

        # Builds bit_wire_map and netlist to be able to get the full nodes and edges of the graph as cells (nodes)
        # and signals representing connections between cells (edges)

        idx = 0
        self.top_module = self.design.top_module()

        with output_manager(silent=self.silent):
            # High-Level RTL Synthesis coarse pass
            self.design.run_pass(f'synth -top {self.top_module.name.str()} -run coarse')

        for module_name, module in self.design.modules_.items():

            self.num_cells += module.cells_size()

            for wire_id, yosys_wire in module.wires_.items():
                wire = Wire(
                    name=str(yosys_wire.name).replace('\\', ''),
                    width=yosys_wire.width,
                    output_wire=yosys_wire.port_output,
                    file_info=self.get_file_info(module_name, yosys_wire.attributes)
                )

                wire.reads_control_or_slices = "trigger" in wire.name.lower() or "activated" in wire.name.lower()

                self.bit_wire_map[wire] = {PortDir.PD_INPUT: [], PortDir.PD_OUTPUT: []}

            for cell_id, yosys_cell in module.cells_.items():

                cell_name = yosys_cell.name.str().replace('\\', '')
                cell_type = yosys_cell.type.str().replace('\\', '')

                cell = Cell(
                    idx=idx,
                    name=cell_name,
                    type=cell_type,
                    file_info=self.get_file_info(module_name, yosys_cell.attributes),
                    ports=[],
                    fan_in=0,
                    fan_out=0
                )

                port_gate_role_map = GATE_ROLE_MAP.get(cell.type, CUSTOM_MODULE_ROLE_MAP)
                #print(idx, cell.file_info.module, cell.name, cell.type)

                for port_id, sig_spec in yosys_cell.connections_.items():

                    port_str = str(port_id).replace('\\', '')
                    port_customtype_str = ''
                    direction = yosys_cell.port_dir(port_id)

                    if direction == PortDir.PD_INPUT:
                        port_customtype_str = "Generic_Native_Port[Input]"
                        cell.fan_in += 1
                    if direction == PortDir.PD_OUTPUT:
                        port_customtype_str = f"Generic_Native_Port[Output]"
                        cell.fan_out += 1

                    port = Port(
                        idx=len(cell.ports),
                        name=port_str,
                        type=port_gate_role_map.get(port_str, port_customtype_str),
                        direction=direction,
                        size=sig_spec.size()
                    )

                    cell.ports.append(port)

                    for sig_bit in sig_spec.bits():

                        offset = sig_bit.offset
                        key = str(sig_bit.wire.name).replace('\\', '') if sig_bit.is_wire() \
                            else (CONST_STATE_MAP.get(sig_bit.data))

                        wire = self.get_wire(key)
                        bit = Bit.from_wire(wire, offset, cell.idx, port.idx)
                        self.bit_wire_map[wire][port.direction].append(bit)

                        cell.max_wire_width = (cell.max_wire_width, wire.width)[wire.width > cell.max_wire_width]

                        if port.direction == PortDir.PD_OUTPUT:
                            if wire.output_wire:
                                cell.drives_module_output = True

                # print(cell.idx, cell.file_info.module, cell.name, cell.type, cell.fan_in, cell.fan_out)
                self.netlist.append(cell)
                idx += 1

    def build_signal_map(self):

        for wire, entries in self.bit_wire_map.items():

            for sink_bit, driver_bit in zip(entries[PortDir.PD_INPUT], entries[PortDir.PD_OUTPUT]):

                if (driver_bit, sink_bit) not in self.signal_map:

                    sink_port = self.get_cell(sink_bit.cell_idx).ports[sink_bit.port_idx]
                    driver_port = self.get_cell(driver_bit.cell_idx).ports[driver_bit.port_idx]

                    self.signal_map[(driver_bit, sink_bit)] = Signal(
                                                                    wire=wire.name,
                                                                    delay=0.0,
                                                                )
                '''else:
                    signal = self.signal_map.get((driver_bit.cell_idx, sink_bit.cell_idx))
                    signal.driver_offset = (*signal.driver_offset[:1], driver_bit.offset)
                    signal.sink_offset = (*signal.sink_offset[:1], sink_bit.offset)'''

        '''for key, signal in self.signal_map.items():
            print(f'({self.get_cell(key[0]).name}[{key[0]}], {self.get_cell(key[1]).name}[{key[1]}])', (signal.src_port.name, signal.dst_port.name, signal.driver_offset, signal.sink_offset))

        print('Nodes:', len(self.netlist), 'Edges:', len(self.signal_map))'''

    def generate_labels(self, cell_idx, wire):

        cell = self.netlist[cell_idx]

        if (cell.is_steering_element or cell.type == '$_XOR_') and (
                cell.drives_module_output or cell.name.lower() in ('state', 'trojan')):
            if cell.trigger_like_cell or "payload" in cell.name.lower():
                cell.label = 1  # PAYLOAD

        if cell.is_combinational_gate and not cell.drives_module_output:
            if cell.fan_in >= 3 or "trig" in cell.name.lower() or wire.reads_control_or_slices:
                cell.label = 2  # TRIGGER

    def get_cell(self, cell_idx):

        return self.netlist[cell_idx]

    def get_wire(self, wire_name):

        return next(key for key in self.bit_wire_map.keys() if key.name == wire_name)

    def get_file_info(self, module, attributes_dict):
        filepath = ''
        filename = ''
        line_start = 0
        line_end = 0

        yosys_cell_src_str = None if not "\\src" in attributes_dict else attributes_dict["\\src"]

        if yosys_cell_src_str:
            filepath, line_nos = yosys_cell_src_str.decode_string().split(':')
            filename = Path(filepath).name
            line_start, line_end = line_nos.split('-')

        file_info = FileInfo(
            filepath=filepath,
            filename=filename,
            module=module.str().replace('\\', ''),
            lines=(float(line_start), float(line_end))
        )

        return file_info

    def to_pyg(self):

        graph = Data(

        )
        for key, val in self.signal_map.items():
            pass
