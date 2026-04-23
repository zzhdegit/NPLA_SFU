`timescale 1ns/1ps

module sfu_tb;
    reg i_clk;
    reg i_rst_n;
    reg i_cfg_en;
    reg i_cfg_we;
    reg [1:0] i_cfg_slot;
    reg [6:0] i_cfg_addr;
    reg [15:0] i_cfg_wdata;
    reg [1:0] i_active_slot;
    reg i_valid;
    wire o_ready;
    reg [255:0] i_data_bus;
    wire o_valid;
    reg i_ready;
    wire [255:0] o_data_bus;
    
    sfu_top dut (
        .i_clk(i_clk),
        .i_rst_n(i_rst_n),
        .i_cfg_en(i_cfg_en),
        .i_cfg_we(i_cfg_we),
        .i_cfg_slot(i_cfg_slot),
        .i_cfg_addr(i_cfg_addr),
        .i_cfg_wdata(i_cfg_wdata),
        .i_active_slot(i_active_slot),
        .i_valid(i_valid),
        .o_ready(o_ready),
        .i_data_bus(i_data_bus),
        .o_valid(o_valid),
        .i_ready(i_ready),
        .o_data_bus(o_data_bus)
    );

    initial begin
        i_clk = 0;
        forever #5 i_clk = ~i_clk;
    end
    
    reg [15:0] cfg_data [0:100];
    reg [15:0] input_data [0:15999];
    integer i, j, k, m, out_fd;
    
    initial begin
        // --- STABLE INITIALIZATION ---
        i_rst_n = 0;
        i_cfg_en = 0; i_cfg_we = 0; i_cfg_slot = 0; i_cfg_addr = 0; i_cfg_wdata = 0;
        i_active_slot = 0; i_valid = 0; i_data_bus = 0; i_ready = 1;
        
        repeat(10) @(posedge i_clk);
        i_rst_n <= 1'b1;
        repeat(10) @(posedge i_clk);
        
        // Pre-load all slots using integer IDs to avoid string pad issues
        load_slot(0, 0);
        load_slot(1, 1);
        load_slot(2, 2);
        
        repeat(50) @(posedge i_clk);
        
        // Test Slot Switching
        i_active_slot <= 2'd0; run_compute(0);
        i_active_slot <= 2'd1; run_compute(1);
        i_active_slot <= 2'd2; run_compute(2);
        
        $finish;
    end
    
    task load_slot(input [1:0] slot_id, input integer type_id);
        begin
            if (type_id == 0) $readmemh("D:/IC_Workspace/SFU/rtl/tb/exp_cfg.hex", cfg_data);
            else if (type_id == 1) $readmemh("D:/IC_Workspace/SFU/rtl/tb/gelu_cfg.hex", cfg_data);
            else if (type_id == 2) $readmemh("D:/IC_Workspace/SFU/rtl/tb/silu_cfg.hex", cfg_data);
            
            for (i=0; i<101; i=i+1) begin
                @(posedge i_clk);
                #2; // Drive away from edge
                i_cfg_en   <= 1'b1;
                i_cfg_we   <= 1'b1;
                i_cfg_slot <= slot_id;
                i_cfg_addr <= i[6:0];
                i_cfg_wdata <= cfg_data[i];
            end
            @(posedge i_clk);
            #2;
            i_cfg_en <= 1'b0;
            i_cfg_we <= 1'b0;
        end
    endtask

    task run_compute(input integer type_id);
        reg [8*30:1] out_file;
        begin
            if (type_id == 0) begin out_file = "exp_out.txt"; $readmemh("D:/IC_Workspace/SFU/rtl/tb/exp_in.hex", input_data); end
            else if (type_id == 1) begin out_file = "gelu_out.txt"; $readmemh("D:/IC_Workspace/SFU/rtl/tb/gelu_in.hex", input_data); end
            else if (type_id == 2) begin out_file = "silu_out.txt"; $readmemh("D:/IC_Workspace/SFU/rtl/tb/silu_in.hex", input_data); end

            out_fd = $fopen(out_file, "w");
            fork
                begin
                    for (i=0; i<1000; i=i+1) begin
                        @(posedge i_clk);
                        while (!o_ready) @(posedge i_clk);
                        #2;
                        i_valid <= 1'b1;
                        for (j=0; j<16; j=j+1) i_data_bus[j*16 +: 16] <= input_data[i*16 + j];
                    end
                    @(posedge i_clk);
                    #2;
                    i_valid <= 1'b0;
                end
                begin
                    // Correct synchronization: wait for the very first valid pulse
                    @(posedge i_clk);
                    while (!o_valid) @(posedge i_clk);
                    
                    for (k=0; k<1000; k=k+1) begin
                        // Sample the current bus
                        for (m=0; m<16; m=m+1) $fdisplay(out_fd, "%h %h", input_data[k*16 + m], o_data_bus[m*16 +: 16]);
                        // Move to next cycle
                        @(posedge i_clk);
                        while (!o_valid && k < 999) @(posedge i_clk);
                    end
                end
            join
            $fclose(out_fd);
            repeat(10) @(posedge i_clk);
        end
    endtask
endmodule
