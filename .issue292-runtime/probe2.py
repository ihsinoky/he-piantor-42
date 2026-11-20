import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
po = p.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(po)
print('outlines polys:', po.OutlineCount())
ch = po.CPolygon(0)
print('chain pts:', ch.PointCount(), 'holes:', po.HoleCount(0))
t = [x for x in b.GetTracks() if type(x).__name__=='PCB_TRACK'][0]
s = t.GetEffectiveShape(p.F_Cu)
print('track shape class:', s.GetClass(), [m for m in dir(s) if not m.startswith('_')][:40])
v = [x for x in b.GetTracks() if type(x).__name__=='PCB_VIA'][0]
sv = v.GetEffectiveShape(p.F_Cu)
print('via shape class:', sv.GetClass())
fp = b.GetFootprints()[0]
pad = list(fp.Pads())[0]
sp = pad.GetEffectiveShape(p.F_Cu)
print('pad shape class:', sp.GetClass())
print('SHAPE_POLY_SET methods:', [m for m in dir(po) if 'oly' in m or 'utline' in m or 'ole' in m])
print('chain methods:', [m for m in dir(ch) if 'oint' in m])
print('has Distance on shape:', hasattr(s,'Distance'), 'Collide:', hasattr(s,'Collide'))
