

proc get_mapped_cell_name {instance top_module artifacts} {
    regsub -all {\[\d+\]} $instance "" instance

    set hierarchy_list [split $instance "/"]
    set end [lindex $hierarchy_list end]

    # 1. First, check if the leaf element is an artifact or a connection bit (e.g., _13_)
    # This regex matches strings that start with an underscore, followed by numbers, ending with an underscore
    if {$end in $artifacts || [regexp {^_\d+_$} $end]} {
        # Trim the suffix out of the list
        set hierarchy_list [lrange $hierarchy_list 0 end-1]
        set instance [join $hierarchy_list "/"]
    }

    # 2. Structural variable handling ($ characters)
    if { [string first {$} $instance] != -1 } {
        set tokens [split $instance "/"]
        set cell_name [join [lrange $tokens 0 end-1] "/"]

        if { $cell_name eq "" || $cell_name eq "." } {
            set cell_name "$top_module"
        } elseif { [string first $top_module $cell_name] == -1 } {
            set cell_name "$top_module/$cell_name"
        }
    } else {
        set cell_name "$top_module/$instance"
    }
    return $cell_name
}

proc compare_area_then_name {a b} {
    set area_a [lindex $a 7]
    set area_b [lindex $b 7]

    if {$area_a > $area_b} { return -1 }
    if {$area_a < $area_b} { return 1 }

    set name_a [lindex $a 0]
    set name_b [lindex $b 0]
    return [string compare -nocase $name_a $name_b]
}

proc compute_netlist_logic_depths {top_module artifacts} {
    set raw_cell_depths [dict create]
    set net_depths      [dict create]

    set net_drivers [dict create]
    set cell_inputs [dict create]
    set cell_outputs [dict create]
    set cell_is_buf_inv [dict create]
    set cell_is_sequential [dict create] ;# Added to track sequential boundaries via string matching

    set consolidated_cell_depths [dict create]

    # 1. BULK IN-MEMORY CAPTURE (Query the database exactly once)
    foreach cell [get_cells -hierarchical *] {
        set cell_name [get_property $cell full_name]
        dict set raw_cell_depths $cell_name 0
        dict set cell_inputs $cell_name {}
        dict set cell_outputs $cell_name {}

        # Safely identify cell attributes via master reference names to avoid instance property crashes
        set ref_name [get_property $cell ref_name]
        set ref_lower [string tolower $ref_name]

        # A. Detect Sequential Cells (Flip-Flops / Latches) via standard library naming patterns
        set is_seq 0
        if {[string match "*flop*" $ref_lower] || [string match "*dff*" $ref_lower] || \
            [string match "*dfx*" $ref_lower] || [string match "*msff*" $ref_lower] || \
            [string match "*latch*" $ref_lower]} {
            set is_seq 1
        }
        dict set cell_is_sequential $cell_name $is_seq

        # B. Detect Buffers / Inverters
        set lib_cell [get_lib_cells -quiet -of_objects $cell]
        set is_buf_or_inv 0
        if {$lib_cell != ""} {
            set is_buffer [get_property $lib_cell is_buffer]
            set is_inverter [get_property $lib_cell is_inverter]
            if {$is_buffer eq "true" || $is_inverter eq "true"} {
                set is_buf_or_inv 1
            }
        } else {
            set is_buf_or_inv 1
        }
        dict set cell_is_buf_inv $cell_name $is_buf_or_inv
    }

    # Map nets to their structural driving cells/ports
    foreach net [get_nets -hierarchical] {
        set net_name [get_property $net full_name]
        dict set net_depths $net_name 0
        dict set net_drivers $net_name {}

        foreach pin [get_pins -quiet -of_objects $net] {
            set parent_cell [get_cells -quiet -of_objects $pin]
            if {$parent_cell == ""} { continue }
            set cell_name [get_property $parent_cell full_name]
            set dir [get_property $pin direction]

            if {$dir eq "output"} {
                dict lappend net_drivers $net_name $cell_name
                dict lappend cell_outputs $cell_name $net_name
            } elseif {$dir eq "input"} {
                dict lappend cell_inputs $cell_name $net_name
            }
        }

        foreach port [get_ports -quiet -of_objects $net] {
            if {[get_property $port direction] eq "input"} {
                dict lappend net_drivers $net_name "CHIP_INPUT"
            }
        }
    }

    # 2. PURE TCL IN-MEMORY PROPAGATION SWEEP (Hyper-fast, loop-aware)
    set changed 1
    set iteration 0
    set max_iterations 100 ;# Higher limit is safe now because loops will be broken

    while {$changed && ($iteration < $max_iterations)} {
        set changed 0
        incr iteration

        # Update all net depths based on their driving cells
        dict for {net_name drivers} $net_drivers {
            set max_d 0
            foreach drv $drivers {
                if {$drv eq "CHIP_INPUT"} { continue }

                # CRITICAL LOOP BREAKER: If the driving cell is a sequential flip-flop,
                # its output Q pin initializes a brand new timing path startpoint (Depth = 0)
                if {[dict get $cell_is_sequential $drv] == 1} {
                    set d 0
                } else {
                    set d [dict get $raw_cell_depths $drv]
                }

                if {$d > $max_d} { set max_d $d }
            }
            if {$max_d > [dict get $net_depths $net_name]} {
                dict set net_depths $net_name $max_d
                set changed 1
            }
        }

        # Update all cell depths based on their input nets
        dict for {cell_name input_nets} $cell_inputs {
            # Skip updating logic depths for sequential elements themselves (registers stay at depth 0)
            if {[dict get $cell_is_sequential $cell_name] == 1} { continue }

            set max_in_d 0
            foreach net $input_nets {
                set d [dict get $net_depths $net]
                if {$d > $max_in_d} { set max_in_d $d }
            }

            set is_buf_or_inv [dict get $cell_is_buf_inv $cell_name]
            set calculated_depth $max_in_d
            if {!$is_buf_or_inv} {
                incr calculated_depth
            }

            if {$calculated_depth > [dict get $raw_cell_depths $cell_name]} {
                dict set raw_cell_depths $cell_name $calculated_depth
                set changed 1
            }
        }
    }

    # ============================================================================
    # CONSOLIDATION & REDUCTION STEP
    # ============================================================================
    dict for {raw_cell_name depth} $raw_cell_depths {
        set consolidated_name [get_mapped_cell_name $raw_cell_name $top_module $artifacts]

        if {![dict exists $consolidated_cell_depths $consolidated_name]} {
            dict set consolidated_cell_depths $consolidated_name $depth
        } else {
            set current_max [dict get $consolidated_cell_depths $consolidated_name]
            if {$depth > $current_max} {
                dict set consolidated_cell_depths $consolidated_name $depth
            }
        }
    }

    return $consolidated_cell_depths
}
