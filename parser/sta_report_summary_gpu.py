def sta_report_summary_gpu(filepath):
    """
    Extracts WNS, TNS, and violation counts from a timing report.
    Returns a dictionary matching exact schema.
    """
    setup_wns        = 0.0
    setup_tns        = 0.0
    hold_wns         = 0.0
    setup_violations = 0
    hold_violations  = 0
    inside_hold = True
    
    with open(filepath,'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('wns'):
                value = float(line.split()[1])
                setup_wns = value
            elif line.startswith('tns'):
                value = float(line.split()[1])
                setup_tns = value
            elif "max" in line:
                inside_hold = True
            elif "min" in line:
                inside_hold = False
            elif "slack (VIOLATED)" in line:
                if inside_hold == True:
                    setup_violations += 1
                elif inside_hold == False:
                    hold_violations += 1
        
        timing_met = (setup_wns >= 0.0 and hold_wns >= 0.0)
        
        return {
            "setup_wns": setup_wns,
            "setup_tns": setup_tns,
            "hold_wns": hold_wns,
            "setup_violations": setup_violations,
            "hold_violations": hold_violations,
            "timing_met": timing_met
        }
             
            


if __name__ == "__main__":
    
    import os
    
    report = [
        '/mnt/openlane_disk/tiny_gpu-STA-analysis/sta_work/gpu_tt.txt',
        '/mnt/openlane_disk/tiny_gpu-STA-analysis/sta_work/gpu_ss.txt',
    ]
    for i in report:
        print(f"\n{'-'*50}")
        print(f'Report : {os.path.basename(i)}')
        print(f'{"-"*50}')
        
        s = sta_report_summary_gpu(i)
        print(f"  setup_wns        : {s['setup_wns']} ns")
        print(f"  setup_tns        : {s['setup_tns']} ns")
        print(f"  hold_wns         : {s['hold_wns']} ns")
        print(f"  setup_violations : {s['setup_violations']}")
        print(f"  hold_violations  : {s['hold_violations']}")
        print(f"  timing_met       : {s['timing_met']}")

