import os, sys, random, math, subprocess

try:
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    print("Installing matplotlib and numpy...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib", "numpy"])
    import matplotlib.pyplot as plt
    import numpy as np

# 1. Write XDC files
with open("sfu_timing_cu50.xdc", "w") as f:
    f.write("create_clock -period 2.02 -name i_clk [get_ports i_clk]\n")
with open("sfu_timing_z7020.xdc", "w") as f:
    f.write("create_clock -period 6.50 -name i_clk [get_ports i_clk]\n")

# 2. Write TCL files
cu50_tcl = """
create_project sfu_impl_cu50 ./sfu_impl_cu50_prj -part xcu50-fsvh2104-2-e -force
add_files {sfu_top.v sfu_lane.v}
add_files -fileset constrs_1 sfu_timing_cu50.xdc
synth_design -top sfu_top -part xcu50-fsvh2104-2-e -retiming -mode out_of_context
opt_design
place_design
phys_opt_design
route_design
report_utilization -file vivadoreport/impl_utilization_cu50.txt
report_timing_summary -file vivadoreport/impl_timing_cu50.txt
"""
with open("run_impl_cu50.tcl", "w") as f: f.write(cu50_tcl)

z7020_tcl = """
create_project sfu_impl_z7020 ./sfu_impl_z7020_prj -part xc7z020clg400-1 -force
add_files {sfu_top.v sfu_lane.v}
add_files -fileset constrs_1 sfu_timing_z7020.xdc
synth_design -top sfu_top -part xc7z020clg400-1 -retiming -mode out_of_context
opt_design
place_design
phys_opt_design
route_design
report_utilization -file vivadoreport/impl_utilization_z7020.txt
report_timing_summary -file vivadoreport/impl_timing_z7020.txt
"""
with open("run_impl_z7020.tcl", "w") as f: f.write(z7020_tcl)

def to_hex(val, bits=16):
    if val < 0: val = (1 << bits) + val
    return f"{val:0{bits//4}X}"

# Parameters
bnd_exp_min = "8000"
bnd_exp = ["9F3F", "AEDD", "B954", "C135", "C787", "CCCD", "D154", "D54B", "D8D3", "DC00", "DEE5", "E18B", "E3FE", "E644", "E864", "EA61", "EC41", "EE07", "EFB4", "F14C", "F2D1", "F444", "F5A7", "F6FB", "F842", "F97D", "FAAB", "FBCF", "FCE9", "FDF9", "FF00"]
coef_a_exp = ["0011", "0042", "0091", "0100", "018D", "0239", "0304", "03EE", "04F7", "061E", "0765", "08CA", "0A4F", "0BF2", "0DB4", "0F95", "1195", "13B3", "15F1", "184D", "1AC9", "1D63", "201C", "22F4", "25EB", "2901", "2C35", "2F89", "32FB", "368C", "3A3D", "3E0C"]
coef_b_exp = ["008A", "01B0", "0343", "052B", "0755", "09B5", "0C3E", "0EE9", "11AB", "147F", "175E", "1A41", "1D25", "2002", "22D6", "259C", "2850", "2AED", "2D72", "2FD9", "3221", "3446", "3645", "381C", "39C8", "3B46", "3C94", "3DB0", "3E97", "3F48", "3FBF", "3FFC"]

bnd_gelu_min = "A000"
bnd_gelu = ["CAFD", "D379", "D926", "DDD5", "E239", "E736", "EE08", "F114", "F383", "F5A1", "F790", "F95F", "FB17", "FCC1", "FE63", "0000", "019D", "033F", "04E9", "06A1", "0870", "0A5F", "0C7D", "0EEC", "11F8", "18CA", "1DC7", "222B", "26DA", "2C87", "3503"]
coef_a_gelu = ["FFF7", "FF48", "FE07", "FC64", "FA89", "F8B1", "F812", "FA53", "FD6D", "011B", "0538", "09AB", "0E60", "1347", "1850", "1D6E", "2292", "27B0", "2CB9", "31A0", "3655", "3AC8", "3EE5", "4293", "45AD", "47EE", "474F", "4577", "439C", "41F9", "40B8", "4009"]
coef_b_gelu = ["FFD0", "FD8C", "FA11", "F616", "F21F", "EEB3", "EDAB", "F033", "F318", "F5F7", "F8A1", "FAFA", "FCED", "FE6E", "FF74", "FFF8", "FFF8", "FF74", "FE6E", "FCED", "FAFA", "F8A1", "F5F7", "F318", "F033", "EDAB", "EEB3", "F21F", "F616", "FA11", "FD8C", "FFD0"]

bnd_silu_min = "A000"
bnd_silu = ["AE07", "B8F3", "C23E", "CACE", "D3CF", "E1B1", "E6D3", "EAC9", "EE27", "F127", "F3E9", "F67F", "F8F7", "FB5A", "FDB0", "0000", "0250", "04A6", "0709", "0981", "0C17", "0ED9", "11D9", "1537", "192D", "1E4F", "2C31", "3532", "3DC2", "470D", "51F9"]
coef_a_silu = ["FEDE", "FDFE", "FCED", "FBB7", "FA78", "F9D6", "FB83", "FDED", "00DF", "043E", "07F5", "0BF5", "102F", "1495", "191A", "1DB1", "224F", "26E6", "2B6B", "2FD1", "340B", "380B", "3BC2", "3F21", "4213", "447D", "462A", "4588", "4449", "4313", "4202", "4122"]
coef_b_silu = ["F84E", "F3D2", "EF12", "EA68", "E644", "E46E", "E79A", "EB67", "EF4F", "F311", "F684", "F98A", "FC0C", "FDFB", "FF4C", "FFF5", "FFF5", "FF4C", "FDFB", "FC0C", "F98A", "F684", "F311", "EF4F", "EB67", "E79A", "E46E", "E644", "EA68", "EF12", "F3D2", "F84E"]

def write_cfg(name, bnd_min, bnd, coef_a, coef_b, shift, pos_val, neg_val, uf_val):
    cfg = ["0000"] * 101
    cfg[0] = bnd_min
    for i in range(32): cfg[1+i] = bnd[i] if i < 31 else "7FFF" # bnd[31] dummy
    for i in range(32): cfg[33+i] = coef_a[i]
    for i in range(32): cfg[65+i] = coef_b[i]
    cfg[97] = shift
    cfg[98] = pos_val
    cfg[99] = neg_val
    cfg[100] = uf_val
    with open(f"{name}_cfg.hex", "w") as f: f.write("\n".join(cfg))

write_cfg("exp", "8000", bnd_exp, coef_a_exp, coef_b_exp, "000B", "8000", "0000", "0000")
write_cfg("gelu", "A000", bnd_gelu, coef_a_gelu, coef_b_gelu, "000E", "6000", "FD48", "0000")
write_cfg("silu", "A000", bnd_silu, coef_a_silu, coef_b_silu, "000E", "6000", "FB8D", "0000")

random.seed(42)
inputs_exp = [to_hex(int(random.uniform(-8.0, 0.0) * 4096)) for _ in range(800)]
inputs_gelu = [to_hex(int(random.uniform(-6.0, 6.0) * 4096)) for _ in range(800)]
inputs_silu = [to_hex(int(random.uniform(-6.0, 6.0) * 4096)) for _ in range(800)]
with open("exp_in.hex", "w") as f: f.write("\n".join(inputs_exp))
with open("gelu_in.hex", "w") as f: f.write("\n".join(inputs_gelu))
with open("silu_in.hex", "w") as f: f.write("\n".join(inputs_silu))

tb_code = r'''`timescale 1ns/1ps

module sfu_tb;
    reg i_clk;
    reg i_rst_n;
    reg i_cfg_en;
    reg i_cfg_we;
    reg [6:0] i_cfg_addr;
    reg [15:0] i_cfg_wdata;
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
        .i_cfg_addr(i_cfg_addr),
        .i_cfg_wdata(i_cfg_wdata),
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
    reg [15:0] input_data [0:799];
    integer i, j, k, m, out_fd;
    
    initial begin
        i_rst_n = 0;
        i_cfg_en = 0; i_cfg_we = 0; i_cfg_addr = 0; i_cfg_wdata = 0;
        i_valid = 0; i_data_bus = 0; i_ready = 1;
        #20 i_rst_n = 1;
        #20;
        run_test(0);
        run_test(1);
        run_test(2);
        $finish;
    end
    
    task run_test(input integer test_id);
        begin
            if (test_id == 0) begin
                $readmemh("exp_cfg.hex", cfg_data);
                $readmemh("exp_in.hex", input_data);
                out_fd = $fopen("exp_out.txt", "w");
            end else if (test_id == 1) begin
                $readmemh("gelu_cfg.hex", cfg_data);
                $readmemh("gelu_in.hex", input_data);
                out_fd = $fopen("gelu_out.txt", "w");
            end else if (test_id == 2) begin
                $readmemh("silu_cfg.hex", cfg_data);
                $readmemh("silu_in.hex", input_data);
                out_fd = $fopen("silu_out.txt", "w");
            end
            
            for (i=0; i<100; i=i+1) begin
                @(posedge i_clk); #1;
                i_cfg_en = 1; i_cfg_we = 1; i_cfg_addr = i; i_cfg_wdata = cfg_data[i];
            end
            @(posedge i_clk); #1;
            i_cfg_en = 0; i_cfg_we = 0;
            #100;
            
            fork
                begin
                    for (i=0; i<50; i=i+1) begin
                        @(posedge i_clk); #1;
                        while (!o_ready) begin @(posedge i_clk); #1; end
                        i_valid = 1;
                        for (j=0; j<16; j=j+1) i_data_bus[j*16 +: 16] = input_data[i*16 + j];
                    end
                    @(posedge i_clk); #1;
                    i_valid = 0;
                end
                begin
                    for (k=0; k<50; k=k+1) begin
                        @(posedge i_clk);
                        while (!o_valid) @(posedge i_clk);
                        for (m=0; m<16; m=m+1) $fdisplay(out_fd, "%h %h", input_data[k*16 + m], o_data_bus[m*16 +: 16]);
                    end
                end
            join
            $fclose(out_fd);
            #100;
        end
    endtask
endmodule
'''
with open("sfu_tb.v", "w") as f: f.write(tb_code)
# Run simulation
print("Running Vivado XSIM simulation...")
# Fixed paths relative to project root
subprocess.run([r"D:\Xilinx\Vivado\2024.2\bin\xvlog.bat", "src/sfu_top.v", "src/sfu_lane.v", "tb/sfu_tb.v"], check=True)
subprocess.run([r"D:\Xilinx\Vivado\2024.2\bin\xelab.bat", "sfu_tb", "-s", "sfu_sim", "-debug", "typical"], check=True)
subprocess.run([r"D:\Xilinx\Vivado\2024.2\bin\xsim.bat", "sfu_sim", "-R"], check=True)

print("Simulation finished. Analyzing and plotting...")
os.makedirs("vivadoreport", exist_ok=True)

def from_hex(hex_str, bits=16, signed=True):
    val = int(hex_str, 16)
    if signed and val >= (1 << (bits - 1)): val -= (1 << bits)
    return val

def analyze(name, math_func, out_scale, is_signed_out=True):
    if not os.path.exists(f"{name}_out.txt"):
        print(f"Error: {name}_out.txt not found!")
        return
    with open(f"{name}_out.txt") as f: lines = f.readlines()
    
    xs, errs = [], []
    for line in lines:
        if not line.strip(): continue
        parts = line.split()
        x = from_hex(parts[0], 16, True) / 4096.0
        y = from_hex(parts[1], 16, is_signed_out) / out_scale
        math_y = math_func(x)
        
        raw_err = y - math_y
        xs.append(x)
        errs.append(raw_err)
        
    plt.scatter(xs, errs, s=8, alpha=0.6)
    plt.title(f"{name.upper()} Error (NPLA - Exact)")
    plt.xlabel("Input Value (x)")
    plt.ylabel("Error")
    plt.grid(True)
    plt.savefig(f"vivadoreport/{name}_error.png")
    plt.clf()

def gelu(x): return 0.5 * x * (1 + math.erf(x / math.sqrt(2)))
def silu(x): return x / (1 + math.exp(-x))

analyze("exp", math.exp, 32768.0, is_signed_out=False)
analyze("gelu", gelu, 4096.0, is_signed_out=True)
analyze("silu", silu, 4096.0, is_signed_out=True)
print("Plots saved in vivadoreport/")
