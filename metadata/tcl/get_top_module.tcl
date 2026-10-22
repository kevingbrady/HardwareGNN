yosys -import

set file_list $::env(input_files)

foreach f $file_list {
    read_verilog -sv $f
}

hierarchy -check -auto-top