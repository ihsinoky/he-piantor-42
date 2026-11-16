"""Stage 2: north-channel harness for N2 at Z13.55.
Bodies: #248 fitted set per pitch, with J_WING bodies rotated 180 deg
about the case anchor (+-27,-42.60) and translated (0,-3.5,0), and a
wiring channel cut into the tray north rim land.
Wires: exit north into the channel, run to the bay waist, south along
the bay margin, climb east/west onto the round-9 [P,G,ep] tail."""
import sys, json
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlib18 as F
import routes_round17 as rr
from OCP.gp import gp_Trsf, gp_Pnt, gp_Dir, gp_Ax1, gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from build123d import Solid
def cast(s):
    return Solid.cast(W(s))

def W(s):
    return s.wrapped if hasattr(s, 'wrapped') else s

def xform(shape, anchor_x):
    t1 = gp_Trsf(); t1.SetRotation(gp_Ax1(gp_Pnt(anchor_x, -42.60, 0), gp_Dir(0, 0, 1)), 3.141592653589793)
    s1 = BRepBuilderAPI_Transform(W(shape), t1, True).Shape()
    t2 = gp_Trsf(); t2.SetTranslation(gp_Vec(0, -2.0, 0))
    return cast(BRepBuilderAPI_Transform(s1, t2, True).Shape())

def cut_channel(tray, side):
    sgn = 1 if side == 'right' else -1
    x0, x1 = (3.5, 36.5) if sgn > 0 else (-36.5, -3.5)
    box = BRepPrimAPI_MakeBox(gp_Pnt(x0, -52.6, 2.2), gp_Pnt(x1, -49.3, 10.0)).Shape()
    c = BRepAlgoAPI_Cut(W(tray), box); c.Build()
    return cast(c.Shape())

# round-9 tails (right side), points [.., P, G, ep]
tails = {}
for i in range(14):
    p = rr.points(i, 'taut')
    tails[i] = [list(p[-4]), list(p[-3]), list(p[-2]), list(p[-1])]  # bow, P, G, ep

CELLS = [(y, z) for z in (3.6, 4.7, 5.8, 6.9, 8.0, 9.1) for y in (-50.2, -51.3, -52.4)]

def wire_points(i, side):
    sgn = 1 if side == 'right' else -1
    pinX = sgn * (18.875 + 1.25 * i)
    laneY, laneZ = CELLS[13 - i]
    bow, P, G, ep = tails[i]
    if sgn < 0:
        bow, P, G, ep = [[-q[0], q[1], q[2]] for q in (bow, P, G, ep)]
    pts = [
        [pinX, -52.15, 5.75],
        [pinX - sgn * 5.0, laneY, laneZ],
        [sgn * 6.5, -20.0, laneZ],
        [sgn * 5.2, -6.0, max(laneZ, 5.1)],
        [sgn * (abs(bow[0]) * 0.45 + 2.3), bow[1] * 0.45 - 2.7, 11.5],
        bow, P, G, ep,
    ]
    return pts

wires, lens, failed = {}, {}, []
for side in ('right', 'left'):
    for i in range(14):
        name = f'Wire-{side}-{i+1:02d}'
        w, r = F.build_wire(wire_points(i, side))
        if w is None:
            failed.append((name, r))
        else:
            wires[name] = w; lens[name] = round(r + 7.30, 2)
print('built', len(wires), 'failed', failed)

bodies_by_pitch = {}
for pitch in (17, 16):
    bl = []
    for n, s in F.bodies_of(pitch):
        if n in ('underside-left-J_WING', 'underside-right-J_WING'):
            side = 'left' if 'left' in n else 'right'
            bl.append((n + '-N2', xform(s, -27.0 if side == 'left' else 27.0)))
        elif n in ('tray-left', 'tray-right'):
            bl.append((n, cut_channel(s, 'left' if 'left' in n else 'right')))
        else:
            bl.append((n, s))
    bodies_by_pitch[pitch] = bl

sc = F.Scorer(wires, bodies_by_pitch)
ww, wf = sc.full()
res = dict(built=len(wires), failed=failed, lens=lens,
           ww={k: v for k, v in ww.items()},
           wf17={k: v for k, v in wf[17].items()},
           wf16={k: v for k, v in wf[16].items()},
           gate1_17=len(ww) + len(wf[17]), gate1_16=len(ww) + len(wf[16]),
           longest=max(lens.values()) if lens else None)
print(json.dumps({k: res[k] for k in ('built', 'failed', 'gate1_17', 'gate1_16', 'longest')}))
print('WW pairs:', len(ww), 'WF17:', len(wf[17]), 'WF16:', len(wf[16]))
from collections import Counter
print('WF17 by body:', Counter(k.split('x', 1)[1].rsplit('-', 0)[0] if False else k.split('x')[1] for k in wf[17]).most_common(12))
json.dump(res, open('/home/hatch/workspace/projects/he-piantor-north/.issue253-runtime/stage2_result.json', 'w'), indent=1)
