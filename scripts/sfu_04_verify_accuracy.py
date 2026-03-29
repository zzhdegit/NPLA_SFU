import numpy as np
import matplotlib.pyplot as plt
import math

# --- 参数配置 ---
NUM_PER_FUNC = 800
TOTAL_SAMPLES = 2400
Q4_12_SCALE = 4096.0
UQ1_15_SCALE = 32768.0

# --- 精确数学公式定义 ---
def gelu_exact(x):
    # GeLU: 0.5 * x * (1 + erf(x / sqrt(2)))
    return 0.5 * x * (1.0 + math.erf(x / math.sqrt(2.0)))

def silu_exact(x):
    # SiLU: x / (1 + exp(-x))
    return x / (1.0 + np.exp(-x))

# 1. 提取 RTL 实际处理的输入 (还原真实 Q4.12 有符号数)
hw_inputs = []
try:
    with open("stimulus_2400.txt", "r") as f:
        for line in f:
            val = int(line.strip(), 16)
            hw_inputs.append(val - 65536 if val >= 32768 else val)
except FileNotFoundError:
    print("❌ 找不到 stimulus_2400.txt，请检查路径！")
    exit()

x_float = np.array(hw_inputs) / Q4_12_SCALE

# 2. 提取 RTL 仿真输出的 16-bit Hex 数据
hw_outputs_raw = []
try:
    with open("rtl_output_2400.txt", "r") as f:
        for line in f:
            hw_outputs_raw.append(int(line.strip(), 16))
except FileNotFoundError:
    print("❌ 找不到 rtl_output_2400.txt，请检查路径！")
    exit()

if len(hw_outputs_raw) != TOTAL_SAMPLES:
    print(f"⚠️ 警告: 输出数据量 ({len(hw_outputs_raw)}) 与预期 ({TOTAL_SAMPLES}) 不符！")

# 3. 分块解析与误差计算
# ==========================================
# Chunk 1: EXP (Mode 00) - 输出为 UQ1.15 无符号
# ==========================================
x_exp = x_float[0:800]
y_true_exp = np.exp(x_exp)
y_hw_exp = np.array(hw_outputs_raw[0:800]) / UQ1_15_SCALE
err_exp = np.abs(y_true_exp - y_hw_exp)

# ==========================================
# Chunk 2: GELU (Mode 01) - 输出为 Q4.12 有符号
# ==========================================
x_gelu = x_float[800:1600]
y_true_gelu = np.array([gelu_exact(xi) for xi in x_gelu])
# Q4.12 补码还原
y_hw_gelu_signed = np.array([val - 65536 if val >= 32768 else val for val in hw_outputs_raw[800:1600]])
y_hw_gelu = y_hw_gelu_signed / Q4_12_SCALE
err_gelu = np.abs(y_true_gelu - y_hw_gelu)

# ==========================================
# Chunk 3: SILU (Mode 10) - 输出为 Q4.12 有符号
# ==========================================
x_silu = x_float[1600:2400]
y_true_silu = silu_exact(x_silu)
# Q4.12 补码还原
y_hw_silu_signed = np.array([val - 65536 if val >= 32768 else val for val in hw_outputs_raw[1600:2400]])
y_hw_silu = y_hw_silu_signed / Q4_12_SCALE
err_silu = np.abs(y_true_silu - y_hw_silu)

# 4. 终端打印评估报告
def print_stats(name, err_array):
    print(f"[{name}]")
    print(f" 最大绝对误差: {np.max(err_array):.6f}")
    print(f" 平均绝对误差: {np.mean(err_array):.6f}")
    print(f" 误差标准差:   {np.std(err_array):.6f}")
    print("-" * 50)

print("\n" + "="*50)
print("多功能 16路并行 SFU 硬件定点数精度评估报告")
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
    max_e = np.max(err)

    # --- 左侧: 误差分布直方图 ---
    axes[i, 0].hist(err, bins=60, color=c_hist, edgecolor='black', alpha=0.7)
    axes[i, 0].axvline(mean_e, color='red', linestyle='dashed', linewidth=2, label=f'Mean: {mean_e:.6f}')
    axes[i, 0].axvline(max_e, color='orange', linestyle='dashed', linewidth=2, label=f'Max: {max_e:.6f}')
    axes[i, 0].set_title(f'[{name}] Error Distribution Histogram', fontsize=13, fontweight='bold')
    axes[i, 0].set_xlabel('Absolute Error', fontsize=11)
    axes[i, 0].set_ylabel('Frequency', fontsize=11)
    axes[i, 0].legend(fontsize=10)
    axes[i, 0].grid(axis='y', alpha=0.3)

    # --- 右侧: 输入值 vs 误差散点图 ---
    axes[i, 1].scatter(x_val, err, color=c_scat, alpha=0.6, s=15, label='Sample Error')
    axes[i, 1].axhline(0, color='black', linewidth=1)
    axes[i, 1].set_title(f'[{name}] Absolute Error vs. Input ($x$)', fontsize=13, fontweight='bold')
    axes[i, 1].set_xlabel('Input Value ($x$)', fontsize=11)
    axes[i, 1].set_ylabel('Absolute Error', fontsize=11)
    axes[i, 1].legend(fontsize=10)
    axes[i, 1].grid(linestyle='--', alpha=0.5)

# 调整子图间距并显示
plt.tight_layout()
plt.show()