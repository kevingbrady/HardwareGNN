set verilog_file __temp_netlist.v
set v_file_path [file join $working_dir $verilog_file]

read_liberty $liberty_file
read_verilog $v_file_path
link_design $top_module

set connections [dict create]

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

            regsub -all {\[\d+\]} $driver "" clean_driver_pin
            regsub -all {\[\d+\]} $sink "" clean_sink_pin

            regsub -all {\$[a-zA-Z0-9_\.:\\[\d+\]]*} $clean_driver_pin "" clean_driver_pin
            regsub -all {\$[a-zA-Z0-9_\.:\\[\d+\]]*} $clean_sink_pin "" clean_sink_pin


            set key_list [list $clean_driver_pin $clean_sink_pin]

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

    set driver [file dirname [lindex $key 0]]
    set sink [file dirname [lindex $key 1]]

    set src_port [string map {"/" ""} [file tail [lindex $key 0]]]
    set dst_port [string map {"/" ""} [file tail [lindex $key 1]]]
    set width [lindex $data_list 0]
    set fan_in [lindex $data_list 1]
    set fan_out [lindex $data_list 2]

    puts "$driver, $src_port, $sink, $dst_port, $fan_in, $fan_out, $width"

}

