from pyosys.libyosys import PortDir, SigSpec
from torch.utils.data import Dataset
from torch_geometric.data import Data
from pyosys import libyosys as yosys
from pathlib import Path
from src.utils import compact_dir, output_manager
from src.cell_mappings import GATE_ROLE_MAP, CUSTOM_MODULE_ROLE_MAP, CONST_STATE_MAP
from src.verilog_dataclasses import Cell, Port, Wire, FileInfo

import subprocess
import json

liberty_file_path = '/usr/local/share/pdk/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_100C_1v80.lib'


# liberty_file_path = '/usr/local/share/pdk/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v'

class HardwareFileDataset(Dataset):

    def __init__(self, data_dir):
        super(HardwareFileDataset, self).__init__()

        self.silent = True
        self.top_module = None
        self.num_cells = 0

        self.netlist: list[Cell] = []  # Nodes
        self.connections: list[Wire] = []  # Edges

        self.design = self.extract_behavioral_design(data_dir)
        self.low_level_design_pass()  # Flatten netlist to get power/timing/area info for each cell/ bit-bit connection
        print('Nodes: ', len(self.netlist), ', Edges: ', len(self.connections))

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

            self.top_module = design.top_module()

        return design

    def low_level_design_pass(self):

        # Flattens netlist to be able to be run with sta to get low level power, timing, and area info
        with output_manager(silent=self.silent):

            self.design.run_pass('keep_hierarchy')

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

        tcl_args = f'''set ::top_module "{self.top_module.name.str().replace('\\', '')}"\nset ::liberty_file "{liberty_file_path}"\nset ::working_dir "{Path.cwd()}"'''
    
        power_data = f'source "{Path.cwd()}/metadata/get_power_timing_area_cell_data.tcl"'
        edge_data = f'source "{Path.cwd()}/metadata/bit_signal_map.tcl"'

        tcl_command = tcl_args + '\n' + power_data
        command = [
            "bash", "-c",
            f'sta -no_splash -exit <(echo "{tcl_command}")',
        ]

        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        for idx, line in enumerate(process.stdout):
            cell_data = [x.strip() for x in line.split(',', maxsplit=8)]

            cell = Cell(
                idx=idx,
                name=cell_data[0],
                types=json.loads(cell_data[8]),
                internal_power=float(cell_data[1]),
                switching_power=float(cell_data[2]),
                leakage_power=float(cell_data[3]),
                total_power=float(cell_data[4]),
                max_delay=float(cell_data[5]),
                max_slew=float(cell_data[6]),
                area=float(cell_data[7]),
                ports=[],
                label=0
            )

            self.netlist.append(cell)

        tcl_command = tcl_args + '\n' + edge_data
        command = [
            "bash", "-c",
            f'sta -no_splash -exit <(echo "{tcl_command}")',
        ]

        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        for line in process.stdout:
            conn_data = [x.strip() for x in line.split(',')]

            driver = self.get_cell(conn_data[0])
            src_port = conn_data[1]

            sink = self.get_cell(conn_data[2])
            dst_port = conn_data[3]

            if src_port not in driver.ports:
                driver.ports.append(Port(name=src_port, type='input'))

            if dst_port not in sink.ports:
                sink.ports.append(Port(name=dst_port, type='output'))

            wire = Wire(
                src=driver.idx,
                src_port=src_port,
                dst=sink.idx,
                dst_port=dst_port,
                fan_in=int(conn_data[4]),
                fan_out=int(conn_data[5]),
                width=int(conn_data[6])
            )

            self.connections.append(wire)

    def get_cell(self, cell_name):

        return next((cell for cell in self.netlist if cell.name == cell_name), None)

    def get_wire(self, wire_name):

        pass

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

