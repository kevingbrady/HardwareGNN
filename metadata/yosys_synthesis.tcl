yosys -import

set file_list $::env(input_files)
set top_module $::env(top_module)
set liberty_library_file $::env(liberty_library_file)
set liberty_verilog_file $::env(liberty_verilog_file)
set temp_verilog_file $::env(temp_verilog_file)
set gate_definitions_1 $::env(gate_definitions_1)
set gate_definitions_2 $::env(gate_definitions_2)

read_liberty -lib $liberty_library_file
read_verilog -lib $liberty_verilog_file
read_verilog $gate_definitions_1
read_verilog $gate_definitions_2

foreach f $file_list {
    read_verilog -sv $f
}

hierarchy -check -top $top_module
procs

memory_dff
memory_collect
memory_map

# Keep Trojan cells from being optimized out of final netlist
setattr -set keep 1 c:*
setattr -set keep 1 w:*

techmap
simplemap
opt -fast

# Technology mapping
dfflibmap -liberty $liberty_library_file
abc -keepff -liberty $liberty_library_file
opt -fast
clean

write_verilog -noexpr -norename $temp_verilog_file


