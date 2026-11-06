"""Remove one redundant dangling stub; add identical non-copper PCBA artwork to
both the unrouted design input and routed output, then requalify the final pair.
No routing conditions or copper pads are changed.
"""
from common import *
import pcbnew as p,sexpdata as sx,math,uuid,shutil
from shapely.geometry import box,LineString,Point
from shapely.ops import unary_union

spec=json.loads((SOURCE/'definition.json').read_text())
raw=E/'runs/KRT-M1-01/out.kicad_pcb';b=p.LoadBoard(str(raw))
fps={f.GetReference():f for f in b.GetFootprints()}
V=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
xy=lambda v:[p.ToMM(v.x),p.ToMM(v.y)]
inside=box(36,60,164,140).buffer(-.4)
obstacles=unary_union([box(p.ToMM(q.GetBoundingBox().GetX()),p.ToMM(q.GetBoundingBox().GetY()),p.ToMM(q.GetBoundingBox().GetRight()),p.ToMM(q.GetBoundingBox().GetBottom())).buffer(.28) for f in fps.values() for q in f.Pads()])
nodes=[];occupied=[];entries=[]
uid=lambda:str(uuid.uuid4())
def line(a,z,role):
 g=LineString([a,z]).buffer(.075)
 assert inside.covers(g) and not g.intersects(obstacles),(role,a,z)
 nodes.append(f'(gr_line (start {a[0]:.6f} {a[1]:.6f}) (end {z[0]:.6f} {z[1]:.6f}) (stroke (width 0.15) (type default)) (layer "F.SilkS") (uuid "{uid()}"))')
 occupied.append(g.buffer(.2));entries.append(dict(kind='line',role=role,start=a,end=z))
def circle(x,y,r,role):
 g=Point(x,y).buffer(r+.075)
 assert inside.covers(g) and not g.intersects(obstacles),(role,x,y)
 nodes.append(f'(gr_circle (center {x:.6f} {y:.6f}) (end {x+r:.6f} {y:.6f}) (stroke (width 0.15) (type default)) (fill none) (layer "F.SilkS") (uuid "{uid()}"))')
 occupied.append(g.buffer(.2));entries.append(dict(kind='circle',role=role,center=[x,y],radius_mm=r))
def text(s,x,y,role,size=.8,search=True):
 candidates=[(x,y,0)]
 if search:
  for radius in [.5,1,1.5,2,2.5,3,4,5,6,7,8]:
   for a in [0,90]:
    for k in range(24):candidates.append((x+radius*math.cos(k*math.pi/12),y+radius*math.sin(k*math.pi/12),a))
 other=unary_union(occupied)
 for cx,cy,a in candidates:
  o=p.PCB_TEXT(b);o.SetText(s);o.SetTextSize(V(size,size));o.SetTextThickness(p.FromMM(.12));o.SetPosition(V(cx,cy));o.SetTextAngle(p.EDA_ANGLE(a,p.DEGREES_T));o.SetLayer(p.F_SilkS)
  bb=o.GetBoundingBox();g=box(p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())).buffer(.12)
  if inside.covers(g) and not g.intersects(obstacles) and not g.intersects(other):break
 else:raise ValueError(('no label position',s))
 nodes.append(f'(gr_text {json.dumps(s)} (at {cx:.6f} {cy:.6f} {a}) (layer "F.SilkS") (uuid "{uid()}") (effects (font (size {size} {size}) (thickness 0.12))))')
 occupied.append(g.buffer(.18));entries.append(dict(kind='text',role=role,text=s,at=[cx,cy],angle_deg=a,size_mm=size))
# Key cells express nominal pitch; they do not assume PCB-mounted switches.
segments=[]
for s in spec['sensor_sites']:
 x,y=xy(fps[s['reference']].GetPosition());h=s['block_pitch_mm']/2
 corners=[[x-h,y-h],[x+h,y-h],[x+h,y+h],[x-h,y+h]]
 segments.extend(LineString([corners[i],corners[(i+1)%4]]) for i in range(4))
for g in unary_union(segments).geoms:
 for a,z in zip(g.coords,list(g.coords)[1:]):line(list(a),list(z),'key-pitch-frame')
for ref,f in sorted(fps.items()):
 if ref.startswith('U_') or ref=='J_WING':
  q=next(q for q in f.Pads() if q.GetNumber()=='1');x,y=xy(q.GetPosition())
  circle(x if ref=='J_WING' else x-1.3,y-1.6 if ref=='J_WING' else y,.22,'pin1:'+ref)
# Fixed identification, before auto reference placement.
text('16mm / ADDR 0-2',66,63,'block16',1,False)
text('17mm / ADDR 3-5',134,62.5,'block17',1,False)
text('M1 MATRIX18 / ISSUE178',139,134,'board-id',1,False)
text('DOT = PIN1',143,137,'legend',.8,False)
text('GH14 / D-017',78,136,'interface',.8,False)
text('35mm MIN KEY CENTER GAP',100,110,'interblock-gap',.8,True)
for ref,f in sorted(fps.items(),key=lambda kv:(kv[0].startswith('TP'),kv[0])):
 x,y=xy(f.GetPosition())
 if ref.startswith('C_'):tx,ty=x,y+2.5
 elif ref.startswith('U_H'):tx,ty=x,y-3
 elif ref.startswith('U_MUX'):tx,ty=x,y-4
 elif ref=='J_WING':tx,ty=x,y-5
 elif ref.startswith('H'):tx,ty=x+(4 if x<100 else -4),y
 else:tx,ty=x,y+2.5
 text(ref,tx,ty,'reference:'+ref)
q=next(q for q in fps['J_WING'].Pads() if q.GetNumber()=='1');x,y=xy(q.GetPosition());text('1 +5V',x+5,y-2,'polarity')
# AST cleanup changes only F.Paste membership on unassembled test pads and
# one exact route segment. Identical drawings/TP changes on both sides make
# subsequent nonroute transfer comparison strict, without exemptions.
def children(n,k):return [x for x in n if isinstance(x,list) and x and str(x[0])==k]
def val(n,k):return children(n,k)[0][1:]
cleanup_uuid='3b526ba3-fcea-418c-ac55-dcc9733483be'
records={}
for label,path in [('input',E/'inputs/m1-matrix18-16-17mm/main.kicad_pcb'),('output',raw)]:
 tree=sx.loads(path.read_text());testpads=[];removed=[]
 for f in children(tree,'footprint'):
  ref=next(q[2] for q in children(f,'property') if str(q[1])=='Reference')
  if str(ref).startswith('TP_'):
   for pad in children(f,'pad'):
    layers=children(pad,'layers')[0];assert 'F.Paste' in layers;layers.remove('F.Paste')
   testpads.append(str(ref))
 if label=='output':
  targets=[x for x in children(tree,'segment') if val(x,'uuid')==[cleanup_uuid]]
  assert len(targets)==1
  for t in targets:
   assert val(t,'width')==[.3] and val(t,'layer')==['F.Cu']
   assert math.dist(val(t,'start'),val(t,'end'))<.142
   removed.append(sx.dumps(t));tree.remove(t)
 assert len(testpads)==18
 tree.extend(sx.loads(n) for n in nodes)
 folder=E/('cell-inputs/final' if label=='input' else 'runs/final');folder.mkdir(parents=True,exist_ok=False)
 pcb=folder/('main.kicad_pcb' if label=='input' else 'out.kicad_pcb')
 pcb.write_text('(kicad_pcb\n'+'\n'.join(sx.dumps(x) for x in tree[1:])+'\n)\n')
 sourcepro=path.with_suffix('.kicad_pro');shutil.copyfile(sourcepro,pcb.with_suffix('.kicad_pro'))
 shutil.copyfile(E/'inputs/m1-matrix18-16-17mm/fp-lib-table',folder/'fp-lib-table')
 records[label]=dict(source=str(path.relative_to(R)),source_sha256=digest(path),final_sha256=digest(pcb),testpads_paste_removed=testpads,route_segments_removed=removed)
shutil.copyfile(E/'cell-inputs/KRT-M1-01/condition.json',E/'cell-inputs/final/condition.json')
save(E/'final-design-derivation.json',dict(utc=now(),records=records,artwork=entries,added_silk_primitives=len(nodes),cleanup_reason='Independent DRC detected one redundant GND track dangling end (0.1414mm); remove only that exact segment, preserve original route and failed assessment. No reroute or rule change.',testpad_policy='18 bare testpads are copper+mask only, excluded from paste, BOM and CPL; no purchased testpoint.'))
print('Prepared final artwork/input/output:',len(nodes),'silk objects')

# Sync the library to the deliberate bare-testpad paste removal, without any
# ignore/exclusion of library DRC findings. All other footprints stay byte equal.
lib=E/'PCBA.pretty'
shutil.copytree(E/'Wing129.pretty',lib)
pad=lib/'testpoint.kicad_mod';content=pad.read_text();assert content.count('"F.Paste"')==1
pad.write_text(content.replace(' "F.Paste"',''))
table='(fp_lib_table (version 7)(lib (name "Wing129")(type "KiCad")(uri "${KIPRJMOD}/../../PCBA.pretty")(options "")(descr "Issue178 PCBA bare testpads without paste")))\n'
for folder in [E/'cell-inputs/final',E/'runs/final']:(folder/'fp-lib-table').write_text(table)
