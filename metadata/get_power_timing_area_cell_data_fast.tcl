set verilog_file "__temp_netlist.v"
set v_file_path [file join $working_dir $verilog_file]

read_liberty $liberty_file
read_verilog $v_file_path
link_design $top_module

# Propagate switching activities to compute actual power metrics
set_power_activity -input -activity 0.1

# 1. BULK INSTANCE EXTRACTION
# Isolate all design cells hierarchically once into an optimal Tcl handle
set all_instances [get_cells -hierarchical *]

# 2. INSTANT BATCH POWER DUMP
# Pass the full instance collection token into the -instances flag directly
puts "=== START_POWER_DUMP ==="
report_power -instances $all_instances
puts "=== END_POWER_DUMP ==="

# 3. INSTANT BATCH TIMING PIN DUMP
# Stream path checks concurrently using high-speed vectorized end-point constraints
puts "=== START_TIMING_DUMP ==="
report_checks -path_delay max -fields {instance pin arrival} -format full -digits 4 -group_count 500000
puts "=== END_TIMING_DUMP ==="

# 4. INSTANT BATCH AREA & MASTER CELL MATRIX
puts "=== START_AREA_DUMP ==="
foreach master_cell [get_lib_cells *] {
    set name [get_full_name $master_cell]
    set area [get_property $master_cell area]
    puts "LIB_CELL_MAP,$name,$area"
}
foreach inst $all_instances {
    set full_name [get_property $inst full_name]
    set lib_cell_obj [get_lib_cells -of_objects $inst]
    set cell_type    [get_full_name $lib_cell_obj]
    puts "INST_MAP,$full_name,$cell_type"
}
puts "=== END_AREA_DUMP ==="

exit