`timescale 1ns / 1ps

module lane_stg6 (
    input  wire               i_clk,
    input  wire               i_ena,
    input  wire               force_0000,
    input  wire               force_8000,
    input  wire               force_6000,
    input  wire               force_fd48,
    input  wire               force_fb8d,
    input  wire [15:0]        normal_val,
    
    output reg  [15:0]        y_out
);

    // 严禁综合器提取控制集，强制走最快的局部数据连线 (D-pin)
    (* extract_reset = "no", extract_set = "no" *)
    always @(posedge i_clk) begin
        if (i_ena) begin
            if      (force_0000) y_out <= 16'h0000;
            else if (force_8000) y_out <= 16'h8000;
            else if (force_6000) y_out <= 16'h6000;
            else if (force_fd48) y_out <= 16'hFD48;
            else if (force_fb8d) y_out <= 16'hFB8D;
            else                 y_out <= normal_val;
        end
    end

endmodule