"""Add board-level F.Silkscreen primitives only; preserve the source byte stream."""
import csv, json, math, shutil, uuid
from pathlib import Path
import pcbnew as p
from shapely.geometry import box, LineString, Point
from shapely.ops import unary_union
from common import R,E,T,SOURCE,save,digest

def uid():return str(uuid.uuid4())
def xy(v):return [p.ToMM(i) for i in v]
def vec(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))

def build(pitch):
 d=E/f'{pitch}mm';d.mkdir(parents=True,exist_ok=True)
 src=SOURCE/f'runs/KRT-{pitch}-2L-P0300/out.kicad_pcb'
 b=p.LoadBoard(str(src)); fps={f.GetReference():f for f in b.GetFootprints()}
 definition_path=R/f'hardware/jitx/wing/generated/representative21-{pitch}mm/definition.json'
 definition=json.loads(definition_path.read_text())
 placements_path=definition_path.with_name('placements.csv')
 placements=list(csv.DictReader(placements_path.open()))
 for row in placements:
  f=fps[row['reference']];x,y=xy(f.GetPosition())
  assert abs(x-(100+float(row['x_mm'])))<1e-6 and abs(y-(100-float(row['y_mm'])))<1e-6
 inv_path=SOURCE/f'KRT-{pitch}-2L-P0300-inventory.json'
 inv=json.loads(inv_path.read_text())
 # Inventory remains a separately frozen input; native positions above check placement definition.
 nodes=[]; entries=[]; occupied=[]
 edges=[g for g in b.GetDrawings() if g.GetLayer()==p.Edge_Cuts]
 xs=[p.ToMM(v) for g in edges for v in (g.GetStart().x,g.GetEnd().x)]
 ys=[p.ToMM(v) for g in edges for v in (g.GetStart().y,g.GetEnd().y)]
 bounds=[min(xs),min(ys),max(xs),max(ys)]; inside=box(*bounds).buffer(-.4)
 # Conservative pad bounding boxes include holes; via mask openings are absent (tented).
 pad_boxes=[]
 for f in fps.values():
  for q in f.Pads():
   bb=q.GetBoundingBox();pad_boxes.append(box(p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())).buffer(.28))
 pads=unary_union(pad_boxes)
 def line(a,z,role,width=.15):
  geom=LineString([a,z]).buffer(width/2)
  assert not geom.intersects(pads), (role,a,z,'pad collision')
  assert inside.covers(geom),(role,'outside')
  nodes.append(f'(gr_line (start {a[0]:.6f} {a[1]:.6f}) (end {z[0]:.6f} {z[1]:.6f}) (stroke (width {width}) (type default)) (layer "F.SilkS") (uuid "{uid()}"))')
  occupied.append(geom.buffer(.2));entries.append(dict(kind='line',role=role,start=a,end=z,width_mm=width))
 def circle(x,y,r,role,width=.15):
  geom=Point(x,y).buffer(r+width/2)
  assert inside.covers(geom) and not geom.intersects(pads),(role,'collision')
  nodes.append(f'(gr_circle (center {x:.6f} {y:.6f}) (end {x+r:.6f} {y:.6f}) (stroke (width {width}) (type default)) (fill none) (layer "F.SilkS") (uuid "{uid()}"))')
  occupied.append(geom.buffer(.2));entries.append(dict(kind='circle',role=role,center=[x,y],radius_mm=r))
 # Deduplicate shared boundaries while retaining exactly 21 pitch-square constructions in evidence.
 squares=[];segments=[]
 for site in definition['sensor_sites']:
  f=fps[site['reference']]; x,y=xy(f.GetPosition()); h=pitch/2
  assert abs(x-(100+site['x_mm']))<1e-6 and abs(y-(100-site['y_mm']))<1e-6
  corners=[[x-h,y-h],[x+h,y-h],[x+h,y+h],[x-h,y+h]]
  squares.append(dict(ref=site['reference'],source_key_id=site['source_key_id'],center=[x,y],side_mm=pitch,corners=corners))
  segments.extend(LineString([corners[i],corners[(i+1)%4]]) for i in range(4))
 merged=unary_union(segments)
 for g in merged.geoms:
  for a,z in zip(g.coords,list(g.coords)[1:]):line(list(a),list(z),'key-frame')
 # All pin1 marks are outside the exposed pad and nearest their identified pad1.
 pins=[]
 for ref,f in sorted(fps.items()):
  if not (ref.startswith('U_') or ref=='J_WING'):continue
  q=next(q for q in f.Pads() if q.GetNumber()=='1');x,y=xy(q.GetPosition())
  if ref=='J_WING': mx,my=x,y-1.6
  elif ref.startswith('U_H'):mx,my=x-1.15,y
  else:mx,my=x-1.3,y
  circle(mx,my,.22,'pin1:'+ref)
  pins.append(dict(ref=ref,pad1=xy(q.GetPosition()),mark=[mx,my],net=q.GetNetname()))
 holes=[]
 for ref,f in sorted(fps.items()):
  if not ref.startswith('H'):continue
  x,y=xy(f.GetPosition());source=next(h for h in definition['mounting_holes'] if abs(100+h['x_mm']-x)<1e-6 and abs(100-h['y_mm']-y)<1e-6)
  circle(x,y,1.65,'mounting-hole:'+ref)
  holes.append(dict(ref=ref,x_mm=x,y_mm=y,diameter_mm=source['diameter_mm'],keepout_diameter_mm=source['keepout_diameter_mm']))
 def text(s,x,y,role,size=.8,angle=0,search=True):
  candidates=[(x,y,angle)]
  if search:
   for radius in [.5,1,1.5,2,2.5,3,4,5,6,7,8]:
    for a in [0,90]:
     for k in range(24):candidates.append((x+radius*math.cos(k*math.pi/12),y+radius*math.sin(k*math.pi/12),a))
  obstacle=unary_union(occupied)
  for cx,cy,ang in candidates:
   obj=p.PCB_TEXT(b);obj.SetText(s);obj.SetTextSize(vec(size,size));obj.SetTextThickness(p.FromMM(.12));obj.SetPosition(vec(cx,cy));obj.SetTextAngle(p.EDA_ANGLE(ang,p.DEGREES_T));obj.SetLayer(p.F_SilkS)
   bb=obj.GetBoundingBox();geom=box(p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())).buffer(.12)
   if inside.covers(geom) and not geom.intersects(pads) and not geom.intersects(obstacle):break
  else:raise ValueError(('no text location',s,x,y))
  nodes.append(f'(gr_text {json.dumps(s)} (at {cx:.6f} {cy:.6f} {ang}) (layer "F.SilkS") (uuid "{uid()}") (effects (font (size {size} {size}) (thickness 0.12))))')
  occupied.append(geom.buffer(.18));entries.append(dict(kind='text',role=role,text=s,at=[cx,cy],angle_deg=ang,size_mm=size))
 # Place assembly references before testpoints; label each footprint including NPTH.
 for ref,f in sorted(fps.items(),key=lambda t:(t[0].startswith('TP'),t[0])):
  x,y=xy(f.GetPosition())
  if ref.startswith('C_'): tx,ty=x+1,y+2.6
  elif ref.startswith('U_H'):tx,ty=x-1,y-3
  elif ref.startswith('U_MUX'):tx,ty=x,y-4
  elif ref=='J_WING':tx,ty=x,y-4
  elif ref.startswith('H'):tx,ty=x+(3 if x<100 else -3),y
  else:tx,ty=x,y+3
  text(ref,tx,ty,'reference:'+ref)
 # Cable direction agrees with the connector cable-access rectangle in the definition.
 j=fps['J_WING'];jx,jy=xy(j.GetPosition())
 for a,z in [([jx,jy+2],[jx,jy+6]),([jx,jy+6],[jx-1,jy+5]),([jx,jy+6],[jx+1,jy+5])]:line(a,z,'J_WING cable direction')
 text('CABLE',jx+5,jy+6,'connector-direction')
 q=next(q for q in j.Pads() if q.GetNumber()=='1');x,y=xy(q.GetPosition());text('1 +5V',x+5,y-2,'connector-polarity')
 text(f'HE PIANTOR WING {pitch}mm Rev SILK-149A',100,bounds[3]-1.5,'board-identification',1)
 text('DOT = PIN1   |   KEY FRAMES = PITCH',80,128,'legend',.8)
 source=src.read_text(); idx=source.rfind(')'); assert not source[idx+1:].strip()
 additions='\n\t'+'\n\t'.join(nodes)+'\n'
 target=d/f'wing-{pitch}mm-silk149.kicad_pcb'; target.write_text(source[:idx]+additions+source[idx:])
 assert target.read_text().replace(additions,'',1)==source
 shutil.copyfile(src.with_suffix('.kicad_pro'),target.with_suffix('.kicad_pro'))
 shutil.copyfile(R/'.issue147-runtime'/f'{pitch}mm/fp-lib-table',d/'fp-lib-table')
 save(d/'design-evidence.json',dict(pitch_mm=pitch,source=str(src.relative_to(R)),source_sha256=digest(src),derived_sha256=digest(target),definition_sha256=digest(definition_path),placements_sha256=digest(placements_path),inventory_sha256=digest(inv_path),outline_bounds_mm=bounds,footprints=len(fps),references=sorted(fps),squares=squares,pin1_marks=pins,mounting_holes=holes,additions=entries,added_nodes=len(nodes),source_bytes_recovered_by_removing_additions=True,text_size_mm=.8,stroke_mm=.12,pad_clearance_bbox_mm=.28))
 print(pitch,len(nodes),'added primitives')

if __name__=='__main__':
 for pitch in (16,17):build(pitch)
