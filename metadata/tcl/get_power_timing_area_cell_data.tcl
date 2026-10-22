set top_module $::env(top_module)
set artifacts $::env(artifacts)
set data_dir $::env(data_dir)

read_liberty $::env(liberty_library_file)
read_verilog $::env(temp_verilog_file)

read_lef $::env(tech_lef)
read_lef $::env(cell_lef)

link_design $top_module

source $::env(utils_file)

set all_instances [get_cells -hierarchical *]

set data [dict create]
set power_file "$data_dir/power_file.rpt"
set scratch_file [open "scratch.txt" w]


# ============================================================================
# PRIMARY I/O INITIALIZATION PASS (Captures ports as Graph Nodes)
# ============================================================================

foreach port [concat [all_inputs] [all_outputs]] {
    set port_name [get_name $port]
    set cell_name [get_mapped_cell_name $port_name $top_module $artifacts]

    # Initialize port entries: Area is 0.0, module type is flagged explicitly as "port"
    if { ![dict exists $data $cell_name] } {
        dict set data $cell_name [list 0.0 0.0 0.0 0.0 0.0 0.0 0.0 "primary i/o" [dict create]]
    }
}

# ============================================================================
# AREA/CELL TYPE PASS
# ============================================================================

foreach inst $all_instances {
    set instance [get_property $inst full_name]
    set type [get_property $inst ref_name]
    set lib_cell_obj [get_lib_cells -of_objects $inst]
    set cell_area 0.0

    set cell_name [get_mapped_cell_name $instance $top_module $artifacts]

    #puts $scratch_file "$instance,    $cell_name,     $type"

    if { $lib_cell_obj ni {"NULL" "" } } {
        set cell_area [get_property $lib_cell_obj area]
    }

    if { ![dict exists $data $cell_name] } {
        # Layout indices: 0:internal_p, 1:switching_p, 2:leakage_p, 3:total_p, 4:max_slew, 5:max_delay, 6:area, 7:module, 8:cell_type_dict
        dict set data $cell_name [list 0.0 0.0 0.0 0.0 0.0 0.0 $cell_area $type [dict create]]
    } else {

        set temp_list [dict get $data $cell_name]
        set p_total [lindex $temp_list 6]
        set cell_type_dict     [lindex $temp_list 8]

        set p_total [expr {$p_total + double($cell_area)}]

        if { [string first "sky130" $type] != -1 } {
            dict incr cell_type_dict $type
        } else {
            lset temp_list 7 $type
        }

        lset temp_list 6 $p_total
        lset temp_list 8 $cell_type_dict
        dict set data $cell_name $temp_list
    }
}

# ============================================================================
# POWER PASS
# ============================================================================

set power_pattern {^([0-9\.e\-+]+)\s+([0-9\.e\-+]+)\s+([0-9\.e\-+]+)\s+([0-9\.e\-+]+)\s+(\S+)$}

# 2. Capture the stdout report directly into a Tcl variable using string names
tee -quiet -variable power_report_content [list report_power -instances $all_instances -digits 6]

foreach line [split $power_report_content "\n"] {
    set trimmed_line [string trim $line]
    #puts $scratch_file $line
    if { [regexp $power_pattern $trimmed_line -> internal_power switching_power leakage_power total_power instance] } {
        set cell_name [get_mapped_cell_name $instance $top_module $artifacts]

        if { ![dict exists $data $cell_name] } {
            dict set data $cell_name [list 0.0 0.0 0.0 0.0 0.0 0.0 0.0 "" [dict create]]
        }

        set temp_list [dict get $data $cell_name]
        if { $internal_power  ne "" } { lset temp_list 0 [expr {double($internal_power)}] }
        if { $switching_power ne "" } { lset temp_list 1 [expr {double($switching_power)}] }
        if { $leakage_power   ne "" } { lset temp_list 2 [expr {double($leakage_power)}] }
        if { $total_power     ne "" } { lset temp_list 3 [expr {double($total_power)}] }
        dict set data $cell_name $temp_list
    }
}
unset power_report_content

# ============================================================================
# TIMING PASS
# ============================================================================


if { [info commands update_timing] ne "" } {
    update_timing
}

set timing_pattern {^\s*([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([v^])\s+(\S+)}

# Captures report stdout straight into 'timing_report_content' variable
# -quiet blocks it from printing to the log screen during execution
tee -quiet -variable timing_report_content {
    report_checks -path_delay max -fields {slew cap} -unconstrained -digits 6 -group_count 50000
}

# Iterate through lines in memory
foreach line [split $timing_report_content "\n"] {
    if { [regexp $timing_pattern $line match cap slew delay total_time edge instance] } {

        # Strip trailing pin components out safely
        set pin_tokens [split $instance "/"]
        set instance_clean [join [lrange $pin_tokens 0 end-1] "/"]
        set cell_name [get_mapped_cell_name $instance_clean $top_module $artifacts]

        if { [dict exists $data $cell_name] } {
            set temp_list [dict get $data $cell_name]
            set max_slew  [lindex $temp_list 4]
            set max_delay [lindex $temp_list 5]

            set slew [expr {double($slew)}]
            set delay [expr {double($delay)}]

            if {$slew > $max_slew}   { set max_slew $slew }
            if {$delay > $max_delay} { set max_delay $delay }

            lset temp_list 4 $max_slew
            lset temp_list 5 $max_delay
            dict set data $cell_name $temp_list
        }
    }
}

# Free memory explicitly when done processing large text blocks
unset timing_report_content

dict for {cell data_list} $data {
    set area [lindex $data_list 6]
    if {$area == 0.0} { continue }
    set parent_modules [split $cell "/"]

    # Traverse up the structural tree path slice by slice
    while { [llength $parent_modules] > 1 } {
        set instance_name [join [lrange $parent_modules 0 end-1] "/"]

        # If parent exists in our records, add the lower area to it
        if { [dict exists $data $instance_name] } {

            set temp_list [dict get $data $instance_name]
            set parent_module_type [lindex $temp_list 7]

             # Ensure we only bubble area into true hierarchical parent structures, not leaf cells
            if {$parent_module_type eq ""} {
                set module_area [lindex $temp_list 6]
                lset temp_list 6 [expr {$module_area + $area}]
                dict set data $instance_name $temp_list
            }
        }

        set parent_modules [lreplace $parent_modules 0 end-1]
    }
}

set print_list {}
dict for { cell data_list } $data {
    lappend print_list [linsert $data_list 0 $cell]
}

set sorted_totals [lsort -command compare_area_then_name $print_list]

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

    set output_string "\[CELL\], $cell_name, $internal_power, $switching_power, $leakage_power, $total_power, $max_slew, $max_delay, $area, $module, \{"

    set json_elements {}
    dict for { cell_type count } $cell_type_dict {
        lappend json_elements "\"$cell_type\": $count"
    }

    append output_string [join $json_elements ", "] "\}"
    puts $output_string
    #puts $scratch_file $output_string
}

close $scratch_file