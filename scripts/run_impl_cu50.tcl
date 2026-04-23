
create_project sfu_impl_cu50 ./sfu_impl_cu50_prj -part xcu50-fsvh2104-2-e -force
add_files {../src/sfu_top.v ../src/sfu_lane.v}
add_files -fileset constrs_1 ../xdc/sfu_timing_cu50.xdc
synth_design -top sfu_top -part xcu50-fsvh2104-2-e -retiming -mode out_of_context
opt_design
place_design
phys_opt_design
route_design
report_utilization -file ../vivadoreport/impl_utilization_cu50.txt
report_timing_summary -file ../vivadoreport/impl_timing_cu50.txt
