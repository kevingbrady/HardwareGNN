read_liberty $::env(liberty_library_file)
read_verilog $::env(temp_verilog_file)

set top_module $::env(top_module)
set artifacts $::env(artifacts)

link_design $top_module

set connections [dict create]
set scratch_file [open "scratch.txt" w]

# Hardcoded reference name extracted directly from the SkyWater Liberty path
set lib_name "sky130_fd_sc_hd__tt_025C_1v80"

foreach net [get_nets -hierarchical] {

    set net_name [get_property $net full_name]

    set pins [get_pins -quiet -of_objects $net]
    set drivers {}
    set sinks {}

    set fan_in 0
    set fan_out 0

    foreach pin $pins {

        set pin_name [get_property $pin full_name]
        set dir [get_property $pin direction]

        set is_clk 0
        if {[sta::is_clock $pin]} {
            set is_clk 1
        }

        set is_invert 0
        set pin_port_name [file tail $pin_name]
        set parent_cell [get_cells -of_objects $pin]

        if {$parent_cell != ""} {
            set lib_cell_name [get_property $parent_cell ref_name]
            set cell_lower [string tolower $lib_cell_name]
            set port_lower [string tolower $pin_port_name]

            # Condition A: It is an explicit inverting gate (inv, nand, nor)
            if {[string match "*inv*" $cell_lower] || \
                [string match "*nand*" $cell_lower] || \
                [string match "*nor*" $cell_lower]} {
                        set is_invert 1
            }

            # Condition B: It is the inverted output port of a register/flip-flop (e.g. QN)
            if {[string match "*qn*" $port_lower] || [string match "*q_n*" $port_lower]} {
                set is_invert 1
            }
        }

        set pin_data [list $pin_name $is_clk $is_invert]

        if {$dir eq "output"} {
            lappend drivers $pin_data
            incr fan_in
        }
        if {$dir eq "input"} {
            lappend sinks $pin_data
            incr fan_out
        }
    }

    foreach driver_data $drivers {
        foreach sink_data $sinks {

            set driver [lindex $driver_data 0]
            set sink [lindex $sink_data 0]
            set src_is_clk [lindex $driver_data 1]
            set dst_is_clk [lindex $sink_data 1]
            set src_is_invert [lindex $driver_data 2]
            set dst_is_invert [lindex $sink_data 2]

            set src_port [file tail $driver]
            set dst_port [file tail $sink]

            regsub -all {\[\d+\]} $src_port "" src_port
            regsub -all {\[\d+\]} $dst_port "" dst_port

            set driver_noport [file dirname $driver]
            set sink_noport [file dirname $sink]

            if { [file tail $driver_noport] in $artifacts } {
                set driver_noport [file dirname $driver_noport]
            }

            if { [file tail $sink_noport] in $artifacts } {
                set sink_noport [file dirname $sink_noport]
            }

            if { [string first {$} $driver_noport] != -1 } {
                set driver_cell_name [file dirname $driver_noport]
                if { $driver_cell_name eq "." } { set driver_cell_name "$top_module"
                } elseif { [string first $top_module $driver_cell_name] == -1 } { set driver_cell_name "$top_module/$driver_cell_name" }
            } else { set driver_cell_name "$top_module/$driver_noport" }

            if { [string first {$} $sink_noport] != -1 } {
                set sink_cell_name [file dirname $sink_noport]
                if { $sink_cell_name eq "." } { set sink_cell_name "$top_module"
                } elseif { [string first $top_module $sink_cell_name] == -1 } { set sink_cell_name "$top_module/$sink_cell_name" }
            } else { set sink_cell_name "$top_module/$sink_noport" }

            #if {$src_is_clk == 1 || $src_is_invert == 1 || $dst_is_clk == 1 || $dst_is_invert == 1} {
            #    puts $scratch_file "$driver_cell_name, $src_port, $src_is_clk, $src_is_invert, $sink_cell_name, $dst_port, $dst_is_clk, $dst_is_invert"
            #}
            set key_list [list $driver_cell_name $src_port $sink_cell_name $dst_port $src_is_clk $src_is_invert $dst_is_clk $dst_is_invert $fan_in $fan_out]

            if {![dict exists $connections $key_list]} {

                dict set connections $key_list 1

            } else {
                set conn_count [dict get $connections $key_list]
                dict set connections $key_list [expr {$conn_count + 1}]
            }
        }
    }
}

dict for {key width} $connections {

    set driver [lindex $key 0]
    set src_port [lindex $key 1]
    set sink [lindex $key 2]
    set dst_port [lindex $key 3]

    set src_is_clk [lindex $key 4]
    set src_is_invert [lindex $key 5]
    set dst_is_clk [lindex $key 6]
    set dst_is_invert [lindex $key 7]

    set fan_in [lindex $key 8]
    set fan_out [lindex $key 9]

    set output_string "$driver, $src_port, $sink, $dst_port, $src_is_clk, $src_is_invert, $dst_is_clk, $dst_is_invert, $fan_in, $fan_out, $width"
    puts $output_string
    #puts $scratch_file $output_string

}
