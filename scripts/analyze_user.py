import sys

def from_hex(hex_str, bits=16):
    val = int(hex_str, 16)
    if val >= (1 << (bits - 1)): val -= (1 << bits)
    return val

def to_hex(val, bits=16):
    if val < 0: val = (1 << bits) + val
    return f"{val:0{bits//4}X}"

with open(r"C:\Users\zzh\Documents\fpga_code\py_sfu\stimulus_2400.txt") as f:
    stimulus = [line.strip() for line in f if line.strip()]

with open(r"C:\Users\zzh\Documents\fpga_code\py_sfu\rtl_output_2400.txt") as f:
    expected = [line.strip() for line in f if line.strip()]

import math

def gelu(x): return 0.5 * x * (1 + math.erf(x / math.sqrt(2)))
def silu(x): return x / (1 + math.exp(-x))

print("Input -> Expected Output -> Float (Input Q4.12) -> Float (Expected Q1.15) -> Expected Math EXP")
for i in range(10):
    hx = stimulus[i]
    hy = expected[i]
    val_x = from_hex(hx) / 4096.0
    val_y_exp = from_hex(hy, 16) / 32768.0
    val_y_gelu = from_hex(hy, 16) / 4096.0
    math_exp = math.exp(val_x)
    print(f"[{i}] x={hx} ({val_x:.4f}) -> y={hy} | y/32768 = {val_y_exp:.6f} | Math EXP = {math_exp:.6f} | Math GELU = {gelu(val_x):.6f}")

print("\nLet's check indices 800-810 (presumably GELU):")
for i in range(800, 810):
    if i >= len(stimulus): break
    hx = stimulus[i]
    hy = expected[i]
    val_x = from_hex(hx) / 4096.0
    val_y_gelu = from_hex(hy, 16) / 4096.0
    print(f"[{i}] x={hx} ({val_x:.4f}) -> y={hy} | y/4096 = {val_y_gelu:.6f} | Math GELU = {gelu(val_x):.6f}")

print("\nLet's check indices 1600-1610 (presumably SiLU):")
for i in range(1600, 1610):
    if i >= len(stimulus): break
    hx = stimulus[i]
    hy = expected[i]
    val_x = from_hex(hx) / 4096.0
    val_y_silu = from_hex(hy, 16) / 4096.0
    print(f"[{i}] x={hx} ({val_x:.4f}) -> y={hy} | y/4096 = {val_y_silu:.6f} | Math SiLU = {silu(val_x):.6f}")
