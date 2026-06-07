# STA Findings — Week 3
**Design: tiny-GPU | Tool: OpenSTA 2.0.17 | PDK: sky130A**

---

## 1. Summary Table

| Metric              | GPU TT (25°C, 1.8V) | GPU SS (100°C, 1.6V) |
|---------------------|--------------------|--------------------|
| Setup WNS (ns)      | -9.02              | -24.39             |
| Setup TNS (ns)      | -7939.87           | -23644.86          |
| Setup Violations    | 50                 | 50                 |
| Hold Violations     | 0                  | 0                  |
| Total Paths         | 60                 | 60                 |
| Timing Met?         | NO                 | NO                 |

---

## 2. Key Observations

### TT vs SS Corner
- SS WNS is **2.7× worse** than TT (-24.39 vs -9.02 ns)
- SS TNS is **3× worse** than TT (-23644 vs -7939 ns)
- Reason: At 100°C and 1.6V, transistors switch slower
  → longer gate delays → harder to meet timing

### Critical Path Analysis
- All 50 violated paths share the same Startpoint (_45801_)
- Data arrival time = ~18.93 ns vs clock period = 10 ns
- The single worst path is 9.016 ns late at TT corner
- 42 out of 50 violations come from flat_group_44000
- 8 out of 50 violations come from flat_group_46000

### Hold Paths
- 0 hold violations at both TT and SS corners
- Hold timing is comfortably met at all conditions

---

## 3. Minimum Safe Clock Period
| Corner | Min Period | Max Frequency |
|--------|-----------|---------------|
| TT     | ~19 ns    | ~52 MHz       |
| SS     | ~25 ns    | ~40 MHz       |

The design cannot run at 100 MHz (10 ns period) at either corner.

---

## 4. Parser Verification Results
- verify_sta_parser.py: **20/20 checks PASS**
- extract_summary() correctly extracts WNS, TNS, violations
- parse_paths() correctly parses all 60 path blocks
- count_by_module() correctly groups violations by module
- print_summary() cleanly displays all metrics

---

## 5. Files Produced
| File | Description |
|------|-------------|
| gpu_tt.txt | OpenSTA report — TT corner (25°C, 1.8V) |
| gpu_ss.txt | OpenSTA report — SS corner (100°C, 1.6V) |
| sta_report_parser.py | Parser — 4 functions |
| verify_sta_parser.py | Verifier — 20/20 PASS |
