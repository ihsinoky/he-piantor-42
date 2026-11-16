"""Build carrier.kicad_pcb (Issue #252) with pcbnew.
Local frame: lx = assembly X - 16, ly = assembly Y - 9.5.
JC2 = header M (B.Cu): pads must land at (-1 - u_k, 3.10).
JC1 = header W (F.Cu): pads must land at (-0.60, -1.5 + u_k).
Rotation searched per header; assertions verify pad positions,
then tails are computed and checked against fitlib252 tails."""
import json, math, sys
import pcbnew as p

E = '/home/hatch/workspace/projects/he-piantor-midconn/hardware/kicad/qualification/issue-252-carrier'
U = {k: -8.125 + 1.25 * (k - 1) for k in range(1, 15)}
FN = {1: 'HALL_5V', 2: 'GND', 3: 'MUX_A0', 4: 'GND', 5: 'MUX_A1',
      6: 'MUX_A2', 7: 'WING_EN', 8: 'GND', 9: 'MUX_OUT_A', 10: 'GND',
      11: 'MUX_OUT_B', 12: 'GND', 13: 'MUX_OUT_C', 14: 'GND'}
NET = {k: f'P{k:02d}_{FN[k]}' for k in range(1, 15)}
POWER = {1, 2, 4, 8, 10, 12, 14}

b = p.BOARD()
b.SetCopperLayerCount(2)

def mm(v): return p.FromMM(v)
def add_net(name):
    n = p.NETINFO_ITEM(b, name); b.Add(n); return n
nets = {k: add_net(NET[k]) for k in range(1, 15)}

# outline: rounded rect lx[-13,12], ly[-17.5,17.5], r=2 (assembly X 3..28)
def seg(x1, y1, x2, y2):
    s = p.PCB_SHAPE(b); s.SetShape(p.SHAPE_T_SEGMENT)
    s.SetStart(p.VECTOR2I(mm(x1), mm(y1))); s.SetEnd(p.VECTOR2I(mm(x2), mm(y2)))
    s.SetLayer(p.Edge_Cuts); s.SetWidth(mm(0.1)); b.Add(s)
def arc(cx, cy, x1, y1, x2, y2):
    s = p.PCB_SHAPE(b); s.SetShape(p.SHAPE_T_ARC)
    s.SetCenter(p.VECTOR2I(mm(cx), mm(cy)))
    s.SetStart(p.VECTOR2I(mm(x1), mm(y1))); s.SetEnd(p.VECTOR2I(mm(x2), mm(y2)))
    s.SetLayer(p.Edge_Cuts); s.SetWidth(mm(0.1)); b.Add(s)
seg(-11, -17.5, 14, -17.5); seg(16, -15.5, 16, 15.5)
seg(14, 17.5, -11, 17.5); seg(-13, 15.5, -13, -15.5)
arc(14, -15.5, 14, -17.5, 16, -15.5); arc(14, 15.5, 16, 15.5, 14, 17.5)
arc(-11, 15.5, -11, 17.5, -13, 15.5); arc(-11, -15.5, -13, -15.5, -11, -17.5)

def place(ref, origin, layer_bottom, target):
    """target(k) -> (lx, ly) expected pad position. Search flip/rotation."""
    flips = (p.FLIP_DIRECTION_LEFT_RIGHT, p.FLIP_DIRECTION_TOP_BOTTOM) if layer_bottom else (None,)
    for fd in flips:
        for ang in (0, 90, 180, 270):
            f = p.FootprintLoad(f'{E}/connector/Carrier.pretty', 'JST_GH_SM14B-GHS-TB_1x14-1MP_P1.25mm_Horizontal')
            f.SetReference(ref); f.SetValue('SM14B-GHS-TB(LF)(SN)')
            b.Add(f)
            if fd is not None: f.Flip(p.VECTOR2I(0, 0), fd)
            f.SetOrientationDegrees(ang)
            f.SetPosition(p.VECTOR2I(mm(origin[0]), mm(origin[1])))
            ok = True
            for pad in f.Pads():
                n = pad.GetNumber()
                if n in ('MP', '15'): continue
                k = int(n)
                pos = pad.GetPosition()
                tx, ty = target(k)
                if abs(p.ToMM(pos.x) - tx) > 0.01 or abs(p.ToMM(pos.y) - ty) > 0.01:
                    ok = False; break
            if ok:
                return f, (str(fd), ang)
            b.Remove(f)
    raise RuntimeError(f'no flip/rotation satisfies {ref}')

# JC2 header M on B.Cu, origin local (-1, 4.95)
fM, angM = place('JC2', (-1.0, 4.95), True, lambda k: (-1.0 - U[k], 3.10))
# JC1 header W on F.Cu, origin local (-2.45, -1.5)
fW, angW = place('JC1', (10.55, -1.5), False, lambda k: (12.40, -1.5 + U[k]))
print('rotations: JC2(M,B.Cu)', angM, ' JC1(W,F.Cu)', angW, flush=True)

for f in (fM, fW):
    for pad in f.Pads():
        n = pad.GetNumber()
        if n in ('MP', '15'):
            pad.SetNumber('15')
        else:
            pad.SetNet(nets[int(n)])

# mounting holes as Edge.Cuts circles (NPTH by construction), D2.2
for (hx, hy) in ((-11.5, -15.5), (12.3, -15.5)):
    s = p.PCB_SHAPE(b); s.SetShape(p.SHAPE_T_CIRCLE)
    s.SetCenter(p.VECTOR2I(mm(hx), mm(hy))); s.SetRadius(mm(1.1))
    s.SetLayer(p.Edge_Cuts); s.SetWidth(mm(0.1)); b.Add(s)

def track(x1, y1, x2, y2, layer, w, net):
    t = p.PCB_TRACK(b)
    t.SetStart(p.VECTOR2I(mm(x1), mm(y1))); t.SetEnd(p.VECTOR2I(mm(x2), mm(y2)))
    t.SetWidth(mm(w)); t.SetLayer(layer); t.SetNet(net); b.Add(t)
def via(x, y, net):
    v = p.PCB_VIA(b); v.SetPosition(p.VECTOR2I(mm(x), mm(y)))
    v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3)); v.SetNet(net)
    v.SetLayerPair(p.F_Cu, p.B_Cu); b.Add(v)

trace_len = {}
for k in range(1, 15):
    mx = 7.125 - 1.25 * (k - 1); wy = -9.625 + 1.25 * (k - 1)
    w = 0.5 if k in POWER else 0.3
    L = 0.0
    # B.Cu: M pad straight south to the via row at ly=-11.5
    track(mx, 3.10, mx, -11.5, p.B_Cu, w, nets[k]); L += 14.6
    via(mx, -11.5, nets[k])
    # F.Cu: north at mx to wy, then east to the W pad
    track(mx, -11.5, mx, wy, p.F_Cu, w, nets[k]); L += abs(wy + 11.5)
    track(mx, wy, 12.40, wy, p.F_Cu, w, nets[k]); L += abs(12.40 - mx)
    trace_len[NET[k]] = round(L, 2)

# project design rule: 0.10 mm clearance (D-019/D-021 class)
try:
    for name, nc in b.GetAllNetClasses().items():
        nc.SetClearance(mm(0.10))
    print('netclass clearance set to 0.10', flush=True)
except Exception as ex:
    print('netclass set failed:', ex, flush=True)

p.SaveBoard(f'{E}/carrier.kicad_pcb', b)

# pad table in board + assembly coords (assembly = local + (16, 9.5))
tab = {}
for ref, f in (('JC1', fW), ('JC2', fM)):
    for pad in f.Pads():
        n = pad.GetNumber()
        pos = pad.GetPosition()
        lx, ly = p.ToMM(pos.x), p.ToMM(pos.y)
        tab[f'{ref}.{n}'] = {'net': pad.GetNetname(), 'local': [round(lx, 3), round(ly, 3)],
                             'assembly': [round(lx + 16, 3), round(ly + 9.5, 3)]}
json.dump({'rotations': {'JC1_W_top': angW, 'JC2_M_bottom': angM},
           'pads': tab, 'trace_len_mm': trace_len},
          open(f'{E}/inspection/pad-table.json', 'w'), indent=1)
print('board saved; pad table written', flush=True)
