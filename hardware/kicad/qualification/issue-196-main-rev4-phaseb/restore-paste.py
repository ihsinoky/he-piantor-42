"""Transfer every retained native stencil graphic with its owning pad's rigid pose.
Rectangles become polygons so the +/-120 degree GH orientation is exact.
"""
from common import *
import pcbnew as p,importlib.util,math
from shapely.geometry import Point
spec=importlib.util.spec_from_file_location('audit',E/'audit-vias.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
old=p.LoadBoard(str(E.parent/'issue-185-main-rev3/inspection/final/main.kicad_pcb'));new=p.LoadBoard(str(E/'inspection/power01/main.kicad_pcb'));fps={f.GetReference():f for f in new.GetFootprints()};oldfps={f.GetReference():f for f in old.GetFootprints()};rows=[];oldhash=digest(E/'inspection/power01/main.kicad_pcb')
pads=[(f.GetReference(),pad,a.pad_polygon(pad,p.F_Cu)) for f in old.GetFootprints() for pad in f.Pads() if pad.GetAttribute()!=p.PAD_ATTRIB_NPTH]
for g in old.GetDrawings():
 if g.GetLayer() not in [p.F_Paste,p.B_Paste]:continue
 start,end=a.xy(g.GetStart()),a.xy(g.GetEnd());center=start if g.GetShape()==p.S_CIRCLE else [(x+y)/2 for x,y in zip(start,end)]
 ranked=sorted([(Point(center).distance(poly),math.dist(center,a.xy(pad.GetPosition())),ref,pad.GetNumber()) for ref,pad,poly in pads]);distance,_,ref,pin=ranked[0];assert distance<1e-6,(ref,distance)
 if ref not in fps:rows.append(dict(source_uuid=g.m_Uuid.AsString(),owner_ref=ref,removed=True));continue
 of,nf=oldfps[ref],fps[ref];ox,oy=a.xy(of.GetPosition());nx,ny=a.xy(nf.GetPosition());theta=math.radians(-(nf.GetOrientationDegrees()-of.GetOrientationDegrees()))
 def transform(pt):
  x,y=pt[0]-ox,pt[1]-oy;return [nx+x*math.cos(theta)-y*math.sin(theta),ny+x*math.sin(theta)+y*math.cos(theta)]
 q=p.PCB_SHAPE();q.SetLayer(g.GetLayer());q.SetWidth(g.GetWidth());q.SetFilled(g.IsFilled())
 if g.GetShape()==p.S_RECT:
  x1,y1=start;x2,y2=end;points=[transform(pt) for pt in [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]];poly=p.SHAPE_POLY_SET();poly.NewOutline()
  for x,y in points:poly.Append(p.FromMM(x),p.FromMM(y))
  q.SetShape(p.S_POLYGON);q.SetPolyShape(poly)
 elif g.GetShape()==p.S_CIRCLE:q.SetShape(p.S_CIRCLE);q.SetStart(a.point(transform(start)));q.SetEnd(a.point(transform(end)))
 else:raise AssertionError(('retained unhandled paste',ref,g.GetShape()))
 new.Add(q);rows.append(dict(source_uuid=g.m_Uuid.AsString(),owner_ref=ref,owner_pin=pin,new_uuid=q.m_Uuid.AsString(),removed=False))
w=E/'runs/paste01';w.mkdir(parents=True,exist_ok=True);p.SaveBoard(str(w/'out.kicad_pcb'),new)
base=p.LoadBoard(str(E/'inputs/final/main.kicad_pcb'))
for q in new.GetDrawings():
 if q.GetLayer() in [p.F_Paste,p.B_Paste]:
  du=q.Duplicate();base.Add(du)
p.SaveBoard(str(w/'reference-with-paste.kicad_pcb'),base)
# Duplicate creates different UUIDs: copy the exact saved paste AST nodes into
# the input, avoiding any geometry-based normalization in the transfer checker.
import sexpdata as sx
ast=sx.loads((E/'inputs/final/main.kicad_pcb').read_text());out=sx.loads((w/'out.kicad_pcb').read_text())
def ispaste(n):return isinstance(n,list) and n and str(n[0]).startswith('gr_') and any(isinstance(c,list) and c and str(c[0])=='layer' and str(c[1]) in ['F.Paste','B.Paste'] for c in n)
ast.extend(n for n in out if ispaste(n));(E/'inputs/final/main.kicad_pcb').write_text(sx.dumps(ast))
save(E/'paste-transfer.json',dict(source_board_sha256=digest(E.parent/'issue-185-main-rev3/inspection/final/main.kicad_pcb'),copper_source_sha256=oldhash,output_sha256=digest(w/'out.kicad_pcb'),rows=rows,retained_graphics=sum(not r['removed'] for r in rows),rule='nearest containing source pad; rigid footprint translation/rotation; native rectangles converted to polygon; removed J1/R1/R2/U2 paste excluded'))
print('Retained paste graphics',sum(not r['removed'] for r in rows),'removed',sum(r['removed'] for r in rows))
