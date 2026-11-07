"""Generate Issue198 Stage2 from Rev3 Stage1b CSV bundle; dimensions in mm."""
from pathlib import Path
import argparse, csv, json
import base
HERE=Path(__file__).resolve().parent

def prepare(source, dest):
    dest.mkdir(parents=True,exist_ok=True)
    data=json.loads(source.read_text())
    def write(name,fields,rows):
        with (dest/name).open('w') as f:
            w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
    for v in data['variants']:
        tag=v['variant'];pitch=v['pitch_mm'];side=v['side']
        write(f'outline-{tag}.csv',['x_mm','y_mm'],[dict(zip(['x_mm','y_mm'],q)) for q in v['outline_local']])
        write(f'holes-{tag}.csv',['kind','reference','x_mm','y_mm','diameter_mm'],[dict(kind='mounting',reference=h['ref'],x_mm=h['local'][0],y_mm=h['local'][1],diameter_mm=2.2) for h in v['mounting_holes'] if not h['removed']])
        (dest/f'keys-{tag}.csv').write_bytes((base.ROOT/f'hardware/case/issue-194-rev2/keys-{tag}.csv').read_bytes())
    return dest

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pitch',type=int,choices=[16,17],default=17)
    p.add_argument('--geometry',type=Path,default=HERE/'inputs/wing-rev3-stage1b.json')
    p.add_argument('--csv-dir',type=Path,default=HERE/'inputs/rev3-stage1b')
    p.add_argument('--out',type=Path)
    p.add_argument('--palm-offset',type=float,choices=[0.,-.5],default=0.,help='flush default or rim 0.5 below PCB; never raised')
    p.add_argument('--prepare-inputs',action='store_true')
    args=p.parse_args()
    args.geometry=args.geometry.resolve()
    args.csv_dir=args.csv_dir.resolve()
    if args.prepare_inputs:prepare(args.geometry,args.csv_dir)
    if args.out is None:args.out=HERE/f'{args.pitch}mm'
    base.generate(args)
