from pyosys.libyosys import PortDir, SigSpec
from torch.utils.data import Dataset
from torch_geometric.data import Data
from pyosys import libyosys as yosys
from pathlib import Path
from src.utils import compact_dir, get_bit_key
from src.cell_mappings import GATE_ROLE_MAP, CUSTOM_MODULE_ROLE_MAP, CONST_STATE_MAP
from src.verilog_dataclasses import Cell, Port, Wire, Bit, Signal
import pprint


class HardwareFileDataset(Dataset):

    def __init__(self, data_dir):
        super(HardwareFileDataset, self).__init__()
        self.silent = True
        self.top_module = None
        self.num_cells = 0

        self.netlist = []  # Nodes
        self.bit_wire_map = {
            Wire(name='GND', width=1, wire_lineno=(0,0)): {PortDir.PD_INPUT: [], PortDir.PD_OUTPUT: []},
            Wire(name='VCC', width=1, wire_lineno=(0, 0)): {PortDir.PD_INPUT: [], PortDir.PD_OUTPUT: []},
            Wire(name='UNCONNECTED_X', width=1, wire_lineno=(0, 0)): {PortDir.PD_INPUT: [], PortDir.PD_OUTPUT: []},
            Wire(name='UNCONNECTED_Z', width=1, wire_lineno=(0, 0)): {PortDir.PD_INPUT: [], PortDir.PD_OUTPUT: []},
            Wire(name='DONT_CARE_MARKER', width=1, wire_lineno=(0, 0)): {PortDir.PD_INPUT: [], PortDir.PD_OUTPUT: []},
            Wire(name='INTERNAL_PASS_MARKER', width=1, wire_lineno=(0, 0)): {PortDir.PD_INPUT: [], PortDir.PD_OUTPUT: []}
        }

        self.signal_map = {}

        self.extract_netlist(data_dir)
        self.build_signal_map()

    def extract_netlist(self, data_dir):

        yosys.yosys_setup()
        design = yosys.Design()
        modules_file_mapping = {}

        tee = 'tee -q ' if self.silent else ''

        for file in Path(data_dir).rglob("*"):

            if file.suffix in ('.v', '.vhd'):
                filepath = str(file.absolute())
                if not filepath.__contains__('test'):
                    design.run_pass(f'{tee}read_verilog {filepath}')

        design.run_pass(f'{tee}hierarchy -auto-top')
        design.run_pass(f'{tee} proc')
        design.run_pass(f'{tee}synth -run coarse')  # Map complex math/blocks to basic gate structures
        design.run_pass(f'{tee}opt')  # Clean up redundant internal Yosys cells

        design.run_pass(f'{tee} techmap')
        design.run_pass(f'{tee} opt')
        design.run_pass(f'{tee}abc -g gates')  # Map to generic standard logic gates
        design.run_pass(f'{tee} opt')

        self.top_module = design.top_module()
        self.num_cells = len(self.top_module.cells_)

        idx = 0
        cell_types = set()

        for module_name, module in design.modules_.items():

            #module_filepath, module_filename, module_line_start, module_line_end = self.get_attribute_info(module.attributes)
            #modules_file_mapping[(module_filename, module_line_start, module_line_end)] = module_name.str()

            for wire_id, yosys_wire in module.wires_.items():
                (
                    wire_filepath,
                    wire_filename,
                    wire_line_start,
                    wire_line_end
                ) = self.get_attribute_info(yosys_wire.attributes)

                wire = Wire(
                    name=str(yosys_wire.name).replace('\\', ''),
                    width=yosys_wire.width,
                    wire_lineno=(wire_line_start, wire_line_end)
                )
                self.bit_wire_map[wire] = {PortDir.PD_INPUT: [], PortDir.PD_OUTPUT: []}


            for cell_id, yosys_cell in module.cells_.items():

                (
                    cell_filepath,
                    cell_filename,
                    cell_line_start,
                    cell_line_end) = self.get_attribute_info(yosys_cell.attributes)

                #cell_module = self.get_module(cell_filename, cell_line_start, cell_line_end, modules_file_mapping)

                cell_name = yosys_cell.name.str().replace('\\', '')
                cell_type = yosys_cell.type.str().replace('\\', '')
                cell_module = module_name.str().replace('\\', '')

                cell = Cell(
                    idx=idx,
                    name=cell_name,
                    type=cell_type,
                    filename=cell_filename,
                    module=cell_module,
                    cell_lineno=(cell_line_start, cell_line_end),
                    fan_in=0,
                    fan_out=0,
                    label=0
                )

                port_gate_role_map = GATE_ROLE_MAP.get(cell.type, CUSTOM_MODULE_ROLE_MAP)
                cell_types.add(cell.type)

                #print(idx, cell.module, cell.name, cell.type)

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
                        name=port_str,
                        type=port_gate_role_map.get(port_str, port_customtype_str),
                        direction=direction
                    )

                    print(module.name, cell.name, port.name, port.type)

                    for sig_bit in sig_spec.bits():
                        offset = sig_bit.offset

                        if sig_bit.is_wire():

                            key = str(sig_bit.wire.name).replace('\\', '')
                            #print(self.get_wire(key), f'{module_name}.{cell.name}.{port.name} {port.type}')
                            wire = self.get_wire(key)
                            bit = Bit.from_wire(wire, offset, port, cell)

                        else:

                            const = CONST_STATE_MAP.get(sig_bit.data)
                            wire = self.get_wire(const)
                            bit = Bit(
                                    name=const,
                                    width=1,
                                    offset=offset,
                                    wire_lineno=(0,0),
                                    port=port,
                                    cell=cell)

                        self.bit_wire_map[wire][port.direction].append(bit)
                self.netlist.append(cell)
                idx += 1
        #print(cell_types)
        #pprint.pprint(self.bit_map, width=1)

    def build_signal_map(self):

        for wire, entries in self.bit_wire_map.items():
            for driver, sink in zip(entries[PortDir.PD_INPUT], entries[PortDir.PD_OUTPUT]):

                driver_str = f'{driver.cell.module}.{driver.cell.name}.{driver.port.name}.{driver.name}.{driver.offset}'
                sink_str = f'{sink.cell.module}.{sink.cell.name}.{sink.port.name}.{sink.name}.{sink.offset}'
                #print((driver_str, sink_str))
                self.signal_map[(driver_str, sink_str)] = Signal(src=driver, dst=sink, wire=wire)

            #print(wire.name, driver_cells, sink_cells)
        #print('Nodes:', len(self.netlist), 'Edges:', len(self.signal_map))


    def get_wire(self, wire_name):

        return next(key for key in self.bit_wire_map.keys() if key.name == wire_name)

    def get_module(self, filename, line_start, line_end, modules_file_mapping):
        return next((val.replace('\\', '') for (m_filename, m_line_start, m_line_end), val in modules_file_mapping.items() if
             filename == m_filename and m_line_start <= line_start <= m_line_end), None)

    def get_attribute_info(self, attributes_dict):
        filepath = ''
        filename = ''
        line_start = 0
        line_end = 0

        yosys_cell_src_str = None if not "\\src" in attributes_dict else attributes_dict["\\src"]

        if yosys_cell_src_str:
            filepath, line_nos = yosys_cell_src_str.decode_string().split(':')
            filename = Path(filepath).name
            line_start, line_end = line_nos.split('-')

        return filepath, filename, float(line_start), float(line_end)

    def to_pyg(self):

        graph = Data(

        )
        for key, val in self.signal_map.items():
            pass
