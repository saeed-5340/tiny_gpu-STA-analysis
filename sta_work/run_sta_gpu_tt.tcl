# ==========================
# run_sta_gpu_tt.tcl
# Corner: TT (25C, 1.8V)
# Usage: sta run_sta_gpu_tt.tcl > gpu_tt.txt
# ==========================
set LIB     "/home/saeed/.ciel/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib"
set NETLIST "/mnt/openlane_disk/tiny_gpu-STA-analysis/sta_work/gpu_netlist.v"
set SDC     "/mnt/openlane_disk/tiny_gpu-STA-analysis/sta_work/gpu_tt.sdc"
set TOP     "gpu"
# ==========================
# Read Design
# ==========================
read_liberty $LIB
read_verilog $NETLIST
link_design $TOP
read_sdc $SDC
# ==========================
# Timing Reports
# ==========================
puts "\n========== WNS =========="
report_wns
puts "\n========== TNS =========="
report_tns
puts "\n========== SETUP =========="
report_checks \
    -path_delay max \
    -group_count 50 \
    -slack_max 0.0 \
    -format full \
    -digits 3
puts "\n========== HOLD =========="
report_checks \
    -path_delay min \
    -group_count 10 \
    -format full \
    -digits 3
puts "\n========== CLOCK SKEW =========="
report_clock_skew -setup
exit
