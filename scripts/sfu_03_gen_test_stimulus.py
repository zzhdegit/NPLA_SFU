import numpy as np
import math

NUM_SAMPLES_PER_FUNC = 800
TOTAL_SAMPLES = NUM_SAMPLES_PER_FUNC * 3
Q4_12_SCALE = 4096.0

np.random.seed(2026)  # 固定种子，保证结果可复现

# ---------------------------------------------------------
# 1. 分别生成三种函数的浮点输入 (覆盖各自的有效逼近区间)
# ---------------------------------------------------------
# EXP: 区间 [-8.0, 0.0]
inputs_exp = np.random.uniform(-8.0, 0.0, NUM_SAMPLES_PER_FUNC)

# GELU: 区间 [-6.0, 6.0]
inputs_gelu = np.random.uniform(-6.0, 6.0, NUM_SAMPLES_PER_FUNC)

# SILU: 区间 [-6.0, 6.0]
inputs_silu = np.random.uniform(-6.0, 6.0, NUM_SAMPLES_PER_FUNC)

# 按照流水线注入顺序拼接: [EXP(800) -> GELU(800) -> SILU(800)]
all_inputs = np.concatenate([inputs_exp, inputs_gelu, inputs_silu])

# ---------------------------------------------------------
# 2. 将浮点数转换为 Q4.12 16-bit Hex，写入 RTL 激励文件
# ---------------------------------------------------------
with open("stimulus_2400.txt", "w") as f_stim:
    for val in all_inputs:
        # 量化为 Q4.12
        q_val = int(np.round(val * Q4_12_SCALE))

        # 饱和限幅到 16-bit 有符号数范围 (防意外溢出)
        max_val = (1 << 15) - 1
        min_val = -(1 << 15)
        q_val = max(min(q_val, max_val), min_val)

        # 转换为补码并格式化为 4 位大写十六进制
        if q_val < 0:
            q_val = (1 << 16) + q_val
        f_stim.write(f"{q_val & 0xFFFF:04X}\n")

print(f"✅ 成功生成 {TOTAL_SAMPLES} 个 RTL 测试向量到 stimulus_2400.txt")


# ---------------------------------------------------------
# 3. 计算高精度真值 (Golden Reference)，供后续误差分析脚本比对
# ---------------------------------------------------------
def gelu_exact(x):
    # GeLU 真实数学公式: 0.5 * x * (1 + erf(x / sqrt(2)))
    return 0.5 * x * (1.0 + math.erf(x / math.sqrt(2.0)))


def silu_exact(x):
    # SiLU 真实数学公式: x / (1 + exp(-x))
    return x / (1.0 + np.exp(-x))


# 计算三组真值
true_exp = np.exp(inputs_exp)
true_gelu = np.array([gelu_exact(x) for x in inputs_gelu])
true_silu = silu_exact(inputs_silu)

all_true = np.concatenate([true_exp, true_gelu, true_silu])

# 写入真值文件
with open("golden_2400.txt", "w") as f_gold:
    for val in all_true:
        f_gold.write(f"{val:.8f}\n")

print(f"✅ 成功生成对应的真实浮点结果到 golden_2400.txt")