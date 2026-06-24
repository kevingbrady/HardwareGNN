set verilog_file "__temp_netlist.v"
set v_file_path [file join $working_dir $verilog_file]

read_liberty $liberty_file
read_verilog $v_file_path
link_design $top_module

# 1. Propagate design switching actions once
set_power_activity -input -activity 0.1

# 2. RUN BATCH TIMING AND POWER COMPUTATIONS
set all_instances [get_cells -hierarchical *]
set sub_blocks [list]
foreach inst $all_instances {
    set full_name [get_property $inst full_name]

    if {![regexp {_\d+_|\$\d+$} $full_name]} {
        lappend sub_blocks $inst
    }
}

puts "=== START_POWER_DUMP ==="

set power_file "power_file.rpt"
report_power -instances $all_instances -digits 6 > $power_file

if {[file exists $power_file]} {
    set fp [open $power_file r]

    while {[gets $fp line] >= 0} {
        if {![regexp {_\d+_|\$\d+$} $line]} {
            #puts "$line"
        }
    }
    close $fp
    file delete -force $power_file

} else {
     puts "Error: Failed to generate power report"
}

puts "=== END_POWER_DUMP ==="

puts "=== START_TIMING_DUMP ==="
# Uncomment if needed; fixed the syntax for OpenSTA compatibility
# report_checks -path_delay max -fields {slew cap input_pins nets fanout} -digits 6 -group_count 10000
puts "=== END_TIMING_DUMP ==="

puts "=== START_INSTANCE_DATA ==="

set area_totals [dict create]

foreach inst $all_instances {

    set c_name [get_property $inst full_name]
    set lib_cell_obj [get_lib_cells -of_objects $inst]


    if {$lib_cell_obj != "NULL" && $lib_cell_obj != ""} {

        set c_area [get_property $lib_cell_obj area]

        # Extract the high-level group name before any $ or _ or space
        if {[regexp {^([^$_]*)[$_](.*)$}  $c_name -> instance cell]} {

             # Check if we already have an entry for this group, default to 0.0
            if {![dict exists $area_totals $instance]} {
                dict set area_totals $instance 0.0
            }

            # Accumulate the float area value
            set current_total [dict get $area_totals $instance]
            set new_total [expr {$current_total + $c_area}]
            dict set area_totals $instance $new_total
        }
    }
}

# Print the final aggregated results
puts "--- Higher Level Cell Area Totals ---"
dict for {cell total} $area_totals {

    puts [format "%-15s : %.6f" $cell $total]
}
