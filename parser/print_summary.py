# ============================================================
# print_summary.py — Student 2 — Day 3
# User-facing output — clean terminal display
# ============================================================
import os
import sys
sys.path.insert(0, '/mnt/openlane_disk/tiny_gpu-STA-analysis/sta_work/parser')
from first_two_sta_report_parser import extract_summary, parse_paths
from count_by_module   import count_by_module

def print_summary(report_path):
    '''
    Print a complete timing summary to the terminal.
    Calls all 3 functions and displays results cleanly.
    '''

    # Step 1: get all data
    summary = extract_summary(report_path)
    paths   = parse_paths(report_path)
    modules = count_by_module(paths)

    # Step 2: get design name from filename
    # ibex_tt.txt  → label = ibex_tt
    # gpu_ss.txt   → label = gpu_ss
    label = os.path.splitext(os.path.basename(report_path))[0]

    # Step 3: print everything cleanly
    print(f'')
    print(f'== STA Report: {label} ==')
    print(f'  Setup WNS          : {summary["setup_wns"]:8.3f} ns')
    print(f'  Setup TNS          : {summary["setup_tns"]:8.3f} ns')
    print(f'  Setup violations   : {summary["setup_violations"]:8d}')
    print(f'  Timing met         : {summary["timing_met"]}')
    print(f'  Total paths parsed : {len(paths):8d}')

    # Step 4: show worst path
    violated = [p for p in paths if p['violated']]
    if violated:
        worst = min(violated, key=lambda p: p['slack'])
        print(f'  Worst endpoint     : {worst["endpoint"]}')
        print(f'  Worst slack        : {worst["slack"]:8.3f} ns')

    # Step 5: show top 5 modules with most violations
    if modules:
        print(f'  Violations by module (top 5):')
        for mod, cnt in list(modules.items())[:5]:
            print(f'    {cnt:4d}  {mod}')
    print()


# ============================================================
# Main block
# Usage: python3 print_summary.py gpu_tt.txt gpu_ss.txt
# ============================================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 print_summary.py <report_file> [...]')
        sys.exit(1)
    for report in sys.argv[1:]:
        print_summary(report)
