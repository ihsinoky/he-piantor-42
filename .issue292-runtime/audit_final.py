"""Final gate audits on wmain-v25-final (tree copy), from placed data."""
import pcbnew as p, math, json
from pathlib import Path
E = Path('.').resolve()
b = p.LoadBoard(str(E/'wmain-v27-final.kicad_pcb'))
LAY = {p.F_Cu: 'F', p.In1_Cu: 'I1', p.In2_Cu: 'I2', p.B_Cu: 'B'}
R = {}

# --- outline delta vs Rev.10 ---
rev = p.LoadBoard(str(E/'../hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb'))
def edges(bb):
    out = set()
    for d in bb.GetDrawings():
        if d.GetLayer() == p.Edge_Cuts:
            s, e = d.GetStart(), d.GetEnd()
            out.add((round(p.ToMM(s.x), 3), round(p.ToMM(s.y), 3), round(p.ToMM(e.x), 3), round(p.ToMM(e.y), 3)))
    return out
em, er = edges(b), edges(rev)
R['outline'] = {'mine_segments': len(em), 'rev10_segments': len(er), 'identical': em == er}

# --- via-pad different-net audit ---
pads = []
for f in b.GetFootprints():
    for pad in f.Pads():
        pos = pad.GetPosition(); sz = pad.GetSize()
        pads.append({'ref': f"{f.GetReference()}.{pad.GetNumber()}", 'net': pad.GetNetname(),
                     'x': p.ToMM(pos.x), 'y': p.ToMM(pos.y),
                     'sx': p.ToMM(sz.x), 'sy': p.ToMM(sz.y), 'rot': pad.GetOrientationDegrees(),
                     'layers': [L for L, nm in ((p.F_Cu, 'F'), (p.B_Cu, 'B')) if pad.IsOnLayer(L)]})
def pad_rect_dist(px, py, pd):
    c, s = math.cos(math.radians(-pd['rot'])), math.sin(math.radians(-pd['rot']))
    dx, dy = px - pd['x'], py - pd['y']
    lx, ly = dx * c - dy * s, dx * s + dy * c
    ex = max(abs(lx) - pd['sx'] / 2, 0.0); ey = max(abs(ly) - pd['sy'] / 2, 0.0)
    return math.hypot(ex, ey)
worst = []
for t in b.GetTracks():
    if not isinstance(t, p.PCB_VIA):
        continue
    pos = t.GetPosition(); vx, vy = p.ToMM(pos.x), p.ToMM(pos.y)
    vr = p.ToMM(t.GetWidth(p.F_Cu)) / 2
    vn = t.GetNetname()
    for pd in pads:
        if pd['net'] == vn:
            continue
        d = pad_rect_dist(vx, vy, pd) - vr
        worst.append((round(d, 4), f"via {vn} @({vx:.2f},{vy:.2f})", pd['ref'], pd['net']))
worst.sort()
R['via_pad'] = {'min': worst[0][0], 'sub_0.125': [w for w in worst if w[0] < 0.125][:14]}

# --- keep-out audits ---
def seg_pts(t):
    s, e = t.GetStart(), t.GetEnd()
    return (p.ToMM(s.x), p.ToMM(s.y)), (p.ToMM(e.x), p.ToMM(e.y))
def seg_circle(t, cx, cy, r):
    (x1, y1), (x2, y2) = seg_pts(t)
    # min distance from centre to segment
    dx, dy = x2 - x1, y2 - y1
    tt = max(0.0, min(1.0, ((cx - x1) * dx + (cy - y1) * dy) / (dx * dx + dy * dy))) if (dx or dy) else 0.0
    return math.hypot(cx - (x1 + tt * dx), cy - (y1 + tt * dy)) < r
tp_tracks = [t for t in b.GetTracks() if not isinstance(t, p.PCB_VIA) and seg_circle(t, 100, 118, 20)]
tp_vias = [t for t in b.GetTracks() if isinstance(t, p.PCB_VIA) and math.hypot(p.ToMM(t.GetPosition().x) - 100, p.ToMM(t.GetPosition().y) - 118) < 20]
R['trackpad_keepout'] = {'tracks_in_circle': len(tp_tracks), 'vias_in_circle': len(tp_vias)}
ANT = (70.3, 79.9, 128.9, 137.9)
def in_ant(x, y): return ANT[0] <= x <= ANT[1] and ANT[2] <= y <= ANT[3]
ant_items = []
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        pos = t.GetPosition()
        if in_ant(p.ToMM(pos.x), p.ToMM(pos.y)):
            ant_items.append(('via', t.GetNetname()))
    else:
        (x1, y1), (x2, y2) = seg_pts(t)
        if in_ant(x1, y1) or in_ant(x2, y2):
            ant_items.append(('track', t.GetNetname()))
R['antenna_keepout'] = {'items_in_strip': ant_items}

# --- Wing census from board ---
cen = {}
for ref in ('J2', 'J3'):
    f = [x for x in b.GetFootprints() if str(x.GetReference()) == ref][0]
    cen[ref] = {pad.GetNumber(): pad.GetNetname() for pad in f.Pads()}
R['wing_census'] = cen

# --- module GND pads connected count (from DRC-known set: total GND pads on U1) ---
u1 = [x for x in b.GetFootprints() if str(x.GetReference()) == 'U1'][0]
R['module_gnd_pads'] = sorted(pad.GetNumber() for pad in u1.Pads() if pad.GetNetname() == 'GND')

# --- HALL_3V3 on-board copper length per connector stub (crude budget input) ---
tot = 0.0
for t in b.GetTracks():
    if not isinstance(t, p.PCB_VIA) and t.GetNetname() == 'HALL_3V3':
        (x1, y1), (x2, y2) = seg_pts(t)
        tot += math.hypot(x2 - x1, y2 - y1)
R['hall_3v3_track_total_mm'] = round(tot, 1)

# --- track_dangling identification comes from drc-v25.json ---
d = json.loads((E/'drc-v25.json').read_text())
R['dangling'] = [v['items'] for v in d['violations'] if v['type'] == 'track_dangling']
ec = [v for v in d['violations'] if v['type'] == 'copper_edge_clearance']
from collections import Counter
R['edge_clearance_items'] = Counter()
for v in ec:
    for i in v['items']:
        R['edge_clearance_items'][i.get('description', '')[:40]] += 1
R['edge_clearance_items'] = dict(R['edge_clearance_items'].most_common(8))
(E/'audit-final.json').write_text(json.dumps(R, indent=1, default=str))
print(json.dumps({k: (v if not isinstance(v, dict) else list(v)[:4]) for k, v in R.items()}, indent=1, default=str)[:1500])
