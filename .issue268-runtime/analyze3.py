"""Issue #268 analysis v2: per link-net components via geometric union-find.
Connect rules (same net): endpoint coincidence / endpoint-on-segment (same layer),
endpoint inside pad rect (pad's layer), via joins F+B at its centre."""
import json, math
import pcbnew as p

SRC = 'hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb'
LINK = ['HALL_5V','GND','MUX_A0','MUX_A1','MUX_A2','WING_EN','MUX_OUT_A','MUX_OUT_B','MUX_OUT_C']
mm = lambda v: v/1e6
EPS = 0.011

b = p.LoadBoard(SRC)

def seg_pt_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2-x1, y2-y1
    L2 = dx*dx+dy*dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px-x1)*dx+(py-y1)*dy)/L2))
    qx, qy = x1+t*dx, y1+t*dy
    return math.hypot(px-qx, py-qy), (qx, qy)

class DSU:
    def __init__(s): s.par = {}
    def find(s, x):
        s.par.setdefault(x, x)
        while s.par[x] != x:
            s.par[x] = s.par[s.par[x]]; x = s.par[x]
        return x
    def union(s, a, c):
        ra, rc = s.find(a), s.find(c)
        if ra != rc: s.par[ra] = rc

out = {}
for net in LINK:
    tracks, vias, pads = [], [], []
    for t in b.GetTracks():
        if t.GetNetname() != net: continue
        if isinstance(t, p.PCB_VIA):
            vias.append((mm(t.GetStart().x), mm(t.GetStart().y)))
        else:
            s, e = t.GetStart(), t.GetEnd()
            tracks.append((mm(s.x), mm(s.y), mm(e.x), mm(e.y), t.GetLayerName(), mm(t.GetWidth())))
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() != net: continue
            pos = pad.GetPosition()
            pads.append((mm(pos.x), mm(pos.y), pad.GetLayerName(), fp.GetReference(),
                         mm(pad.GetSize().x), mm(pad.GetSize().y), pad.GetOrientationDegrees()))
    d = DSU()
    nodes = [('T', i) for i in range(len(tracks))] + [('V', i) for i in range(len(vias))] + [('P', i) for i in range(len(pads))]
    for n in nodes: d.find(n)
    def ends(i):
        x1, y1, x2, y2, lay, w = tracks[i]
        return [(x1, y1), (x2, y2)]
    # track-track
    for i in range(len(tracks)):
        for j in range(i+1, len(tracks)):
            if tracks[i][4] != tracks[j][4]: continue
            hit = False
            for (px, py) in ends(i):
                if seg_pt_dist(px, py, *tracks[j][:4])[0] <= EPS: hit = True
            for (px, py) in ends(j):
                if seg_pt_dist(px, py, *tracks[i][:4])[0] <= EPS: hit = True
            if hit: d.union(('T', i), ('T', j))
    # track-via (via joins both layers at centre)
    for i in range(len(tracks)):
        for k, (vx, vy) in enumerate(vias):
            for (px, py) in ends(i):
                if math.hypot(px-vx, py-vy) <= EPS: d.union(('T', i), ('V', k))
    # track-pad: endpoint inside pad rect on pad layer (SMD) - pads here are axis aligned-ish; use circle approx r=min(size)/2+eps plus rect test with rotation
    for i in range(len(tracks)):
        lay = tracks[i][4]
        for k, (px, py, play, ref, sx, sy, rot) in enumerate(pads):
            if play != lay and play != '*': continue
            th = math.radians(rot)
            for (qx, qy) in ends(i):
                dx, dy = qx-px, qy-py
                lx = dx*math.cos(th) + dy*math.sin(th)
                ly = -dx*math.sin(th) + dy*math.cos(th)
                if abs(lx) <= sx/2 + EPS and abs(ly) <= sy/2 + EPS:
                    d.union(('T', i), ('P', k))
    # via-pad: via centre inside pad rect (either layer via is through)
    for k, (vx, vy) in enumerate(vias):
        for m, (px, py, play, ref, sx, sy, rot) in enumerate(pads):
            th = math.radians(rot)
            dx, dy = vx-px, vy-py
            lx = dx*math.cos(th) + dy*math.sin(th)
            ly = -dx*math.sin(th) + dy*math.cos(th)
            if abs(lx) <= sx/2 + EPS and abs(ly) <= sy/2 + EPS:
                d.union(('V', k), ('P', m))
    comps = {}
    for n in nodes: comps.setdefault(d.find(n), []).append(n)
    clist = []
    for root, ns in comps.items():
        pp = [pads[k] for (t, k) in ns if t == 'P']
        tt = [tracks[k] for (t, k) in ns if t == 'T']
        xs = [x for tr in tt for x in (tr[0], tr[2])] + [q[0] for q in pp]
        ys = [y for tr in tt for y in (tr[1], tr[3])] + [q[1] for q in pp]
        ends = []
        for tr in tt:
            ends.append([round(tr[0], 3), round(tr[1], 3), tr[4]])
            ends.append([round(tr[2], 3), round(tr[3], 3), tr[4]])
        clist.append(dict(items=len(ns), pads=len(pp), refs=sorted({q[3] for q in pp}),
                          bbox=[round(min(xs),2), round(min(ys),2), round(max(xs),2), round(max(ys),2)] if xs else None,
                          ends=ends))
    clist.sort(key=lambda c: -c['pads'])
    out[net] = clist
    print(net, 'components:', len(clist))
    for c in clist:
        print('   pads=%d items=%d refs=%s bbox=%s' % (c['pads'], c['items'], c['refs'][:5], c['bbox']))
json.dump(out, open('.issue268-runtime/components.json','w'), indent=1)
print('saved')
