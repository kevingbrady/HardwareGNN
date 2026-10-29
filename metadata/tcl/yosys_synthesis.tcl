yosys -import

set file_list $::env(input_files)
set top_module $::env(top_module)
set liberty_library_file $::env(liberty_library_file)
set liberty_verilog_file $::env(liberty_verilog_file)
set temp_verilog_file $::env(temp_verilog_file)
set macro_list $::env(macro_list)

read_liberty -lib $liberty_library_file
read_verilog -lib -sv $liberty_verilog_file
read_verilog $macro_list

eval read_verilog -sv $::env(input_files)

setattr -set keep 1 c:*
setattr -set keep 1 w:*

prep -top $top_module
alumacc

techmap
simplemap
#opt -fast

# Technology mapping
dfflibmap -liberty $liberty_library_file
abc -keepff -liberty $liberty_library_file
#clean

# Keep Trojan cells from being optimized out of final netlist

write_verilog -noexpr -norename $temp_verilog_file



