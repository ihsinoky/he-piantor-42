import sys
import pcbnew as p
step = sys.argv[1]
b = p.BOARD(); b.SetCopperLayerCount(2)
mm = p.FromMM
E = '/home/hatch/workspace/projects/he-piantor-midconn/hardware/kicad/qualification/issue-252-carrier'
# outline shapes
s = p.PCB_SHAPE(b); s.SetShape(p.SHAPE_T_SEGMENT)
s.SetStart(p.VECTOR2I(mm(-10), mm(-17.5))); s.SetEnd(p.VECTOR2I(mm(10), mm(-17.5)))
s.SetLayer(p.Edge_Cuts); s.SetWidth(mm(0.1)); b.Add(s); print('seg ok', flush=True)
if step == '1': sys.exit(0)
a = p.PCB_SHAPE(b); a.SetShape(p.SHAPE_T_ARC)
a.SetCenter(p.VECTOR2I(mm(10), mm(-15.5)))
a.SetStart(p.VECTOR2I(mm(10), mm(-17.5))); a.SetEnd(p.VECTOR2I(mm(12), mm(-15.5)))
a.SetLayer(p.Edge_Cuts); a.SetWidth(mm(0.1)); b.Add(a); print('arc ok', flush=True)
if step == '2': sys.exit(0)
c = p.PCB_SHAPE(b); c.SetShape(p.SHAPE_T_CIRCLE)
c.SetCenter(p.VECTOR2I(mm(-8), mm(-5.5))); c.SetRadius(mm(1.1))
c.SetLayer(p.Edge_Cuts); c.SetWidth(mm(0.1)); b.Add(c); print('circle ok', flush=True)
if step == '3': sys.exit(0)
f = p.FootprintLoad(f'{E}/connector/Carrier.pretty', 'JST_GH_SM14B-GHS-TB_1x14-1MP_P1.25mm_Horizontal')
f.Flip(p.VECTOR2I(0, 0), False); print('flip ok', flush=True)
f.SetOrientationDegrees(180); f.SetPosition(p.VECTOR2I(mm(-1), mm(4.95)))
for pad in f.Pads():
    pos = pad.GetPosition(); print(' pad', pad.GetNumber(), round(p.ToMM(pos.x),2), round(p.ToMM(pos.y),2), flush=True)
b.Add(f); print('fp ok', flush=True)
if step == '4': sys.exit(0)
n = p.NETINFO_ITEM(b, 'TEST'); b.Add(n)
t = p.PCB_TRACK(b); t.SetStart(p.VECTOR2I(mm(0), mm(0))); t.SetEnd(p.VECTOR2I(mm(5), mm(0)))
t.SetWidth(mm(0.3)); t.SetLayer(p.B_Cu); t.SetNet(n); b.Add(t); print('track ok', flush=True)
v = p.PCB_VIA(b); v.SetPosition(p.VECTOR2I(mm(5), mm(0)))
v.SetWidth(mm(0.6)); v.SetDrill(mm(0.3)); v.SetNet(n); v.SetLayerPair(p.F_Cu, p.B_Cu); b.Add(v)
print('via ok', flush=True)
p.SaveBoard('/home/hatch/workspace/projects/he-piantor-midconn/.issue252-runtime/probe2.kicad_pcb', b)
print('saved ok', flush=True)
