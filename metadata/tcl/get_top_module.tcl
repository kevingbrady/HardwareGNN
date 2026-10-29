yosys -import

eval read_verilog -sv $::env(input_files)
hierarchy -check -auto-top