# ============================================================
# parse_paths.py — Student 2
# Reads every timing path block using a state machine
# ============================================================
import re

def parse_paths(report_path):
    '''
    Reads report line by line using a state machine.
    Returns a list of dicts — one dict per path.
    Each dict has exactly: startpoint, endpoint, path_type, slack, violated
    '''
    paths   = []
    current = {}

    with open(report_path) as f:
        for line in f:
            s = line.strip()

            # --- Detect new path start ---
            # A new path always begins with 'Startpoint:'
            # Save the previous path (if any) before starting a new one
            if s.startswith('Startpoint:'):
                if current and 'startpoint' in current:
                    paths.append(current)
                current = {}

                # Extract startpoint name — everything after 'Startpoint: '
                # Remove parenthetical comment like (rising edge-triggered flip-flop)
                raw = s.split(':', 1)[1].strip()
                current['startpoint'] = re.sub(r'\s*\(.*?\)\s*$', '', raw).strip()

            # --- Extract endpoint ---
            elif s.startswith('Endpoint:'):
                raw = s.split(':', 1)[1].strip()
                current['endpoint'] = re.sub(r'\s*\(.*?\)\s*$', '', raw).strip()

            # --- Detect path type: setup or hold ---
            elif s.startswith('Path Type:'):
                raw = s.split(':', 1)[1].strip()
                if 'max' in raw:
                    current['path_type'] = 'setup'
                elif 'min' in raw:
                    current['path_type'] = 'hold'
                else:
                    current['path_type'] = raw

            # --- Extract slack value ---
            # slack line looks like:  -9.016   slack (VIOLATED)
            # or:                      0.312   slack (MET)
            elif 'slack (' in s:
                parts = s.split()
                try:
                    current['slack']    = float(parts[0])
                    current['violated'] = current['slack'] < 0
                except (ValueError, IndexError):
                    current['slack']    = 0.0
                    current['violated'] = False

    # Save the last path (loop ends before final append)
    if current and 'startpoint' in current:
        paths.append(current)

    return paths


# ============================================================
# Quick test
# ============================================================
if __name__ == '__main__':
    import os
    reports = [
        '/mnt/openlane_disk/tiny_gpu-STA-analysis/sta_work/gpu_tt.txt',
        '/mnt/openlane_disk/tiny_gpu-STA-analysis/sta_work/gpu_ss.txt',
    ]
    for report in reports:
        paths = parse_paths(report)
        print(f"\n{'='*55}")
        print(f"Report : {os.path.basename(report)}")
        print(f"{'='*55}")
        print(f"  Total paths    : {len(paths)}")
        print(f"  Violated paths : {sum(1 for p in paths if p.get('violated'))}")
        print(f"  Setup paths    : {sum(1 for p in paths if p.get('path_type')=='setup')}")
        print(f"  Hold paths     : {sum(1 for p in paths if p.get('path_type')=='hold')}")
        print(f"\n  First path:")
        if paths:
            p = paths[0]
            print(f"    startpoint : {p.get('startpoint')}")
            print(f"    endpoint   : {p.get('endpoint')}")
            print(f"    path_type  : {p.get('path_type')}")
            print(f"    slack      : {p.get('slack')}")
            print(f"    violated   : {p.get('violated')}")
