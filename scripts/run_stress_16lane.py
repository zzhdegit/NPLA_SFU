import os, sys, random, math, subprocess, shutil
import matplotlib.pyplot as plt

def to_hex(val, bits=16):
    if val < 0: val = (1 << bits) + val
    return f"{val:0{bits//4}X}"

# 1. Generate 16000 inputs for 16-lane stress test (16 lanes * 1000 cycles = 16000)
print("Generating 16000 test vectors for Stress Test...")
random.seed(12345) # Changed seed for new parameters
inputs_exp = [to_hex(int(random.uniform(-8.0, 0.0) * 4096)) for _ in range(16000)]
inputs_gelu = [to_hex(int(random.uniform(-6.0, 6.0) * 4096)) for _ in range(16000)]
inputs_silu = [to_hex(int(random.uniform(-6.0, 6.0) * 4096)) for _ in range(16000)]

with open("tb/exp_in.hex", "w") as f: f.write("\n".join(inputs_exp))
with open("tb/gelu_in.hex", "w") as f: f.write("\n".join(inputs_gelu))
with open("tb/silu_in.hex", "w") as f: f.write("\n".join(inputs_silu))

# 2. Modify tb/sfu_tb.v to handle 1000 cycles
print("Updating tb/sfu_tb.v for 1000 cycles...")
with open("tb/sfu_tb.v", "r") as f:
    tb_code = f.read()

tb_code = tb_code.replace("reg [15:0] input_data [0:799];", "reg [15:0] input_data [0:15999];")
tb_code = tb_code.replace("for (i=0; i<50; i=i+1)", "for (i=0; i<1000; i=i+1)")
tb_code = tb_code.replace("for (k=0; k<50; k=k+1)", "for (k=0; k<1000; k=k+1)")
tb_code = tb_code.replace("while (!o_valid && k < 49)", "while (!o_valid && k < 999)")

with open("tb/sfu_tb.v", "w") as f:
    f.write(tb_code)

# 3. Run Simulation
print("Running Vivado XSIM simulation...")
subprocess.run([r"D:\Xilinx\Vivado\2024.2\bin\xvlog.bat", "src/sfu_top.v", "src/sfu_lane.v", "tb/sfu_tb.v"], check=True)
subprocess.run([r"D:\Xilinx\Vivado\2024.2\bin\xelab.bat", "sfu_tb", "-s", "sfu_sim", "-debug", "typical"], check=True)
subprocess.run([r"D:\Xilinx\Vivado\2024.2\bin\xsim.bat", "sfu_sim", "-R"], check=True)

# 4. Analyze and Plot
print("Analyzing results and generating new plots...")
os.makedirs("outputs", exist_ok=True)
os.makedirs("vivadoreport", exist_ok=True)

def from_hex(hex_str, bits=16, signed=True):
    val = int(hex_str, 16)
    if signed and val >= (1 << (bits - 1)): val -= (1 << bits)
    return val

def analyze(name, math_func, out_scale, is_signed_out=True):
    if not os.path.exists(f"{name}_out.txt"):
        print(f"Error: {name}_out.txt not found!")
        return
    with open(f"{name}_out.txt") as f: lines = f.readlines()
    
    xs, errs = [], []
    for line in lines:
        if not line.strip(): continue
        parts = line.split()
        if 'x' in parts[0].lower() or 'x' in parts[1].lower(): continue
        x = from_hex(parts[0], 16, True) / 4096.0
        y = from_hex(parts[1], 16, is_signed_out) / out_scale
        math_y = math_func(x)
        
        raw_err = y - math_y
        xs.append(x)
        errs.append(raw_err)
        
    plt.scatter(xs, errs, s=2, alpha=0.5, color='blue')
    plt.title(f"{name.upper()} Error (16-Lane Stress Test, N=16000)")
    plt.xlabel("Input Value (x)")
    plt.ylabel("Error")
    plt.grid(True)
    
    # Replace current plots in vivadoreport
    plt.savefig(f"vivadoreport/{name}_error.png")
    # Also save to outputs
    plt.savefig(f"outputs/{name}_error.png")
    plt.clf()
    
    # Move txt results to outputs
    if os.path.exists(f"outputs/{name}_out.txt"):
        os.remove(f"outputs/{name}_out.txt")
    shutil.move(f"{name}_out.txt", f"outputs/{name}_out.txt")
    print(f"[{name.upper()}] Processed {len(xs)} samples. Max Error: {max([abs(e) for e in errs]):.8f}")

def gelu(x): return 0.5 * x * (1 + math.erf(x / math.sqrt(2)))
def silu(x): return x / (1 + math.exp(-x))

analyze("exp", math.exp, 32768.0, is_signed_out=False)
analyze("gelu", gelu, 4096.0, is_signed_out=True)
analyze("silu", silu, 4096.0, is_signed_out=True)

print("Stress test complete. Data results and new plots saved to outputs/ and vivadoreport/.")