`timescale 1ns / 1ps

module lane_stg2 (

    input  wire [1:0]         mode_in,            
    input  wire signed [15:0] x_in,              
    input  wire        [4:0]  idx_in,             
    input  wire               underflow_flag_in,  
    

    output wire signed [15:0] x_out,              
    output reg  signed [15:0] a_out,            
    output reg  signed [15:0] b_out,             
    output wire               underflow_flag_out  
);


    `include "npla_coef_params.vh"


    assign x_out = x_in;
    assign underflow_flag_out = underflow_flag_in;


    always @(*) begin
        case (mode_in)
            2'b01: begin 
                case (idx_in)
                    5'd0 : begin a_out = COEF_A_GELU_00; b_out = COEF_B_GELU_00; end
                    5'd1 : begin a_out = COEF_A_GELU_01; b_out = COEF_B_GELU_01; end
                    5'd2 : begin a_out = COEF_A_GELU_02; b_out = COEF_B_GELU_02; end
                    5'd3 : begin a_out = COEF_A_GELU_03; b_out = COEF_B_GELU_03; end
                    5'd4 : begin a_out = COEF_A_GELU_04; b_out = COEF_B_GELU_04; end
                    5'd5 : begin a_out = COEF_A_GELU_05; b_out = COEF_B_GELU_05; end
                    5'd6 : begin a_out = COEF_A_GELU_06; b_out = COEF_B_GELU_06; end
                    5'd7 : begin a_out = COEF_A_GELU_07; b_out = COEF_B_GELU_07; end
                    5'd8 : begin a_out = COEF_A_GELU_08; b_out = COEF_B_GELU_08; end
                    5'd9 : begin a_out = COEF_A_GELU_09; b_out = COEF_B_GELU_09; end
                    5'd10: begin a_out = COEF_A_GELU_10; b_out = COEF_B_GELU_10; end
                    5'd11: begin a_out = COEF_A_GELU_11; b_out = COEF_B_GELU_11; end
                    5'd12: begin a_out = COEF_A_GELU_12; b_out = COEF_B_GELU_12; end
                    5'd13: begin a_out = COEF_A_GELU_13; b_out = COEF_B_GELU_13; end
                    5'd14: begin a_out = COEF_A_GELU_14; b_out = COEF_B_GELU_14; end
                    5'd15: begin a_out = COEF_A_GELU_15; b_out = COEF_B_GELU_15; end
                    5'd16: begin a_out = COEF_A_GELU_16; b_out = COEF_B_GELU_16; end
                    5'd17: begin a_out = COEF_A_GELU_17; b_out = COEF_B_GELU_17; end
                    5'd18: begin a_out = COEF_A_GELU_18; b_out = COEF_B_GELU_18; end
                    5'd19: begin a_out = COEF_A_GELU_19; b_out = COEF_B_GELU_19; end
                    5'd20: begin a_out = COEF_A_GELU_20; b_out = COEF_B_GELU_20; end
                    5'd21: begin a_out = COEF_A_GELU_21; b_out = COEF_B_GELU_21; end
                    5'd22: begin a_out = COEF_A_GELU_22; b_out = COEF_B_GELU_22; end
                    5'd23: begin a_out = COEF_A_GELU_23; b_out = COEF_B_GELU_23; end
                    5'd24: begin a_out = COEF_A_GELU_24; b_out = COEF_B_GELU_24; end
                    5'd25: begin a_out = COEF_A_GELU_25; b_out = COEF_B_GELU_25; end
                    5'd26: begin a_out = COEF_A_GELU_26; b_out = COEF_B_GELU_26; end
                    5'd27: begin a_out = COEF_A_GELU_27; b_out = COEF_B_GELU_27; end
                    5'd28: begin a_out = COEF_A_GELU_28; b_out = COEF_B_GELU_28; end
                    5'd29: begin a_out = COEF_A_GELU_29; b_out = COEF_B_GELU_29; end
                    5'd30: begin a_out = COEF_A_GELU_30; b_out = COEF_B_GELU_30; end
                    5'd31: begin a_out = COEF_A_GELU_31; b_out = COEF_B_GELU_31; end
                    default: begin a_out = 16'sh0000; b_out = 16'sh0000; end
                endcase
            end

            2'b10: begin 
                case (idx_in)
                    5'd0 : begin a_out = COEF_A_SILU_00; b_out = COEF_B_SILU_00; end
                    5'd1 : begin a_out = COEF_A_SILU_01; b_out = COEF_B_SILU_01; end
                    5'd2 : begin a_out = COEF_A_SILU_02; b_out = COEF_B_SILU_02; end
                    5'd3 : begin a_out = COEF_A_SILU_03; b_out = COEF_B_SILU_03; end
                    5'd4 : begin a_out = COEF_A_SILU_04; b_out = COEF_B_SILU_04; end
                    5'd5 : begin a_out = COEF_A_SILU_05; b_out = COEF_B_SILU_05; end
                    5'd6 : begin a_out = COEF_A_SILU_06; b_out = COEF_B_SILU_06; end
                    5'd7 : begin a_out = COEF_A_SILU_07; b_out = COEF_B_SILU_07; end
                    5'd8 : begin a_out = COEF_A_SILU_08; b_out = COEF_B_SILU_08; end
                    5'd9 : begin a_out = COEF_A_SILU_09; b_out = COEF_B_SILU_09; end
                    5'd10: begin a_out = COEF_A_SILU_10; b_out = COEF_B_SILU_10; end
                    5'd11: begin a_out = COEF_A_SILU_11; b_out = COEF_B_SILU_11; end
                    5'd12: begin a_out = COEF_A_SILU_12; b_out = COEF_B_SILU_12; end
                    5'd13: begin a_out = COEF_A_SILU_13; b_out = COEF_B_SILU_13; end
                    5'd14: begin a_out = COEF_A_SILU_14; b_out = COEF_B_SILU_14; end
                    5'd15: begin a_out = COEF_A_SILU_15; b_out = COEF_B_SILU_15; end
                    5'd16: begin a_out = COEF_A_SILU_16; b_out = COEF_B_SILU_16; end
                    5'd17: begin a_out = COEF_A_SILU_17; b_out = COEF_B_SILU_17; end
                    5'd18: begin a_out = COEF_A_SILU_18; b_out = COEF_B_SILU_18; end
                    5'd19: begin a_out = COEF_A_SILU_19; b_out = COEF_B_SILU_19; end
                    5'd20: begin a_out = COEF_A_SILU_20; b_out = COEF_B_SILU_20; end
                    5'd21: begin a_out = COEF_A_SILU_21; b_out = COEF_B_SILU_21; end
                    5'd22: begin a_out = COEF_A_SILU_22; b_out = COEF_B_SILU_22; end
                    5'd23: begin a_out = COEF_A_SILU_23; b_out = COEF_B_SILU_23; end
                    5'd24: begin a_out = COEF_A_SILU_24; b_out = COEF_B_SILU_24; end
                    5'd25: begin a_out = COEF_A_SILU_25; b_out = COEF_B_SILU_25; end
                    5'd26: begin a_out = COEF_A_SILU_26; b_out = COEF_B_SILU_26; end
                    5'd27: begin a_out = COEF_A_SILU_27; b_out = COEF_B_SILU_27; end
                    5'd28: begin a_out = COEF_A_SILU_28; b_out = COEF_B_SILU_28; end
                    5'd29: begin a_out = COEF_A_SILU_29; b_out = COEF_B_SILU_29; end
                    5'd30: begin a_out = COEF_A_SILU_30; b_out = COEF_B_SILU_30; end
                    5'd31: begin a_out = COEF_A_SILU_31; b_out = COEF_B_SILU_31; end
                    default: begin a_out = 16'sh0000; b_out = 16'sh0000; end
                endcase
            end

            default: begin 
                case (idx_in)
                    5'd0 : begin a_out = COEF_A_EXP_00; b_out = COEF_B_EXP_00; end
                    5'd1 : begin a_out = COEF_A_EXP_01; b_out = COEF_B_EXP_01; end
                    5'd2 : begin a_out = COEF_A_EXP_02; b_out = COEF_B_EXP_02; end
                    5'd3 : begin a_out = COEF_A_EXP_03; b_out = COEF_B_EXP_03; end
                    5'd4 : begin a_out = COEF_A_EXP_04; b_out = COEF_B_EXP_04; end
                    5'd5 : begin a_out = COEF_A_EXP_05; b_out = COEF_B_EXP_05; end
                    5'd6 : begin a_out = COEF_A_EXP_06; b_out = COEF_B_EXP_06; end
                    5'd7 : begin a_out = COEF_A_EXP_07; b_out = COEF_B_EXP_07; end
                    5'd8 : begin a_out = COEF_A_EXP_08; b_out = COEF_B_EXP_08; end
                    5'd9 : begin a_out = COEF_A_EXP_09; b_out = COEF_B_EXP_09; end
                    5'd10: begin a_out = COEF_A_EXP_10; b_out = COEF_B_EXP_10; end
                    5'd11: begin a_out = COEF_A_EXP_11; b_out = COEF_B_EXP_11; end
                    5'd12: begin a_out = COEF_A_EXP_12; b_out = COEF_B_EXP_12; end
                    5'd13: begin a_out = COEF_A_EXP_13; b_out = COEF_B_EXP_13; end
                    5'd14: begin a_out = COEF_A_EXP_14; b_out = COEF_B_EXP_14; end
                    5'd15: begin a_out = COEF_A_EXP_15; b_out = COEF_B_EXP_15; end
                    5'd16: begin a_out = COEF_A_EXP_16; b_out = COEF_B_EXP_16; end
                    5'd17: begin a_out = COEF_A_EXP_17; b_out = COEF_B_EXP_17; end
                    5'd18: begin a_out = COEF_A_EXP_18; b_out = COEF_B_EXP_18; end
                    5'd19: begin a_out = COEF_A_EXP_19; b_out = COEF_B_EXP_19; end
                    5'd20: begin a_out = COEF_A_EXP_20; b_out = COEF_B_EXP_20; end
                    5'd21: begin a_out = COEF_A_EXP_21; b_out = COEF_B_EXP_21; end
                    5'd22: begin a_out = COEF_A_EXP_22; b_out = COEF_B_EXP_22; end
                    5'd23: begin a_out = COEF_A_EXP_23; b_out = COEF_B_EXP_23; end
                    5'd24: begin a_out = COEF_A_EXP_24; b_out = COEF_B_EXP_24; end
                    5'd25: begin a_out = COEF_A_EXP_25; b_out = COEF_B_EXP_25; end
                    5'd26: begin a_out = COEF_A_EXP_26; b_out = COEF_B_EXP_26; end
                    5'd27: begin a_out = COEF_A_EXP_27; b_out = COEF_B_EXP_27; end
                    5'd28: begin a_out = COEF_A_EXP_28; b_out = COEF_B_EXP_28; end
                    5'd29: begin a_out = COEF_A_EXP_29; b_out = COEF_B_EXP_29; end
                    5'd30: begin a_out = COEF_A_EXP_30; b_out = COEF_B_EXP_30; end
                    5'd31: begin a_out = COEF_A_EXP_31; b_out = COEF_B_EXP_31; end
                    default: begin a_out = 16'sh0000; b_out = 16'sh0000; end
                endcase
            end
        endcase
    end

endmodule