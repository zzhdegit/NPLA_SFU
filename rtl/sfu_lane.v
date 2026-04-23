`timescale 1ns / 1ps

module sfu_lane (
    input  wire        i_clk,
    input  wire        i_rst_n,
    input  wire        i_ena_stg1, i_ena_stg2, i_ena_stg3, i_ena_stg4, i_ena_stg5, i_ena_stg6, i_ena_stg7,
    input  wire signed [15:0] i_x,
    input  wire signed [15:0] cfg_bnd_min,
    input  wire [511:0]       cfg_bnd, cfg_coef_a, cfg_coef_b,
    input  wire [4:0]         cfg_norm_shift,
    input  wire [15:0]        cfg_sat_pos_val, cfg_sat_neg_val, cfg_sat_uf_val,
    output reg  [15:0]        o_y
);

    wire signed [15:0] bnd [0:31];
    genvar i;
    generate
        for (i = 0; i < 32; i = i + 1) begin : gen_bnd
            assign bnd[i] = cfg_bnd[i*16 +: 16];
        end
    endgenerate

    reg [4:0]  r_stg1_idx;
    reg [15:0] r_stg1_x;
    reg        r_stg1_uf;

    always @(posedge i_clk or negedge i_rst_n) begin
        if (!i_rst_n) begin r_stg1_idx <= 5'd0; r_stg1_x <= 16'sh0; r_stg1_uf <= 1'b0; end
        else if (i_ena_stg1) begin
            r_stg1_x <= i_x; r_stg1_uf <= (i_x < cfg_bnd_min);
            if (i_x < bnd[15]) begin
                if (i_x < bnd[7]) begin
                    if (i_x < bnd[3]) begin
                        if (i_x < bnd[1]) r_stg1_idx <= (i_x < bnd[0]) ? 5'd0 : 5'd1;
                        else r_stg1_idx <= (i_x < bnd[2]) ? 5'd2 : 5'd3;
                    end else begin
                        if (i_x < bnd[5]) r_stg1_idx <= (i_x < bnd[4]) ? 5'd4 : 5'd5;
                        else r_stg1_idx <= (i_x < bnd[6]) ? 5'd6 : 5'd7;
                    end
                end else begin
                    if (i_x < bnd[11]) begin
                        if (i_x < bnd[9]) r_stg1_idx <= (i_x < bnd[8]) ? 5'd8 : 5'd9;
                        else r_stg1_idx <= (i_x < bnd[10]) ? 5'd10 : 5'd11;
                    end else begin
                        if (i_x < bnd[13]) r_stg1_idx <= (i_x < bnd[12]) ? 5'd12 : 5'd13;
                        else r_stg1_idx <= (i_x < bnd[14]) ? 5'd14 : 5'd15;
                    end
                end
            end else begin
                if (i_x < bnd[23]) begin
                    if (i_x < bnd[19]) begin
                        if (i_x < bnd[17]) r_stg1_idx <= (i_x < bnd[16]) ? 5'd16 : 5'd17;
                        else r_stg1_idx <= (i_x < bnd[18]) ? 5'd18 : 5'd19;
                    end else begin
                        if (i_x < bnd[21]) r_stg1_idx <= (i_x < bnd[20]) ? 5'd20 : 5'd21;
                        else r_stg1_idx <= (i_x < bnd[22]) ? 5'd22 : 5'd23;
                    end
                end else begin
                    if (i_x < bnd[27]) begin
                        if (i_x < bnd[25]) r_stg1_idx <= (i_x < bnd[24]) ? 5'd24 : 5'd25;
                        else r_stg1_idx <= (i_x < bnd[26]) ? 5'd26 : 5'd27;
                    end else begin
                        if (i_x < bnd[29]) r_stg1_idx <= (i_x < bnd[28]) ? 5'd28 : 5'd29;
                        else r_stg1_idx <= (i_x < bnd[30]) ? 5'd30 : 5'd31;
                    end
                end
            end
        end
    end

    reg signed [15:0] r_stg2_x, r_stg2_a, r_stg2_b;
    reg r_stg2_uf;
    always @(posedge i_clk or negedge i_rst_n) begin
        if (!i_rst_n) {r_stg2_x, r_stg2_a, r_stg2_b, r_stg2_uf} <= 49'b0;
        else if (i_ena_stg2) begin
            r_stg2_x <= r_stg1_x; r_stg2_uf <= r_stg1_uf;
            r_stg2_a <= cfg_coef_a[r_stg1_idx * 16 +: 16]; r_stg2_b <= cfg_coef_b[r_stg1_idx * 16 +: 16];
        end
    end

    reg signed [15:0] r_stg3_a, r_stg3_x;
    reg signed [32:0] r_stg3_b_ext;
    reg r_stg3_uf;
    always @(posedge i_clk or negedge i_rst_n) begin
        if (!i_rst_n) {r_stg3_a, r_stg3_x, r_stg3_b_ext, r_stg3_uf} <= 66'b0;
        else if (i_ena_stg3) begin
            r_stg3_a <= r_stg2_a; r_stg3_x <= r_stg2_x; r_stg3_uf <= r_stg2_uf;
            r_stg3_b_ext <= {{5{r_stg2_b[15]}}, r_stg2_b, 12'd0};
        end
    end

    reg signed [31:0] r_stg4_mult;
    reg signed [32:0] r_stg4_b_ext;
    reg r_stg4_uf;
    always @(posedge i_clk or negedge i_rst_n) begin
        if (!i_rst_n) {r_stg4_mult, r_stg4_b_ext, r_stg4_uf} <= 66'b0;
        else if (i_ena_stg4) begin
            r_stg4_mult <= r_stg3_a * r_stg3_x; r_stg4_b_ext <= r_stg3_b_ext; r_stg4_uf <= r_stg3_uf;
        end
    end

    reg signed [32:0] r_stg5_sum;
    reg r_stg5_uf;
    always @(posedge i_clk or negedge i_rst_n) begin
        if (!i_rst_n) {r_stg5_sum, r_stg5_uf} <= 34'b0;
        else if (i_ena_stg5) begin
            r_stg5_sum <= r_stg4_mult + r_stg4_b_ext; r_stg5_uf <= r_stg4_uf;
        end
    end

    reg r_stg6_uf, r_stg6_pos_ovf, r_stg6_neg_ovf;
    reg [15:0] r_stg6_trunc_val;
    always @(posedge i_clk or negedge i_rst_n) begin
        if (!i_rst_n) {r_stg6_uf, r_stg6_pos_ovf, r_stg6_neg_ovf, r_stg6_trunc_val} <= 19'b0;
        else if (i_ena_stg6) begin
            r_stg6_uf <= r_stg5_uf;
            r_stg6_trunc_val <= (r_stg5_sum >>> cfg_norm_shift);
            r_stg6_pos_ovf <= (r_stg5_sum > 0) && ((r_stg5_sum >>> cfg_norm_shift) > $signed({17'd0, cfg_sat_pos_val}));
            r_stg6_neg_ovf <= (r_stg5_sum < 0) && ((r_stg5_sum >>> cfg_norm_shift) < $signed({{17{cfg_sat_neg_val[15]}}, cfg_sat_neg_val}));
        end
    end

    always @(posedge i_clk or negedge i_rst_n) begin
        if (!i_rst_n) o_y <= 16'h0000;
        else if (i_ena_stg7) begin
            if (r_stg6_uf) o_y <= cfg_sat_uf_val;
            else if (r_stg6_pos_ovf) o_y <= cfg_sat_pos_val;
            else if (r_stg6_neg_ovf) o_y <= cfg_sat_neg_val;
            else o_y <= r_stg6_trunc_val;
        end
    end
endmodule
