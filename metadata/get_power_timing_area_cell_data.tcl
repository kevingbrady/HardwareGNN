read_liberty $::env(liberty_library_file)
read_verilog $::env(temp_verilog_file)

set top_module $::env(top_module)
set artifacts $::env(artifacts)
set data_dir $::env(data_dir)

link_design $top_module

set all_instances [get_cells -hierarchical *]
set data [dict create]
set clk_port [get_ports -quiet clk]

set_power_activity -input -activity 0.1
create_clock -name virtual_clk -period 10.0 $clk_port

set power_file "$data_dir/power_file.rpt"
#set scratch_file [open "scratch.txt" a]

report_power -instances $all_instances -digits 6 > $power_file
set power_pattern {^([0-9\.e\-+]+)\s+([0-9\.e\-+]+)\s+([0-9\.e\-+]+)\s+([0-9\.e\-+]+)\s+(\S+)$}

if {[file exists $power_file]} {
    set fp [open $power_file r]

    while {[gets $fp line] >= 0} {
        set trimmed_line [string trim $line]
        #puts $scratch_file $line
        if { [regexp $power_pattern $trimmed_line -> internal_power switching_power leakage_power total_power instance] } {

            set end [file tail $instance]

            if {$end in $artifacts} {
                set instance [file dirname $instance]
            }

            if { [string first {$} $instance] != -1 } {
                set cell_name [file dirname $instance]
                if { $cell_name eq "." } { set cell_name "$top_module"
                } elseif { [string first $top_module $cell_name] == -1 } { set cell_name "$top_module/$cell_name" }
            } else { set cell_name "$top_module/$instance" }

            if { ![dict exists $data $cell_name] } {
                set temp_list [list 0.0 0.0 0.0 0.0 0.0 0.0 0.0 "" [dict create]]
                if { $internal_power ne "" } { lset temp_list 0 $internal_power }
                if { $switching_power ne "" } { lset temp_list 1 $switching_power }
                if { $leakage_power ne "" } { lset temp_list 2 $leakage_power }
                if { $total_power ne "" } { lset temp_list 3 $total_power }
                dict set data $cell_name $temp_list
            }

        }
    }
    close $fp
    file delete -force $power_file

}

set timing_file "$data_dir/timing_file.rpt"
set timing_pattern {^\s*([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([v^])\s+(\S+)}

report_checks -path_delay max -fields {slew cap} -unconstrained -digits 6 -group_count 10000 > $timing_file
set file_handle [open $timing_file r]

while { [gets $file_handle line] >= 0 } {
    if { [regexp $timing_pattern $line match cap slew delay total_time edge instance] } {

        # Remove port value
        set instance [file dirname $instance]
        set end [file tail $instance]

        if {$end in $artifacts} {
            set instance [file dirname $instance]
        }

        set slew [expr {double($slew)}]
        set delay [expr {double($delay)}]

         if { [string first {$} $instance] != -1 } {
                set cell_name [file dirname $instance]
                if { $cell_name eq "." } { set cell_name "$top_module"
                } elseif { [string first $top_module $cell_name] == -1 } { set cell_name "$top_module/$cell_name" }
            } else { set cell_name "$top_module/$instance" }

        if { [dict exists $data $cell_name] } {
            set temp_list [dict get $data $cell_name]
            set max_slew [lindex $temp_list 4]
            set max_delay [lindex $temp_list 5]

            if {$slew > $max_slew} { set max_slew $slew }
            if {$delay > $max_delay} { set max_delay $delay }

            lset temp_list 4 $max_slew
            lset temp_list 5 $max_delay

            dict set data $cell_name $temp_list
        }
    }
}

close $file_handle
file delete -force $timing_file

foreach inst $all_instances {

    set instance [get_property $inst full_name]
    set end [file tail $instance]
    set type [get_property $inst ref_name]
    set lib_cell_obj [get_lib_cells -of_objects $inst]
    set cell_area 0.0

    #puts $scratch_file "$instance, $type"

    if {$end in $artifacts} {
       set instance [file dirname $instance]
    }

    if { [string first {$} $instance] != -1 } {
       set cell_name [file dirname $instance]
       if { $cell_name eq "." } { set cell_name "$top_module"
       } elseif { [string first $top_module $cell_name] == -1 } { set cell_name "$top_module/$cell_name" }
    } else { set cell_name "$top_module/$instance"}

    if { $lib_cell_obj ni {"NULL" "" } } { set cell_area [get_property $lib_cell_obj area]}

    set temp_list [dict get $data $cell_name]
    set p_total [lindex $temp_list 6]
    set cell_type_dict [lindex $temp_list 8]

    set p_total [expr {$p_total + $cell_area}]


    if { [string first "sky130" $type] != -1 } {
        dict incr cell_type_dict $type
    } else { lset temp_list 7 $type }

    lset temp_list 6 $p_total
    lset temp_list 8 $cell_type_dict

    dict set data $cell_name $temp_list
}

dict for {cell data_list} $data {
    set area [lindex $data_list 6]
    set parent_modules [split $cell "/"]

    # Traverse up the structural tree path slice by slice
    while { [llength $parent_modules] > 1 } {
        set instance_name [join [lrange $parent_modules 0 end-1] "/"]

        # If parent exists in our records, add the lower area to it
        if { [dict exists $data $instance_name] } {

            set temp_list [dict get $data $instance_name]
            set module_area [lindex $temp_list 6]

            lset temp_list 6 [expr {$module_area + $area}]

            dict set data $instance_name $temp_list
        }

        set parent_modules [lreplace $parent_modules end end]
    }
}

set print_list {}
dict for { cell data_list } $data {

    set internal_power [lindex $data_list 0]
    set switching_power [lindex $data_list 1]
    set leakage_power [lindex $data_list 2]
    set total_power [lindex $data_list 3]
    set max_slew [lindex $data_list 4]
    set max_delay [lindex $data_list 5]
    set area [lindex $data_list 6]
    set module [lindex $data_list 7]
    set cell_type_dict [lindex $data_list 8]

    lappend print_list [list $cell $internal_power $switching_power $leakage_power $total_power $max_slew $max_delay $area $module $cell_type_dict]
}

set sort_by_area [lsort -decreasing -real -index 7 $print_list]
set sorted_totals [lsort -dictionary -index 0 $sort_by_area]

foreach entry $sorted_totals {

    set cell_name [lindex $entry 0]
    set internal_power [lindex $entry 1]
    set switching_power [lindex $entry 2]
    set leakage_power [lindex $entry 3]
    set total_power [lindex $entry 4]
    set max_slew [lindex $entry 5]
    set max_delay [lindex $entry 6]
    set area [lindex $entry 7]
    set module [lindex $entry 8]
    set cell_type_dict [lindex $entry 9]

    set output_string "$cell_name, $internal_power, $switching_power, $leakage_power, $total_power, $max_slew, $max_delay, $area, $module, \{"

    set json_elements {}
    dict for { cell_type count } $cell_type_dict {
        lappend json_elements "\"$cell_type\": $count"
    }

    append output_string [join $json_elements ", "] "\}"
    puts $output_string
    #puts $scratch_file $output_string
}

#close $scratch_file