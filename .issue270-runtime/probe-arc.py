import pcbnew as p
s = p.PCB_SHAPE()
print([m for m in dir(s) if 'Arc' in m or m in ('SetShape','SetStart','SetEnd','SetMid')])
print("SHAPE_T_ARC =", p.SHAPE_T_ARC)
