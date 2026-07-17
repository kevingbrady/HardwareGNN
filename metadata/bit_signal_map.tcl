read_liberty $::env(liberty_library_file)
read_verilog $::env(temp_verilog_file)

set top_module $::env(top_module)
set artifacts $::env(artifacts)

link_design $top_module

set connections [dict create]
set scratch_file [open "scratch.txt" w]

foreach net [get_nets -hierarchical] {

    set net_name [get_property $net full_name]
    set fan_in 0
    set fan_out 0

    set pins [get_pins -quiet -of_objects $net]
    set drivers {}
    set sinks {}

    foreach pin $pins {
        set pin_name [get_property $pin full_name]
        set dir [get_property $pin direction]

        if {$dir eq "output"} {
            lappend sinks $pin_name
            incr fan_in
        }
        if {$dir eq "input"} {
            lappend drivers $pin_name
            incr fan_out
        }
    }

    foreach driver $drivers {
        foreach sink $sinks {

            set src_port [file tail $driver]
            set dst_port [file tail $sink]

            regsub -all {\[\d+\]} $src_port "" src_port
            regsub -all {\[\d+\]} $dst_port "" dst_port

            set driver_noport [file dirname $driver]
            set sink_noport [file dirname $sink]

            if {[file tail $driver_noport] in $artifacts} {
                set driver_noport [file dirname $driver_noport]
            }

            if {[file tail $sink_noport] in $artifacts} {
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

            set key_list [list $driver_cell_name $src_port $sink_cell_name $dst_port]

            if {![dict exists $connections $key_list]} {

                set temp_list [list 1 $fan_in $fan_out]
                dict set connections $key_list $temp_list

            } else {
                set temp_list [dict get $connections $key_list]
                set conn_count [lindex $temp_list 0]
                set temp_list [lreplace $temp_list 0 0 [expr {$conn_count + 1}]]
                dict set connections $key_list $temp_list
            }
        }
    }
}

dict for {key data_list} $connections {

    set driver [lindex $key 0]
    set src_port [lindex $key 1]
    set sink [lindex $key 2]
    set dst_port [lindex $key 3]

    set width [lindex $data_list 0]
    set fan_in [lindex $data_list 1]
    set fan_out [lindex $data_list 2]

    set output_string "$driver, $src_port, $sink, $dst_port, $fan_in, $fan_out, $width"
    puts $output_string
    puts $scratch_file $output_string

}

close $scratch_file
