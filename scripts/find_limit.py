import subprocess
import os
import re

def run_impl(part, period, project_name, tcl_file, xdc_file, report_prefix):
    # Determine the project root relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    xdc_path = os.path.join(root_dir, "xdc", xdc_file)
    reports_dir = os.path.join(root_dir, "reports")

    with open(xdc_path, "w") as f:
        f.write(f"create_clock -period {period:.3f} -name i_clk [get_ports i_clk]\n")

    tcl_content = f"""
create_project {project_name} ./{project_name}_prj -part {part} -force
add_files {{../src/sfu_top.v ../src/sfu_lane.v}}
add_files -fileset constrs_1 ../xdc/{xdc_file}
synth_design -top sfu_top -part {part} -retiming -mode out_of_context
opt_design
place_design
phys_opt_design
route_design
report_utilization -file ../reports/{report_prefix}_util.txt
report_timing_summary -file ../reports/{report_prefix}_timing.txt
"""
    tcl_path = os.path.join(script_dir, tcl_file)
    with open(tcl_path, "w") as f: f.write(tcl_content)

    print(f"Starting {project_name} with period {period:.3f}ns...")
    subprocess.run([r"D:\Xilinx\Vivado\2024.2\bin\vivado.bat", "-mode", "batch", "-source", tcl_path], check=True, cwd=script_dir)

    timing_report = os.path.join(reports_dir, f"{report_prefix}_timing.txt")
    with open(timing_report, "r") as f:
        content = f.read()
        match = re.search(r"WNS\(ns\)\s+TNS\(ns\)\s+.*\n-+\s+.*\n\s+(-?\d+\.\d+)", content)
        if match:
            wns = float(match.group(1))
            return wns
    return -999.0

# Initial guesses based on previous fail/pass
# U50: Passed at 2.02 (WNS +0.101). Try 1.92
# Z7020: Failed at 6.50 (WNS -0.196). Try 6.75

os.makedirs("vivadoreport", exist_ok=True)

print("--- Iterating U50 ---")
u50_period = 2.02
while True:
    wns = run_impl("xcu50-fsvh2104-2-e", u50_period, "sfu_impl_cu50", "run_impl_cu50.tcl", "sfu_timing_cu50.xdc", "impl_cu50")
    print(f"U50 Period {u50_period:.3f} -> WNS {wns:.3f}")
    if wns > 0.05: # Have slack, tighten
        u50_period -= wns - 0.01
    elif wns < 0: # Failed, relax
        u50_period += abs(wns) + 0.05
    else: # 0 < wns < 0.05, close enough
        break
    if u50_period < 1.0: break # Safety

print("--- Iterating Z7020 ---")
z7020_period = 6.50 + 0.196 + 0.1 # Start at 6.8 approx
while True:
    wns = run_impl("xc7z020clg400-1", z7020_period, "sfu_impl_z7020", "run_impl_z7020.tcl", "sfu_timing_z7020.xdc", "impl_z7020")
    print(f"Z7020 Period {z7020_period:.3f} -> WNS {wns:.3f}")
    if wns > 0.1: # Have slack, tighten
        z7020_period -= wns - 0.02
    elif wns < 0: # Failed, relax
        z7020_period += abs(wns) + 0.1
    else: # 0 < wns < 0.1
        break
    if z7020_period > 10.0: break # Safety
