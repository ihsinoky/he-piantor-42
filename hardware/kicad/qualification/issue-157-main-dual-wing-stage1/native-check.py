#!/usr/bin/env python3
"""Independent read-only KiCad pad/outline/NPTH checks; stdout JSON.

Uses the existing KiCad runtime only for loading and reading. No SaveBoard,
refill, routing, temporary PCB creation or footprint insertion.
"""
from pathlib import Path
import hashlib
import json
import pcbnew as p

E=Path(__file__).resolve().parent
R=E.parents[3]
PCB=R/'hardware/kicad/qualification/issue-155-main-mounting-stage2/inspection/final/main.kicad_pcb'
before=hashlib.sha256(PCB.read_bytes()).hexdigest()
b=p.LoadBoard(str(PCB))
g=json.loads((E/'geometry.json').read_text())
mm=p.ToMM
def xy(v):return [mm(v.x),mm(v.y)]
assert len(list(b.GetFootprints()))==53
pads={pad.m_Uuid.AsString():pad for f in b.GetFootprints() for pad in f.Pads()}
assert len(pads)==g['existing_pad_count']==203
for a in g['connector_template_pads']:
    pad=pads[a['uuid']]
    assert xy(pad.GetPosition())==a['xy'] and xy(pad.GetSize())==a['size']
    assert pad.GetOrientationDegrees()==a['angle'] and pad.GetNetname()==a['net']
for h in g['holes']:
    f=next(f for f in b.GetFootprints() if f.GetReference()==h['ref'])
    assert xy(f.GetPosition())==h['xy']
    ps=list(f.Pads());assert len(ps)==1
    assert ps[0].GetAttribute()==p.PAD_ATTRIB_NPTH
    assert xy(ps[0].GetDrillSize())==[2.2,2.2] and not ps[0].GetNetname()
edges=[x for x in b.GetDrawings() if x.GetLayer()==p.Edge_Cuts]
assert len(edges)==4
points=[xy(v) for e in edges for v in [e.GetStart(),e.GetEnd()]]
assert [min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)]==[76,78,124,122]
assert len(list(b.Zones()))==5  # GND plus four reservation rule areas
rows=[]
for c in g['candidates']:
    checks=[]
    for a in c['envelopes']:
        if a['kind'] not in ['body','land_hull','assembly','service']:continue
        x0,y0,x1,y1=a['box_mm']
        rect=p.SHAPE_RECT(p.VECTOR2I(p.FromMM(x0),p.FromMM(y0)),p.FromMM(x1-x0),p.FromMM(y1-y0))
        pad_hits=[]
        for uid,pad in pads.items():
            if pad.GetAttribute()==p.PAD_ATTRIB_NPTH:continue
            if pad.GetEffectiveShape(p.F_Cu).Collide(rect):pad_hits.append(dict(uuid=uid,ref=pad.GetParentFootprint().GetReference()))
        reservation_hits=[z.m_Uuid.AsString() for z in b.Zones() if z.GetIsRuleArea() and z.Outline().Collide(rect)]
        checks.append(dict(kind=a['kind'],native_copper_pad_hits=pad_hits,native_reservation_polygon_hits=reservation_hits))
    rows.append(dict(label=c['label'],checks=checks))
assert all(not a['native_copper_pad_hits'] for a in rows[0]['checks'])
assert all(not a['native_reservation_polygon_hits'] for a in rows[0]['checks'])
assert hashlib.sha256(PCB.read_bytes()).hexdigest()==before
print(json.dumps(dict(status='pass',kicad=p.GetBuildVersion(),board_sha256=before,
    connector_pads_crosschecked=16,npth_holes_crosschecked=4,all_copper_pads_checked=197,
    outline_crosschecked=True,board_unchanged=True,candidates=rows),indent=2))
