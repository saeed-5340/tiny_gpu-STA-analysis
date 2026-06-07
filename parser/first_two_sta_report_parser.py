# ============================================================
# sta_report_parser.py — End of Day 2 Merged File
# Both functions must be importable:
# from sta_report_parser import extract_summary, parse_paths
# ============================================================
import re
import os

# ============================================================
# extract_summary()
# ============================================================
def extract_summary(filepath):
    """
    Extracts WNS, TNS, and violation counts from a timing report.
    Returns a dictionary matching exact schema.
    """
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
#  parse_paths()
# ============================================================
def parse_paths(filepath):
    """
    Reads every timing path block using a state machine.
    Returns a list of dicts — one dict per path.
    Each dict has: startpoint, endpoint, path_type, slack, violated
    """
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
# End of Day 2 — Merge check (as teacher requires)
# ============================================================
if __name__ == '__main__':

    reports = [
        '/mnt/openlane_disk/tiny_gpu-STA-analysis/sta_work/gpu_tt.txt',
        '/mnt/openlane_disk/tiny_gpu-STA-analysis/sta_work/gpu_ss.txt',
    ]

    for report in reports:
        print(f"\n{'='*55}")
        print(f"Report : {os.path.basename(report)}")
        print(f"{'='*55}")

        s = extract_summary(report)
        paths = parse_paths(report)

        print(f"  setup_wns        : {s['setup_wns']} ns")
        print(f"  setup_tns        : {s['setup_tns']} ns")
        print(f"  hold_wns         : {s['hold_wns']} ns")
        print(f"  setup_violations : {s['setup_violations']}")
        print(f"  hold_violations  : {s['hold_violations']}")
        print(f"  timing_met       : {s['timing_met']}")
        
        if paths:
            p = paths[0]
            print('\n')
            print(f"  startpoint : {p.get('startpoint')}")
            print(f"  endpoint   : {p.get('endpoint')}")
            print(f"  path_type  : {p.get('path_type')}")
            print(f"  slack      : {p.get('slack')}")
            print(f"  violated   : {p.get('violated')}")
