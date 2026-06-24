set verilog_file __temp_netlist.v
set v_file_path [file join $working_dir $verilog_file]

read_liberty $liberty_file
read_verilog $v_file_path
link_design $top_module


set all_instances [get_cells -hierarchical *]

foreach inst_obj $all_instances {

    # Extract the full hierarchical name string of the cell
    set inst_name [get_property -object_type cell $inst_obj name]
    set parent_module [get_property -object_type cell $inst_obj ref_name]

    # Get all pins belonging to this specific instance object
    set inst_pins [get_pins -of_objects $inst_obj]

    foreach pin_obj $inst_pins {
        # Grab the simple pin leaf name (e.g., "D", "Q", "A1")
        set pin_name [file tail [get_property $pin_obj name]]

        # Find the net object tied to this physical pin
        set connected_net [get_nets -of_objects $pin_obj]

        # Check if the pin is physically hooked up to a wire
        if {$connected_net != "" && $connected_net != "NULL"} {
            set hdl_signal_name [get_property $connected_net name]
        } else {
            # Mark clearly so your GNN graph builder knows it is a floating/dead-end pin
            set hdl_signal_name "UNCONNECTED"
        }

        # 3. Stream the entry straight to the CSV file
        puts "$parent_module,$inst_name,$pin_name,$hdl_signal_name"
    }
}

