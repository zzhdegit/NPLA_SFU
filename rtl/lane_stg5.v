`timescale 1ns / 1ps

module lane_stg5 (
    input  wire               i_clk,
    input  wire               i_ena,
    input  wire [1:0]         mode_in,
    input  wire signed [32:0] sum_in,
    input  wire               uf_in,
    
    // 不再需要传递 mode_pipe，因为所有状态已互斥
    output reg                force_0000,
    output reg                force_8000,
    output reg                force_6000,
    output reg                force_fd48,
    output reg                force_fb8d,
    output reg  [15:0]        normal_val
);

    wire sign_bit = sum_in[32];
    wire is_exp   = (mode_in == 2'b00);
    wire is_gelu  = (mode_in == 2'b01);
    wire is_silu  = (mode_in == 2'b10);

    wire exp_pos_ovf = sum_in[26] || (|sum_in[31:27]);

    wire signed [15:0] trunc_val = sum_in[29:14];
    wire hi_bits_not_all_0 = (|sum_in[31:29]);
    wire hi_bits_not_all_1 = (~&sum_in[31:29]);

    wire gs_pos_ovf   = (sign_bit == 1'b0) && (hi_bits_not_all_0 || ($signed(trunc_val) > 16'sh6000));
    wire gelu_neg_ovf = (sign_bit == 1'b1) && (hi_bits_not_all_1 || ($signed(trunc_val) < 16'shFD48));
    wire silu_neg_ovf = (sign_bit == 1'b1) && (hi_bits_not_all_1 || ($signed(trunc_val) < 16'shFB8D));

    always @(posedge i_clk) begin
        if (i_ena) begin
            force_0000 <= uf_in || (is_exp && sign_bit);
            force_8000 <= is_exp && !sign_bit && exp_pos_ovf;
            force_6000 <= !is_exp && gs_pos_ovf;
            force_fd48 <= is_gelu && gelu_neg_ovf;
            force_fb8d <= is_silu && silu_neg_ovf;
            normal_val <= is_exp ? sum_in[26:11] : trunc_val;
        end
    end

endmodule