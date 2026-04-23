import sys
import subprocess
import math
import os
import shutil

def from_hex(hex_str, bits=16, signed=True):
    val = int(hex_str, 16)
    if signed and val >= (1 << (bits - 1)): val -= (1 << bits)
    return val

def to_hex(val, bits=16):
    if val < 0: val = (1 << bits) + val
    return f"{val:0{bits//4}X}"

def gelu(x): return 0.5 * x * (1 + math.erf(x / math.sqrt(2)))
def silu(x): return x / (1 + math.exp(-x))

print("Starting Stress Test Verification...")

print("Copying test data to root for simulation...")
for f in ["exp_cfg.hex", "gelu_cfg.hex", "silu_cfg.hex", "exp_in.hex", "gelu_in.hex", "silu_in.hex"]:
    shutil.copy(os.path.join("tb", f), f)

# 1. Run the Multi-Slot Simulation
# The sfu_tb.v already tests switching slots 0->1->2
# We'll use the existing test_multi_slot.py logic but focus on reporting PASS/FAIL

print("Running Vivado XSIM simulation...")
# Note: we need to run from the root or provide correct relative paths
# Let's adjust paths for this execution
subprocess.run([r"D:\Xilinx\Vivado\2024.2\bin\xvlog.bat", "src/sfu_top.v", "src/sfu_lane.v", "tb/sfu_tb.v"], check=True)
subprocess.run([r"D:\Xilinx\Vivado\2024.2\bin\xelab.bat", "sfu_tb", "-s", "sfu_sim", "-debug", "typical"], check=True)
subprocess.run([r"D:\Xilinx\Vivado\2024.2\bin\xsim.bat", "sfu_sim", "-R"], check=True)

# 2. Performance & Accuracy Analysis
def check_func(name, math_func, out_scale, is_signed_out=True):
    out_file = f"{name}_out.txt"
    if not os.path.exists(out_file):
        print(f"FAILED: {out_file} not generated.")
        return False
    
    with open(out_file) as f: lines = f.readlines()
    max_err = 0
    total = 0
    for line in lines:
        if not line.strip(): continue
        parts = line.split()
        if 'x' in parts[0].lower() or 'x' in parts[1].lower(): continue
        x = from_hex(parts[0], 16, True) / 4096.0
        y = from_hex(parts[1], 16, is_signed_out) / out_scale
        math_y = math_func(x)
        err = abs(y - math_y)
        max_err = max(max_err, err)
        total += 1
    
    print(f"Function {name.upper()}: Tested {total} samples.")
    print(f"  -> Max Absolute Error: {max_err:.8f}")
    if max_err < 0.0015: # Standard NPLA tolerance for 16-bit
        print(f"  -> ACCURACY STATUS: [PASS]")
        return True
    else:
        print(f"  -> ACCURACY STATUS: [FAIL] (Error too high)")
        return False

exp_pass = check_func("exp", math.exp, 32768.0, is_signed_out=False)
gelu_pass = check_func("gelu", gelu, 4096.0, is_signed_out=True)
silu_pass = check_func("silu", silu, 4096.0, is_signed_out=True)

if exp_pass and gelu_pass and silu_pass:
    print("\nOVERALL MODULE PERFORMANCE VERIFICATION: [SUCCESS]")
else:
    print("\nOVERALL MODULE PERFORMANCE VERIFICATION: [FAILED]")

print("Cleanup temporary files...")
for f in ["exp_cfg.hex", "gelu_cfg.hex", "silu_cfg.hex", "exp_in.hex", "gelu_in.hex", "silu_in.hex"]:
    if os.path.exists(f): os.remove(f)
