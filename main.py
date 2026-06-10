import os
from src.VerilogParser import VerilogParser
from src.HardwareFileDataset import HardwareFileDataset

if __name__ == '__main__':

    data_dir = '/home/kgb/PycharmProjects/HardwareGNN/data/decompressed/AES-T100/src/TjIn'
    dataset = HardwareFileDataset(data_dir)
