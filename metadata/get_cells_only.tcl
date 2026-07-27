read_liberty $::env(liberty_library_file)
read_verilog $::env(temp_verilog_file)

set top_module $::env(top_module)
set artifacts $::env(artifacts)
set data_dir $::env(data_dir)

link_design $top_module

set all_instances [get_cells -hierarchical *]
set data [dict create]

foreach inst $all_instances {
    set instance [get_property $inst full_name]
    set end [file tail $instance]

    if {$end in $artifacts} {
       set instance [file dirname $instance]
    }

    if { [string first {$} $instance] != -1 } {
       set cell_name [file dirname $instance]
       if { $cell_name eq "." } { set cell_name "$top_module"
       } elseif { [string first $top_module $cell_name] == -1 } { set cell_name "$top_module/$cell_name" }
    } else { set cell_name "$top_module/$instance"}

    dict set data $cell_name 1
}

dict for {cell n} $data {
    puts "$cell"
}