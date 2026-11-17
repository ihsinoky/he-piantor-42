"""Issue #268 build step 1: swap J_WING GH -> FH12 on B.Cu; delete link-net copper in zone Z2.
Outputs the working board + a JSON ledger (deleted items, stub endpoints)."""
import json, sys
import pcbnew as p

SRC = 'hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb'
LIB = 'hardware/kicad/qualification/issue-268-matrix-rev4/PCBA.pretty'
NAME = 'Hirose_FH12-14S-0.5SH_1x14-1MP_P0.50mm_Horizontal'
LINK = ['HALL_5V','GND','MUX_A0','MUX_A1','MUX_A2','WING_EN','MUX_OUT_A','MUX_OUT_B','MUX_OUT_C']
Z2 = (85.0, 115.0, 129.5, 140.03)  # xmin, xmax, ymin, ymax
mm = lambda v: v/1e6

b = p.LoadBoard(SRC)
jw = None
for fp in b.GetFootprints():
    if fp.GetReference() == 'J_WING':
        jw = fp
padnet = {pad.GetNumber(): pad.GetNetname() for pad in jw.Pads()}
assert padnet['1'] == 'HALL_5V' and padnet['14'] == 'GND', padnet
b.RemoveNative(jw)

# --- place FH12 ---
fp = p.FootprintLoad(LIB, NAME)
fp.SetReference('J_WING')
fp.SetValue('FH12-14S-0.5SH(55)')
try:
    fp.SetFPID(p.LIB_ID('Wing129', NAME))
except Exception as e:
    print('SetFPID failed:', e)
fp.SetPosition(p.VECTOR2I(p.FromMM(100.0), p.FromMM(133.0)))
fp.SetLayer(p.B_Cu)
fp.SetOrientationDegrees(0.0)
# assign nets
netinfo = b.GetNetInfo()
for pad in fp.Pads():
    n = pad.GetNumber()
    if n in padnet and padnet[n]:
        pad.SetNet(netinfo.GetNetItem(padnet[n]))
b.Add(fp)
meas = {}
cen = fp.GetPosition()
meas['anchor'] = (mm(cen.x), mm(cen.y))
sig = [(pad.GetNumber(), pad.GetPosition()) for pad in fp.Pads() if pad.GetNumber().isdigit()]
sig.sort(key=lambda t: int(t[0]))
p1, p14 = sig[0][1], sig[-1][1]
meas['pad1'] = (mm(p1.x), mm(p1.y)); meas['pad14'] = (mm(p14.x), mm(p14.y))
mps = [pad.GetPosition() for pad in fp.Pads() if not pad.GetNumber().isdigit()]
meas['mp_centroid'] = (sum(mm(q.x) for q in mps)/len(mps), sum(mm(q.y) for q in mps)/len(mps))
meas['layer'] = int(fp.GetLayer())
print('FH12 placement:', json.dumps(meas))

# --- delete link-net copper intersecting Z2 ---
def inZ(x, y, pad=0.0):
    return Z2[0]-pad <= x <= Z2[1]+pad and Z2[2]-pad <= y <= Z2[3]+pad
def seg_hits_Z2(t):
    s, e = t.GetStart(), t.GetEnd()
    pts = [(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]
    if any(inZ(x, y) for x, y in pts):
        return True
    # segment crossing the box without endpoints inside: sample midpoint
    mx, my = (pts[0][0]+pts[1][0])/2, (pts[0][1]+pts[1][1])/2
    return inZ(mx, my)
deleted, stubs = [], {}
for t in list(b.GetTracks()):
    if t.GetNetname() not in LINK:
        continue
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition()
        hit = inZ(mm(q.x), mm(q.y))
    else:
        hit = seg_hits_Z2(t)
    if not hit:
        continue
    s, e = t.GetStart(), t.GetEnd()
    for q in (s, e):
        x, y = mm(q.x), mm(q.y)
        if not inZ(x, y, 0.001):
            stubs.setdefault(t.GetNetname(), set()).add((round(x, 4), round(y, 4), int(t.GetLayer())))
    deleted.append(dict(uuid=t.m_Uuid.AsString(), net=t.GetNetname(),
                        via=isinstance(t, p.PCB_VIA)))
    b.RemoveNative(t)
print('deleted items:', len(deleted))
json.dump(dict(meas=meas, deleted=deleted,
               stubs={k: sorted(v) for k, v in stubs.items()}),
          open('.issue268-runtime/step1.json', 'w'), indent=1)
b.Save(SRC)
print('saved')
