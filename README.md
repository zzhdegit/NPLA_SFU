# 16-Lane Parallel SFU (Special Function Unit)

这是一个面向神经网络硬件加速器（如 Transformer）的高性能、多功能非线性算子 IP 核。

## 方法与代码功能

* **核心功能**：支持在单周期内并行处理 16 路数据的非线性激活函数计算。目前支持三种核心模式：**e^x (Softmax 指数项)**、**GeLU**、**SiLU**。
* **实现方法**：采用 **NPLA（非均匀分段线性近似）** 算法。通过将定义域划分为 32 个非均匀区间，硬件根据输入值动态查表提取斜率与截距，并调用 DSP 执行单周期乘加运算 (`y = a*x + b`)。
* **微架构设计**：采用 7 级全弹性握手流水线（Fully Elastic Pipeline）。代码在 RTL 级进行了深度物理优化，通过切割 DSP48 内部的 M-Register 并克隆高扇出控制流，在 Xilinx Zynq UltraScale+ 平台上可轻松达成 500MHz+ 主频。

## 接口定义 (I/O Ports)

模块对外采用标准的 Valid/Ready 弹性握手协议，便于直接封装为 AXI4-Stream 接口。

| 信号名称 | 方向 | 位宽 | 描述 |
| :--- | :--- | :--- | :--- |
| `i_clk` | Input | 1 | 系统时钟 |
| `i_rst_n` | Input | 1 | 全局异步复位，低电平有效 |
| `i_func_mode` | Input | 2 | 模式选择：`00` = e^x, `01` = GeLU, `10` = SiLU |
| `i_valid` | Input | 1 | 输入数据有效标志 |
| `o_ready` | Output | 1 | 模块就绪标志，拉高表示允许接收新数据 |
| `i_data_bus` | Input | 256 | 16 路输入数据总线 (16 x 16-bit, Q4.12 格式) |
| `o_valid` | Output | 1 | 输出数据有效标志 |
| `i_ready` | Input | 1 | 下游就绪标志（反压输入） |
| `o_data_bus` | Output | 256 | 16 路输出数据总线 (e^x 为 UQ1.15，GeLU/SiLU 为 Q4.12) |

## 移植与集成说明

1.  **纯 RTL 实现**：本 IP 核采用纯 Verilog HDL 编写，不依赖任何特定厂商的封闭 IP Core（Vivado 会自动推断并例化 DSP48 宏单元）。可平滑移植至 Xilinx 7 系列、UltraScale+ 甚至 ASIC 前端流程。
2.  **文件依赖**：集成时，只需将 `rtl/` 目录下的所有 `.v` 文件以及参数定义头文件 `npla_bnd_params.vh` 加入你的工程即可。
3.  **握手级联**：请确保外部互联总线严格遵守 `i_valid` 与 `o_ready` 同高时才更新数据的握手规则，以保证流水线数据不丢失。

## Python 工具链使用说明

本项目配备了一套完整的 Python 自动化脚本链，用于算法寻优、RTL 头文件生成以及硬件精度验证。请按以下顺序运行：

### 1. `sfu_01_train_pwl_coeffs.py`
* **功能**：执行 NPLA 算法的参数训练。计算 e^x、GeLU、SiLU 在各个分段区间的最佳线性拟合斜率 (a) 和截距 (b)。
* **输出**：生成浮点/定点格式的参数表格。

### 2. `sfu_02_gen_rtl_headers.py`
* **功能**：将第一步训练好的定点数参数自动化转换为 Verilog 语法。
* **输出**：生成 `npla_bnd_params.vh` 头文件。直接覆盖到 `rtl/` 目录下供硬件综合使用。

### 3. `sfu_03_gen_test_stimulus.py`
* **功能**：生成覆盖各类边缘情况（边界、极值、非线性转折区）的硬件测试激励。
* **输出**：生成 `stimulus_2400.txt`。请将该文件放入 Vivado/ModelSim 的仿真目录中，供 Testbench 读取。

### 4. `sfu_04_verify_accuracy.py`
* **功能**：读取 Testbench 跑出来的真实硬件结果 `rtl_output_2400.txt`，将其与 Python 浮点双精度理论计算值进行逐一比对。
* **输出**：在终端打印每种激活函数的最大绝对误差、平均绝对误差 (MAE) 等精度评估报告。

### 5. `sfu_05_plot_hardware_curves.py`
* **功能**：将硬件实际输出的定点数散点与完美的数学理论曲线进行可视化叠加。
* **输出**：生成高分辨率的误差散点图与数据拟合图 (PNG)，用于直观评估硬件精度表现。
