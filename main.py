import os
import circuitgraph
from pyosys import libyosys as yosys
from pathlib import Path
from torch_geometric.utils import from_networkx
from torch_geometric.data import Data
from src.VerilogParser import VerilogParser
from src.DataFlowGraph import DataFlowGraph
from src.HardwareFileDataset import HardwareFileDataset

if __name__ == '__main__':

    data_dir = '/home/kgb/PycharmProjects/HardwareGNN/data/decompressed/AES-T100/src/TjIn'
    #circuit_info = VerilogParser(data_dir)
    dataset = HardwareFileDataset(data_dir)



    #data_graph = DataFlowGraph(circuit_info.ast)
    #print(data_graph)

