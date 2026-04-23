
create_project sfu_impl_z7020 ./sfu_impl_z7020_prj -part xc7z020clg400-1 -force
add_files {../src/sfu_top.v ../src/sfu_lane.v}
add_files -fileset constrs_1 ../xdc/sfu_timing_z7020.xdc
synth_design -top sfu_top -part xc7z020clg400-1 -retiming -mode out_of_context
opt_design
place_design
phys_opt_design
route_design
report_utilization -file ../vivadoreport/impl_utilization_z7020.txt
report_timing_summary -file ../vivadoreport/impl_timing_z7020.txt
