create_project sfu_eval ./sfu_eval_prj -part xcu50-fsvh2104-2-e -force
add_files {sfu_top.v sfu_lane.v}
add_files -fileset constrs_1 sfu_timing.xdc
update_compile_order -fileset sources_1
synth_design -top sfu_top -part xcu50-fsvh2104-2-e -retiming
report_utilization -file synth_utilization.txt
report_timing_summary -file synth_timing.txt
