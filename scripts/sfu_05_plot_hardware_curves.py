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

# 3. 分块提取硬件坐标点 (x, y)
# Exp (Mode 00) - 输出为 UQ1.15 无符号
x_exp = x_float[0:800]
y_hw_exp = np.array(hw_outputs_raw[0:800]) / UQ1_15_SCALE

# GELU (Mode 01) - 输出为 Q4.12 有符号
x_gelu = x_float[800:1600]
y_hw_gelu_signed = np.array([val - 65536 if val >= 32768 else val for val in hw_outputs_raw[800:1600]])
y_hw_gelu = y_hw_gelu_signed / Q4_12_SCALE

# SILU (Mode 10) - 输出为 Q4.12 有符号
x_silu = x_float[1600:2400]
y_hw_silu_signed = np.array([val - 65536 if val >= 32768 else val for val in hw_outputs_raw[1600:2400]])
y_hw_silu = y_hw_silu_signed / Q4_12_SCALE

# 4. 绘图 (3行1列，高分辨率)
# dpi=300 保证图像整体分辨率极大
fig, axes = plt.subplots(3, 1, figsize=(10, 16), dpi=300)

# 打包数据方便循环画图: (名称, x硬件, y硬件, 数学函数, 曲线颜色, 散点颜色)
plot_data = [
    ("e^x (Mode 00)", x_exp, y_hw_exp, np.exp, 'royalblue', 'red'),
    ("GeLU (Mode 01)", x_gelu, y_hw_gelu, lambda x: np.array([gelu_exact(xi) for xi in x]), 'seagreen', 'orange'),
    ("SiLU (Mode 10)", x_silu, y_hw_silu, lambda x: x / (1.0 + np.exp(-x)), 'purple', 'magenta')
]

for i, (name, x_hw, y_hw, exact_func, c_line, c_scat) in enumerate(plot_data):
    # 将硬件散点按 x 大小排序，让图像显得更加整洁
    sort_idx = np.argsort(x_hw)
    x_hw_sorted = x_hw[sort_idx]
    y_hw_sorted = y_hw[sort_idx]

    # 生成 2000 个平滑密集点用于画完美的数学理论曲线
    x_smooth = np.linspace(min(x_hw), max(x_hw), 2000)
    y_smooth = exact_func(x_smooth)

    # --- 绘制数学理论曲线 (实线) ---
    # linewidth=1.5 让线看起来细致平滑
    axes[i].plot(x_smooth, y_smooth, color=c_line, linewidth=1.5, label='Math Exact Curve', zorder=1)

    # --- 绘制硬件输出散点 (点) ---
    # s=3 让像素点非常小，可以精确观察散点与实线的重合度
    axes[i].scatter(x_hw_sorted, y_hw_sorted, color=c_scat, s=3, alpha=0.8, label='RTL Hardware Output', zorder=2)

    # 图表修饰
    axes[i].set_title(f'RTL vs Exact Math: {name}', fontsize=15, fontweight='bold')
    axes[i].set_xlabel('Input Value ($x$)', fontsize=12)
    axes[i].set_ylabel('Output Value ($y$)', fontsize=12)
    axes[i].legend(fontsize=11, loc='upper left')
    axes[i].grid(linestyle='--', alpha=0.6)

# 调整子图间距
plt.tight_layout()

# 保存高清大图到本地
output_img = "SFU_Activation_Comparison_HighRes.png"
plt.savefig(output_img, dpi=300, bbox_inches='tight')
print(f"✅ 绘图完成！已保存高清图至: {output_img}")

# 弹出窗口显示
plt.show()