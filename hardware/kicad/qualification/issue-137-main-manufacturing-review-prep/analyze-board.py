"""Read-only KiCad 9 geometry check of #121's 25 logged observations.

Run at repo root, with pcbnew on PYTHONPATH. Output is JSON on stdout.
No routing, refill, save, project update, or manufacture-file modification.
"""
import collections
import hashlib
import json
from pathlib import Path
import pcbnew

BASE = Path('hardware/kicad/qualification/issue-121-full-auto-conditions/evidence/inspection/main-cell1/krt')
PCB = BASE/'main.kicad_pcb'
LOG = BASE/'router-structured-log.json'
board = pcbnew.LoadBoard(str(PCB))
log = json.loads(LOG.read_text())['VIA_IN_PAD_JSON'][0]
vias = [t for t in board.GetTracks() if isinstance(t, pcbnew.PCB_VIA)]
pads = [(f.GetReference(), p) for f in board.GetFootprints() for p in f.Pads()]
graphics = [d for d in board.GetDrawings() if d.GetLayer() == pcbnew.F_Paste]

def mm(n): return round(pcbnew.ToMM(n), 6)
def xy(v): return [mm(v.x), mm(v.y)]
def uid(item): return item.m_Uuid.AsString()
def pad_record(ref, p):
    return dict(ref=ref, pad=p.GetNumber(), uuid=uid(p), position_mm=xy(p.GetPosition()),
                size_mm=xy(p.GetSize()), orientation_deg=p.GetOrientationDegrees(),
                net=p.GetNetname(), attribute=int(p.GetAttribute()), shape=int(p.GetShape()))

def inspect(v):
    position=v.GetPosition()
    copper=v.GetEffectiveShape(pcbnew.F_Cu)
    hole=pcbnew.SHAPE_CIRCLE(position, v.GetDrillValue()//2)
    copper_hits=[]; graphic_hits=[]
    for ref, p in pads:
        if not p.IsOnLayer(pcbnew.F_Cu) or p.GetAttribute()==pcbnew.PAD_ATTRIB_NPTH: continue
        shape=p.GetEffectiveShape(pcbnew.F_Cu)
        if shape.Collide(copper):
            item=pad_record(ref,p)
            item.update(via_center_in_pad=shape.Collide(position), drill_overlaps_pad=shape.Collide(hole),
                        same_net=p.GetNetname()==v.GetNetname())
            copper_hits.append(item)
    for d in graphics:
        shape=d.GetEffectiveShape(pcbnew.F_Paste)
        if shape.Collide(copper):
            center=d.GetCenter()
            owners=[pad_record(ref,p) for ref,p in pads if (p.GetPosition()-center).EuclideanNorm() <= 2]
            graphic_hits.append(dict(uuid=uid(d),shape=int(d.GetShape()),start_mm=xy(d.GetStart()),
                end_mm=xy(d.GetEnd()),center_mm=xy(center),
                via_center_in_graphic=shape.Collide(position), drill_overlaps_graphic=shape.Collide(hole),
                owner_by_center_match_2nm=owners))
    return dict(position_mm=xy(position), net=v.GetNetname(), uuid=uid(v),
        diameter_mm=mm(v.GetWidth(pcbnew.F_Cu)), drill_mm=mm(v.GetDrillValue()),
        copper_pad_hits=copper_hits, paste_graphic_hits=graphic_hits)

all_vias=[inspect(v) for v in vias]
rows=[]
for index, site in enumerate(log['unprotected'], 1):
    matches=[r for r in all_vias if r['position_mm']==[site['x'],site['y']]]
    assert len(matches)==1, (site, len(matches))
    row=dict(log_index=index, log_site=site['site'], **matches[0])
    row['classification']='copper-pad-overlap' if row['copper_pad_hits'] else 'paste-graphic-only'
    rows.append(row)
assert len(rows)==log['count']==25
assert len({r['uuid'] for r in rows})==25
j1=next(f for f in board.GetFootprints() if f.GetReference()=='J1')
j1pads=[dict(**pad_record('J1',p),drill_mm=xy(p.GetDrillSize()),
             front_copper=p.IsOnLayer(pcbnew.F_Cu),back_copper=p.IsOnLayer(pcbnew.B_Cu),
             front_paste=p.IsOnLayer(pcbnew.F_Paste)) for p in j1.Pads()]
for p in j1pads:
    p['board_paste_graphics']=[dict(uuid=uid(d), shape=int(d.GetShape()), stroke_width_mm=mm(d.GetWidth()), start_mm=xy(d.GetStart()), end_mm=xy(d.GetEnd()))
        for d in graphics if xy(d.GetCenter())==p['position_mm']]
result=dict(kicad=pcbnew.GetBuildVersion(), units='mm; absolute board XY, unmirrored top view',
    inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (PCB,LOG)},
    method='KiCad native effective copper/paste shapes Collide at 0 clearance; solid via disk and drill disk separately. No manufacturing tolerances added. Paste graphic owners identified only by center match within 2nm.',
    logged_count=25, board_vias=len(vias), front_paste_graphics=len(graphics),
    classification_counts=dict(collections.Counter(r['classification'] for r in rows)),
    observations=rows,
    all_board_via_collisions=all_vias,
    j1=dict(position_mm=xy(j1.GetPosition()),orientation_deg=j1.GetOrientationDegrees(), pads=j1pads))
print(json.dumps(result, ensure_ascii=False, indent=2))
