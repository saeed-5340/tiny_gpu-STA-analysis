# ============================================================
# verify_sta_parser.py
# 10 automated checks across 2 reports = 20 total checks
# Run: python3 verify_sta_parser.py
# ALL must show PASS
# ============================================================
import subprocess
import os
import sys
sys.path.insert(0, '/mnt/openlane_disk/tiny_gpu-STA-analysis/sta_work/parser')
from sta_report_parser import extract_summary, parse_paths, count_by_module

REPORTS = [
    '/mnt/openlane_disk/tiny_gpu-STA-analysis/sta_work/gpu_tt.txt',
    '/mnt/openlane_disk/tiny_gpu-STA-analysis/sta_work/gpu_ss.txt',
]

passed = 0
failed = 0

def check(name, result, expected):
    global passed, failed
    if result == expected:
        print(f"  PASS  {name}")
        passed += 1
    else:
        print(f"  FAIL  {name}")
        print(f"        expected : {expected}")
        print(f"        got      : {result}")
        failed += 1

def grep_float(keyword, filepath):
    result = subprocess.run(
        ['grep', keyword, filepath],
        capture_output=True, text=True)
    line = result.stdout.strip()
    return float(line.split()[1]) if line else None

def grep_count(pattern, filepath):
    result = subprocess.run(
        ['grep', '-c', pattern, filepath],
        capture_output=True, text=True)
    return int(result.stdout.strip())

def grep_first(pattern, filepath):
    result = subprocess.run(
        ['grep', pattern, filepath],
        capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()
    return lines[0] if lines else ''

# ============================================================
print("\n" + "="*55)
print("  verify_sta_parser.py — 10 checks × 2 reports")
print("="*55)

for report in REPORTS:
    name = os.path.basename(report)
    print(f"\n--- {name} ---")

    s = extract_summary(report)
    p = parse_paths(report)
    m = count_by_module(p)

    # CHECK 1: setup_wns type is float
    check("1. setup_wns is float",
          type(s['setup_wns']), float)

    # CHECK 2: setup_wns is negative
    check("2. setup_wns is negative",
          s['setup_wns'] < 0, True)

    # CHECK 3: setup_wns matches grep ground truth
    check("3. setup_wns matches grep",
          s['setup_wns'], grep_float('wns', report))

    # CHECK 4: setup_tns matches grep ground truth
    check("4. setup_tns matches grep",
          s['setup_tns'], grep_float('tns', report))

    # CHECK 5: setup_violations matches grep -c VIOLATED
    check("5. setup_violations matches grep -c VIOLATED",
          s['setup_violations'], grep_count('VIOLATED', report))

    # CHECK 6: timing_met is False (WNS < 0)
    check("6. timing_met is False",
          s['timing_met'], False)

    # CHECK 7: parse_paths returns list
    check("7. parse_paths returns list",
          type(p), list)

    # CHECK 8: path count matches grep -c Startpoint
    check("8. path count matches grep -c Startpoint",
          len(p), grep_count('Startpoint:', report))

    # CHECK 9: count_by_module returns dict
    check("9. count_by_module returns dict",
          type(m), dict)

    # CHECK 10: sum of module violations == setup_violations
    check("10. module violation sum == setup_violations",
          sum(m.values()), s['setup_violations'])

# ============================================================
print(f"\n{'='*55}")
print(f"  Results: {passed} PASSED  |  {failed} FAILED")
print(f"{'='*55}")
if failed == 0:
    print("  ALL PASS ✓")
else:
    print("  SOME FAILED — fix parser and re-run")
