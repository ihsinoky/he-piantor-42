"""Issue #268 analysis v3: capsule-model union-find per link net.
Items: tracks = capsules (segment + width/2), vias = circles (dia/2, both layers),
pads = oriented rects (SMD: own layer). Two items connect if shapes on a common
layer come within 0.002mm. Cross-check counts against kicad-cli DRC."""
import json, math
import pcbnew as p

SRC = 'hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb'
LINK = ['HALL_5V','GND','MUX_A0','MUX_A1','MUX_A2','WING_EN','MUX_OUT_A','MUX_OUT_B','MUX_OUT_C']
mm = lambda v: v/1e6
TOL = 0.002

def pt_seg(px, py, x1, y1, x2, y2):
    dx, dy = x2-x1, y2-y1
    L2 = dx*dx + dy*dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px-x1)*dx + (py-y1)*dy)/L2))
    return math.hypot(px-(x1+t*dx), py-(y1+t*dy))

def seg_seg(a, b):
    (x1, y1, x2, y2), (x3, y3, x4, y4) = a, b
    def orient(px, py, qx, qy, rx, ry):
        return (qx-px)*(ry-py) - (qy-py)*(rx-px)
    d1 = orient(x3, y3, x4, y4, x1, y1); d2 = orient(x3, y3, x4, y4, x2, y2)
    d3 = orient(x1, y1, x2, y2, x3, y3); d4 = orient(x1, y1, x2, y2, x4, y4)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)): return 0.0
    return min(pt_seg(x1, y1, x3, y3, x4, y4), pt_seg(x2, y2, x3, y3, x4, y4),
               pt_seg(x3, y3, x1, y1, x2, y2), pt_seg(x4, y4, x1, y1, x2, y2))

class DSU:
    def __init__(s): s.par = {}
    def find(s, x):
        s.par.setdefault(x, x)
        while s.par[x] != x: s.par[x] = s.par[s.par[x]]; x = s.par[x]
        return x
    def union(s, a, c):
        ra, rc = s.find(a), s.find(c)
        if ra != rc: s.par[ra] = rc

b = p.LoadBoard(SRC)
out = {}
for net in LINK:
    # shapes: (kind, layer_set, seg or None, radius, cx, cy, rect or None, label)
    shapes = []
    for t in b.GetTracks():
        if t.GetNetname() != net: continue
        s, e = t.GetStart(), t.GetEnd()
        if isinstance(t, p.PCB_VIA):
            shapes.append(('V', {'F.Cu', 'B.Cu'}, None, mm(t.GetDrill())/2 + 0.30, mm(s.x), mm(s.y), None, 'via'))
        else:
            shapes.append(('T', {t.GetLayerName()}, (mm(s.x), mm(s.y), mm(e.x), mm(e.y)), mm(t.GetWidth())/2, 0, 0, None, 'trk'))
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() != net: continue
            pos = pad.GetPosition()
            ls = pad.GetLayerSet()
            layers = set()
            if ls.Contains(p.F_Cu): layers.add('F.Cu')
            if ls.Contains(p.B_Cu): layers.add('B.Cu')
            if not layers: layers = {'F.Cu', 'B.Cu'}
            rect = (mm(pos.x), mm(pos.y), mm(pad.GetSize().x), mm(pad.GetSize().y), pad.GetOrientationDegrees())
            shapes.append(('P', layers, None, 0.0, rect[0], rect[1], rect, fp.GetReference() + '.' + pad.GetNumber()))
    def shape_dist(s1, s2):
        # returns (dist, layer) minimal over common layers; rect handled as 4 edge segs + centre seg cross
        def segs_of(sh):
            if sh[2] is not None: return [sh[2]]
            if sh[0] == 'V': return [(sh[4], sh[5], sh[4], sh[5])]
            cx, cy, sx, sy, rot = sh[6]
            th = math.radians(rot)
            c, s = math.cos(th), math.sin(th)
            pts = []
            for lx, ly in [(-sx/2, -sy/2), (sx/2, -sy/2), (sx/2, sy/2), (-sx/2, sy/2)]:
                pts.append((cx + lx*c - ly*s, cy + lx*s + ly*c))
            return [(pts[i][0], pts[i][1], pts[(i+1) % 4][0], pts[(i+1) % 4][1]) for i in range(4)] + \
                   [(pts[0][0], pts[0][1], pts[2][0], pts[2][1]), (pts[1][0], pts[1][1], pts[3][0], pts[3][1])]
        best = 1e9
        for a in segs_of(s1):
            for c in segs_of(s2):
                best = min(best, seg_seg(a, c))
        return best - s1[3] - s2[3]
    d = DSU()
    for i in range(len(shapes)): d.find(i)
    for i in range(len(shapes)):
        for j in range(i+1, len(shapes)):
            if not (shapes[i][1] & shapes[j][1]): continue
            if shape_dist(shapes[i], shapes[j]) <= TOL: d.union(i, j)
    comps = {}
    for i in range(len(shapes)): comps.setdefault(d.find(i), []).append(i)
    clist = []
    for root, idxs in comps.items():
        labs = [shapes[i][7] for i in idxs if shapes[i][0] == 'P']
        pts = []
        for i in idxs:
            sh = shapes[i]
            if sh[2]: pts += [(sh[2][0], sh[2][1]), (sh[2][2], sh[2][3])]
            else: pts.append((sh[4], sh[5]))
        clist.append(dict(items=len(idxs), pads=len(labs), padlabels=labs,
                          bbox=[round(min(x for x, y in pts), 2), round(min(y for x, y in pts), 2),
                                round(max(x for x, y in pts), 2), round(max(y for x, y in pts), 2)] if pts else None))
    clist.sort(key=lambda c: -c['pads'])
    out[net] = clist
    print(net, 'components:', len(clist))
    for c in clist:
        print('   pads=%d items=%d %s bbox=%s' % (c['pads'], c['items'], c['padlabels'][:4], c['bbox']))
json.dump(out, open('.issue268-runtime/components3.json', 'w'), indent=1)
print('saved components3.json')
