"""Apply a gaproute result to a board file (in place).
Usage: apply_gap.py <board> <route.json> <netname>"""
import pcbnew as p, sys, json
b = p.LoadBoard(sys.argv[1])
route = json.load(open(sys.argv[2]))
net = b.FindNet(sys.argv[3])
assert net is not None
LAY = {'F': p.F_Cu, 'I1': p.In1_Cu, 'I2': p.In2_Cu, 'B': p.B_Cu}
def nm(v): return p.FromMM(v)
for t in route['tracks']:
    tr = p.PCB_TRACK(b)
    tr.SetNet(net)
    tr.SetLayer(LAY[t['layer']])
    tr.SetWidth(nm(t['w']))
    tr.SetStart(p.VECTOR2I(nm(t['x1']), nm(t['y1'])))
    tr.SetEnd(p.VECTOR2I(nm(t['x2']), nm(t['y2'])))
    b.Add(tr)
for v in route['vias']:
    via = p.PCB_VIA(b)
    via.SetNet(net)
    via.SetPosition(p.VECTOR2I(nm(v['x']), nm(v['y'])))
    via.SetWidth(nm(0.6))
    via.SetDrill(nm(0.3))
    via.SetViaType(p.VIATYPE_THROUGH)
    via.SetLayerPair(p.F_Cu, p.B_Cu)
    b.Add(via)
b.Save(sys.argv[1])
print(f"applied {len(route['tracks'])} tracks, {len(route['vias'])} vias of {sys.argv[3]}")
