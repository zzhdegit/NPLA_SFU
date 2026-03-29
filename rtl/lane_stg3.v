`timescale 1ns / 1ps

module lane_stg3 (
    input  wire               i_clk,
    input  wire               i_ena,
    input  wire [1:0]         mode_in,
    input  wire signed [15:0] x_in,
    input  wire signed [15:0] a_in,
    input  wire signed [15:0] b_in,
    input  wire               uf_in,
    
    output reg  [1:0]         mode_pipe,
    output reg  signed [15:0] a_reg,    // 传给 DSP A 端口
    output reg  signed [15:0] x_reg,    // 传给 DSP B 端口
    output reg  signed [32:0] b_ext_reg,// 传给 DSP C 端口
    output reg                uf_pipe
);

    // 仅做符号扩展，不加任何 offset
    wire signed [32:0] b_ext = {{5{b_in[15]}}, b_in, 12'd0};

    always @(posedge i_clk) begin
        if (i_ena) begin
            mode_pipe <= mode_in;
            a_reg     <= a_in;
            x_reg     <= x_in;
            b_ext_reg <= b_ext; 
            uf_pipe   <= uf_in;
        end
    end
endmodule