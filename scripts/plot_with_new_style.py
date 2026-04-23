import os
import numpy as np
import matplotlib.pyplot as plt
import math

# --- 参数配置 ---
TOTAL_SAMPLES = 16000
Q4_12_SCALE = 4096.0
UQ1_15_SCALE = 32768.0

# --- 精确数学公式定义 ---
def exp_exact(x):
    return np.exp(x)

def gelu_exact(x):
    return 0.5 * x * (1.0 + math.erf(x / math.sqrt(2.0)))

def silu_exact(x):
    return x / (1.0 + np.exp(-x))

def from_hex(hex_str, bits=16, signed=True):
    val = int(hex_str, 16)
    if signed and val >= (1 << (bits - 1)): val -= (1 << bits)
    return val

def load_data(name, math_func, out_scale, is_signed_out=True):
    file_path = f"outputs/{name}_out.txt"
    if not os.path.exists(file_path):
        print(f"❌ 找不到 {file_path}，请检查路径！")
        return None, None
        
    x_vals = []
    err_vals = []
    
    with open(file_path, "r") as f:
        for line in f:
            if not line.strip(): continue
            parts = line.split()
            if 'x' in parts[0].lower() or 'x' in parts[1].lower(): continue
            
            x = from_hex(parts[0], 16, True) / Q4_12_SCALE
            y_hw = from_hex(parts[1], 16, is_signed_out) / out_scale
            y_true = math_func(x)
            
            x_vals.append(x)
            err_vals.append(y_hw - y_true) # 保留符号的原始误差 (Fitted - True)
            
    return np.array(x_vals), np.array(err_vals)

# 读取之前 16000 样本压力测试生成的数据
x_exp, err_exp = load_data("exp", exp_exact, UQ1_15_SCALE, is_signed_out=False)
x_gelu, err_gelu = load_data("gelu", gelu_exact, Q4_12_SCALE, is_signed_out=True)
x_silu, err_silu = load_data("silu", silu_exact, Q4_12_SCALE, is_signed_out=True)

if x_exp is None or x_gelu is None or x_silu is None:
    exit(1)

# 4. 终端打印评估报告
def print_stats(name, err_array):
    print(f"[{name}]")
    print(f" 最大绝对误差: {np.max(np.abs(err_array)):.6e}")
    print(f" 平均绝对误差: {np.mean(np.abs(err_array)):.6e}")
    print(f" 误差标准差:   {np.std(err_array):.6e}")
    print("-" * 50)

print("\n" + "="*50)
print("多功能 16路并行 SFU 硬件定点数精度评估报告 (N=16000 压力测试)")
print("="*50)
print_stats("e^x  (Mode 00, UQ1.15)", err_exp)
print_stats("GeLU (Mode 01, Q4.12)", err_gelu)
print_stats("SiLU (Mode 10, Q4.12)", err_silu)

# 5. 绘图 (3行2列 子图矩阵)
fig, axes = plt.subplots(3, 2, figsize=(16, 15))

# 打包数据方便循环画图
plot_data = [
    ("e^x", err_exp, x_exp, 'teal', 'royalblue'),
    ("GeLU", err_gelu, x_gelu, 'seagreen', 'darkgreen'),
    ("SiLU", err_silu, x_silu, 'purple', 'mediumorchid')
]

for i, (name, err, x_val, c_hist, c_scat) in enumerate(plot_data):
    mean_e = np.mean(err)
    max_abs_e = np.max(np.abs(err))

    # --- 左侧: 误差分布直方图 ---
    axes[i, 0].hist(err, bins=60, color=c_hist, edgecolor='black', alpha=0.7)
    axes[i, 0].axvline(mean_e, color='red', linestyle='dashed', linewidth=2, label=f'Mean: {mean_e:.2e}')
    axes[i, 0].set_title(f'[{name}] Error Distribution Histogram (N=16000)', fontsize=13, fontweight='bold')
    axes[i, 0].set_xlabel('Error (Fitted - True)', fontsize=11)
    axes[i, 0].set_ylabel('Frequency', fontsize=11)
    axes[i, 0].legend(fontsize=10)
    axes[i, 0].grid(axis='y', alpha=0.3)

    # --- 右侧: 输入值 vs 误差散点图 ---
    # 由于样本量大(16000)，稍微减小点的大小和透明度以更好地展示分布
    axes[i, 1].scatter(x_val, err, color=c_scat, alpha=0.3, s=5, label='Sample Error')
    axes[i, 1].axhline(0, color='black', linewidth=1)
    axes[i, 1].set_title(f'[{name}] Error vs. Input ($x$)', fontsize=13, fontweight='bold')
    axes[i, 1].set_xlabel('Input Value ($x$)', fontsize=11)
    axes[i, 1].set_ylabel('Error', fontsize=11)
    axes[i, 1].legend(fontsize=10)
    axes[i, 1].grid(linestyle='--', alpha=0.5)

# 调整子图间距并保存
plt.tight_layout()
output_fig = "outputs/evaluation_plot_16k_raw.png"
plt.savefig(output_fig, dpi=300)
plt.savefig("vivadoreport/evaluation_plot_16k_raw.png", dpi=300)
print(f"绘图已保存至: {output_fig} 和 vivadoreport/evaluation_plot_16k_raw.png")