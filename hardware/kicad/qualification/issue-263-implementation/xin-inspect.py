"""Local geometry for XIN/XOUT repair: U1/Y1 pads + nearby copper, all layers."""
import pcbnew as p
from verify import xy

E = '/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation'
b = p.LoadBoard(f'{E}/main-rev8/routed.kicad_pcb')
LN = {p.F_Cu: 'F', p.In1_Cu: 'In1', p.In2_Cu: 'In2', p.B_Cu: 'B'}
for f in b.GetFootprints():
    if f.GetReference() in ('U1', 'Y1'):
        print(f.GetReference(), 'at', [round(v, 2) for v in xy(f.GetPosition())], 'rot', f.GetOrientationDegrees())
        for a in f.Pads():
            if a.GetNetname() in ('XIN', 'XOUT') or f.GetReference() == 'Y1':
                layers = [LN[l] for l in LN if a.IsOnLayer(l)]
                print(f"  {f.GetReference()}.{a.GetNumber()} {a.GetNetname()} at {[round(v, 3) for v in xy(a.GetPosition())]} layers {layers} size {[round(p.ToMM(a.GetSize().x), 2), round(p.ToMM(a.GetSize().y), 2)]}")
# all XIN/XOUT copper
for t in b.GetTracks():
    if t.GetNetname() in ('XIN', 'XOUT'):
        if isinstance(t, p.PCB_VIA):
            print('VIA', t.GetNetname(), [round(v, 2) for v in xy(t.GetPosition())])
        else:
            print('TRK', t.GetNetname(), LN[t.GetLayer()], [round(v, 2) for v in xy(t.GetStart())], '->', [round(v, 2) for v in xy(t.GetEnd())], 'w', p.ToMM(t.GetWidth()))
