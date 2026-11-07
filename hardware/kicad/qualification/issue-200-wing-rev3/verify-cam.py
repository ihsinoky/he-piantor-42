"""Independently read emitted Excellon/BOM/CPL and compare with final CAD."""
from pathlib import Path
import collections,csv,hashlib,json,math,re
import pcbnew as p
E=Path(__file__).resolve().parent

def drill(path):
 tools={};current=None;hits=[]
 for line in path.read_text().splitlines():
  m=re.fullmatch(r'T(\d+)C([\d.]+)',line)
  if m:tools[int(m[1])]=float(m[2]);continue
  m=re.fullmatch(r'T(\d+)',line)
  if m:current=int(m[1]);continue
  m=re.fullmatch(r'X(-?[\d.]+)Y(-?[\d.]+)',line)
  if m:assert current in tools;hits.append((round(float(m[1]),6),round(float(m[2]),6),tools[current]))
 return collections.Counter(hits)
def check(w):
 b=p.LoadBoard(str(w/'main.kicad_pcb'));expected=collections.defaultdict(collections.Counter)
 # Parse emitted profile coordinates independently, including every chamfer.
 um=lambda nm:((nm+500)//1000)/1000
 profile=(w/'gerber/main-Edge_Cuts.gm1').read_text()
 assert '%FSLAX46Y46*%' in profile and '%MOMM*%' in profile
 def segment(a,z):return tuple(sorted((tuple(a),tuple(z))))
 emitted=[];position=None
 for line in profile.splitlines():
  m=re.fullmatch(r'X(-?\d+)Y(-?\d+)D0([12])\*',line)
  if not m:continue
  end=(int(m[1]),-int(m[2]))
  if m[3]=='1':
   assert position is not None
   emitted.append(segment(position,end))
  position=end
 edges=[segment((d.GetStart().x,d.GetStart().y),(d.GetEnd().x,d.GetEnd().y)) for d in b.GetDrawings() if d.GetLayer()==p.Edge_Cuts]
 assert collections.Counter(emitted)==collections.Counter(edges),(w.name,'Gerber profile differs from CAD')
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):expected['PTH'][(um(t.GetPosition().x),um(-t.GetPosition().y),p.ToMM(t.GetDrillValue()))]+=1
 for f in b.GetFootprints():
  for a in f.Pads():
   if a.GetAttribute()==p.PAD_ATTRIB_NPTH:expected['NPTH'][(um(a.GetPosition().x),um(-a.GetPosition().y),p.ToMM(a.GetDrillSize().x))]+=1
 for kind in ('PTH','NPTH'):
  actual=drill(w/'gerber'/f'main-{kind}.drl');assert actual==expected[kind],(w.name,kind,'drill mismatch',actual-expected[kind],expected[kind]-actual)
 cpl=list(csv.DictReader((w/'cpl.csv').open()));bom=list(csv.DictReader((w/'bom.csv').open()));fs={f.GetReference():f for f in b.GetFootprints() if not f.GetAttributes()&p.FP_EXCLUDE_FROM_POS_FILES and not f.GetReference().startswith(('TP','L_TP','R_TP'))}
 assert {r['Designator'] for r in cpl}==set(fs) and len(cpl)==len(fs)
 for r in cpl:
  f=fs[r['Designator']];assert abs(float(r['MidX'].removesuffix('mm'))-p.ToMM(f.GetPosition().x))<1e-6 and abs(float(r['MidY'].removesuffix('mm'))+p.ToMM(f.GetPosition().y))<1e-6
  assert r['Layer']==('bottom' if f.GetLayer()==p.B_Cu else 'top') and abs(float(r['Rotation'])-f.GetOrientationDegrees())<1e-6
 refs=[]
 for r in bom:
  row=r['Designator'].split(',');assert len(row)==int(r['Quantity'])
  for ref in row:assert fs[ref].GetValue()==r['Comment']
  refs.extend(row)
 assert len(refs)==len(set(refs)) and set(refs)==set(fs)
 manifest=json.loads((w/'cam-manifest.json').read_text());assert manifest['source_sha256']==hashlib.sha256((w/'main.kicad_pcb').read_bytes()).hexdigest()
 for name,sha in manifest['files'].items():assert hashlib.sha256((w/name).read_bytes()).hexdigest()==sha
 if w.name.startswith('panel-'):
  drc=json.loads((w/'drc.json').read_text());assert not drc['violations'] and not drc['unconnected_items'],w.name
  assert len(cpl)==98 and collections.Counter(r['Layer'] for r in cpl)=={'bottom':84,'top':14}
  meta=json.loads((w/'panel.json').read_text());assert meta['tabs_copper_free'] and meta['min_copper_to_tab_mm']>=1.99998
 else:assert len(cpl)==49 and collections.Counter(r['Layer'] for r in cpl)=={'bottom':42,'top':7}
 return dict(name=w.name,pth_drills=sum(expected['PTH'].values()),npth_drills=sum(expected['NPTH'].values()),placements=len(cpl),side_counts=dict(collections.Counter(r['Layer'] for r in cpl)),bom_refs_unique=True,origin_and_drills_match=True,cam_hashes_match=True,profile_segments_match=len(edges))
results=[check(w) for w in sorted(E.glob('wing-rev3-*'))+sorted(E.glob('panel-*mm'))]
(E/'cam-verification.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
