#!/usr/bin/env python3
"""Independent KiCad read of the unchanged starting PCB; never SaveBoard."""
from pathlib import Path
import hashlib
import json
import pcbnew as p

E = Path(__file__).resolve().parent
R = E.parents[3]
pcb = R / 'hardware/kicad/qualification/issue-155-main-mounting-stage2/inspection/final/main.kicad_pcb'
before = hashlib.sha256(pcb.read_bytes()).hexdigest()
assert before == 'fdc1a7748f94714e395eb50f3e08c43afa24192ee76eb3d1804a8cba28690222'
b = p.LoadBoard(str(pcb))
fps = {f.GetReference(): f for f in b.GetFootprints()}
assert len(fps) == 53 and 'J3' not in fps
assert sum(len(list(f.Pads())) for f in fps.values()) == 203
positions = {'J1': [85,81], 'J2': [110,116], 'H1': [79,92], 'H2': [121,81], 'H3': [79,119], 'H4': [102,111.5]}
for ref, xy in positions.items():
    v = fps[ref].GetPosition()
    assert [p.ToMM(v.x), p.ToMM(v.y)] == xy
u18 = next(x for x in fps['U1'].Pads() if x.GetNumber() == '8')
assert not u18.GetNetname()
assert b.GetCopperLayerCount() == 4
assert abs(p.ToMM(b.GetDesignSettings().GetBoardThickness())-1.2) < 1e-9
assert hashlib.sha256(pcb.read_bytes()).hexdigest() == before
result = dict(kicad=p.GetBuildVersion(), PCB_sha256=before,
    footprints=53, pads=203, layers=4, thickness_mm=1.2,
    positions=positions, J3_present=False, U1_8_net=str(u18.GetNetname()),
    scope='Starting PCB identity only; not qualification of a new revision',
    power_devices={r:dict(value=str(fps[r].GetValue()),
        pad_nets={str(x.GetNumber()):str(x.GetNetname()) for x in fps[r].Pads()})
        for r in ['J1','U4','U5','R1','R2','R6','R7']},
    board_unchanged=True)
(E/'native-readback.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
