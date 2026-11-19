"""Build wmain.kicad_pcb: Rev.10 donor surgery (outline/settings kept),
fresh placement per design.py, zones + rule areas. Routing is separate."""
import pcbnew as p, sys
sys.path.insert(0, '.')
from design import PARTS
from pathlib import Path
E = Path('.').resolve(); W = E.parent
TREE = W/'hardware/kicad/qualification/issue-292-wmain'
LIB = str(TREE/'wmain.pretty')
REV10 = W/'hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb'

# ref -> (x, y, rot_deg)
PLACE = {
 'U1': (75.1, 124.85, 90), 'J2': (75.7452, 111.8239, 43), 'J3': (124.2548, 111.8239, -43),
 'J4': (100.0, 90.0, 180), 'U2': (89.0, 97.0, 0), 'L1': (95.5, 94.5, 0),
 'CIN1': (90.0, 92.5, 90), 'CIN2': (85.8, 99.3, 90), 'COUT1': (92.2, 95.9, 90),
 'COUT2': (81.8, 104.8, 90), 'CVAUX': (85.5, 101.8, 0),
 'RFB1': (92.5, 91.8, 0), 'RFB2': (94.7, 97.9, 0), 'RPG': (104.5, 96.8, 90),
 'D1': (97.0, 85.8, 0), 'D2': (121.5, 124.8, 0), 'JBATT': (124.0, 134.5, 0),
 'U3': (124.5, 128.8, 0), 'U4': (119.0, 132.0, 0),
 'CHIN': (126.5, 128.5, 90), 'CHOUT': (128.5, 127.5, 90), 'CPOUT': (114.8, 101.3, 90),
 'RPD1': (131.0, 128.0, 0), 'RPD2': (117.5, 135.8, 90), 'RPD3': (118.5, 136.2, 90),
 'RFA': (121.2, 119.5, 90), 'RFB': (124.7, 119.5, 90), 'RFC': (128.2, 119.5, 90),
 'CFA': (121.2, 123.0, 90), 'CFB': (124.7, 123.0, 90), 'CFC': (128.2, 123.0, 90),
 'RV1': (102.0, 93.2, 0), 'RV2': (106.0, 93.2, 0), 'Q1': (108.0, 96.0, 0),
 'RVG': (125.5, 126.3, 90), 'RVPD': (121.5, 130.2, 0), 'CVS': (93.5, 84.8, 90),
 'JPAD': (112.5, 96.8, 0), 'RPU1': (105.5, 91.5, 0), 'RPU2': (109.0, 91.5, 0),
 'JSWD': (113.5, 136.2, 0), 'RLED': (99.5, 83.0, 0), 'DLED': (96.0, 83.0, 0),
 'SW1': (84.5, 134.5, 90), 'RRST': (93.0, 87.5, 0),
 'CVCC1': (76.5, 118.3, 0), 'CVCC2': (71.8, 118.6, 90),
 'TP1': (90.8, 89.6, 0), 'TP2': (102.5, 96.5, 0), 'TP3': (128.8, 130.5, 0),
 'TP4': (107.0, 88.0, 0), 'TP5': (87.0, 136.3, 0),
 'H1': (100.0, 79.2679, 0), 'H2': (68.1073, 134.4, 0), 'H3': (131.8927, 134.4, 0),
}
assert set(PLACE) == {r for (r, *_rest) in PARTS}, set(PLACE) ^ {r for (r, *_rest) in PARTS}

donor = p.LoadBoard(str(REV10))
b = p.BOARD()
b.SetCopperLayerCount(4)
for i, nm in [(0, 'F.Cu'), (4, 'In1.Cu'), (6, 'In2.Cu'), (2, 'B.Cu')]:
    b.SetLayerName(i, nm)
EDGES = [((64.1073, 134.4359), (66.1073, 137.9)), ((66.1073, 137.9), (133.8927, 137.9)),
 ((133.8927, 137.9), (135.8927, 134.4359)), ((135.8927, 134.4359), (128.9362, 122.3869)),
 ((128.9362, 122.3869), (132.9488, 115.4381)), ((132.9488, 115.4381), (119.8213, 103.1964)),
 ((119.8213, 103.1964), (117.8562, 103.1958)), ((117.8562, 103.1958), (102.0, 75.7321)),
 ((102.0, 75.7321), (98.0, 75.7321)), ((98.0, 75.7321), (82.1438, 103.1958)),
 ((82.1438, 103.1958), (80.1787, 103.1964)), ((80.1787, 103.1964), (67.0512, 115.4381)),
 ((67.0512, 115.4381), (71.0638, 122.3869)), ((71.0638, 122.3869), (64.1073, 134.4359))]
for (x1, y1), (x2, y2) in EDGES:
    sh = p.PCB_SHAPE(b)
    sh.SetShape(p.SHAPE_T_SEGMENT)
    sh.SetStart(p.VECTOR2I(round(x1 * 1e6), round(y1 * 1e6)))
    sh.SetEnd(p.VECTOR2I(round(x2 * 1e6), round(y2 * 1e6)))
    sh.SetLayer(p.Edge_Cuts)
    sh.SetWidth(round(0.05 * 1e6))
    b.Add(sh)

# nets
netobjs = {}
def getnet(name):
    if name not in netobjs:
        n = b.FindNet(name)
        if not n or n.GetNetCode() == 0:
            n = p.NETINFO_ITEM(b, name)
            b.Add(n)
        netobjs[name] = n
    return netobjs[name]

for (ref, value, sym, fp, pins) in PARTS:
    f = p.FootprintLoad(LIB, fp)
    assert f, fp
    b.Add(f)
    x, y, rot = PLACE[ref]
    f.SetPosition(p.VECTOR2I(round(x * 1e6), round(y * 1e6)))
    f.SetOrientationDegrees(rot)
    f.SetReference(ref)
    f.SetValue(value)
    for pad in f.Pads():
        num = str(pad.GetNumber())
        if num in pins and pins[num] is not None:
            pad.SetNetCode(getnet(pins[num]).GetNetCode())
        elif num == '' :
            pass  # unnumbered pads (EZmate shell): no net, as Rev.10
        else:
            pad.SetNetCode(0)

def rule_area(points, layers, name, tracks=False, vias=False, pour=False, fps=False, pads=False):
    made = []
    for L in layers:
        z = p.ZONE(b)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks(tracks); z.SetDoNotAllowVias(vias)
        z.SetDoNotAllowCopperPour(pour); z.SetDoNotAllowFootprints(fps); z.SetDoNotAllowPads(pads)
        z.SetLayer(L)
        o = z.Outline(); o.NewOutline()
        for (x, y) in points:
            o.Append(round(x * 1e6), round(y * 1e6))
        z.SetZoneName(name)
        b.Add(z)
        made.append(z)
    return made

CU = [p.F_Cu, p.In1_Cu, p.In2_Cu, p.B_Cu]
import math
# trackpad component keep-out: dia.40 @ (100,118) - footprints only
circ = [(100 + 20 * math.cos(math.radians(a)), 118 + 20 * math.sin(math.radians(a))) for a in range(0, 360, 6)]
rule_area(circ, CU, 'TRACKPAD_KEEP_OUT', fps=True)
# antenna keep-out: south strip under module antenna edge
rule_area([(70.3, 127.9), (79.9, 127.9), (79.9, 137.9), (70.3, 137.9)], CU,
          'ANTENNA_KEEP_OUT', tracks=True, vias=True, pour=True)
# hole reservations dia.5 at H1/H2/H3
for (hx, hy) in [(100.0, 79.2679), (68.1073, 134.4), (131.8927, 134.4)]:
    c = [(hx + 2.5 * math.cos(math.radians(a)), hy + 2.5 * math.sin(math.radians(a))) for a in range(0, 360, 10)]
    rule_area(c, CU, 'HOLE_RESERVATION', tracks=True, vias=True, pour=True)

# GND plane on In1.Cu over the Rev.10 outline loop
LOOP = [(64.1073, 134.4359), (66.1073, 137.9), (133.8927, 137.9), (135.8927, 134.4359),
        (128.9362, 122.3869), (132.9488, 115.4381), (119.8213, 103.1964),
        (117.8562, 103.1958), (102.0, 75.7321), (98.0, 75.7321), (82.1438, 103.1958),
        (80.1787, 103.1964), (67.0512, 115.4381), (71.0638, 122.3869)]
z = p.ZONE(b)
z.SetLayer(p.In1_Cu)
z.SetNetCode(getnet('GND').GetNetCode())
z.SetLocalClearance(round(0.2 * 1e6))
o = z.Outline(); o.NewOutline()
for (x, y) in LOOP:
    o.Append(round(x * 1e6), round(y * 1e6))
b.Add(z)

tb = b.GetTitleBlock()
tb.SetTitle('Issue 292 wireless Main (ISP1807-LR)')
tb.SetComment(0, 'DRAFT - NOT FOR ORDER')
b.Save(str(TREE/'wmain.kicad_pcb'))
print('board saved:', len(list(b.GetFootprints())), 'footprints,',
      sum(len(list(f.Pads())) for f in b.GetFootprints()), 'pads')
