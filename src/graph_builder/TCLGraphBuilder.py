from pathlib import Path
from src.graph_builder.verilog_dataclasses import Cell, Port, Net
from src.graph_builder.artifacts import artifacts
from src.graph_builder.errors import YosysSynthesisError, TCLError
from torch_geometric.data import Data
from torch.nn import Sequential, Linear, EmbeddingBag

import torch
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

        self.netlist: dict[str, Cell] = {}  # Nodes
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
            check_top_module = subprocess.run(['yosys', '-c', f'{Path.cwd()}/metadata/get_top_module.tcl'], env=env,
                                              text=True, capture_output=True)
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

        cell_idx = 0

        for line in process.stdout:

            try:

                cell_data = [x.strip() for x in line.split(',', maxsplit=9)]

                cell = Cell(
                    idx=cell_idx,          # PyG requires 0 based indexing
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
                    ports={}
                )

                self.netlist[cell.name] = cell
                cell_idx += 1

            except (AttributeError, IndexError) as e:
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
                sink = self.get_cell(conn_data[2])

                if not driver:
                    driver = self.create_dummy_cell(conn_data[0])

                if not sink:
                    sink = self.create_dummy_cell(conn_data[2])

                src_port = driver.get_port(conn_data[1])
                dst_port = sink.get_port(conn_data[3])

                if not src_port:
                    src_port = Port(name=conn_data[1], type='output')
                    driver.ports[src_port.name] = src_port

                if not dst_port:
                    dst_port = Port(name=conn_data[3], type='input')
                    sink.ports[dst_port.name] = dst_port

                net = Net(
                    src=driver.idx,
                    dst=sink.idx,
                    src_port=src_port,
                    dst_port=dst_port,
                    fan_in=int(conn_data[4]),
                    fan_out=int(conn_data[5]),
                    width=int(conn_data[6])
                )

                self.connections.append(net)

            except (AttributeError, IndexError) as e:
                if not line.startswith('Warning'):
                    raise TCLError(line)

    def create_dummy_cell(self, cell_name):
        cell = Cell(
            idx=len(self.netlist) + 1,
            name=cell_name,
            module='',
            types={},
            internal_power=0,
            switching_power=0,
            leakage_power=0,
            total_power=0,
            max_delay=0,
            max_slew=0,
            area=0,
            ports={}
        )

        self.netlist[cell.name] = cell

        return cell

    def get_trojan_cells(self):
        return [x.name for x in self.netlist.values() if x.label == 1]


    def get_cell(self, cell_name):
        return self.netlist.get(cell_name, None)


    def get_net(self, driver, sink, src_port, dst_port):
        for net in self.connections:
            if net.src == driver.idx and net.dst == sink.idx and net.src_port == src_port and net.dst_port == dst_port:
                return net
        return None


    def to_pyg(self):
        node_features = []
        labels = []
        type_lengths = []
        type_indices = []
        type_counts = []

        for cell in self.netlist.values():
            node_features.append([
                cell.internal_power, cell.leakage_power, cell.switching_power,
                cell.total_power, cell.max_slew, cell.max_delay, cell.area
            ])

            labels.append(cell.label)

            type_lengths.append(len(cell.get_type_ids()))
            type_indices.extend(cell.get_type_ids())
            type_counts.extend(cell.get_type_counts_vector())

        if len(type_indices) != len(type_counts):
            raise Exception(f"Length of 'type_indices' is {len(type_indices)} and Length of 'type_counts' is {len(type_counts)} in directory {self.directory}")


        node_features_tensor = torch.tensor(node_features, dtype=torch.float32)
        label_tensor = torch.tensor(labels, dtype=torch.long)

        # ZIP extracts columns instantly instead of looping index by index
        # This extracts src and dst into two separate lists at C-speed
        src_nodes, dst_nodes = zip(*[(net.src, net.dst) for net in self.connections])
        edge_index_tensor = torch.tensor([src_nodes, dst_nodes], dtype=torch.long).contiguous()

        # Vectorized feature generation for edges
        edge_features = [
            [
                net.src_port.get_index(),
                net.dst_port.get_index(),
                net.fan_in,
                net.fan_out,
                net.width
            ]
            for net in self.connections
        ]
        edge_attr_tensor = torch.tensor(edge_features, dtype=torch.float32)

        graph =  Data(
            x=node_features_tensor,
            edge_index=edge_index_tensor,
            edge_attr=edge_attr_tensor,
            y=label_tensor,

            type_indices=torch.tensor(type_indices, dtype=torch.long),
            type_counts=torch.tensor(type_counts, dtype=torch.float32),
            type_lengths=torch.tensor(type_lengths, dtype=torch.long)
        )
        try:
            graph.validate(raise_on_error=True)
        except ValueError as e:
            custom_message = {
                f"\nGraph Validation Error\n"
                f"File: {self.directory}\n"
                f"Graph Nodes: {len(self.netlist)} Graph Edges: {len(self.connections)}\n"
                f"Graph Edge Index Min ID: {graph.edge_index.min()}\n"
                f"Graph Edge Index Max ID: {graph.edge_index.max()}\n"
                f"Error: {e}\n"
            }

            raise ValueError(custom_message) from e

        return graph
