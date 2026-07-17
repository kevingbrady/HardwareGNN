import os
import sys
from src.VerilogGraphDataset import VerilogGraphDataset

if __name__ == '__main__':

    if sys._is_gil_enabled():
        print('GIL is enabled (not free-threaded)')
    else:
        print('GIL is disabled (free-threaded)')

    data_dir = '/home/kgb/PycharmProjects/HardwareGNN/data/decompressed'     #/AES-T100/src/TjIn'
    dataset = VerilogGraphDataset(data_dir)
