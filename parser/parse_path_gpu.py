import re
import os

def parse_path(filepath):
    
    paths = []
    current = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('Startpoint:'):
                if current and 'startpoint' in current:
                    paths.append(current)
                current = {}
                raw = line.split(':',1)[1].strip()
                current['startpoint'] = re.sub(r'\s*\(.*?\)\s*$','', raw).strip()
            
            elif line.startswith('Endpoint:'):
                raw = line.split(':',1)[1].strip()
                current['endpoint'] = re.sub(r'\s*\(.*?\)\s*$','', raw).strip()
            
            elif line.startswith('Path Type:'):
                raw = line.split(':',1)[1].strip()
                if 'max' in raw:
                    current['path_type'] = 'setup'
                elif 'min' in raw:
                    current['path_type'] = 'hold'
                else:
                    current['path_type'] = raw
            elif 'slack (' in line:
                parts = line.split()
                
                try:
                    current['slack'] = float(parts[0])
                    current['violated'] = current['slack'] < 0.0
                except:
                    current['slack'] = 0.0
                    current['violated'] = False
            
        if current and 'startpoint' in current:
            paths.append(current)
            current = {}
        return paths
            
if __name__ == '__main__':
    
    report = ['/mnt/openlane_disk/tiny_gpu-STA-analysis/sta_work/gpu_tt.txt',
              '/mnt/openlane_disk/tiny_gpu-STA-analysis/sta_work/gpu_ss.txt']
    
    for i in report:
        paths = parse_path(i)
        print(f"\n{'-'*30}")
        print(f'Report : {os.path.basename(i)}')
        print(f"{'-'*30}")
        # print(f"  Total paths    : {len(paths)}")
        # print(f"  Violated paths : {sum(1 for p in paths if p.get('violated'))}")
        # print(f"  Setup paths    : {sum(1 for p in paths if p.get('path_type')=='setup')}")
        # print(f"  Hold paths     : {sum(1 for p in paths if p.get('path_type')=='hold')}")
        # print(f"\n  First path:")
        if paths:
            p = paths[0]
            print(f"    startpoint : {p.get('startpoint')}")
            print(f"    endpoint   : {p.get('endpoint')}")
            print(f"    path_type  : {p.get('path_type')}")
            print(f"    slack      : {p.get('slack')}")
            print(f"    violated   : {p.get('violated')}")
