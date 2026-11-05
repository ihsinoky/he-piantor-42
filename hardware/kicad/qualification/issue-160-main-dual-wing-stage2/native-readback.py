#!/usr/bin/env python3
"""Read the unmodified #155 board using KiCad; never save it."""
from pathlib import Path
import hashlib
import json
import pcbnew as p
E=Path(__file__).resolve().parent
R=E.parents[3]
PCB=R/'hardware/kicad/qualification/issue-155-main-mounting-stage2/inspection/final/main.kicad_pcb'
before=hashlib.sha256(PCB.read_bytes()).hexdigest()
b=p.LoadBoard(str(PCB))
fps={f.GetReference():f for f in b.GetFootprints()}
assert len(fps)==53 and 'J3' not in fps
assert sum(len(list(f.Pads())) for f in fps.values())==203
def xy(v):return [p.ToMM(v.x),p.ToMM(v.y)]
for ref,pos in {'J1':[85,81],'J2':[110,116],'H1':[79,92],'H2':[121,81],'H3':[79,119],'H4':[102,111.5]}.items():
    assert xy(fps[ref].GetPosition())==pos
    if ref.startswith('H'):
        pad=list(fps[ref].Pads())[0]
        assert pad.GetAttribute()==p.PAD_ATTRIB_NPTH and xy(pad.GetDrillSize())==[2.2,2.2]
        assert not pad.GetNetname()
u18=next(pad for pad in fps['U1'].Pads() if pad.GetNumber()=='8')
assert not u18.GetNetname()
boxes=[pad.GetEffectiveShape(p.F_Cu).BBox() for pad in fps['R2'].Pads()]
bounds=[min(x.GetX() for x in boxes),min(x.GetY() for x in boxes),max(x.GetRight() for x in boxes),max(x.GetBottom() for x in boxes)]
bounds=[p.ToMM(v) for v in bounds]
g=json.loads((E/'mechanical-gate.json').read_text())
assert all(abs(a-c)<2e-6 for a,c in zip(bounds,g['actual_R2_pad_hull_mm']))
assert hashlib.sha256(PCB.read_bytes()).hexdigest()==before
print(json.dumps({'status':'pass','kicad':p.GetBuildVersion(),'board_sha256':before,
 'footprints':len(fps),'pads':203,'R2_native_pad_hull_mm':bounds,
 'J3_present':False,'U1_8_unconnected':True,'board_unchanged':True,
 'scope':'Original board identity and geometry crosscheck only, not new-board qualification'},indent=2))
