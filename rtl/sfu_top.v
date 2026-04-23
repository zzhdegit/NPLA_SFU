`timescale 1ns / 1ps

module sfu_top (
    input  wire         i_clk,
    input  wire         i_rst_n,
    
    // --- Config Interface ---
    input  wire         i_cfg_en,
    input  wire         i_cfg_we,
    input  wire [1:0]   i_cfg_slot,     // Target slot for configuration
    input  wire [6:0]   i_cfg_addr,
    input  wire [15:0]  i_cfg_wdata,
    
    // --- Active Control ---
    input  wire [1:0]   i_active_slot,  // Current slot used for computation
    
    // --- Data Interface ---
    input  wire         i_valid,
    output wire         o_ready,
    input  wire [255:0] i_data_bus,
    output wire         o_valid,
    input  wire         i_ready,
    output wire [255:0] o_data_bus
);

    // =========================================================================
    // 1. Multi-Slot Configuration Register File (4 Slots)
    // =========================================================================
    reg [15:0] r_cfg_bnd_min     [0:3];
    reg [15:0] r_cfg_bnd         [0:3][0:31];
    reg [15:0] r_cfg_coef_a      [0:3][0:31];
    reg [15:0] r_cfg_coef_b      [0:3][0:31];
    reg [4:0]  r_cfg_norm_shift  [0:3];
    reg [15:0] r_cfg_sat_pos_val [0:3];
    reg [15:0] r_cfg_sat_neg_val [0:3];
    reg [15:0] r_cfg_sat_uf_val  [0:3];
    
    // Config write safe gate
    wire w_pipeline_busy;
    wire w_safe_cfg_we   = i_cfg_en && i_cfg_we && !w_pipeline_busy;
    
    integer si, ki;
    initial begin
        for (si = 0; si < 4; si = si + 1) begin
            r_cfg_bnd_min[si] = 16'h0;
            r_cfg_norm_shift[si] = 5'h0;
            r_cfg_sat_pos_val[si] = 16'h0;
            r_cfg_sat_neg_val[si] = 16'h0;
            r_cfg_sat_uf_val[si] = 16'h0;
            for (ki = 0; ki < 32; ki = ki + 1) begin
                r_cfg_bnd[si][ki] = 16'h0;
                r_cfg_coef_a[si][ki] = 16'h0;
                r_cfg_coef_b[si][ki] = 16'h0;
            end
        end
    end

    always @(posedge i_clk or negedge i_rst_n) begin
        if (!i_rst_n) begin
            for (si = 0; si < 4; si = si + 1) begin
                r_cfg_bnd_min[si]     <= 16'sh8000;
                r_cfg_norm_shift[si]  <= 5'd11;
                r_cfg_sat_pos_val[si] <= 16'sh8000;
                r_cfg_sat_neg_val[si] <= 16'shFD48;
                r_cfg_sat_uf_val[si]  <= 16'h0000;
                for (ki = 0; ki < 32; ki = ki + 1) begin
                    r_cfg_bnd[si][ki]    <= 16'h0000;
                    r_cfg_coef_a[si][ki] <= 16'h0000;
                    r_cfg_coef_b[si][ki] <= 16'h0000;
                end
            end
        end else if (w_safe_cfg_we) begin
            if (i_cfg_addr == 7'h00) r_cfg_bnd_min[i_cfg_slot] <= i_cfg_wdata;
            else if (i_cfg_addr >= 7'h01 && i_cfg_addr <= 7'h20) r_cfg_bnd[i_cfg_slot][i_cfg_addr - 7'h01] <= i_cfg_wdata;
            else if (i_cfg_addr >= 7'h21 && i_cfg_addr <= 7'h40) r_cfg_coef_a[i_cfg_slot][i_cfg_addr - 7'h21] <= i_cfg_wdata;
            else if (i_cfg_addr >= 7'h41 && i_cfg_addr <= 7'h60) r_cfg_coef_b[i_cfg_slot][i_cfg_addr - 7'h41] <= i_cfg_wdata;
            else if (i_cfg_addr == 7'h61) r_cfg_norm_shift[i_cfg_slot] <= i_cfg_wdata[4:0];
            else if (i_cfg_addr == 7'h62) r_cfg_sat_pos_val[i_cfg_slot] <= i_cfg_wdata;
            else if (i_cfg_addr == 7'h63) r_cfg_sat_neg_val[i_cfg_slot] <= i_cfg_wdata;
            else if (i_cfg_addr == 7'h64) r_cfg_sat_uf_val[i_cfg_slot] <= i_cfg_wdata;
        end
    end

    // =========================================================================
    // 2. Parameter Selection & Broadcast
    // =========================================================================
    wire [511:0] w_active_bnd_bus, w_active_coef_a_bus, w_active_coef_b_bus;
    genvar p;
    generate
        for (p = 0; p < 32; p = p + 1) begin : gen_param_mux
            assign w_active_bnd_bus[p*16 +: 16]    = r_cfg_bnd[i_active_slot][p];
            assign w_active_coef_a_bus[p*16 +: 16] = r_cfg_coef_a[i_active_slot][p];
            assign w_active_coef_b_bus[p*16 +: 16] = r_cfg_coef_b[i_active_slot][p];
        end
    endgenerate

    // =========================================================================
    // 3. Lane Instantiations & Local Pipeline Control
    // =========================================================================
    wire [15:0] vld_stg1_bus, vld_stg2_bus, vld_stg3_bus, vld_stg4_bus, vld_stg5_bus, vld_stg6_bus, vld_stg7_bus;
    wire [15:0] allow_in_stg1_bus;

    assign o_ready = &allow_in_stg1_bus;
    assign o_valid = |vld_stg7_bus;
    assign w_pipeline_busy = |vld_stg1_bus | |vld_stg2_bus | |vld_stg3_bus | |vld_stg4_bus | |vld_stg5_bus | |vld_stg6_bus | |vld_stg7_bus;

    genvar i;
    generate
        for (i = 0; i < 16; i = i + 1) begin : LANE
            reg vld_stg1, vld_stg2, vld_stg3, vld_stg4, vld_stg5, vld_stg6, vld_stg7;
            initial {vld_stg1, vld_stg2, vld_stg3, vld_stg4, vld_stg5, vld_stg6, vld_stg7} = 7'b0;

            assign vld_stg1_bus[i] = vld_stg1; assign vld_stg2_bus[i] = vld_stg2;
            assign vld_stg3_bus[i] = vld_stg3; assign vld_stg4_bus[i] = vld_stg4;
            assign vld_stg5_bus[i] = vld_stg5; assign vld_stg6_bus[i] = vld_stg6;
            assign vld_stg7_bus[i] = vld_stg7;

            wire allow_in_stg7 = !vld_stg7 || i_ready;
            wire allow_in_stg6 = !vld_stg6 || allow_in_stg7;
            wire allow_in_stg5 = !vld_stg5 || allow_in_stg6;
            wire allow_in_stg4 = !vld_stg4 || allow_in_stg5;
            wire allow_in_stg3 = !vld_stg3 || allow_in_stg4;
            wire allow_in_stg2 = !vld_stg2 || allow_in_stg3;
            wire allow_in_stg1 = !vld_stg1 || allow_in_stg2;
            assign allow_in_stg1_bus[i] = allow_in_stg1;

            always @(posedge i_clk or negedge i_rst_n) begin
                if (!i_rst_n) {vld_stg1, vld_stg2, vld_stg3, vld_stg4, vld_stg5, vld_stg6, vld_stg7} <= 7'b0;
                else begin
                    if (allow_in_stg1) vld_stg1 <= i_valid;
                    if (allow_in_stg2) vld_stg2 <= vld_stg1;
                    if (allow_in_stg3) vld_stg3 <= vld_stg2;
                    if (allow_in_stg4) vld_stg4 <= vld_stg3;
                    if (allow_in_stg5) vld_stg5 <= vld_stg4;
                    if (allow_in_stg6) vld_stg6 <= vld_stg5;
                    if (allow_in_stg7) vld_stg7 <= vld_stg6;
                end
            end

            sfu_lane u_lane (
                .i_clk(i_clk), .i_rst_n(i_rst_n),
                .i_ena_stg1(i_valid && allow_in_stg1), .i_ena_stg2(vld_stg1 && allow_in_stg2),
                .i_ena_stg3(vld_stg2 && allow_in_stg3), .i_ena_stg4(vld_stg3 && allow_in_stg4),
                .i_ena_stg5(vld_stg4 && allow_in_stg5), .i_ena_stg6(vld_stg5 && allow_in_stg6),
                .i_ena_stg7(vld_stg6 && allow_in_stg7),
                .i_x(i_data_bus[i*16 +: 16]),
                .cfg_bnd_min(r_cfg_bnd_min[i_active_slot]), .cfg_bnd(w_active_bnd_bus),
                .cfg_coef_a(w_active_coef_a_bus), .cfg_coef_b(w_active_coef_b_bus),
                .cfg_norm_shift(r_cfg_norm_shift[i_active_slot]),
                .cfg_sat_pos_val(r_cfg_sat_pos_val[i_active_slot]),
                .cfg_sat_neg_val(r_cfg_sat_neg_val[i_active_slot]),
                .cfg_sat_uf_val(r_cfg_sat_uf_val[i_active_slot]),
                .o_y(o_data_bus[i*16 +: 16])
            );
        end
    endgenerate
endmodule
