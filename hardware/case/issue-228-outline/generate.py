"""Generate Issue198 final case from the Wing Rev.3 final CSVs (Issue #200 / D-034); dimensions in mm."""
from pathlib import Path
import argparse
import base
HERE=Path(__file__).resolve().parent

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pitch',type=int,choices=[16,17],default=17)
    p.add_argument('--geometry',type=Path,default=HERE.parent/'issue-198-final/inputs/wing-rev3-geometry.json')
    p.add_argument('--csv-dir',type=Path,default=HERE.parent/'issue-198-final/inputs/rev3-final')
    p.add_argument('--out',type=Path)
    p.add_argument('--palm-offset',type=float,choices=[0.,-.5],default=0.,help='flush default or rim 0.5 below PCB; never raised')
    args=p.parse_args()
    args.geometry=args.geometry.resolve()
    args.csv_dir=args.csv_dir.resolve()
    if args.out is None:args.out=HERE/f'{args.pitch}mm'
    base.generate(args)
