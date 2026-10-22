set top_module $::env(top_module)
set artifacts $::env(artifacts)
set data_dir $::env(data_dir)

read_liberty $::env(liberty_library_file)
read_verilog $::env(temp_verilog_file)

read_lef $::env(tech_lef)
read_lef $::env(cell_lef)

link_design $top_module

source $::env(utils_file)
set connections [dict create]
#set scratch_file [open "scratch.txt" w]


foreach net [get_nets -hierarchical] {

    set net_name [get_property $net full_name]

    set pins [get_pins -quiet -of_objects $net]
    set ports [get_ports -quiet -of_objects $net]

    set drivers {}
    set sinks {}

    set fan_in 0
    set fan_out 0

    # ============================================================================
    # PROCESS INTERNAL CELL PINS
    # ============================================================================
    foreach pin $pins {
        set pin_name [get_property $pin full_name]
        set dir [get_property $pin direction]
        set is_clk [get_property $pin is_register_clock]

        set is_invert 0
        set pin_tokens [split $pin_name "/"]
        set pin_port_name [lindex $pin_tokens end]
        set parent_cell [get_cells -quiet -of_objects $pin]

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

        # Type tag "pin" identifies internal nodes
        set pin_data [list $pin_name $is_clk $is_invert "pin"]

        if {$dir eq "output"} {
            lappend drivers $pin_data
            incr fan_in
        }
        if {$dir eq "input"} {
            lappend sinks $pin_data
            incr fan_out
        }
    }

    # ============================================================================
    # PROCESS PRIMARY INPUTS/OUTPUTS (PORTS)
    # ============================================================================
    foreach port $ports {
        set port_name [get_property $port full_name]
        set dir [get_property $port direction]

        # Ports themselves don't have register clocks or internal inversions
        set is_clk 0
        set is_invert 0

        # Type tag "port" isolates primary I/O boundary nodes
        set port_data [list $port_name $is_clk $is_invert "port"]

        # CRITICAL DIRECTION SWAP:
        # A primary chip input drives internal logic (Source/Driver)
        # A primary chip output is driven by internal logic (Sink/Load)
        if {$dir eq "input"} {
            lappend drivers $port_data
            incr fan_in
        }
        if {$dir eq "output"} {
            lappend sinks $port_data
            incr fan_out
        }
    }

    # ============================================================================
    # CROSS-PRODUCT DRIVERS TO SINKS
    # ============================================================================

    foreach driver_data $drivers {
        foreach sink_data $sinks {

            set driver [lindex $driver_data 0]
            set src_is_clk [lindex $driver_data 1]
            set src_is_invert [lindex $driver_data 2]
            set src_type      [lindex $driver_data 3]

            set sink [lindex $sink_data 0]
            set dst_is_clk [lindex $sink_data 1]
            set dst_is_invert [lindex $sink_data 2]
            set dst_type      [lindex $sink_data 3]

            # Normalize Driver naming depending on whether it's a Port or a Pin
            if {$src_type eq "port"} {
                set src_port "IN"
                set driver_cell_name [get_mapped_cell_name $driver $top_module $artifacts]
            } else {
                set driver_tokens [split $driver "/"]
                set src_port [lindex $driver_tokens end]
                regsub -all {\[\d+\]} $src_port "" src_port
                set driver_noport [join [lrange $driver_tokens 0 end-1] "/"]
                set driver_cell_name [get_mapped_cell_name $driver_noport $top_module $artifacts]
            }

            # Normalize Sink naming depending on whether it's a Port or a Pin
            if {$dst_type eq "port"} {
                set dst_port "OUT"
                set sink_cell_name [get_mapped_cell_name $sink $top_module $artifacts]
            } else {
                set sink_tokens [split $sink "/"]
                set dst_port [lindex $sink_tokens end]
                regsub -all {\[\d+\]} $dst_port "" dst_port
                set sink_noport [join [lrange $sink_tokens 0 end-1] "/"]
                set sink_cell_name [get_mapped_cell_name $sink_noport $top_module $artifacts]
            }

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

    set output_string "\[NET\], $driver, $src_port, $sink, $dst_port, $src_is_clk, $src_is_invert, $dst_is_clk, $dst_is_invert, $fan_in, $fan_out, $width"
    puts $output_string
    #puts $scratch_file $output_string

}
