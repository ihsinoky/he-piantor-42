"""Independent public KiCad reader vs committed JSON/CSV; never imports builder code."""
import pcbnew as p,json,math,csv,hashlib,datetime,sys,collections
from pathlib import Path
E=Path(__file__).resolve().parent;R=E.parents[4];tol=.000002
report={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pass_equivalence':False,'boards':{},'tolerance_mm':tol}
def close(a,b):assert abs(a-b)<=tol,(a,b)
def xy(v):return [p.ToMM(v.x),p.ToMM(v.y)]
def compare(a,b):
 assert len(a)==len(b)
 for x,y in zip(a,b):close(x,y)
def h(f):return hashlib.sha256(f.read_bytes()).hexdigest()
try:
 lib=json.loads((E/'library-pads.json').read_text());hashes=json.loads((E/'input-hashes.json').read_text())
 for name in ['pitch9-16mm','representative21-16mm','representative21-17mm']:
  source=R/'hardware/jitx/wing/generated'/name;d=json.loads((source/'definition.json').read_text());w=E/'inputs'/name;pcb=w/'main.kicad_pcb';b=p.LoadBoard(str(pcb));mgr=p.GetSettingsManager();mgr.LoadProject(str(w/'main.kicad_pro'));b.SetProject(mgr.Prj())
  assert all(h(w/f)==hashes[name][f] for f in hashes[name])
  footprints={f.GetReference():f for f in b.GetFootprints()};assert len(footprints)==len(d['components'])+4
  assert set(footprints)=={c['reference'] for c in d['components']}|{'H1','H2','H3','H4'}
  ends=collections.defaultdict(set);ncs=set();pad_count=0
  for c in d['components']:
   f=footprints[c['reference']];compare(xy(f.GetPosition()),[100+c['x_mm'],100-c['y_mm']]);close(f.GetOrientationDegrees(),c['rotation_ccw_deg']);assert f.GetLayer()==p.F_Cu;assert f.GetValue()==c['mpn'];assert c['side']=='top';assert f.GetFPIDAsString()=='Wing129:'+c['kind']
   actual=list(f.Pads());expected=lib[c['kind']];assert len(actual)==len(expected);used=set()
   for a in actual:
    num=a.GetNumber();key=c['reference']+'.'+num;net=c['pins'][num];assert a.GetNetname()==(net or '');assert a.GetAttribute()==p.PAD_ATTRIB_SMD;assert a.IsOnLayer(p.F_Cu) and not a.IsOnLayer(p.B_Cu)
    candidates=[(i,g) for i,g in enumerate(expected) if i not in used and g['number']==num and all(abs(x-y)<=tol for x,y in zip(xy(a.GetPosition()),[100+c['x_mm']+g['x_mm'],100-c['y_mm']-g['y_mm']]))];assert len(candidates)==1,(key,candidates,xy(a.GetPosition()));i,g=candidates[0];used.add(i)
    compare(xy(a.GetSize()),[g['width_mm'],g['height_mm']]);assert a.GetShape()==(p.PAD_SHAPE_CIRCLE if g['shape']=='circle' else p.PAD_SHAPE_RECT)
    if net:ends[net].add(key)
    else:ncs.add(key)
    pad_count+=1
  assert dict(ends)=={k:set(v) for k,v in d['nets'].items()};assert ncs==set(d['intentional_nc'])
  assert {str(n.GetNetname()) for n in b.GetNetsByNetcode().values() if n.GetNetname()}==set(d['nets'])
  gh=footprints['J_WING'];contacts={a.GetNumber():a.GetNetname() for a in gh.Pads() if a.GetNumber()!='MP'};assert sorted([n for n in contacts if contacts[n]=='GND'],key=int)==['2','4','8','10','12','14']
  for i,hole in enumerate(d['mounting_holes'],1):
   f=footprints['H'+str(i)];compare(xy(f.GetPosition()),[100+hole['x_mm'],100-hole['y_mm']]);a=list(f.Pads());assert len(a)==1;a=a[0];assert a.GetAttribute()==p.PAD_ATTRIB_NPTH and not a.GetNetname() and not a.GetNumber();compare(xy(a.GetDrillSize()),[hole['diameter_mm']]*2);compare(xy(a.GetSize()),[hole['diameter_mm']]*2)
  assert len(b.Zones())==4
  for i,z in enumerate(b.Zones(),1):
   assert z.GetIsRuleArea();assert z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and not z.GetDoNotAllowPads() and z.GetDoNotAllowCopperPour() and z.GetDoNotAllowFootprints();assert z.IsOnLayer(p.F_Cu) and z.IsOnLayer(p.B_Cu)
   index=int(z.GetZoneName().split()[-1])-1;hole=d['mounting_holes'][index];poly=z.Outline();assert poly.OutlineCount()==1;chain=poly.COutline(0);assert chain.PointCount()==256
   points=[xy(chain.CPoint(i)) for i in range(chain.PointCount())];center=[100+hole['x_mm'],100-hole['y_mm']];rad=hole['keepout_diameter_mm']/2
   # Circumscribed circle: every vertex and every edge stays outside the reserved disk (1nm rounding allowed).
   from shapely.geometry import Polygon,Point
   g=Polygon(points);assert g.contains(Point(center));assert rad-.000002<=g.boundary.distance(Point(center))<=rad+.000002
   assert max(math.dist(center,q) for q in points)<rad+.000191
  def edgekey(a,c):return tuple(sorted([tuple(round(v,6) for v in a),tuple(round(v,6) for v in c)]))
  edges=[x for x in b.GetDrawings() if x.GetLayer()==p.Edge_Cuts];assert len(edges)==4;expected=set()
  for i,q in enumerate(d['outline_mm']):
   r=d['outline_mm'][(i+1)%4];expected.add(edgekey([100+q[0],100-q[1]],[100+r[0],100-r[1]]))
  assert {edgekey(xy(e.GetStart()),xy(e.GetEnd())) for e in edges}==expected
  xs=[p.ToMM(e.GetStart().x) for e in edges];ys=[p.ToMM(e.GetStart().y) for e in edges];compare([max(xs)-min(xs),max(ys)-min(ys)],[d['width_mm'],d['height_mm']])
  access=[x for x in b.GetDrawings() if isinstance(x,p.PCB_SHAPE) and x.GetLayer()==p.Dwgs_User];assert len(access)==4
  x0,y0,x1,y1=d['connector_cable_access_mm'];q=[[100+x0,100-y0],[100+x1,100-y0],[100+x1,100-y1],[100+x0,100-y1]]
  assert {edgekey(xy(e.GetStart()),xy(e.GetEnd())) for e in access}=={edgekey(q[i],q[(i+1)%4]) for i in range(4)}
  assert b.GetCopperLayerCount()==d['layers']==2;close(p.ToMM(b.GetDesignSettings().GetBoardThickness()),d['thickness_mm']);assert len(b.GetTracks())==0
  ds=b.GetDesignSettings();nc=ds.m_NetSettings.GetDefaultNetclass()
  compare([p.ToMM(ds.m_MinClearance),p.ToMM(ds.m_TrackMinWidth),p.ToMM(nc.GetClearance()),p.ToMM(nc.GetTrackWidth()),p.ToMM(nc.GetViaDiameter()),p.ToMM(nc.GetViaDrill())],[.2,.2,.2,.2,.6,.3])
  pro=json.loads((w/'main.kicad_pro').read_text());rules=pro['board']['design_settings']['rules'];assert rules['min_via_diameter']==.6 and rules['min_through_hole_diameter']==.3
  # Independently corroborate the two input connectivity encodings (mechanical MP duplicates collapse as a logical NC).
  rows=list(csv.DictReader((source/'nets.csv').open()));assert rows
  csvends=collections.defaultdict(set);csvnc=set()
  for r in rows:
   key=r['reference']+'.'+r['physical_pin']
   if r['net']=='NC':csvnc.add(key)
   else:csvends[r['net']].add(key)
  assert dict(csvends)==dict(ends) and csvnc==ncs
  placements=list(csv.DictReader((source/'placements.csv').open()));assert len(placements)==len(d['components'])
  byref={c['reference']:c for c in d['components']}
  for r in placements:
   c=byref[r['reference']];compare([float(r['x_mm']),float(r['y_mm']),float(r['rotation_ccw_deg'])],[c['x_mm'],c['y_mm'],c['rotation_ccw_deg']]);assert r['mpn']==c['mpn'] and r['side']==c['side']
  bom=list(csv.DictReader((source/'bom.csv').open()));assert sum(int(r['quantity']) for r in bom)==len(d['components'])
  for r in bom:
   refs=r['references'].split();assert len(refs)==int(r['quantity'])
   for ref in refs:assert byref[ref]['kind']==r['kind'] and byref[ref]['mpn']==r['mpn']
  report['boards'][name]=dict(pass_equivalence=True,components=len(d['components']),physical_copper_pads=pad_count,named_nets=len(ends),intentional_nc=sorted(ncs),ground_connector_contacts=contacts,outline_mm=[d['width_mm'],d['height_mm']],mounting_npth=4,all_copper_keepouts=4,cable_access_mechanical_envelope=True,pcb_sha256=h(pcb),project_sha256=h(w/'main.kicad_pro'))
 report['pass_equivalence']=True
except Exception as error:
 import traceback
 report['failure']=repr(error);report['traceback']=traceback.format_exc()
finally:
 (E/'equivalence-gate.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print(json.dumps(report,indent=2,ensure_ascii=False))
 if not report['pass_equivalence']:sys.exit(1)
