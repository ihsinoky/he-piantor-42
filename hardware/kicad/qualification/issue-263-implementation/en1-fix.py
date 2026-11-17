"""Hand-route the last Main escape: J3.8 MUX_EN1 -> B.Cu stub end (106.8,120.2).
F escape along the fanout channel direction, one via, B.Cu run west.
Validated afterwards by audit-main + DRC (no rule relaxation)."""
import pcbnew as p

E = '/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation'
V = lambda a: p.VECTOR2I(round(a[0] * 1e6), round(a[1] * 1e6))
b = p.LoadBoard(f'{E}/main-rev8/routed.kicad_pcb')
net = b.FindNet('MUX_EN1')
PAD = (125.12, 111.263)
VIA = (125.9, 113.2)
PATH_B = [(125.9, 113.2), (121.0, 116.5), (114.0, 119.2), (106.8, 120.2)]

def track(a, z, layer):
    t = p.PCB_TRACK(b); t.SetStart(V(a)); t.SetEnd(V(z)); t.SetWidth(p.FromMM(0.1))
    t.SetLayer(layer); t.SetNetCode(net.GetNetCode()); b.Add(t)

track(PAD, (125.9, 112.2), p.F_Cu)
track((125.9, 112.2), VIA, p.F_Cu)
v = p.PCB_VIA(b); v.SetPosition(V(VIA)); v.SetWidth(600000); v.SetDrill(300000)
v.SetViaType(p.VIATYPE_THROUGH); v.SetLayerPair(p.F_Cu, p.B_Cu); v.SetNetCode(net.GetNetCode()); b.Add(v)
for a, z in zip(PATH_B, PATH_B[1:]):
    track(a, z, p.B_Cu)
b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones()); b.BuildConnectivity()
p.SaveBoard(f'{E}/main-rev8/routed.kicad_pcb', b)
print('EN1 hand route applied')
