import sys
import math

def from_hex(hex_str, bits=16, signed=True):
    val = int(hex_str, 16)
    if signed and val >= (1 << (bits - 1)): val -= (1 << bits)
    return val

def gelu(x): return 0.5 * x * (1 + math.erf(x / math.sqrt(2)))
def silu(x): return x / (1 + math.exp(-x))

with open(r"C:\Users\zzh\Documents\fpga_code\py_sfu\stimulus_2400.txt") as f:
    stimulus = [line.strip() for line in f if line.strip()]

with open(r"C:\Users\zzh\Documents\fpga_code\py_sfu\rtl_output_2400.txt") as f:
    expected = [line.strip() for line in f if line.strip()]

print("Analyzing first 800 (assuming EXP):")
max_abs_exp = 0
max_rel_exp = 0
for i in range(800):
    x = from_hex(stimulus[i], 16, True) / 4096.0
    y = from_hex(expected[i], 16, False) / 32768.0
    math_y = math.exp(x)
    abs_err = abs(y - math_y)
    rel_err = abs_err / max(abs(math_y), 1e-6)
    max_abs_exp = max(max_abs_exp, abs_err)
    max_rel_exp = max(max_rel_exp, rel_err)
print(f"  Max Abs Error: {max_abs_exp:.6f}")
print(f"  Max Rel Error: {max_rel_exp:.6f}")

print("\nAnalyzing middle 800 (assuming GELU):")
max_abs_gelu = 0
max_rel_gelu = 0
for i in range(800, 1600):
    x = from_hex(stimulus[i], 16, True) / 4096.0
    y = from_hex(expected[i], 16, True) / 4096.0
    math_y = gelu(x)
    abs_err = abs(y - math_y)
    rel_err = abs_err / max(abs(math_y), 1e-6)
    max_abs_gelu = max(max_abs_gelu, abs_err)
    max_rel_gelu = max(max_rel_gelu, rel_err)
print(f"  Max Abs Error: {max_abs_gelu:.6f}")
print(f"  Max Rel Error: {max_rel_gelu:.6f}")

print("\nAnalyzing last 800 (assuming SiLU):")
max_abs_silu = 0
max_rel_silu = 0
for i in range(1600, 2400):
    x = from_hex(stimulus[i], 16, True) / 4096.0
    y = from_hex(expected[i], 16, True) / 4096.0
    math_y = silu(x)
    abs_err = abs(y - math_y)
    rel_err = abs_err / max(abs(math_y), 1e-6)
    max_abs_silu = max(max_abs_silu, abs_err)
    max_rel_silu = max(max_rel_silu, rel_err)
print(f"  Max Abs Error: {max_abs_silu:.6f}")
print(f"  Max Rel Error: {max_rel_silu:.6f}")
