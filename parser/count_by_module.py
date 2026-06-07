# ============================================================
# count_by_module.py — Student 1 — Day 3
# Takes paths list from parse_paths()
# Counts how many violations each module has
# ============================================================
from collections import Counter

def count_by_module(paths):
    '''
    Group violations by top sub-module of endpoint path.
    Endpoint: u_core/u_alu/result_reg/Q  -> module u_alu
    Endpoint: core_0/alu/add_out_reg/D   -> module core_0
    Returns {module: count} sorted by count descending.
    Only counts violated paths.
    '''

    # Step 1: filter only violated paths
    violated = [p for p in paths if p.get('violated', False)]

    # Step 2: extract module name from each endpoint
    modules = []
    for p in violated:
        ep    = p.get('endpoint', '')
        parts = ep.split('/')

        # endpoint has hierarchy: u_core/u_alu/result_reg
        #   parts[0] = u_core   (top module)
        #   parts[1] = u_alu    (sub-module) ← we want this
        #   parts[2] = result_reg

        # endpoint has no hierarchy: top_reg
        #   parts[0] = top_reg  ← only one part, use it

        module = parts[1] if len(parts) >= 2 else parts[0] if parts else 'unknown'
        modules.append(module)

    # Step 3: count and sort
    return dict(Counter(modules).most_common())


# ============================================================
# Test — run this file directly
# ============================================================
if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/mnt/openlane_disk/tiny_gpu-STA-analysis/sta_work/parser')
    from first_two_sta_report_parser import parse_paths

    reports = [
        '/mnt/openlane_disk/tiny_gpu-STA-analysis/sta_work/gpu_tt.txt',
        '/mnt/openlane_disk/tiny_gpu-STA-analysis/sta_work/gpu_ss.txt',
    ]

    for report in reports:
        paths = parse_paths(report)
        result = count_by_module(paths)
        print(f"\nReport: {report.split('/')[-1]}")
        print(f"Violations by module:")
        for mod, cnt in result.items():
            print(f"  {cnt:4d}  {mod}")
