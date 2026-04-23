import sys
import subprocess

def from_hex(hex_str, bits=16):
    val = int(hex_str, 16)
    if val >= (1 << (bits - 1)): val -= (1 << bits)
    return val

def to_hex(val, bits=16):
    if val < 0: val = (1 << bits) + val
    return f"{val:0{bits//4}X}"

# Read user stimulus
with open(r"C:\Users\zzh\Documents\fpga_code\py_sfu\stimulus_2400.txt") as f:
    stimulus = [line.strip() for line in f if line.strip()]

# Write to hex files
with open("exp_in.hex", "w") as f: f.write("\n".join(stimulus[0:800]))
with open("gelu_in.hex", "w") as f: f.write("\n".join(stimulus[800:1600]))
with open("silu_in.hex", "w") as f: f.write("\n".join(stimulus[1600:2400]))

# Run simulation
print("Running Vivado XSIM simulation...")
subprocess.run([r"D:\Xilinx\Vivado\2024.2\bin\xvlog.bat", "sfu_top.v", "sfu_lane.v", "sfu_tb.v"], check=True)
subprocess.run([r"D:\Xilinx\Vivado\2024.2\bin\xelab.bat", "sfu_tb", "-s", "sfu_sim", "-debug", "typical"], check=True)
subprocess.run([r"D:\Xilinx\Vivado\2024.2\bin\xsim.bat", "sfu_sim", "-R"], check=True)

# Compare outputs
with open("exp_out.txt") as f:
    exp_out = [line.split()[1] for line in f if line.strip()]
with open("gelu_out.txt") as f:
    gelu_out = [line.split()[1] for line in f if line.strip()]
with open("silu_out.txt") as f:
    silu_out = [line.split()[1] for line in f if line.strip()]

my_out = exp_out + gelu_out + silu_out

with open(r"C:\Users\zzh\Documents\fpga_code\py_sfu\rtl_output_2400.txt") as f:
    user_out = [line.strip() for line in f if line.strip()]

mismatches = 0
for i in range(2400):
    if my_out[i].lower() != user_out[i].lower():
        mismatches += 1
        if mismatches <= 10:
            print(f"Mismatch at {i}: User {user_out[i]} != My {my_out[i]}")

print(f"Total Mismatches: {mismatches} / 2400")
