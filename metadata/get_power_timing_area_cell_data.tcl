set verilog_file "__temp_netlist.v"
set v_file_path [file join $working_dir $verilog_file]

read_liberty $liberty_file
read_verilog $v_file_path
link_design $top_module

# 1. Propagate design switching actions once
set_power_activity -input -activity 0.1

# If your netlist has an explicit clock port name (e.g., "clk"), use: [get_ports clk]
create_clock -name virtual_clk -period 10.0 [get_ports clk]

# 2. RUN BATCH TIMING AND POWER COMPUTATIONS (FAST SEPARATE PASSES)
set all_instances [get_cells -hierarchical *]

puts "=== START_POWER_DUMP ==="
report_power -instances $all_instances
puts "=== END_POWER_DUMP ==="

puts "=== START_TIMING_DUMP ==="
# Dump raw worst-case maximum arrival endpoints across all nodes
report_checks -path_delay max -fields {instance pin arrival} -format full -digits 4 -group_count 500000 -unconstrained
puts "=== END_TIMING_DUMP ==="

puts "=== START_INSTANCE_DATA ==="
# Map instance paths, cell types, and areas directly from the design library definitions
foreach inst $all_instances {
    set full_name [get_property $inst full_name]
    set lib_cell_obj [get_lib_cells -of_objects $inst]
    #set cell_type    [get_full_name $lib_cell_obj]
    #set cell_area    [get_property $lib_cell_obj area]

    if {$lib_cell_obj != "NULL" && $lib_cell_obj != ""} {
        set cell_type    [get_full_name $lib_cell_obj]
        set cell_area    [get_property $lib_cell_obj area]
        puts "CELL_RECORD,$full_name,$cell_type,$cell_area"
    }

    #puts "CELL_RECORD,$full_name,$cell_type,$cell_area"
}
puts "=== END_INSTANCE_DATA ==="

exit
