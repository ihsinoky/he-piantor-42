"""Issue219/PR220 frame method, rederived from Rev5 PCB and new Edge_Cuts."""
from common import *
sys.path.insert(0,str(BASE/'.issue147-runtime/viewer-venv/lib/python3.12/site-packages'))
import sexpdata as sx,csv,io,itertools,warnings
from decimal import Decimal as D
from gerbonara import GerberFile
from gerbonara.graphic_objects import Line
w=E/'manufacturing';root=sx.loads((E/'inspection/final/main.kicad_pcb').read_text())
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def child(n,t):return next(x for x in n if tag(x)==t)
lookup={next(x[2] for x in n if tag(x)=='property' and x[1]=='Reference'):child(n,'at')[1:] for n in root if tag(n)=='footprint'}
rows=list(csv.DictReader((w/'CPL.csv').open()));native={r['Ref']:r for r in csv.DictReader((w/'native-pos-absolute.csv').open())};translations=set()
expected={r['Designator']:(D(str(lookup[r['Designator']][0])),-D(str(lookup[r['Designator']][1]))) for r in rows}
xy=lambda r:(D(r['Mid X'].removesuffix('mm')),D(r['Mid Y'].removesuffix('mm')))
for r in rows:translations.add(tuple(a-b for a,b in zip(expected[r['Designator']],xy(r))))
assert len(translations)==1;dx,dy=translations.pop();out=[];points=[]
for r in rows:
 q=dict(r);x,y=xy(r);q['Mid X']=f'{x+dx:.6f}mm';q['Mid Y']=f'{y+dy:.6f}mm';out.append(q)
 ex=expected[r['Designator']];actual=xy(q);assert actual==ex
 n=native[r['Designator']];assert (D(n['PosX']),D(n['PosY']))==ex and n['Rot']==r['Rotation'] and n['Side']==r['Layer']
 assert {k:r[k] for k in ['Designator','Layer','Rotation']}=={k:q[k] for k in ['Designator','Layer','Rotation']}
 points.append(dict(designator=r['Designator'],pcb_to_gerber_mm=list(map(str,ex)),actual_mm=list(map(str,actual)),error_mm=['0','0'],rotation=q['Rotation']))
for a,b in itertools.combinations(rows,2):assert tuple(x-y for x,y in zip(xy(a),xy(b)))==tuple(x-y for x,y in zip(expected[a['Designator']],expected[b['Designator']] ))
with (w/'CPL-jlcpcb-gerber-frame.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(out)
def seg(a,b):return tuple(sorted([tuple(round(float(x),6) for x in a),tuple(round(float(x),6) for x in b)]))
with warnings.catch_warnings():
 warnings.simplefilter('ignore');edge=GerberFile.open(w/'gerber/main-rev5-Edge_Cuts.gm1')
assert all(isinstance(o,Line) for o in edge.objects)
gedges=[seg((o.x1,o.y1),(o.x2,o.y2)) for o in edge.objects];pedges=[]
for n in root:
 if tag(n)=='gr_line' and child(n,'layer')[1]=='Edge.Cuts':
  a,b=child(n,'start')[1:],child(n,'end')[1:];pedges.append(seg((a[0],-a[1]),(b[0],-b[1])))
assert sorted(gedges)==sorted(pedges);pts=[p for line in gedges for p in line];bounds=[min(p[i] for p in pts) for i in [0,1]]+[max(p[i] for p in pts) for i in [0,1]]
save(E/'cpl-frame-check.json',dict(pass_check=True,source_sha256=digest(w/'CPL.csv'),output_sha256=digest(w/'CPL-jlcpcb-gerber-frame.csv'),board_sha256=digest(E/'inspection/final/main.kicad_pcb'),gerber_edge_sha256=digest(w/'gerber/main-rev5-Edge_Cuts.gm1'),translation_mm=list(map(str,[dx,dy])),gerber_centerline_bounds_mm=bounds,pcb_gerber_edges_exact=True,edge_segments=len(gedges),rows=len(out),native_secondary_export_matches=len(out),pairwise_vectors_checked=len(rows)*(len(rows)-1)//2,max_axis_error_mm='0',tolerance_mm='0.000001',designators_layers_rotations_order_preserved=True,points=points))
print('Gerber frame CPL PASS',len(rows),'rows,',len(rows)*(len(rows)-1)//2,'pairs')
