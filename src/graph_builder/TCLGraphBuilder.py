from pathlib import Path
from src.graph_builder.verilog_dataclasses import Cell, Port, Net
from src.graph_builder.artifacts import artifacts
from src.graph_builder.errors import YosysSynthesisError, TCLError
from metadata.module_translator.ModuleTranslator import ModuleTranslator
from torch_geometric.data import Data
import torch
import subprocess
import json
import os
import time

pdk_base = '/usr/local/share/pdk/sky130A/libs.ref/sky130_fd_sc_hd'

tech_lef = f'{pdk_base}/techlef/sky130_fd_sc_hd__nom.tlef'
cell_lef = f'{pdk_base}/lef/sky130_fd_sc_hd.lef'

liberty_verilog_file = f'{pdk_base}/verilog/sky130_fd_sc_hd.v'
liberty_primitives_file =  f'{pdk_base}/verilog/primitives.v'
liberty_library_file = f'{pdk_base}/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'

class TCLGraph:

    def __init__(self, verilog_circuit_dir):
        super(TCLGraph, self).__init__()
        self.builder_start_time = time.time()
        self.builder_end_time = 0

        self.directory = verilog_circuit_dir
        self.silent = True
        self.top_module = None
        #self.module_translator = MacroGenerator()
        self.module_translator = ModuleTranslator()

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
                if not filepath.lower().__contains__('test') and not filepath.lower().__contains__('tb'):
                    if file.name in ('aes_synth.v', '__temp_netlist.v'):
                        continue

                    input_files.append(filepath)

        return input_files

    def set_up_tcl_env(self):

        custom_env = os.environ.copy()
        macro_filepath = f'{self.directory}/macro_list.v'
        #self.module_translator.write_macro_definitions(self.input_files, macro_filepath)
        self.module_translator.write_macro_definitions(self.input_files, macro_filepath)

        custom_env["input_files"] = " ".join(self.input_files)
        custom_env["artifacts"] = " ".join(artifacts)
        custom_env["tech_lef"] = tech_lef
        custom_env['cell_lef'] = cell_lef
        custom_env['liberty_verilog_file'] = liberty_verilog_file
        custom_env['liberty_primitives_file'] = liberty_primitives_file
        custom_env['liberty_library_file'] = liberty_library_file
        custom_env['utils_file'] = f'{Path.cwd()}/metadata/tcl/utils.tcl'
        custom_env['macro_list'] = macro_filepath
        custom_env["data_dir"] = f'{self.directory}'
        custom_env["temp_verilog_file"] = f'{self.directory}/__temp_netlist.v'

        return custom_env

    def low_level_design_pass(self):

        env = self.yosys_synthesis_pass()
        self.power_timing_area_pass(env)
        self.pin_pin_connection_pass(env)

        os.remove(env['macro_list'])
        os.remove(env['temp_verilog_file'])

    def yosys_synthesis_pass(self):

        env = self.set_up_tcl_env()

        if not self.top_module:

            check_top_module = subprocess.run(['yosys', '-c', f'{Path.cwd()}/metadata/tcl/get_top_module.tcl'], env=env,
                                              text=True, capture_output=True)
            raw_top = ''
            for line in check_top_module.stdout.splitlines():
                if "Automatically selected" in line and "as design top module" in line:
                    # Line format: "Automatically selected $abstract\regfile_tb as design top module."
                    line_break = line.split(' ')
                    raw_top = line_break[2]  # This gets "$abstract\regfile_tb"

                    # Strip out Yosys internal prefixes, backslashes, or punctuation
                    raw_top = raw_top.replace("$abstract\\", "").replace("\\", "").strip(".")
                    break
            env['top_module'] = raw_top

        yosys_synthesis = f'{Path.cwd()}/metadata/tcl/yosys_synthesis.tcl'
        process = subprocess.run(["yosys", '-c', yosys_synthesis], env=env, text=True, capture_output=True)

        if process.returncode != 0: raise YosysSynthesisError(process.stderr)
        return env

    def power_timing_area_pass(self, env):

        power_timing_area_data = f'{Path.cwd()}/metadata/tcl/get_power_timing_area_cell_data.tcl'
        #power_timing_area_data = f'{Path.cwd()}/metadata/tcl/cell_data_aggregator.tcl'

        process = subprocess.Popen(['openroad', '-no_splash', '-exit', power_timing_area_data], env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        cell_idx = 0

        for line in process.stdout:

            try:
                
                cell_data = [x.strip() for x in line.split(',', maxsplit=11)]

                power = {
                    'internal_power': float(cell_data[2]),
                    'switching_power': float(cell_data[3]),
                    'leakage_power': float(cell_data[4]),
                    'total_power': float(cell_data[5])
                }

                timing = {
                    'max_delay': float(cell_data[6]),
                    'max_slew': float(cell_data[7])
                }

                area = float(cell_data[8])

                cell = Cell(
                    idx=cell_idx,          # PyG requires 0 based indexing
                    name=cell_data[1],
                    module=cell_data[10],
                    types=json.loads(cell_data[11]),
                    power=power,
                    timing=timing,
                    area=area,
                    logic_depth=int(cell_data[9]),
                    ports={}
                )

                self.netlist[cell.name] = cell
                cell_idx += 1

            except (AttributeError, IndexError, ValueError) as e:
                if line.lower().__contains__('error'):
                    raise TCLError(line)

    def pin_pin_connection_pass(self, env):

        connection_data = f'{Path.cwd()}/metadata/tcl/bit_signal_map.tcl'
        process = subprocess.Popen(['openroad', '-no_splash', '-exit', connection_data], env=env,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, bufsize=1)

        for line in process.stdout:

            try:
                conn_data = [x.strip() for x in line.split(',', maxsplit=11)]

                driver = self.get_cell(conn_data[1])
                sink = self.get_cell(conn_data[3])

                src_port = driver.get_port(conn_data[2])
                dst_port = sink.get_port(conn_data[4])

                src_is_clk = int(conn_data[5])
                src_is_invert = int(conn_data[6])
                dst_is_clk = int(conn_data[7])
                dst_is_invert = int(conn_data[8])

                if not src_port:
                    src_port = Port(name=conn_data[2], type='output', is_clk=src_is_clk, is_invert=src_is_invert, parent_cell=driver)
                    driver.ports[src_port.name] = src_port

                if not dst_port:
                    dst_port = Port(name=conn_data[4], type='input', is_clk=dst_is_clk, is_invert=dst_is_invert, parent_cell=sink)
                    sink.ports[dst_port.name] = dst_port

                fan_in = int(conn_data[9])
                fan_out = int(conn_data[10])
                width = int(conn_data[11])

                driver.fanout['sum'] += fan_out
                driver.fanout['max'] = max(driver.fanout['max'], fan_out)
                driver.width_metrics['out_width_sum'] += width
                driver.total_sinks += 1

                #if driver.combinational_density > 0.85 and sink.combinational_density > 0.85:
                #sink.in_degree += 1

                sink.fanin['sum'] += fan_in
                sink.fanin['max'] = max(sink.fanin['max'], fan_in)
                sink.width_metrics['in_width_sum'] += width
                sink.total_drivers += 1

                driver_fanout_to_sink_fanin_ratio = driver.fanout['sum'] / sink.fanin['sum'] if sink.fanin['sum'] > 0 else 0.0

                net = Net(
                    driver=(driver.idx, driver.name),
                    sink=(sink.idx, sink.name),
                    src_port=src_port,
                    dst_port=dst_port,
                    fan_in=fan_in,
                    fan_out=fan_out,
                    driver_fanout_to_sink_fanin_ratio=driver_fanout_to_sink_fanin_ratio,
                    width=width
                )

                self.connections.append(net)

            except (AttributeError, IndexError) as e:
                #print(e)
                if line.lower().__contains__('error'):
                    raise TCLError(line)

    def get_trojan_cells(self):
        return [x.name for x in self.netlist.values() if x.label == 1]


    def get_cell(self, cell_name):
        return self.netlist.get(cell_name, None)


    def to_pyg(self):

        node_features = []
        labels = []
        type_lengths = []
        type_indices = []
        type_counts = []

        for cell in self.netlist.values():

            fanin = cell.get_fanin_metrics()
            fanout = cell.get_fanout_metrics()
            width_metrics = cell.get_width_metrics()

            node_features.append([
                cell.power['internal_power'],
                cell.power['leakage_power'],
                cell.power['switching_power'],
                cell.power['total_power'],
                cell.timing['max_slew'],
                cell.timing['max_delay'],
                cell.area,
                cell.total_drivers,
                cell.total_sinks,
                cell.combinational_density,
                cell.sequential_density,
                cell.is_hybrid,
                cell.logic_depth,
                fanin['sum'],
                fanin['max'],
                fanin['mean'],
                fanout['sum'],
                fanout['max'],
                fanout['mean'],
                width_metrics['in_width_mean'],
                width_metrics['out_width_mean']
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
        src_nodes, dst_nodes = zip(*[(net.driver[0], net.sink[0]) for net in self.connections])
        edge_index_tensor = torch.tensor([src_nodes, dst_nodes], dtype=torch.long).contiguous()

        # Vectorized feature generation for edges
        edge_features = []

        for net in self.connections:

            edge_features.append([
                net.src_port.class_idx,
                net.dst_port.class_idx,
                net.src_port.is_clk,
                net.src_port.is_invert,
                net.src_port.is_sequential,
                net.dst_port.is_clk,
                net.dst_port.is_invert,
                net.dst_port.is_sequential,
                net.driver_fanout_to_sink_fanin_ratio,
                net.fan_in,
                net.fan_out,
                net.width
            ])

        edge_attr_tensor = torch.tensor(edge_features, dtype=torch.float32)

        graph = Data(
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
