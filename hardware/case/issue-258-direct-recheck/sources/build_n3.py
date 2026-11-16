"""Build N3 inputs: rotate J_WING in place so the mating axis points
toward the bay. Rotation defined in CASE frame (+90 CCW right -> exit
-Y becomes -X; -90 CW left -> exit +X), about the footprint origin.
Native->case similarity solved from pads 1/14 case coords (#253 CASE)
and verified on all 14 pads + the Rev.4 exit row."""
import sys, os, json, cmath, math
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/lib/python3/dist-packages')
import pcbnew

BASE = '/home/hatch/workspace/projects/he-piantor-direct/hardware/kicad/qualification/issue-235-wing-round2'
OUT = '/home/hatch/workspace/projects/he-piantor-direct/.issue258-runtime'
CASE_ROW = {  # pin k case coords: (x0 - 1.25*(k-1), -42.85)
    '17mm-right': (35.125, -42.85), '16mm-right': (35.125, -42.85),
    '17mm-left': (-18.875, -42.85), '16mm-left': (-18.875, -42.85)}
THETA = {'right': +90.0, 'left': -90.0}

def case_pad(var, k):
    x0, y = CASE_ROW[var]
    sgn = -1.0  # both rows run -X with pin number (case frame)
    return (x0 + sgn * 1.25 * (k - 1), y)

result = {}
for var in ('17mm-right', '17mm-left', '16mm-right', '16mm-left'):
    side = var.split('-')[1]
    b = pcbnew.LoadBoard(f'{BASE}/wing-rev4-{var}/input.kicad_pcb')
    fp = b.FindFootprintByReference('J_WING')
    pads = {int(p.GetNumber()): (p.GetCenter().x / 1e6, p.GetCenter().y / 1e6)
            for p in fp.Pads() if p.GetNumber().isdigit()}
    anc = (fp.GetPosition().x / 1e6, fp.GetPosition().y / 1e6)
    # solve rotation from pad1->pad14
    va = complex(pads[14][0] - pads[1][0], pads[14][1] - pads[1][1])
    c1, c14 = case_pad(var, 1), case_pad(var, 14)
    vc = complex(c14[0] - c1[0], c14[1] - c1[1])
    rot = vc / va
    assert abs(abs(rot) - 1) < 1e-6, abs(rot)
    t = complex(c1[0], c1[1]) - rot * complex(*pads[1])
    def to_case(p):
        z = rot * complex(*p) + t
        return (z.real, z.imag)
    err = max(abs(complex(*to_case(pads[k])) - complex(*case_pad(var, k)))
              for k in range(1, 15))
    o_case = to_case(anc)
    th = math.radians(THETA[side])
    R = complex(math.cos(th), math.sin(th))
    def rot_case(p):
        z = complex(*o_case) + R * (complex(*p) - complex(*o_case))
        return (z.real, z.imag)
    exits_old = [(case_pad(var, k)[0], -34.95) for k in range(1, 15)]
    exits_new = [rot_case(p) for p in exits_old]
    pads_new = [rot_case(case_pad(var, k)) for k in range(1, 15)]
    fp.SetOrientationDegrees(fp.GetOrientationDegrees() + THETA[side])
    od = os.path.join(OUT, f'n3-{var}')
    os.makedirs(od, exist_ok=True)
    b.Save(os.path.join(od, 'input.kicad_pcb'))
    result[var] = {'verify_err_mm': round(err, 4), 'o_case': [round(v, 3) for v in o_case],
                   'exits_new': [[round(x, 3), round(y, 3)] for x, y in exits_new],
                   'pads_new_case': [[round(x, 3), round(y, 3)] for x, y in pads_new],
                   'orient_new': fp.GetOrientationDegrees()}
    print(var, 'err', round(err, 4), 'O_case', [round(v, 2) for v in o_case],
          'exit0', [round(v, 2) for v in exits_new[0]], 'exit13', [round(v, 2) for v in exits_new[13]])
json.dump(result, open(os.path.join(OUT, 'n3_exits.json'), 'w'), indent=1)
print('saved n3_exits.json')
