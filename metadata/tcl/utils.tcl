

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

