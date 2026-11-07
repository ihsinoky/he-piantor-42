"""Regenerate individual CAM and one left/right Standard-PCBA panel per pitch.
No copper crosses tabs. All panel nets and refs stay distinct by L_/R_ prefix.
"""
from pathlib import Path
import collections,csv,hashlib,json,shutil,subprocess,sys
import pcbnew as p
from shapely.geometry import box,Polygon,Point,LineString
from shapely.ops import unary_union
from verify import xy,polys,padgeom
E=Path(__file__).resolve().parent;R=E.parents[3];T=E.parents[4]
# Keep native parent boards alive while their duplicated SWIG wrappers exist.
native_boards=[]
V=lambda x,y:p.VECTOR2I(round(x*1e6),round(y*1e6))
def save(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def writecsv(path,fields,rows):
 with path.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def npth(b,ref,x,y,d):
 f=p.FOOTPRINT(b);f.SetReference(ref);f.SetValue(f'NPTH_{d}');f.Reference().SetVisible(False);f.Value().SetVisible(False);f.SetAttributes(p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
 a=p.PAD(f);a.SetAttribute(p.PAD_ATTRIB_NPTH);a.SetShape(p.PAD_SHAPE_CIRCLE);a.SetSize(V(d,d));a.SetDrillSize(V(d,d));a.SetLayerSet(p.LSET.AllCuMask());f.Add(a);f.SetPosition(V(x,y));b.Add(f)
def contour(b,polygon):
 for ring in [polygon.exterior,*polygon.interiors]:
  pts=list(ring.coords)
  for a,z in zip(pts,pts[1:]):
   t=p.PCB_SHAPE();t.SetShape(p.SHAPE_T_SEGMENT);t.SetStart(V(*a));t.SetEnd(V(*z));t.SetLayer(p.Edge_Cuts);t.SetWidth(p.FromMM(.05));b.Add(t)
def cam(w):
 source=w/'main.kicad_pcb';cam=w/'gerber';cam.mkdir(exist_ok=True)
 for old in cam.iterdir():
  if old.is_file():old.unlink()
 cmds=[['kicad-cli','pcb','export','gerbers','-o',str(cam)+'/', '--layers','F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts',str(source)],['kicad-cli','pcb','export','drill','-o',str(cam)+'/', '--format','excellon','--excellon-separate-th',str(source)]]
 for argv in cmds:subprocess.run(argv,check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 # Top-view CCW angles with physical bottom side stated; machine/library corrections
 # must be verified against the component pin1 overlay, never guessed by mirroring.
 b=p.LoadBoard(str(source));bom=collections.defaultdict(list);cpl=[]
 for f in sorted(b.GetFootprints(),key=lambda f:f.GetReference()):
  if f.GetAttributes()&p.FP_EXCLUDE_FROM_POS_FILES or f.GetReference().startswith(('TP','L_TP','R_TP')):continue
  ref=f.GetReference();bom[f.GetValue()].append(ref);x,y=xy(f.GetPosition());cpl.append(dict(Designator=ref,MidX=f'{x:.6f}mm',MidY=f'{-y:.6f}mm',Layer='bottom' if f.GetLayer()==p.B_Cu else 'top',Rotation=f'{f.GetOrientationDegrees():.6f}'))
 writecsv(w/'bom.csv',['Comment','Designator','Quantity'],[dict(Comment=mpn,Designator=','.join(refs),Quantity=len(refs)) for mpn,refs in sorted(bom.items())])
 writecsv(w/'cpl.csv',['Designator','MidX','MidY','Layer','Rotation'],cpl)
 # Explicit pad-1 reference avoids dependence on a guessed bottom CPL sign convention.
 writecsv(w/'pin1.csv',['reference','side','origin_x_mm','origin_y_mm','rotation_ccw_deg','pad1_x_mm','pad1_y_mm'],[dict(reference=f.GetReference(),side='bottom' if f.GetLayer()==p.B_Cu else 'top',origin_x_mm=xy(f.GetPosition())[0],origin_y_mm=xy(f.GetPosition())[1],rotation_ccw_deg=f.GetOrientationDegrees(),pad1_x_mm=xy(a.GetPosition())[0],pad1_y_mm=xy(a.GetPosition())[1]) for f in b.GetFootprints() for a in f.Pads() if a.GetNumber()=='1'])
 save(w/'cam-manifest.json',dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),files={str(f.relative_to(w)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(cam.iterdir()) if f.is_file()},assembly='Standard PCBA; double-sided; Hall+local C bottom',cpl_frame='KiCad absolute X, negated KiCad Y, top-view CCW angle, side explicit; compare pin1.csv and assembly drawing before machine correction'))
 with __import__('zipfile').ZipFile(w/'fabrication.zip','w',compression=__import__('zipfile').ZIP_DEFLATED) as z:
  for f in sorted(cam.iterdir()):
   if f.is_file():z.write(f,'gerber/'+f.name)
for pitch in (16,17):
 if len(sys.argv)>1 and str(pitch) not in sys.argv[1:]:continue
 w=E/f'panel-{pitch}mm';w.mkdir(exist_ok=True)
 b=p.BOARD();b.SetCopperLayerCount(2);b.GetDesignSettings().SetBoardThickness(p.FromMM(1.2));nets={};rects=[];transforms=[];offsets={};height=None;width=None;sources=[]
 for index,side in enumerate(('left','right')):
  boarddir=E/f'wing-rev3-{pitch}mm-{side}'
  q=json.loads((boarddir/'qualification.json').read_text());assert q['pass']
  source=p.LoadBoard(str(boarddir/'main.kicad_pcb'));sources.append(source);native_boards.append(source);ps=p.SHAPE_POLY_SET();source.GetBoardPolygonOutlines(ps);x0,y0,x1,y1=polys(ps).bounds;width=x1-x0;height=y1-y0
  dx=28-x0;dy=20+index*(height+3)-y0;offsets[side]=(dx,dy);offset=V(dx,dy);prefix='L_' if side=='left' else 'R_'
  for rawname in source.GetNetsByName():
   name=str(rawname)
   if not name:continue
   n=p.NETINFO_ITEM(b,prefix+name);b.Add(n);nets[prefix+name]=n
  for f in source.GetFootprints():
   copy=f.Duplicate();copy.SetParent(b);copy.SetReference(prefix+f.GetReference());copy.Move(offset)
   for a in copy.Pads():
    name=a.GetNetname()
    if name:a.SetNet(nets[prefix+name])
   b.Add(copy)
  for t in source.GetTracks():
   copy=t.Duplicate();copy.SetParent(b);copy.SetNet(nets[prefix+t.GetNetname()]);copy.Move(offset);b.Add(copy)
  for z in source.Zones():
   copy=z.Duplicate();copy.SetParent(b);copy.Move(offset)
   if not copy.GetIsRuleArea():copy.SetNet(nets[prefix+z.GetNetname()]);copy.UnFill()
   elif copy.GetZoneName().startswith('Panel tab '):
    # Mouse-bite NPTHs may touch this area; all actual pad copper is audited below.
    copy.SetDoNotAllowPads(False)
   b.Add(copy)
  for t in source.GetDrawings():
   if t.GetLayer()==p.Edge_Cuts:continue
   copy=t.Duplicate();copy.SetParent(b);copy.Move(offset);b.Add(copy)
  from shapely.affinity import translate
  rects.append(translate(polys(ps),dx,dy));transforms.append(dict(side=side,dx_mm=dx,dy_mm=dy,prefix=prefix,source_sha256=q['sha256']))
 # Shoulder/stepped profiles cannot share the old rectangular inter-board tabs.
 # Each independent board attaches to both full-height rails at two side stations.
 tabs=[];drills=[];totalheight=2*height+3
 rails=[box(20,20,25,20+totalheight),box(31+width,20,36+width,20+totalheight)]
 for side in ('left','right'):
  for native_y in (70.,95.):
   cy=native_y+offsets[side][1]
   for xa,xb in ((25,28),(28+width,31+width)):
    tabs.append(box(xa,cy-2.5,xb,cy+2.5))
    for xx in (xa+.3,xb-.3):
     for i in range(6):drills.append((xx,cy+(i-2.5)*.9))
 shape=unary_union(rects+tabs+rails);assert shape.geom_type=='Polygon' and shape.is_valid
 contour(b,shape)
 for i,(x,y) in enumerate(drills,1):npth(b,f'MB_{i}',x,y,.6)
 for i,(x,y) in enumerate([(22.5,25),(22.5,15+totalheight),(33.5+width,25),(33.5+width,15+totalheight)],1):npth(b,f'TOOL_{i}',x,y,2)
 # Optical marks on copper-free rails, no paste, on both assembly sides.
 for i,(x,y) in enumerate([(22.5,30),(33.5+width,30),(22.5,10+totalheight)],1):
  f=p.FOOTPRINT(b);f.SetReference(f'FID{i}');f.SetValue('Fiducial_1mm');f.SetPosition(V(x,y));f.Reference().SetVisible(False);f.Value().SetVisible(False);f.SetAttributes(p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
  for layer in (p.F_Cu,p.B_Cu):
   a=p.PAD(f);a.SetAttribute(p.PAD_ATTRIB_SMD);a.SetShape(p.PAD_SHAPE_CIRCLE);a.SetSize(V(1,1));ls=p.LSET();ls.AddLayer(layer);ls.AddLayer(p.F_Mask if layer==p.F_Cu else p.B_Mask);a.SetLayerSet(ls);a.SetLocalSolderMaskMargin(p.FromMM(1.0));f.Add(a)
  b.Add(f)
 project=json.loads((E/f'wing-rev3-{pitch}mm-left/main.kicad_pro').read_text());project['net_settings']['netclass_patterns']=[dict(netclass='Power',pattern=prefix+net) for prefix in ('L_','R_') for net in ('HALL_5V','GND')];save(w/'main.kicad_pro',project)
 shutil.copyfile(E/f'wing-rev3-{pitch}mm-left/fp-lib-table',w/'fp-lib-table')
 # Normalize duplicated SWIG objects through native serialization before fill.
 p.SaveBoard(str(w/'main.kicad_pcb'),b,True)
 # SaveBoard of a new BOARD creates default project settings. Restore the
 # qualified source rules before reopening/filling the serialized panel.
 save(w/'main.kicad_pro',project)
 native_boards.append(b)
 b=p.LoadBoard(str(w/'main.kicad_pcb'));manager=p.GetSettingsManager();manager.LoadProject(str(w/'main.kicad_pro'));b.SetProject(manager.Prj());b.BuildConnectivity()
 native_boards.append(b)
 print(w.name,'fill panel',flush=True)
 p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();p.SaveBoard(str(w/'main.kicad_pcb'),b,True)
 # Actual filled copper must miss every tab, and stay confined to its half.
 tabshape=unary_union(tabs);failures=[];min_tab=float('inf')
 for t in b.GetTracks():
  g=Point(xy(t.GetPosition())).buffer(.3) if isinstance(t,p.PCB_VIA) else LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2)
  min_tab=min(min_tab,g.distance(tabshape))
  if g.intersects(tabshape):failures.append(t.m_Uuid.AsString())
 for f in b.GetFootprints():
  for a in f.Pads():
   if a.GetAttribute()==p.PAD_ATTRIB_NPTH:continue
   for l in (p.F_Cu,p.B_Cu):
    if a.IsOnLayer(l):
     g=padgeom(a,l);min_tab=min(min_tab,g.distance(tabshape))
     if g.intersects(tabshape):failures.append(f.GetReference())
 for z in b.Zones():
  if z.GetIsRuleArea():continue
  for l in (p.F_Cu,p.B_Cu):
   if z.IsOnLayer(l):
    g=polys(z.GetFilledPolysList(l));min_tab=min(min_tab,g.distance(tabshape))
    if g.intersects(tabshape):failures.append(z.GetZoneName())
 assert not failures,failures
 assert min_tab>=1.99998,('tab setback',min_tab)
 save(w/'panel.json',dict(pitch_mm=pitch,panel_width_mm=width+16,panel_height_mm=totalheight,transforms=transforms,independent_circuits=True,gap_mm=3,rail_width_mm=5,tab_width_mm=5,tab_count=len(tabs),mouse_bite_diameter_mm=.6,mouse_bite_pitch_mm=.9,mouse_bite_count=len(drills),tabs_copper_free=True,min_copper_to_tab_mm=min_tab,standard_pcba_required=True,tab_break_drawing_requires_fabricator_review=True))
 cam(w)
 for side in ('left','right'):cam(E/f'wing-rev3-{pitch}mm-{side}')
 print(w.name,flush=True)
