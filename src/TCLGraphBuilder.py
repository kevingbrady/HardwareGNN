from pathlib import Path
from src.verilog_dataclasses import Cell, Port, Net
from src.artifacts import artifacts
from src.errors import YosysSynthesisError, TCLError

import subprocess
import json
import os
import time

liberty_verilog_file = '/usr/local/share/pdk/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v'
liberty_library_path = '/usr/local/share/pdk/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'

class TCLGraph:

    def __init__(self, verilog_circuit_dir):
        super(TCLGraph, self).__init__()
        self.builder_start_time = time.time()
        self.builder_end_time = 0

        self.directory = verilog_circuit_dir
        self.silent = True
        self.top_module = None

        self.netlist: list[Cell] = []  # Nodes
        self.connections: list[Net] = []  # Edges

        self.input_files = self.get_input_files(verilog_circuit_dir)

    def get_cells_only(self):

        cells = []
        env = self.yosys_synthesis_pass()

        cell_data = f'{Path.cwd()}/metadata/get_cells_only.tcl'
        process = subprocess.Popen(['sta', '-no_splash', '-exit', cell_data], env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

        for idx, line in enumerate(process.stdout):
            cell = line.strip()
            cells.append(cell)

        os.remove(env['temp_verilog_file'])

        return cells


    def get_input_files(self, data_dir):

        input_files = []

        for file in Path(data_dir).rglob("*"):
            if file.suffix == '.v':
                filepath = str(file.absolute())
                if not filepath.__contains__('test') and not filepath.__contains__('tb'):
                    if file.name in ('aes_synth.v', '__temp_netlist.v'):
                        continue

                    input_files.append(filepath)

        return input_files

    def set_up_tcl_env(self):

        custom_env = os.environ.copy()

        custom_env["input_files"] = " ".join(self.input_files)
        custom_env["artifacts"] = " ".join(artifacts)
        custom_env["liberty_library_file"] = liberty_library_path
        custom_env["liberty_verilog_file"] = liberty_verilog_file
        custom_env["gate_definitions_1"] = f'{Path.cwd()}/metadata/gate_definitions_1.v'
        custom_env["gate_definitions_2"] = f'{Path.cwd()}/metadata/gate_definitions_2.v'
        custom_env["data_dir"] = f'{self.directory}'
        custom_env["temp_verilog_file"] = f'{self.directory}/__temp_netlist.v'

        return custom_env

    def low_level_design_pass(self):

        env = self.yosys_synthesis_pass()
        self.power_timing_area_pass(env)
        self.pin_pin_connection_pass(env)

        os.remove(env['temp_verilog_file'])

    def yosys_synthesis_pass(self):

        env = self.set_up_tcl_env()

        if not self.top_module:
            check_top_module = subprocess.run(['yosys', '-c', f'{Path.cwd()}/metadata/get_top_module.tcl'], env=env, text=True, capture_output=True)
            for line in check_top_module.stdout.splitlines():
                if "Automatically selected" in line:
                    line_break = line.split(' ')
                    self.top_module = line_break[2]

            env['top_module'] = self.top_module

        yosys_synthesis = f'{Path.cwd()}/metadata/yosys_synthesis.tcl'
        process = subprocess.run(["yosys", '-c', yosys_synthesis], env=env, text=True, capture_output=self.silent)

        if process.returncode != 0: raise YosysSynthesisError(process.stderr)
        return env

    def power_timing_area_pass(self, env):

        power_timing_area_data = f'{Path.cwd()}/metadata/get_power_timing_area_cell_data.tcl'
        process = subprocess.Popen(['sta', '-no_splash', '-exit', power_timing_area_data], env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

        for idx, line in enumerate(process.stdout):

            try:

                cell_data = [x.strip() for x in line.split(',', maxsplit=9)]

                cell = Cell(
                    idx=idx,
                    name=cell_data[0],
                    module=cell_data[8],
                    types=json.loads(cell_data[9]),
                    internal_power=float(cell_data[1]),
                    switching_power=float(cell_data[2]),
                    leakage_power=float(cell_data[3]),
                    total_power=float(cell_data[4]),
                    max_delay=float(cell_data[5]),
                    max_slew=float(cell_data[6]),
                    area=float(cell_data[7]),
                    ports=[]
                )

                self.netlist.append(cell)

            except IndexError as e:
                if not line.startswith('Warning'):
                    raise TCLError(line)

    def pin_pin_connection_pass(self, env):

        connection_data = f'{Path.cwd()}/metadata/bit_signal_map.tcl'
        process = subprocess.Popen(['sta', '-no_splash', '-exit', connection_data], env=env,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, bufsize=1)

        for line in process.stdout:

            try:
                conn_data = [x.strip() for x in line.split(',')]

                driver = self.get_cell(conn_data[0])
                src_port = driver.get_port(conn_data[1])

                sink = self.get_cell(conn_data[2])
                dst_port = sink.get_port(conn_data[3])

                if not src_port:
                    src_port = Port(name=conn_data[1], type='output')
                    driver.ports.append(src_port)

                if not dst_port:
                    dst_port = Port(name=conn_data[3], type='input')
                    sink.ports.append(dst_port)

                net = Net(
                    src=driver.idx,
                    dst=sink.idx,
                    src_port=src_port,
                    dst_port=dst_port,
                    fan_in=int(conn_data[4]),
                    fan_out=int(conn_data[5]),
                    width=int(conn_data[6])
                )

                driver.fan_out += net.fan_out
                sink.fan_in += net.fan_in

                self.connections.append(net)

            except AttributeError as e:
                if not line.startswith('Warning'):
                    raise TCLError(line)

    def get_trojan_cells(self):
        return [x.name for x in self.netlist if x.label == 1]

    def get_cell(self, cell_name):
        return next((cell for cell in self.netlist if cell.name == cell_name), None)

    def get_net(self, driver, sink, src_port, dst_port):
        for net in self.connections:
            if net.src == driver.idx and net.dst == sink.idx and net.src_port == src_port and net.dst_port == dst_port:
                return net
        return None
