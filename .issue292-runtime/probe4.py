import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
po = p.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(po)
ch = po.Outline(0)
print('chain methods:', [m for m in dir(ch) if not m.startswith('_')])
print('ArcCount:', ch.GetArcCount() if hasattr(ch,'GetArcCount') else 'n/a', 'IsClosed:', ch.IsClosed())
t = [x for x in b.GetTracks() if type(x).__name__=='PCB_TRACK'][0]
s = t.GetEffectiveShape(p.F_Cu)
print('shape Type():', s.Type(), 'SH_SEGMENT=', p.SH_SEGMENT if hasattr(p,'SH_SEGMENT') else '?')
try:
    seg = p.SHAPE_SEGMENT.Cast(s); print('cast seg ok:', seg.GetSeg(), seg.GetWidth())
except Exception as e: print('cast err:', e)
v = [x for x in b.GetTracks() if type(x).__name__=='PCB_VIA'][0]
sv = v.GetEffectiveShape(p.In1_Cu)
print('via eff Type():', sv.Type(), 'SH_CIRCLE=', getattr(p,'SH_CIRCLE','?'))
try:
    c = p.SHAPE_CIRCLE.Cast(sv); print('cast circle ok:', c.GetCenter(), c.GetRadius())
except Exception as e: print('cast err:', e)
# pad shape variety
from collections import Counter
kinds = Counter()
for f in b.GetFootprints():
    for pad in f.Pads():
        kinds[(pad.GetShape(), pad.GetAttribute())] += 1
print('pad shapes (shape,attr):', dict(kinds))
print('PAD_SHAPE enum:', [(n,getattr(p,n)) for n in ('PAD_SHAPE_RECT','PAD_SHAPE_OVAL','PAD_SHAPE_CIRCLE','PAD_SHAPE_ROUNDRECT','PAD_SHAPE_TRAPEZOID','PAD_SHAPE_CUSTOM','PAD_SHAPE_CHAMFERED_RECT') if hasattr(p,n)])
