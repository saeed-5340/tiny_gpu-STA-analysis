# OpenLane Static Timing Analysis (STA) — Setup & Usage Guide

> **What this repo does:** Runs Static Timing Analysis (STA) on RTL designs (e.g., tiny-GPU, ibex RISC-V CPU) using the open-source EDA toolchain — sv2v → Yosys → OpenSTA — and generates timing reports that a Python parser reads.

---

## Table of Contents

1. [The Full Pipeline](#the-full-pipeline)
2. [Prerequisites](#prerequisites)
3. [Step 1 — Install Ubuntu](#step-1--install-ubuntu)
4. [Step 2 — Install Required Packages](#step-2--install-required-packages)
5. [Step 3 — Install Docker](#step-3--install-docker)
6. [Step 4 — Install OpenLane](#step-4--install-openlane)
7. [Step 5 — Install sv2v](#step-5--install-sv2v)
8. [Step 6 — Verify All Tools](#step-6--verify-all-tools)
9. [Running the STA Flow (tiny-GPU example)](#running-the-sta-flow-tiny-gpu-example)
10. [Common Errors & Fixes](#common-errors--fixes)
11. [Key Concepts Glossary](#key-concepts-glossary)
12. [Output Files Reference](#output-files-reference)

---

## The Full Pipeline

```
RTL source (.sv)
      │
      ▼  sv2v
Flat Verilog (.v)         ← SystemVerilog converted to plain Verilog
      │
      ▼  Yosys
Gate-level Netlist (.v)   ← RTL synthesized into real sky130 gates
      │
      ▼  OpenSTA
Timing Report (.txt)      ← THIS is what sta_report_parser.py reads
```

---

## Prerequisites

- A machine running **Ubuntu** (22.04 or later recommended)
- Internet access
- At least **20 GB** of free disk space (OpenLane Docker images are large)
- Basic familiarity with the Linux terminal

---

## Step 1 — Install Ubuntu

If you don't have Ubuntu installed yet, follow this tutorial:
👉 https://www.youtube.com/watch?v=zZf4YH4WiZo

Once Ubuntu is running, open a terminal and continue below.

---

## Step 2 — Install Required Packages

Run these commands one by one:

```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install build-essential
sudo apt-get install python3
sudo apt-get install python3-venv
sudo apt-get install python3-pip
sudo apt-get install python3-tk
sudo apt-get install curl
sudo apt-get install make
sudo apt-get install git
```

---

## Step 3 — Install Docker

OpenLane runs inside a Docker container. Follow all steps carefully.

### 3a — Install Docker packages

```bash
sudo apt-get install ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 3b — Verify Docker

```bash
sudo docker --version
# Expected: Docker version 29.x.x or similar

sudo docker run hello-world
# Expected: "Hello from Docker! This message shows that your installation appears to be working correctly"
```

### 3c — Configure Docker (run without sudo)

```bash
sudo groupadd docker
whoami                          # Note your Ubuntu username
sudo usermod -aG docker YOUR_USERNAME   # Replace YOUR_USERNAME with the output of whoami
sudo reboot                     # Reboot is required for group changes to take effect
```

After rebooting, verify Docker works without sudo:

```bash
docker run hello-world
```

---

## Step 4 — Install OpenLane

```bash
git clone https://github.com/The-OpenROAD-Project/OpenLane.git
cd OpenLane
make mount
make test    # Verifies OpenLane and the PDK are installed correctly
```

> ⚠️ `make mount` downloads large Docker images. This may take 15–30 minutes depending on your internet speed.

For full OpenLane documentation, visit:
👉 https://armleo-openlane.readthedocs.io/en/latest/index.html

---

## Step 5 — Install sv2v

sv2v converts SystemVerilog (`.sv`) files to plain Verilog (`.v`), which Yosys can read.

> **Skip this step** if your design is already in plain Verilog (`.v` files only).

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl make gcc g++ libgmp-dev zlib1g-dev

# Install Haskell Stack (required to build sv2v)
curl -sSL https://get.haskellstack.org/ | sh

# Verify Haskell Stack installed
stack --version

# Clone and build sv2v
git clone https://github.com/zachjs/sv2v.git
cd sv2v
make
```

> ⚠️ Building sv2v with Haskell Stack takes a while (10–20 minutes). This is normal.

---

## Step 6 — Verify All Tools

Run all checks below before starting any STA flow:

```bash
# OpenSTA  — binary is named 'sta', NOT 'opensta'
which sta
sta -help 2>&1 | head -5

# Yosys  — use -h flag, NOT --version
yosys -h 2>&1 | head -3

# sv2v
/path/to/sv2v/bin/sv2v --version
# Expected: sv2v v0.0.13 or similar

# Python
python3 --version
python3 -m pip --version

# Docker
docker --version
docker run hello-world
```

> 💡 **Important:** OpenSTA's binary is called `sta`, not `opensta`. Running `opensta --version` will return `command not found` — this is expected.

---

## Running the STA Flow (tiny-GPU example)

This section walks through producing `gpu_tt.txt` and `gpu_ss.txt`.

### Setup — Create working directory

```bash
mkdir -p /tiny_gpu-STA-analysis/sta_work
cd /tiny_gpu-STA-analysis/sta_work
```
(If you clone this repo you don't need to create working directory.

### Phase 1 — Clone the design

```bash
git clone https://github.com/saeed-5340/tiny_gpu-STA-analysis.git
# RTL files are in: /tiny_gpu-STA-analysis/src/
# Top module: gpu   |   Clock port: clk
```

### Phase 2 — Convert SystemVerilog → Verilog (sv2v)

```bash
/sv2v/bin/sv2v \
 /tiny_gpu-STA-analysis/src/*.sv \
  > tiny_gpu-STA-analysis/sta_work/gpu_flat.v 2>&1

# Verify output
wc -l /tiny_gpu-STA-analysis/sta_work/gpu_flat.v
head -5 /tiny_gpu-STA-analysis/sta_work/gpu_flat.v
# Expected: ~1265 lines of real Verilog code
```

### Phase 3 — Synthesize with Yosys

Create the synthesis script:

# Create synth_gpu.ys — the Yosys synthesis script
# Step 1: Read the flat Verilog file
# Step 2: Synthesize, setting 'gpu' as the top module
# Step 3: Map flip-flops to sky130 DFF cells
# Step 4: Map combinational logic to sky130 cells (with optimization)
# Step 5: Write gate-level netlist

```bash
read_verilog /tiny_gpu-STA-analysis/sta_work/gpu_flat.v 
synth -top gpu
dfflibmap -liberty ~/.ciel/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib 
abc -liberty ~/.ciel/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib 
write_verilog -noattr /tiny_gpu-STA-analysis/sta_work/gpu_netlist.v
```
Code is given [/tiny_gpu-STA-analysis/sta_work/synth_gpu.ys]

Run synthesis:

```bash
yosys /tiny_gpu-STA-analysis/sta_work/synth_gpu.ys 2>&1 | tee /tiny_gpu-STA-analysis/sta_work/yosys_gpu.log | tail -15
# Expected: "End of script." with CPU/MEM stats — no errors

# Verify netlist
wc -l /tiny_gpu-STA-analysis/sta_work/gpu_netlist.v
# Expected: ~118,000 lines of gate-level Verilog
```

### Phase 4 — Create SDC constraint file

```bash
cat > /tiny_gpu-STA-analysis/sta_work/sta_work/gpu_tt.sdc << 'EOF'
create_clock -name clk -period 10.0 [get_ports clk]
set_input_delay  2.0 -clock clk [all_inputs]
set_output_delay 2.0 -clock clk [all_outputs]
EOF
```
Code is given [/tiny_gpu-STA-analysis/sta_work/gpu_tt.sdc]
This sets a 100 MHz clock (10 ns period) with 2 ns I/O delays.

### Phase 5 — Write OpenSTA script 
OpenSTA script is written in:
[tiny_gpu-STA-analysis/sta_work/run_sta_gpu_tt.tcl]
[tiny_gpu-STA-analysis/sta_work/run_sta_gpu_ss.tcl]


### Phase 6 — Run OpenSTA and generate the timing report

```bash
sta /tiny_gpu-STA-analysis/sta_work/run_sta_gpu_tt.tcl 2>&1 | tee /tiny_gpu-STA-analysis/sta_work/gpu_tt.txt | tail -40
```
```bash
sta /tiny_gpu-STA-analysis/sta_work/run_sta_gpu_ss.tcl 2>&1 | tee /tiny_gpu-STA-analysis/sta_work/gpu_ss.txt | tail -40
```

The final timing report is saved at:
```
/tiny_gpu-STA-analysis/sta_work/gpu_tt.txt
```
```
/tiny_gpu-STA-analysis/sta_work/gpu_ss.txt
```

---

## Common Errors & Fixes

| Error | Cause | Fix |
|---|---|---|
| `command not found: opensta` | Binary is named `sta`, not `opensta` | Use `sta` instead |
| `command not found: opensta` after `sudo apt install opensta` | Package installs as `sta` | Run `which sta` to confirm location |
| `Could not find file "prim_assert.sv"` | Missing include path for sv2v | Add `-I/path/to/vendor/rtl/` to sv2v command |
| `sv2v: could not find package "prim_xxx_pkg"` | ibex has deep vendor dependencies | Use tiny-GPU first; ibex requires resolving OpenTitan library deps |
| `-slack_lesser_than` not recognized | Wrong flag for OpenSTA 2.0 | Use `-slack_less_than` (correct syntax) |
| `report_check_types` not found | Not available in OpenSTA 2.0.17 | Remove that line from the TCL script |
| `Warning: default_operating_condition not found` | Older lib file format | Safe to ignore — does not affect results |
| `Warning: set_input_delay relative to a clock defined on the same port` | SDC constraint quirk | Safe to ignore — does not affect results |

---

## Key Concepts Glossary

| Term | Meaning |
|---|---|
| **WNS** | Worst Negative Slack — the most violated timing path. Negative = failing timing |
| **TNS** | Total Negative Slack — sum of all timing violations |
| **TT corner** | Typical process, 25°C, 1.8V — normal operating conditions |
| **SS corner** | Slow process, 100°C, 1.6V — worst-case conditions |
| **Liberty (.lib)** | Database of gate delays provided by the foundry (sky130 here) |
| **SDC** | Synopsys Design Constraints — defines clock period and I/O timing |
| **Netlist** | Gate-level Verilog — RTL mapped to real physical standard cells |
| **sv2v** | Converts SystemVerilog (`.sv`) → plain Verilog 2005 (`.v`) |
| **PDK** | Process Design Kit — sky130 is the open-source 130nm PDK from Google/SkyWater |

---

## Output Files Reference

```
/mnt/openlane_disk/sta_work/
├── gpu_flat.v          ← sv2v output (tiny-GPU in plain Verilog, ~1265 lines)
├── gpu_netlist.v       ← Yosys synthesis output (gate-level, ~118K lines)
├── gpu_tt.sdc          ← Clock constraints for TT corner
├── synth_gpu.ys        ← Yosys synthesis script
├── run_sta_gpu_tt.tcl  ← OpenSTA TCL script (TT corner)
├── gpu_tt.txt          ← FINAL TIMING REPORT  ← sta_report_parser.py reads this
└── yosys_gpu.log       ← Full synthesis log
```

---

## Next Steps

After `gpu_tt.txt` and `gpu_ss.txt` is confirmed working:

1. **SS corner report** — rerun with `ss_100C_1v60.lib` and change SDC clock period to `12.0`
2. **ibex design** — resolve vendor library dependencies, then run the same sv2v → Yosys → OpenSTA flow
3. **Parser** — implement `sta_report_parser.py` starting with an `extract_summary()` function that reads `gpu_tt.txt`

---

*Maintained as part of the STA setup project. If you run into an issue not listed here, check the OpenSTA documentation or open an issue in this repository.*
