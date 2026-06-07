# ============================================================
# sta_report_parser.py
# from sta_report_parser import extract_summary, parse_paths
# ============================================================
import re
import os
import sys
from collections import Counter

# ============================================================
# Student 1 — extract_summary()
# ============================================================
def extract_summary(filepath):
    setup_wns        = 0.0
    setup_tns        = 0.0
    hold_wns         = 0.0
    setup_violations = 0
    hold_violations  = 0
    inside_hold      = False

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if '===== HOLD =====' in line:
                inside_hold = True
            elif '===== SETUP =====' in line:
                inside_hold = False
            elif line.startswith('wns'):
                setup_wns = float(line.split()[1])
            elif line.startswith('tns'):
                setup_tns = float(line.split()[1])
            elif 'slack (VIOLATED)' in line:
                if inside_hold:
                    hold_violations += 1
                else:
                    setup_violations += 1

    timing_met = (setup_wns >= 0.0 and hold_wns >= 0.0)

    return {
        'setup_wns':        setup_wns,
        'setup_tns':        setup_tns,
        'hold_wns':         hold_wns,
        'setup_violations': setup_violations,
        'hold_violations':  hold_violations,
        'timing_met':       timing_met
    }


# ============================================================
# parse_paths()
# ============================================================
def parse_paths(filepath):
    paths   = []
    current = {}

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()

            if line.startswith('Startpoint:'):
                if current and 'startpoint' in current:
                    paths.append(current)
                current = {}
                raw = line.split(':', 1)[1].strip()
                current['startpoint'] = re.sub(r'\s*\(.*?\)\s*$', '', raw).strip()

            elif line.startswith('Endpoint:'):
                raw = line.split(':', 1)[1].strip()
                current['endpoint'] = re.sub(r'\s*\(.*?\)\s*$', '', raw).strip()

            elif line.startswith('Path Type:'):
                raw = line.split(':', 1)[1].strip()
                if 'max' in raw:
                    current['path_type'] = 'setup'
                elif 'min' in raw:
                    current['path_type'] = 'hold'
                else:
                    current['path_type'] = raw

            elif 'slack (' in line:
                parts = line.split()
                try:
                    current['slack']    = float(parts[0])
                    current['violated'] = current['slack'] < 0.0
                except:
                    current['slack']    = 0.0
                    current['violated'] = False

    if current and 'startpoint' in current:
        paths.append(current)

    return paths


# ============================================================
# Student 1 — count_by_module()
# ============================================================
def count_by_module(paths):
    '''
    Group violations by top sub-module of endpoint path.
    Endpoint: u_core/u_alu/result_reg/Q  -> module u_alu
    Endpoint: core_0/alu/add_out_reg/D   -> module core_0
    Returns {module: count} sorted by count descending.
    Only counts violated paths.
    '''
    violated = [p for p in paths if p.get('violated', False)]

    modules = []
    for p in violated:
        ep    = p.get('endpoint', '')
        parts = ep.split('/')
        module = parts[1] if len(parts) >= 2 else parts[0] if parts else 'unknown'
        modules.append(module)

    return dict(Counter(modules).most_common())


# ============================================================
# Student 2 — print_summary()
# ============================================================
def print_summary(report_path):
    '''Print a complete timing summary to the terminal.'''
    summary = extract_summary(report_path)
    paths   = parse_paths(report_path)
    modules = count_by_module(paths)

    label = os.path.splitext(os.path.basename(report_path))[0]

    print(f'')
    print(f'== STA Report: {label} ==')
    print(f"  setup_wns        : {summary['setup_wns']} ns")
    print(f"  setup_tns        : {summary['setup_tns']} ns")
    print(f"  hold_wns         : {summary['hold_wns']} ns")
    print(f"  setup_violations : {summary['setup_violations']}")
    print(f"  hold_violations  : {summary['hold_violations']}")
    print(f"  timing_met       : {summary['timing_met']}")

    if paths:
        violated = [p for p in paths if p['violated']]
        if violated:
            worst = min(violated, key=lambda k: k['slack'])
            print(f' Worst endpoint          : {worst["endpoint"]}')
            print(f' Worst slack             : {worst["slack"]}')

    if modules:
        print(f'  Violations by module (top 5):')
        for mod, cnt in list(modules.items())[:5]:
            print(f'    {cnt:4d}  {mod}')
    print()


# ============================================================
# Main block
# python3 sta_report_parser.py gpu_tt.txt gpu_ss.txt
# ============================================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 sta_report_parser.py <report_file> [report_file2 ...]')
        sys.exit(1)
    for report in sys.argv[1:]:
        print_summary(report)
