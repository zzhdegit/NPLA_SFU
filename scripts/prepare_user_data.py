import os

with open(r"C:\Users\zzh\Documents\fpga_code\py_sfu\stimulus_2400.txt") as f:
    stimulus = [line.strip() for line in f if line.strip()]

with open("tb/exp_in.hex", "w") as f:
    f.write("\n".join(stimulus[0:800]))

with open("tb/gelu_in.hex", "w") as f:
    f.write("\n".join(stimulus[800:1600]))

with open("tb/silu_in.hex", "w") as f:
    f.write("\n".join(stimulus[1600:2400]))

print("Overwrote tb/*_in.hex with user stimulus data.")
