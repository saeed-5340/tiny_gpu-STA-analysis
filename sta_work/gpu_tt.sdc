# Define the clock: name=clk, period=10ns (100MHz), on port 'clk'
create_clock -name clk -period 10.0 [get_ports clk]
 
# Input delay: all inputs arrive 2ns after the rising clock edge
set_input_delay  2.0 -clock clk [all_inputs]
 
# Output delay: all outputs must be stable 2ns before the next clock edge
set_output_delay 2.0 -clock clk [all_outputs]
