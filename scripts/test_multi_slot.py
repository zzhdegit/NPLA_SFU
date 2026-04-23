import os, sys, random, math, subprocess

def from_hex(hex_str, bits=16, signed=True):
    val = int(hex_str, 16)
    if signed and val >= (1 << (bits - 1)): val -= (1 << bits)
    return val

def to_hex(val, bits=16):
    if val < 0: val = (1 << bits) + val
    return f"{val:0{bits//4}X}"

# Re-generate input files in the current scripts directory or tb?
# Let's put them in root temporarily for xvlog/xsim easy access
# We'll use the ones already in /tb by copying them to root

print("Running Vivado XSIM simulation for Multi-Slot...")
# Paths are relative to the 'scripts' directory where we run this
subprocess.run([r"D:\Xilinx\Vivado\2024.2\bin\xvlog.bat", "../src/sfu_top.v", "../src/sfu_lane.v", "../tb/sfu_tb.v"], check=True)
subprocess.run([r"D:\Xilinx\Vivado\2024.2\bin\xelab.bat", "sfu_tb", "-s", "sfu_sim", "-debug", "typical"], check=True)
subprocess.run([r"D:\Xilinx\Vivado\2024.2\bin\xsim.bat", "sfu_sim", "-R"], check=True)

def analyze(name, math_func, out_scale, is_signed_out=True):
    out_file = f"{name}_out.txt"
    if not os.path.exists(out_file):
        print(f"Error: {out_file} not found!")
        return
    with open(out_file) as f: lines = f.readlines()
    
    xs, errs = [], []
    max_err = 0
    for line in lines:
        if not line.strip(): continue
        parts = line.split()
        if parts[1] == 'xxxx':
             print(f"Warning: xxxx found in {name} output!")
             continue
        x = from_hex(parts[0], 16, True) / 4096.0
        y = from_hex(parts[1], 16, is_signed_out) / out_scale
        math_y = math_func(x)
        err = abs(y - math_y)
        max_err = max(max_err, err)
    
    print(f"Result for {name.upper()}: Max Absolute Error = {max_err:.6f}")

def gelu(x): return 0.5 * x * (1 + math.erf(x / math.sqrt(2)))
def silu(x): return x / (1 + math.exp(-x))

analyze("exp", math.exp, 32768.0, is_signed_out=False)
analyze("gelu", gelu, 4096.0, is_signed_out=True)
analyze("silu", silu, 4096.0, is_signed_out=True)

print("Cleanup temporary files...")
for f in ["exp_out.txt", "gelu_out.txt", "silu_out.txt"]:
    if os.path.exists(f): os.remove(f)
