"""J3.8 MUX_EN1: pad environment + the net's copper endpoints."""
import pcbnew as p
from verify import xy

E = '/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation'
b = p.LoadBoard(f'{E}/main-rev8/routed.kicad_pcb')
LN = {p.F_Cu: 'F', p.In1_Cu: 'In1', p.In2_Cu: 'In2', p.B_Cu: 'B'}
print('--- MUX_EN1 pads')
for f in b.GetFootprints():
    for a in f.Pads():
        if a.GetNetname() == 'MUX_EN1':
            print(f"  {f.GetReference()}.{a.GetNumber()} at {[round(v, 2) for v in xy(a.GetPosition())]} layers {[LN[l] for l in LN if a.IsOnLayer(l)]}")
print('--- MUX_EN1 tracks/vias')
for t in b.GetTracks():
    if t.GetNetname() == 'MUX_EN1':
        if isinstance(t, p.PCB_VIA):
            print('  VIA', [round(v, 2) for v in xy(t.GetPosition())])
        else:
            print('  TRK', LN[t.GetLayer()], [round(v, 2) for v in xy(t.GetStart())], '->', [round(v, 2) for v in xy(t.GetEnd())])
print('--- J3 pads (all)')
for f in b.GetFootprints():
    if f.GetReference() == 'J3':
        for a in f.Pads():
            print(f"  J3.{a.GetNumber()} {a.GetNetname()} at {[round(v, 3) for v in xy(a.GetPosition())]}")
