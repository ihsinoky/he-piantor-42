"""16L esc board: list physical components of MUX_A1/MUX_A2 with pad members
and bbox centres, to locate the breaks."""
import pcbnew as p, sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation')
from verify import polys
from pathlib import Path
from shapely.ops import unary_union
w = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation/wing-rev5-16mm-left')
b = p.LoadBoard(str(w / 'main.kicad_pcb'))
p.ZONE_FILLER(b).Fill(b.Zones())
MM = 1e6

def shapes_of(item, layer):
    try:
        return polys(item.GetEffectiveShape(layer))
    except Exception:
        return None

for net in ('MUX_A1', 'MUX_A2'):
    items = []  # (kind, ident, [shapes per layer])
    for f in b.GetFootprints():
        for a in f.Pads():
            if a.GetNetname() == net:
                sh = {}
                for l in (p.F_Cu, p.B_Cu):
                    s = shapes_of(a, l)
                    if s is not None and not s.is_empty:
                        sh[l] = s
                if sh:
                    items.append((f'{f.GetReference()}.{a.GetNumber()}', sh))
    for t in b.GetTracks():
        if t.GetNetname() == net:
            sh = {}
            layers = (p.F_Cu, p.B_Cu) if t.Type() == p.PCB_VIA_T else (t.GetLayer(),)
            for l in layers:
                s = shapes_of(t, l)
                if s is not None and not s.is_empty:
                    sh[l] = s
            if sh:
                items.append((f'track:{t.m_Uuid.AsString()[:6]}', sh))
    for z in b.Zones():
        if z.GetNetname() == net:
            for l in (p.F_Cu, p.B_Cu):
                s = z.GetFilledPolysList(l)
                if s is not None and s.OutlineCount():
                    items.append((f'zone:{z.GetZoneName()}', {l: polys(s)}))
    # union-find over shared layers with touching shapes
    parent = list(range(len(items)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            for l in set(items[i][1]) & set(items[j][1]):
                if items[i][1][l].distance(items[j][1][l]) < 1e-9:
                    parent[find(i)] = find(j); break
    comps = {}
    for i, (ident, _) in enumerate(items):
        comps.setdefault(find(i), []).append(ident)
    print(net, '->', len(comps), 'components')
    for root, members in comps.items():
        pads = [m for m in members if not m.startswith(('track', 'zone'))]
        print('   pads:', pads, '| n_items:', len(members))
print('done')
