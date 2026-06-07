# ==========================
# run_sta_gpu_ss.tcl
# Corner: SS (100C, 1.6V)
# Usage: sta run_sta_gpu_ss.tcl > gpu_ss.txt
# ==========================
set LIB     "/home/saeed/.ciel/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__ss_100C_1v60.lib"
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
