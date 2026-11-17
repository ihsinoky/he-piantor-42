"""Diagnose the 7 dangling tracks: endpoints, and same-net items near the free end."""
import json, math
import pcbnew as p

SRC = 'hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb'
mm = lambda v: v/1e6
b = p.LoadBoard(SRC)
d = json.load(open('.issue268-runtime/drc5.json'))
targets = []
for v in d['violations']:
    if v['type'] != 'track_dangling': continue
    it = v['items'][0]
    targets.append((round(it['pos']['x'], 2), round(it['pos']['y'], 2), it['description']))

tracks = []
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA): continue
    s, e = t.GetStart(), t.GetEnd()
    tracks.append((t, (mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))))

def touches(pt, t, layname):
    # does pt lie on track t (same layer), within t width/2 + 0.01?
    (x1, y1), (x2, y2) = t[1], t[2]
    dx, dy = x2-x1, y2-y1
    L2 = dx*dx + dy*dy
    u = 0.0 if L2 == 0 else max(0.0, min(1.0, ((pt[0]-x1)*dx + (pt[1]-y1)*dy)/L2))
    return math.hypot(pt[0]-(x1+u*dx), pt[1]-(y1+u*dy))

for (px, py, desc) in targets:
    print('==', desc)
    for (t, s, e) in tracks:
        if (abs(s[0]-px) < 0.01 and abs(s[1]-py) < 0.01) or (abs(e[0]-px) < 0.01 and abs(e[1]-py) < 0.01):
            net = t.GetNetname(); lay = t.GetLayerName()
            print('   track %s %s %s-%s w=%.2f' % (net, lay, tuple(round(v, 2) for v in s), tuple(round(v, 2) for v in e), mm(t.GetWidth())))
            for end, other in ((s, e), (e, s)):
                # count items touching each end
                cnt = 0
                for (t2, s2, e2) in tracks:
                    if t2 is t or t2.GetNetname() != net: continue
                    if touches(end, (t2, s2, e2), lay) <= mm(t2.GetWidth())/2 + mm(t.GetWidth())/2 + 0.01: cnt += 1
                print('     end %s touches %d other items' % (tuple(round(v, 2) for v in end), cnt))
