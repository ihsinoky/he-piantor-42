"""Build N2 inputs for 17R/16L/16R: solve native->case rotation from
J_WING pads 1/14 vs placement.json case coords; rotate J_WING +180,
translate by case-north 3.5 mm in native coords."""
import pcbnew, math, os, json

BASE = '/home/hatch/workspace/projects/he-piantor-north/hardware/kicad/qualification/issue-235-wing-round2'
OUT = '/home/hatch/workspace/projects/he-piantor-north/.issue253-runtime'
CASE = {  # pin1, pin14 case coords from connector/placement.json
 '17mm-left': ((-18.875, -42.85), (-35.125, -42.85)),
 '17mm-right': ((35.125, -42.85), (18.875, -42.85)),
 '16mm-left': ((-18.875, -42.85), (-35.125, -42.85)),
 '16mm-right': ((35.125, -42.85), (18.875, -42.85)),
}

def v(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))

for var in ('17mm-right', '16mm-left', '16mm-right'):
    src = f'{BASE}/wing-rev4-{var}/input.kicad_pcb'
    b = pcbnew.LoadBoard(src)
    fp = b.FindFootprintByReference('J_WING')
    pads = {p.GetNumber(): p.GetCenter() for p in fp.Pads() if p.GetNumber() in ('1', '14')}
    a1 = (pads['1'].x/1e6, pads['1'].y/1e6); a14 = (pads['14'].x/1e6, pads['14'].y/1e6)
    c1, c14 = CASE[var]
    va = complex(a14[0]-a1[0], a14[1]-a1[1]); vc = complex(c14[0]-c1[0], c14[1]-c1[1])
    rot = vc/va  # native->case rotation (unit)
    dn = (0 - 3.5j) / rot  # case (0,-3.5) in native coords
    fp.SetOrientationDegrees(fp.GetOrientationDegrees() + 180.0)
    pos = fp.GetPosition()
    fp.SetPosition(v(pos.x/1e6 + dn.real, pos.y/1e6 + dn.imag))
    outdir = os.path.join(OUT, f'n2-{var}')
    os.makedirs(outdir, exist_ok=True)
    b.Save(os.path.join(outdir, 'input.kicad_pcb'))
    print(var, 'native delta', round(dn.real, 3), round(dn.imag, 3), 'orient', fp.GetOrientationDegrees())
