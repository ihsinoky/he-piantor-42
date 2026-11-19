"""S2.6 manufacturing package (per repo #267 / Rev.3 conventions).

- gerbers + drill via kicad-cli into manufacturing/gerber/
- BOM-jlcpcb.csv (Comment, Designator, Footprint, LCSC Part #) - every
  row carries a verified LCSC code; hand-fit parts (XIAO socket, battery
  header) and bare TPs / NPTH are excluded and listed in FABRICATION.md.
- CPL-jlcpcb-gerber-frame.csv: Mid X = KiCadX, Mid Y = -KiCadY (gerber
  frame, Y up), Rotation = KiCad orientation, Layer top.
- FABRICATION.md + quote-handoff.md, DRAFT / NOT FOR ORDER.
"""
import csv
import subprocess
import sys
from pathlib import Path

import pcbnew

WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'
MFG = TREE / 'manufacturing'
BOARD = TREE / 'wmatrix.kicad_pcb'
MM = 1e6
KCLI = '/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/bin/kicad-cli'

# designator prefix -> (Comment, BOM footprint label, LCSC)
BOM_MAP = [
    ('U_H', 'TMAG5253BA3IQDMRR', 'X2SON-4', 'C22401868'),
    ('U_MUX', 'TMUX1208PWR', 'TSSOP-16', 'C494728'),
    ('U_LDO', 'AP2112K-3.3TRG1', 'SOT-23-5', 'C51118'),
    ('Q_PROT', 'AO3401A', 'SOT-23', 'C15127'),
    ('J_USB', 'TYPE-C-31-M-12', 'USB-C', 'C165948'),
    ('C_LDO', 'CL21A106KAYNNNE 10uF', '0805', 'C15850'),
    ('C_', 'GRM188R71C104KA01D 100nF', '0603', 'C45000'),
    ('R_CC', '5.1k 0603 UNI-ROYAL', '0603', 'C23186'),
    ('R_DIV', '10k 0603 UNI-ROYAL', '0603', 'C25804'),
    ('R_LED', '1k 0603 UNI-ROYAL', '0603', 'C21190'),
    ('R_SHUNT', '0R 0603 UNI-ROYAL', '0603', 'C21189'),
    ('D_LED', 'KT-0805G green LED', '0805', 'C2297'),
]
EXCLUDE_PREFIXES = ('TP', 'NT', 'MH')  # test points / mounting holes


def bom_row(ref):
    for prefix, comment, fplabel, lcsc in BOM_MAP:
        if ref.startswith(prefix):
            return comment, fplabel, lcsc
    return None


def main():
    MFG.mkdir(exist_ok=True)
    (MFG / 'gerber').mkdir(exist_ok=True)
    env = {'PATH': '/usr/bin:/bin', 'HOME': '/home/hatch',
           'LD_LIBRARY_PATH': '/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/lib/x86_64-linux-gnu:/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/lib/kicad'}
    r = subprocess.run([KCLI, 'pcb', 'export', 'gerbers', '--output', str(MFG / 'gerber'),
                        str(BOARD)], capture_output=True, text=True, env=env)
    print('gerbers rc', r.returncode)
    r = subprocess.run([KCLI, 'pcb', 'export', 'drill', '--output', str(MFG / 'gerber') + '/',
                        str(BOARD)], capture_output=True, text=True, env=env)
    print('drill rc', r.returncode)

    b = pcbnew.LoadBoard(str(BOARD))
    fps = sorted(list(b.GetFootprints()), key=lambda f: f.GetReference())
    groups = {}
    cpl_rows = []
    excluded = []
    for f in fps:
        ref = f.GetReference()
        if ref.startswith(EXCLUDE_PREFIXES) or ref in ('U_XIAO', 'J_BATT'):
            excluded.append(ref)
            continue
        row = bom_row(ref)
        if row is None:
            print('UNMAPPED BOM REF:', ref)
            sys.exit(1)
        groups.setdefault(row, []).append(ref)
        p = f.GetPosition()
        cpl_rows.append([ref, f'{p.x / MM:.6f}mm', f'{-p.y / MM:.6f}mm', 'top',
                         f'{f.GetOrientationDegrees():.1f}'])
    with open(MFG / 'BOM-jlcpcb.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part #'])
        for (comment, fplabel, lcsc), refs in sorted(groups.items(), key=lambda kv: kv[0][0]):
            w.writerow([comment, ','.join(refs), fplabel, lcsc])
    with open(MFG / 'CPL-jlcpcb-gerber-frame.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
        w.writerows(sorted(cpl_rows))
    print('BOM groups:', {k[0]: len(v) for k, v in groups.items()})
    print('CPL rows:', len(cpl_rows), 'excluded:', excluded)


if __name__ == '__main__':
    main()
