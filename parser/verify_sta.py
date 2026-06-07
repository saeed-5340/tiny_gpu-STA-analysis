import subprocess
import sys
import re
from sta_report_parser import extract_summary, parse_paths, count_by_module

def chk(label, ok, detail=''):
    status = 'PASS' if ok else 'FAIL'
    print(f'  [{status}]  {label}')
    if not ok and detail:
        print(f'         -> {detail}')
    return ok

def grep_count(pattern, filepath):
    r = subprocess.run(['grep', '-c', pattern, filepath],
                       capture_output=True, text=True)
    return int(r.stdout.strip()) if r.returncode == 0 else 0

def grep_value(pattern, filepath):
    r = subprocess.run(['grep', pattern, filepath],
                       capture_output=True, text=True)
    m = re.search(r'(-?\d+\.\d+)', r.stdout)
    return float(m.group(1)) if m else None

def verify_report(report_path):
    label = report_path
    print(f'\n-- Verifying: {label} ---------')
    all_pass = True
    summary = extract_summary(report_path)
    paths = parse_paths(report_path)
    modules = count_by_module(paths)
    grep_wns = grep_value('wns', report_path)
    grep_paths = grep_count('Startpoint:', report_path)
    grep_violated = grep_count('VIOLATED', report_path)
    all_pass &= chk('setup_wns is a float',
                    isinstance(summary['setup_wns'], float),
                    f'type was {type(summary["setup_wns"])}')
    if grep_wns is not None:
        all_pass &= chk('setup_wns matches grep output',
                        abs(summary['setup_wns'] - grep_wns) < 0.001,
                        f'parser={summary["setup_wns"]:.3f}  grep={grep_wns:.3f}')
    all_pass &= chk('path count matches grep Startpoint: count',
                    len(paths) == grep_paths,
                    f'parser={len(paths)}  grep={grep_paths}')
    all_pass &= chk('violated count matches grep VIOLATED count',
                    summary['setup_violations'] == grep_violated,
                    f'parser={summary["setup_violations"]}  grep={grep_violated}')
    required = ['startpoint', 'endpoint', 'path_type', 'slack', 'violated']
    missing = [k for p in paths for k in required if k not in p]
    all_pass &= chk('all paths have all 5 required fields',
                    len(missing) == 0,
                    f'missing fields: {set(missing)}')
    all_pass &= chk('all slack values are floats',
                    all(isinstance(p['slack'], float) for p in paths),
                    'some slack values are not float')
    all_pass &= chk('timing_met is a bool (not a string)',
                    isinstance(summary['timing_met'], bool),
                    f'type was {type(summary["timing_met"])}')
    if summary['setup_wns'] < 0:
        all_pass &= chk('timing_met is False when setup_wns < 0',
                        summary['timing_met'] == False,
                        'timing_met should be False but is True')
    all_pass &= chk('count_by_module returns a dict',
                    isinstance(modules, dict))
    if summary['setup_violations'] > 0:
        all_pass &= chk('setup_tns <= 0 when violations exist',
                        summary['setup_tns'] <= 0,
                        f'tns={summary["setup_tns"]} but violations={summary["setup_violations"]}')
    print(f'  Result: {"ALL PASS" if all_pass else "SOME CHECKS FAILED"}')
    return all_pass

if __name__ == '__main__':
    reports = sys.argv[1:] if len(sys.argv) > 1 else []
    if not reports:
        print('Usage: python3 verify_sta_parser.py <report1> [report2] ...')
        sys.exit(1)
    results = [verify_report(r) for r in reports]
    print()
    print(f'== Final result: {sum(results)}/{len(results)} reports ALL PASS ==')
    sys.exit(0 if all(results) else 1)