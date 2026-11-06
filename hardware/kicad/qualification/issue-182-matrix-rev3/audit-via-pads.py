"""Independent saved-board audit: analytic pad copper distance + native collision.

No router geometry or obstacles are imported. Checks every via against every
copper-bearing component pad, including NC reinforcement lands and bare TPs.
NPTH pads carry no copper and are enumerated separately. Unsupported shapes fail.
"""
from common import *
import pcbnew as p
import math,csv,io,sys,collections
path=Path(sys.argv[1]);dest=Path(sys.argv[2]);dest.mkdir(parents=True,exist_ok=True)
b=p.LoadBoard(str(path));mm=p.ToMM
pads=[];excluded=[]
for f in b.GetFootprints():
 for q in f.Pads():
  row=(f.GetReference(),q)
  if q.GetAttribute()==p.PAD_ATTRIB_NPTH or not any(q.IsOnLayer(l) for l in [p.F_Cu,p.B_Cu]):excluded.append(f.GetReference()+'.'+q.GetNumber())
  else:pads.append(row)
def signed_distance(q,pos):
 dx,dy=mm(pos.x-q.GetPosition().x),mm(pos.y-q.GetPosition().y)
 # KiCad positive rotation is CCW in Cartesian Y-up; inverse in screen Y-down.
 theta=math.radians(q.GetOrientationDegrees());x=dx*math.cos(theta)-dy*math.sin(theta);y=dx*math.sin(theta)+dy*math.cos(theta)
 w,h=mm(q.GetSize().x),mm(q.GetSize().y);s=q.GetShape()
 if s==p.PAD_SHAPE_RECT:
  a,c=abs(x)-w/2,abs(y)-h/2
  return math.hypot(max(a,0),max(c,0))+min(max(a,c),0)
 if s==p.PAD_SHAPE_CIRCLE:
  assert w==h
  return math.hypot(x,y)-w/2
 if s==p.PAD_SHAPE_OVAL:
  return math.hypot(max(abs(x)-max(w-h,0)/2,0),max(abs(y)-max(h-w,0)/2,0))-min(w,h)/2
 raise AssertionError(('unsupported copper pad shape',int(s)))
rows=[];native_hits=[]
for t in b.GetTracks():
 if not isinstance(t,p.PCB_VIA):continue
 r=mm(t.GetWidth())/2;pos=t.GetPosition()
 pairs=sorted((signed_distance(q,pos)-r,ref,q.GetNumber()) for ref,q in pads)
 native=[]
 # Enlarged via disk includes the entire annulus, including its outer boundary.
 disk=p.SHAPE_CIRCLE(pos,t.GetWidth()//2+p.FromMM(.1))
 copper_disk=p.SHAPE_CIRCLE(pos,t.GetWidth()//2)
 overlaps=[]
 for ref,q in pads:
  if q.GetEffectiveShape(p.F_Cu if q.IsOnLayer(p.F_Cu) else p.B_Cu).Collide(disk):native.append(ref+'.'+q.GetNumber())
  if q.GetEffectiveShape(p.F_Cu if q.IsOnLayer(p.F_Cu) else p.B_Cu).Collide(copper_disk):overlaps.append(ref+'.'+q.GetNumber())
 gap,ref,num=pairs[0]
 rows.append(dict(uuid=t.m_Uuid.AsString(),x_mm=mm(pos.x),y_mm=mm(pos.y),net=t.GetNetname(),diameter_mm=mm(t.GetWidth()),drill_mm=mm(t.GetDrillValue()),minimum_pad_gap_mm=gap,nearest_pad=ref+'.'+num,pad_overlap=gap<0,clearance_violation=gap<.1,native_expanded_disk_hits=native,native_copper_disk_hits=overlaps))
rows.sort(key=lambda x:(x['net'],x['x_mm'],x['y_mm'],x['uuid']))
report=dict(utc=now(),board_sha256=digest(path),required_annulus_to_pad_clearance_mm=.1,via_count=len(rows),copper_pad_count=len(pads),testpad_count=sum(ref.startswith('TP_') for ref,q in pads),excluded_non_copper_pads=excluded,pair_tests=len(rows)*len(pads),minimum_gap_mm=min(r['minimum_pad_gap_mm'] for r in rows),overlapping_vias=sum(r['pad_overlap'] for r in rows),clearance_violating_vias=sum(r['clearance_violation'] for r in rows),native_expanded_disk_hit_vias=sum(bool(r['native_expanded_disk_hits']) for r in rows),native_overlap_vias=sum(bool(r['native_copper_disk_hits']) for r in rows),pad_shape_histogram=dict(collections.Counter(str(int(q.GetShape())) for _,q in pads)),method='Exact analytic signed point-to-rectangle/circle/capsule distance minus via outer radius; all pairs irrespective of net. Independent KiCad native effective-shape collision with copper disk and disk expanded by exactly 0.10mm. No polygon tessellation or acceptance tolerance.',all_vias=rows)
report['pass_acceptance']=report['overlapping_vias']==report['clearance_violating_vias']==report['native_expanded_disk_hit_vias']==report['native_overlap_vias']==0
save(dest/'via-pad-audit.json',report)
s=io.StringIO();fields=list(rows[0]);w=csv.DictWriter(s,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows);(dest/'all-vias.csv').write_text(s.getvalue())
print(json.dumps({k:v for k,v in report.items() if k!='all_vias'},indent=2))
