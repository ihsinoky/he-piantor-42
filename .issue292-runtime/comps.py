"""Shapely-based per-net component analysis (pads/tracks/vias).
Elements of one pad/via across layers are unioned first (plated barrel),
then per-layer geometric intersection unions the rest.
Usage: comps.py <board> <net1,net2,...>"""
import pcbnew as p, sys
from shapely.geometry import Point, LineString, box as sbox
from shapely.strtree import STRtree
SRC = sys.argv[1]
TARGETS = set(sys.argv[2].split(','))
b = p.LoadBoard(SRC)
LAY = {p.F_Cu: 'F', p.In1_Cu: 'I1', p.In2_Cu: 'I2', p.B_Cu: 'B'}
def mm(v): return p.ToMM(v)

class DSU:
    def __init__(self): self.par = {}
    def find(self, x):
        self.par.setdefault(x, x)
        while self.par[x] != x:
            self.par[x] = self.par[self.par[x]]; x = self.par[x]
        return x
    def union(self, a, c):
        ra, rc = self.find(a), self.find(c)
        if ra != rc: self.par[ra] = rc

for net in sorted(TARGETS):
    dsu = DSU()
    elems = []  # (layer, geom, tag, group)
    for f in b.GetFootprints():
        ref = str(f.GetReference())
        for pad in f.Pads():
            if pad.GetNetname() != net: continue
            if net == 'GND' and ref != 'U1': continue
            pos = pad.GetPosition(); sz = pad.GetSize()
            cx, cy = mm(pos.x), mm(pos.y)
            hw, hh = mm(sz.x) / 2, mm(sz.y) / 2
            pth = pad.GetAttribute() == p.PAD_ATTRIB_PTH
            grp = f"pad:{ref}.{pad.GetNumber()}"
            for lid, lname in LAY.items():
                if pth or pad.IsOnLayer(lid):
                    elems.append((lname, sbox(cx - hw, cy - hh, cx + hw, cy + hh), f"PAD {ref}.{pad.GetNumber()}", grp))
    ti = 0
    for t in b.GetTracks():
        if t.GetNetname() != net: continue
        if isinstance(t, p.PCB_VIA):
            pos = t.GetPosition(); cx, cy = mm(pos.x), mm(pos.y)
            r = mm(t.GetWidth(p.F_Cu)) / 2
            grp = f"via:{cx:.3f},{cy:.3f}"
            for lid, lname in LAY.items():
                if t.IsOnLayer(lid):
                    elems.append((lname, Point(cx, cy).buffer(r, resolution=8), f"VIA ({cx:.2f},{cy:.2f})", grp))
        else:
            s, e = t.GetStart(), t.GetEnd()
            g = LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2, resolution=4, cap_style=1)
            elems.append((LAY[t.GetLayer()], g, f"TRK ({mm(s.x):.2f},{mm(s.y):.2f})-({mm(e.x):.2f},{mm(e.y):.2f})", f"trk:{ti}"))
            ti += 1
    by_group = {}
    for i, (_, _, _, grp) in enumerate(elems):
        by_group.setdefault(grp, []).append(i)
    for idxs in by_group.values():
        for i in idxs[1:]:
            dsu.union(idxs[0], i)
    by_layer = {}
    for i, (lname, g, tag, grp) in enumerate(elems):
        by_layer.setdefault(lname, []).append(i)
    for lname, idxs in by_layer.items():
        geoms = [elems[i][1] for i in idxs]
        tree = STRtree(geoms)
        for j, i in enumerate(idxs):
            for k in tree.query(geoms[j], predicate='intersects'):
                if k != j:
                    dsu.union(i, idxs[k])
    comps = {}
    for i, (lname, g, tag, grp) in enumerate(elems):
        comps.setdefault(dsu.find(i), []).append((lname, tag))
    print(f"===== {net}: {len(comps)} components")
    for root, members in sorted(comps.items(), key=lambda kv: -len(kv[1])):
        pads_ = sorted({t for _, t in members if t.startswith('PAD')})
        vias_ = sorted({t for _, t in members if t.startswith('VIA')})
        ntrk = sum(1 for _, t in members if t.startswith('TRK'))
        print(f"  comp[{len(members)}] pads={pads_} vias={vias_} tracks={ntrk}")
