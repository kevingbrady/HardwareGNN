set verilog_file "__temp_netlist.v"
set v_file_path [file join $working_dir $verilog_file]

read_liberty $liberty_file
read_verilog $v_file_path
link_design $top_module

set all_instances [get_cells -hierarchical *]
set data [dict create]

set pattern {^(?:(.+)/)?([^$_][^/]*)$}
set clk_port [get_ports -quiet clk]

set_power_activity -input -activity 0.1
create_clock -name virtual_clk -period 10.0 $clk_port

set power_file "power_file.rpt"
report_power -instances $all_instances -digits 6 > $power_file

if {[file exists $power_file]} {
    set fp [open $power_file r]

    while {[gets $fp line] >= 0} {
        if {[regexp $pattern $line]} {
            set power_list [split $line " "]

            set internal_power [lindex $power_list 1]
            set switching_power [lindex $power_list 2]
            set leakage_power [lindex $power_list 3]
            set total_power [lindex $power_list 4]
            set cell_name [string trim [lindex $power_list 5]]

            if {$cell_name eq "Internal"} {
                continue
            }

            if {[regexp $pattern $cell_name] && ![dict exists $data $cell_name]} {
                set temp_list [list $internal_power $switching_power $leakage_power $total_power 0 0 0 [dict create]]
                dict set data $cell_name $temp_list
            }

        }
    }
    close $fp
    file delete -force $power_file

}

set timing_file "timing_file.rpt"
report_checks -path_delay max -fields {slew cap} -unconstrained -digits 6 -group_count 10000 > $timing_file

if {[file exists $timing_file]} {
    set fp [open $timing_file r]

    while {[gets $fp line] >= 0} {
        if {[regexp $pattern $line]} {
            set timing_list [regexp -all -inline {\S+} $line]

            set slew [lindex $timing_list 1]
            set delay [lindex $timing_list 2]
            set pin_name [lindex $timing_list 5]

            if {[regexp {^([^$]+)/} $pin_name -> instance_name cell_name]} {

                if {[dict exists $data $instance_name]} {

                    set temp_list [dict get $data $instance_name]
                    set max_slew [lindex $temp_list 4]
                    set max_delay [lindex $temp_list 5]

                      # Perform numeric comparisons safely
                    if {[string is double -strict $slew] && $slew > $max_slew} { set max_slew $slew }
                    if {[string is double -strict $delay] && $delay > $max_delay} { set max_delay $delay }

                    # UPDATED: Packed the worst_slack back into index 6
                    lset temp_list 4 $max_slew
                    lset temp_list 5 $max_delay

                    dict set data $instance_name $temp_list
                }
            }

        }
    }
    close $fp
    file delete -force $timing_file

}


foreach inst $all_instances {
    set c_name [get_property $inst full_name]
    set c_type [get_property $inst ref_name]
    if {$c_type eq ""} { set c_type "None"}

    set instance_name [string trimright [file dirname $c_name] "/"]
    set lib_cell_obj [get_lib_cells -of_objects $inst]
    set cell_area 0.0

    if {$lib_cell_obj != "NULL" && $lib_cell_obj != ""} {

        set cell_area [get_property $lib_cell_obj area]

    set temp_list [dict get $data $instance_name]
    set p_total [lindex $temp_list 6]
    set cell_type_dict [lindex $temp_list 7]

    set p_total [expr {$p_total + $cell_area}]
    dict incr cell_type_dict $c_type

    lset temp_list 6 $p_total
    lset temp_list 7 $cell_type_dict

    dict set data $instance_name $temp_list

    }
}

dict for {cell data_list} $data {
    set area [lindex $data_list 6]
    set parent_modules [split $cell "/"]

    # Traverse up the structural tree path slice by slice
    while {[llength $parent_modules] > 1} {
        set instance_name [join [lrange $parent_modules 0 end-1] "/"]

        # If parent exists in our records, add the lower area to it
        if {[dict exists $data $instance_name]} {

            set temp_list [dict get $data $instance_name]
            set module_area [lindex $temp_list 6]

            lset temp_list 6 [expr {$module_area + $area}]

            dict set data $instance_name $temp_list

        }

        set parent_modules [lreplace $parent_modules end end]
    }
}

set print_list {}
dict for {cell data_list} $data {

    set internal_power [lindex $data_list 0]
    set switching_power [lindex $data_list 1]
    set leakage_power [lindex $data_list 2]
    set total_power [lindex $data_list 3]
    set max_slew [lindex $data_list 4]
    set max_delay [lindex $data_list 5]
    set area [lindex $data_list 6]
    set cell_type_dict [lindex $data_list 7]

    lappend print_list [list $cell $internal_power $switching_power $leakage_power $total_power $max_slew $max_delay $area $cell_type_dict]
}

set sorted_area_totals [lsort -decreasing -real -index 7 $print_list]

foreach entry $sorted_area_totals {

    set cell_name [lindex $entry 0]
    set internal_power [lindex $entry 1]
    set switching_power [lindex $entry 2]
    set leakage_power [lindex $entry 3]
    set total_power [lindex $entry 4]
    set max_slew [lindex $entry 5]
    set max_delay [lindex $entry 6]
    set area [lindex $entry 7]
    set cell_type_dict [lindex $entry 8]

    set output_string "$cell_name, $internal_power, $switching_power, $leakage_power, $total_power, $max_slew, $max_delay, $area, \{"

    set json_elements {}
    dict for {cell_type count} $cell_type_dict {
        lappend json_elements "\"$cell_type\": $count"
    }

    append output_string [join $json_elements ", "] "\}"
    puts $output_string
}
