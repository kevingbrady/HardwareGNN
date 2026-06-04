import os
import re
import pyverilog.vparser.parser as parser
from pathlib import Path
from pyverilog.vparser.ast import ModuleDef, InstanceList


class VerilogParser:
    def __init__(self, verilog_data_dir):

        self.verilog_data_dir = verilog_data_dir
        self.file_list = []

        for file in Path(self.verilog_data_dir).rglob("*"):

            if file.suffix in ('.v', '.vhd'):
                filepath = str(file.absolute())
                if not filepath.__contains__('test'):
                    self.file_list.append(filepath)

        self.preprocessed_verilog_files = self.parse_verilog_files()

        self.ast, self.directives = self.generate_abstract_syntax_tree(self.preprocessed_verilog_files)
        self.top_module = self.find_implicit_top_module(self.ast)


    def parse_verilog_files(self):

        verilog_preprocessed_files = []
        pattern_commas = re.compile(r'(,)\s*(,)')
        pattern_paren = re.compile(r'(,)\s*(\))')

        for file in self.file_list:
            with open(file, 'r') as f:
                v_file = f.read()

                old_code = ""
                while old_code != v_file:
                    old_code = v_file
                    v_file = pattern_commas.sub(r'\1 pyverilog_dummy_net \2', v_file)
                v_file = pattern_paren.sub(r'\1 pyverilog_dummy_net \2', v_file)
                verilog_preprocessed_files.append(v_file)

        return verilog_preprocessed_files

    def generate_abstract_syntax_tree(self, verilog_preprocessed_files):

        ast, directives = parser.parse(verilog_preprocessed_files, outputdir=self.verilog_data_dir)

        os.remove(self.verilog_data_dir + '/parser.out')
        os.remove(self.verilog_data_dir + '/parsetab.py')

        return ast, directives

    def find_implicit_top_module(self, ast):

        defined_modules = set()
        instantiated_modules = set()

        for definition in ast.description.definitions:
            if isinstance(definition, ModuleDef):
                # Track every unique module definition block
                defined_modules.add(definition.name)

                # Look inside this module to see what it instantiates
                for item in definition.items:
                    if isinstance(item, InstanceList):
                        # Track the template module type being called
                        instantiated_modules.add(item.module)

        # The implicit top module is defined but never instantiated by anything
        top_modules = defined_modules - instantiated_modules

        if not top_modules:
            raise ValueError('No top-level module found (possible cyclic dependencies)')

        return list(top_modules)

