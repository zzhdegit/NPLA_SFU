import os
import numpy as np
import matplotlib.pyplot as plt
import math

# --- 参数配置 ---
TOTAL_SAMPLES = 16000
Q4_12_SCALE = 4096.0
UQ1_15_SCALE = 32768.0

def exp_exact(x): return np.exp(x)
def gelu_exact(x): return 0.5 * x * (1.0 + math.erf(x / math.sqrt(2.0)))
def silu_exact(x): return x / (1.0 + np.exp(-x))

def from_hex(hex_str, bits=16, signed=True):
    val = int(hex_str, 16)
    if signed and val >= (1 << (bits - 1)): val -= (1 << bits)
    return val

def load_data(name, math_func, out_scale, is_signed_out=True):
    file_path = f"outputs/{name}_out.txt"
    if not os.path.exists(file_path): return None, None
    x_vals, err_vals = [], []
    with open(file_path, "r") as f:
        for line in f:
            if not line.strip(): continue
            parts = line.split()
            if 'x' in parts[0].lower(): continue
            x = from_hex(parts[0], 16, True) / Q4_12_SCALE
            y_hw = from_hex(parts[1], 16, is_signed_out) / out_scale
            x_vals.append(x); err_vals.append(y_hw - math_func(x))
    return np.array(x_vals), np.array(err_vals)

x_exp, err_exp = load_data("exp", exp_exact, UQ1_15_SCALE, is_signed_out=False)
x_gelu, err_gelu = load_data("gelu", gelu_exact, Q4_12_SCALE, is_signed_out=True)
x_silu, err_silu = load_data("silu", silu_exact, Q4_12_SCALE, is_signed_out=True)

fig, axes = plt.subplots(3, 2, figsize=(16, 15))
plot_data = [
    ("e^x", err_exp, x_exp, 'teal', 'royalblue'),
    ("GeLU", err_gelu, x_gelu, 'seagreen', 'darkgreen'),
    ("SiLU", err_silu, x_silu, 'purple', 'mediumorchid')
]

for i, (name, err, x_val, c_hist, c_scat) in enumerate(plot_data):
    mean_e = np.mean(err)
    max_abs_e = np.max(np.abs(err))

    # 左侧：直方图
    axes[i, 0].hist(err, bins=60, color=c_hist, edgecolor='black', alpha=0.7)
    axes[i, 0].axvline(mean_e, color='red', linestyle='dashed', label=f'Mean: {mean_e:.2e}')
    axes[i, 0].set_title(f'[{name}] Error Distribution', fontsize=13, fontweight='bold')
    axes[i, 0].set_xlabel('Error (Fitted - True)')
    axes[i, 0].legend()

    # 右侧：散点图 (增加 Max Error 标注)
    axes[i, 1].scatter(x_val, err, color=c_scat, alpha=0.3, s=5, label='Sample Error')
    axes[i, 1].axhline(0, color='black', linewidth=1)
    # 标注最大绝对误差
    axes[i, 1].text(0.05, 0.9, f'Max Abs Error: {max_abs_e:.6f}', 
                    transform=axes[i, 1].transAxes, fontsize=12, fontweight='bold',
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='red'))
    
    axes[i, 1].set_title(f'[{name}] Error vs. Input ($x$)', fontsize=13, fontweight='bold')
    axes[i, 1].set_xlabel('Input Value ($x$)')
    axes[i, 1].set_ylabel('Error')
    axes[i, 1].grid(linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig("result/final_evaluation_plot.png", dpi=300)
print("Updated plot saved to result/final_evaluation_plot.png")
