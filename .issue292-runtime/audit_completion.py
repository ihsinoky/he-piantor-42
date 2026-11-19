"""Completion-round corrected audit: prev (2f0b4526) vs final tree board.
Proper rotated-rect geometry (rect_poly convention). Outputs JSON."""
import pcbnew as p, math, json
from pathlib import Path
from shapely.geometry import Polygon, LineString, Point
from shapely.strtree import STRtree
E = Path('.').resolve()
TREE = E.parent/'hardware/kicad/qualification/issue-292-wmain'
prev = p.LoadBoard(str(E/'board-prev.kicad_pcb'))
fin = p.LoadBoard(str(TREE/'wmain.kicad_pcb'))
rev = p.LoadBoard(str(E.parent/'hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb'))
FIELD = (69.3, 119.05, 80.9, 128.9)
def mm(v): return p.ToMM(v)
def rect_poly(cx, cy, w, h, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return Polygon([(cx + dx * c - dy * s, cy + dx * s + dy * c)
                    for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])
def edges(bb):
    out = set()
    for d in bb.GetDrawings():
        if d.GetLayer() == p.Edge_Cuts:
            s, e = d.GetStart(), d.GetEnd()
            a = (round(mm(s.x), 3), round(mm(s.y), 3)); bq = (round(mm(e.x), 3), round(mm(e.y), 3))
            out.add(tuple(sorted([a, bq])))
    return out
R = {}
ep, ef, er = edges(prev), edges(fin), edges(rev)
R['outline'] = {'prev_eq_final': ep == ef, 'final_eq_rev10': ef == er,
                'only_in_final_vs_rev10': sorted(ef - er), 'only_in_rev10': sorted(er - ef)}
def pads_of(bb):
    out = []
    for f in bb.GetFootprints():
        for pad in f.Pads():
            pos, sz = pad.GetPosition(), pad.GetSize()
            out.append({'ref': f"{f.GetReference()}.{pad.GetNumber()}", 'net': pad.GetNetname(),
                        'poly': rect_poly(mm(pos.x), mm(pos.y), mm(sz.x), mm(sz.y), pad.GetOrientationDegrees()),
                        'x': mm(pos.x), 'y': mm(pos.y)})
    return out
def via_pad(bb):
    pads = pads_of(bb)
    res = []
    for t in bb.GetTracks():
        if not isinstance(t, p.PCB_VIA): continue
        pos = t.GetPosition(); vx, vy = mm(pos.x), mm(pos.y)
        disc = Point(vx, vy).buffer(mm(t.GetWidth(p.F_Cu)) / 2, resolution=12)
        vn = t.GetNetname()
        for pd in pads:
            if pd['net'] == vn: continue
            d = disc.distance(pd['poly'])
            if d < 0.125:
                res.append((round(d, 4), f"via {vn} @({vx:.2f},{vy:.2f})", pd['ref'], pd['net'],
                            FIELD[0] <= vx <= FIELD[2] and FIELD[1] <= vy <= FIELD[3]))
    return sorted(res)
vp_prev, vp_fin = via_pad(prev), via_pad(fin)
def summ(vp):
    out_f = [r for r in vp if not r[4]]; in_f = [r for r in vp if r[4]]
    return {'outside_min': out_f[0][0] if out_f else None, 'outside_sub125': out_f,
            'inside_min': in_f[0][0] if in_f else None, 'inside_sub125_count': len(in_f)}
R['via_pad_prev'] = summ(vp_prev)
R['via_pad_final'] = summ(vp_fin)
R['via_pad_new_in_final'] = [r for r in vp_fin if r not in vp_prev]
# trackpad: pads whose rect intersects circle r20 @(100,118)
circ = Point(100, 118).buffer(20, resolution=64)
def tp(bb):
    return sorted(pd['ref'] for pd in pads_of(bb) if pd['poly'].intersects(circ))
R['trackpad_pads_in_circle'] = {'prev': tp(prev), 'final': tp(fin)}
# wing census equality
def census(bb):
    out = {}
    for ref in ('J2', 'J3'):
        f = [x for x in bb.GetFootprints() if str(x.GetReference()) == ref][0]
        out[ref] = {str(pad.GetNumber()): pad.GetNetname() for pad in f.Pads()}
    return out
R['wing_census_equal'] = census(prev) == census(fin)
# HALL_3V3 copper keyset equality prev vs final
def keyset(bb, net):
    ks = set()
    for t in bb.GetTracks():
        if t.GetNetname() != net: continue
        if isinstance(t, p.PCB_VIA):
            pos = t.GetPosition(); ks.add(('v', round(mm(pos.x), 3), round(mm(pos.y), 3)))
        else:
            s, e = t.GetStart(), t.GetEnd()
            ks.add(('t', t.GetLayer(), round(mm(s.x), 3), round(mm(s.y), 3), round(mm(e.x), 3), round(mm(e.y), 3), round(mm(t.GetWidth()), 3)))
    return ks
R['hall_3v3_identical_prev_final'] = keyset(prev, 'HALL_3V3') == keyset(fin, 'HALL_3V3')
# per-net track/via counts prev vs final for the 5 closed nets
for net in ('GND', 'VBUS', 'SYS_3V3', 'PAD_EN', 'VBAT_SENSE'):
    def cnt(bb):
        tr = sum(1 for t in bb.GetTracks() if t.GetNetname() == net and not isinstance(t, p.PCB_VIA))
        vi = sum(1 for t in bb.GetTracks() if t.GetNetname() == net and isinstance(t, p.PCB_VIA))
        return (tr, vi)
    R[f'count_{net}'] = {'prev': cnt(prev), 'final': cnt(fin)}
(E/'audit-completion.json').write_text(json.dumps(R, indent=1, default=str))
print(json.dumps(R, indent=1, default=str)[:3000])
