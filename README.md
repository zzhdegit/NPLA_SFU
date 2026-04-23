# 16-Lane Parallel SFU (Special Function Unit)

这是一个面向神经网络硬件加速器（如 Transformer）的高性能、多功能非线性算子 IP 核。

## 方法与代码功能

* **核心功能**：支持在单周期内并行处理 16 路数据的非线性激活函数计算。目前支持三种核心模式：**e^x (Softmax 指数项)**、**GeLU**、**SiLU**。在 v2.0 版本中，进一步引入了 **4 槽位配置预载** 架构，支持算子参数的**运行时 0 延迟瞬时切换**。
* **实现方法**：采用 **NPLA（非均匀分段线性近似）** 算法。通过将定义域划分为 32 个非均匀区间，硬件根据输入值动态查表提取斜率与截距，并调用 DSP 执行单周期乘加运算 (`y = a*x + b`)。
* **微架构设计**：采用 7 级全弹性握手流水线（Fully Elastic Pipeline）。代码在 RTL 级进行了深度物理优化，通过切割 DSP48 内部的 M-Register 并克隆高扇出控制流，在 Xilinx Alveo U50 平台上可稳定运行在 400MHz+ 主频。

---

## 🛠️ v2.0 快速上手指南 (Quick Start)

*这是新增的指导章节，帮助您快速跑通 4 槽位可编程流程。*

### 第一步：获取拟合参数 (Parameters)
本 IP 核需要先录入参数。预训练好的 32 段系数存放在 `tb/` 目录下：
- `tb/exp_cfg.hex` / `tb/gelu_cfg.hex` / `tb/silu_cfg.hex`

### 第二步：参数录入 (Parameter Loading)
计算前通过 **Config Interface** 将参数写入目标槽位（Slot）：
1.  通过 `i_cfg_slot` 选择仓库（0-3）。
2.  按照地址映射依次写入 31 个边界点、32 个斜率 $a$ 和 32 个截距 $b$。
3.  **参考图表**：详细地址分配请查看 `result/sfu_memory_map.svg`。

### 第三步：配置切换与计算
*   设置 `i_active_slot` 指向对应槽位即可实现瞬时算子切换。
*   通过 256-bit `i_data_bus` 输入 16 路 Q4.12 数据，7 拍后获得结果。

---

## 接口定义 (I/O Ports)

模块对外采用标准的 Valid/Ready 弹性握手协议，便于直接封装为 AXI4-Stream 接口。

### 1. 配置总线接口 (Config Interface)
| 信号名称 | 方向 | 位宽 | 描述 |
| :--- | :--- | :--- | :--- |
| `i_cfg_en` | Input | 1 | 配置模块总使能 |
| `i_cfg_we` | Input | 1 | 配置写使能 |
| `i_cfg_slot` | Input | 2 | 目标配置槽位选择 (0-3) |
| `i_cfg_addr` | Input | 7 | 寄存器映射地址 (0x00 - 0x64) |
| `i_cfg_wdata` | Input | 16 | 配置写入数据 (16-bit 定点补码) |
| `i_active_slot` | Input | 2 | **当前计算生效槽位选择** (0-3) |

### 2. 数据计算接口 (Data Interface)
| 信号名称 | 方向 | 位宽 | 描述 |
| :--- | :--- | :--- | :--- |
| `i_clk` | Input | 1 | 系统时钟 |
| `i_rst_n` | Input | 1 | 全局异步复位，低电平有效 |
| `i_valid` | Input | 1 | 输入数据有效标志 |
| `o_ready` | Output | 1 | 模块就绪标志，拉高表示允许接收新数据 |
| `i_data_bus` | Input | 256 | 16 路输入数据总线 (16 x 16-bit, Q4.12 格式) |
| `o_valid` | Output | 1 | 输出数据有效标志 |
| `i_ready` | Input | 1 | 下游就绪标志（反压输入） |
| `o_data_bus` | Output | 256 | 16 路输出数据总线 (e^x 为 UQ1.15，GeLU/SiLU 为 Q4.12) |

## 移植与集成说明

1.  **纯 RTL 实现**：本 IP 核采用纯 Verilog HDL 编写，不依赖任何特定厂商的封闭 IP Core（Vivado 会自动推断并例化 DSP48 宏单元）。可平滑移植至 Xilinx 7 系列、UltraScale+ 甚至 ASIC 前端流程。
2.  **文件依赖**：集成时，只需将 `rtl/` 目录下的 `sfu_top.v` 和 `sfu_lane.v` 加入你的工程即可。
3.  **握手级联**：请确保外部互联总线严格遵守 `i_valid` 与 `o_ready` 同高时才更新数据的握手规则，以保证流水线数据不丢失。

## Python 工具链使用说明

本项目配备了一套完整的 Python 自动化脚本链。*（注：脚本名称已更新以匹配最新版本路径）*

### 1. `scripts/run_stress_16lane.py` (原 sfu_03/04 合并)
* **功能**：自动生成 16,000 个随机压力测试激励，并调用 Vivado XSIM 验证硬件精度与稳定性。
* **输出**：生成 `outputs/` 原始计算数据。

### 2. `scripts/plot_with_new_style.py` (原 sfu_05)
* **功能**：将 16 路并发测试的误差分布进行可视化处理。
* **输出**：在 `result/` 目录下生成高分辨率误差散点图与直方图矩阵。

### 3. `scripts/gen_hex.py` (原 sfu_01/02)
* **功能**：执行 NPLA 算法寻优，计算任意非线性函数的 32 段最佳拟合斜率与截距。
* **输出**：生成供硬件录入使用的 `.hex` 参数文件。

## 精度表现 (v2.0 验证)
经过 16,000 个样本验证，最大绝对误差：
- **EXP**: < 0.00039
- **GELU**: < 0.00085
- **SiLU**: < 0.00102


---
*Maintained by zzhdegit | Version 2.0 (Stable)*
