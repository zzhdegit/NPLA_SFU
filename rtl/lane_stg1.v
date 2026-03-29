`timescale 1ns / 1ps

module lane_stg1 (
    input  wire [1:0]         mode_in,        // 00: e^x, 01: GeLU, 10: SiLU
    input  wire signed [15:0] x_in,           // 输入数据 Q4.12
    output wire signed [15:0] x_out,          // 透传输出数据
    output reg  [4:0]         idx_out,        // 区间索引 (0~31)
    output wire               underflow_flag  // 下溢出标志
);

    // =========================================================================
    // 包含 NPLA 参数头文件 (定义了 BND_EXP_xx, BND_GELU_xx, BND_SILU_xx)
    // 同时也包含了新增的 BND_EXP_MIN, BND_GELU_MIN, BND_SILU_MIN
    // =========================================================================
    `include "npla_bnd_params.vh"

    // =========================================================================
    // 1. 数据透传
    // =========================================================================
    assign x_out = x_in;

    // =========================================================================
    // 2. 动态边界 MUX (多路选择)
    // 根据功能模式预先选定该 Lane 当前周期的 31 个判定边界以及真实下界
    // =========================================================================
    
    // 【核心修复】: 增加真正的函数起点（最小边界）选择
    wire signed [15:0] bnd_min = (mode_in == 2'b01) ? BND_GELU_MIN : ((mode_in == 2'b10) ? BND_SILU_MIN : BND_EXP_MIN);

    wire signed [15:0] bnd_00 = (mode_in == 2'b01) ? BND_GELU_00 : ((mode_in == 2'b10) ? BND_SILU_00 : BND_EXP_00);
    wire signed [15:0] bnd_01 = (mode_in == 2'b01) ? BND_GELU_01 : ((mode_in == 2'b10) ? BND_SILU_01 : BND_EXP_01);
    wire signed [15:0] bnd_02 = (mode_in == 2'b01) ? BND_GELU_02 : ((mode_in == 2'b10) ? BND_SILU_02 : BND_EXP_02);
    wire signed [15:0] bnd_03 = (mode_in == 2'b01) ? BND_GELU_03 : ((mode_in == 2'b10) ? BND_SILU_03 : BND_EXP_03);
    wire signed [15:0] bnd_04 = (mode_in == 2'b01) ? BND_GELU_04 : ((mode_in == 2'b10) ? BND_SILU_04 : BND_EXP_04);
    wire signed [15:0] bnd_05 = (mode_in == 2'b01) ? BND_GELU_05 : ((mode_in == 2'b10) ? BND_SILU_05 : BND_EXP_05);
    wire signed [15:0] bnd_06 = (mode_in == 2'b01) ? BND_GELU_06 : ((mode_in == 2'b10) ? BND_SILU_06 : BND_EXP_06);
    wire signed [15:0] bnd_07 = (mode_in == 2'b01) ? BND_GELU_07 : ((mode_in == 2'b10) ? BND_SILU_07 : BND_EXP_07);
    wire signed [15:0] bnd_08 = (mode_in == 2'b01) ? BND_GELU_08 : ((mode_in == 2'b10) ? BND_SILU_08 : BND_EXP_08);
    wire signed [15:0] bnd_09 = (mode_in == 2'b01) ? BND_GELU_09 : ((mode_in == 2'b10) ? BND_SILU_09 : BND_EXP_09);
    wire signed [15:0] bnd_10 = (mode_in == 2'b01) ? BND_GELU_10 : ((mode_in == 2'b10) ? BND_SILU_10 : BND_EXP_10);
    wire signed [15:0] bnd_11 = (mode_in == 2'b01) ? BND_GELU_11 : ((mode_in == 2'b10) ? BND_SILU_11 : BND_EXP_11);
    wire signed [15:0] bnd_12 = (mode_in == 2'b01) ? BND_GELU_12 : ((mode_in == 2'b10) ? BND_SILU_12 : BND_EXP_12);
    wire signed [15:0] bnd_13 = (mode_in == 2'b01) ? BND_GELU_13 : ((mode_in == 2'b10) ? BND_SILU_13 : BND_EXP_13);
    wire signed [15:0] bnd_14 = (mode_in == 2'b01) ? BND_GELU_14 : ((mode_in == 2'b10) ? BND_SILU_14 : BND_EXP_14);
    wire signed [15:0] bnd_15 = (mode_in == 2'b01) ? BND_GELU_15 : ((mode_in == 2'b10) ? BND_SILU_15 : BND_EXP_15);
    wire signed [15:0] bnd_16 = (mode_in == 2'b01) ? BND_GELU_16 : ((mode_in == 2'b10) ? BND_SILU_16 : BND_EXP_16);
    wire signed [15:0] bnd_17 = (mode_in == 2'b01) ? BND_GELU_17 : ((mode_in == 2'b10) ? BND_SILU_17 : BND_EXP_17);
    wire signed [15:0] bnd_18 = (mode_in == 2'b01) ? BND_GELU_18 : ((mode_in == 2'b10) ? BND_SILU_18 : BND_EXP_18);
    wire signed [15:0] bnd_19 = (mode_in == 2'b01) ? BND_GELU_19 : ((mode_in == 2'b10) ? BND_SILU_19 : BND_EXP_19);
    wire signed [15:0] bnd_20 = (mode_in == 2'b01) ? BND_GELU_20 : ((mode_in == 2'b10) ? BND_SILU_20 : BND_EXP_20);
    wire signed [15:0] bnd_21 = (mode_in == 2'b01) ? BND_GELU_21 : ((mode_in == 2'b10) ? BND_SILU_21 : BND_EXP_21);
    wire signed [15:0] bnd_22 = (mode_in == 2'b01) ? BND_GELU_22 : ((mode_in == 2'b10) ? BND_SILU_22 : BND_EXP_22);
    wire signed [15:0] bnd_23 = (mode_in == 2'b01) ? BND_GELU_23 : ((mode_in == 2'b10) ? BND_SILU_23 : BND_EXP_23);
    wire signed [15:0] bnd_24 = (mode_in == 2'b01) ? BND_GELU_24 : ((mode_in == 2'b10) ? BND_SILU_24 : BND_EXP_24);
    wire signed [15:0] bnd_25 = (mode_in == 2'b01) ? BND_GELU_25 : ((mode_in == 2'b10) ? BND_SILU_25 : BND_EXP_25);
    wire signed [15:0] bnd_26 = (mode_in == 2'b01) ? BND_GELU_26 : ((mode_in == 2'b10) ? BND_SILU_26 : BND_EXP_26);
    wire signed [15:0] bnd_27 = (mode_in == 2'b01) ? BND_GELU_27 : ((mode_in == 2'b10) ? BND_SILU_27 : BND_EXP_27);
    wire signed [15:0] bnd_28 = (mode_in == 2'b01) ? BND_GELU_28 : ((mode_in == 2'b10) ? BND_SILU_28 : BND_EXP_28);
    wire signed [15:0] bnd_29 = (mode_in == 2'b01) ? BND_GELU_29 : ((mode_in == 2'b10) ? BND_SILU_29 : BND_EXP_29);
    wire signed [15:0] bnd_30 = (mode_in == 2'b01) ? BND_GELU_30 : ((mode_in == 2'b10) ? BND_SILU_30 : BND_EXP_30);

    // =========================================================================
    // 3. 越界处理 (下溢出)
    // =========================================================================
    
    // 【核心修复】: 小于真实起点的数值，才算是下溢出！
    assign underflow_flag = (x_in < bnd_min);

    // =========================================================================
    // 4. 400MHz 友好型比较器树 (二叉搜索树结构)
    // =========================================================================
    always @(*) begin
        if (x_in < bnd_15) begin
            if (x_in < bnd_07) begin
                if (x_in < bnd_03) begin
                    if (x_in < bnd_01) begin
                        if (x_in < bnd_00) idx_out = 5'd0;
                        else               idx_out = 5'd1;
                    end else begin
                        if (x_in < bnd_02) idx_out = 5'd2;
                        else               idx_out = 5'd3;
                    end
                end else begin
                    if (x_in < bnd_05) begin
                        if (x_in < bnd_04) idx_out = 5'd4;
                        else               idx_out = 5'd5;
                    end else begin
                        if (x_in < bnd_06) idx_out = 5'd6;
                        else               idx_out = 5'd7;
                    end
                end
            end else begin
                if (x_in < bnd_11) begin
                    if (x_in < bnd_09) begin
                        if (x_in < bnd_08) idx_out = 5'd8;
                        else               idx_out = 5'd9;
                    end else begin
                        if (x_in < bnd_10) idx_out = 5'd10;
                        else               idx_out = 5'd11;
                    end
                end else begin
                    if (x_in < bnd_13) begin
                        if (x_in < bnd_12) idx_out = 5'd12;
                        else               idx_out = 5'd13;
                    end else begin
                        if (x_in < bnd_14) idx_out = 5'd14;
                        else               idx_out = 5'd15;
                    end
                end
            end
        end else begin
            // x_in >= bnd_15
            if (x_in < bnd_23) begin
                if (x_in < bnd_19) begin
                    if (x_in < bnd_17) begin
                        if (x_in < bnd_16) idx_out = 5'd16;
                        else               idx_out = 5'd17;
                    end else begin
                        if (x_in < bnd_18) idx_out = 5'd18;
                        else               idx_out = 5'd19;
                    end
                end else begin
                    if (x_in < bnd_21) begin
                        if (x_in < bnd_20) idx_out = 5'd20;
                        else               idx_out = 5'd21;
                    end else begin
                        if (x_in < bnd_22) idx_out = 5'd22;
                        else               idx_out = 5'd23;
                    end
                end
            end else begin
                if (x_in < bnd_27) begin
                    if (x_in < bnd_25) begin
                        if (x_in < bnd_24) idx_out = 5'd24;
                        else               idx_out = 5'd25;
                    end else begin
                        if (x_in < bnd_26) idx_out = 5'd26;
                        else               idx_out = 5'd27;
                    end
                end else begin
                    if (x_in < bnd_29) begin
                        if (x_in < bnd_28) idx_out = 5'd28;
                        else               idx_out = 5'd29;
                    end else begin
                        if (x_in < bnd_30) idx_out = 5'd30;
                        else               idx_out = 5'd31;
                    end
                end
            end
        end
    end

endmodule