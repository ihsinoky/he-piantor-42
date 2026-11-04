"""Author native inputs from generated JSON only; geometry from existing component library."""
from common import *
import pcbnew as p,math,shutil
V=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
lib=E/'Wing129.pretty';lib.mkdir(exist_ok=False);io=p.PCB_IO_KICAD_SEXPR()
pads=json.loads((E/'library-pads.json').read_text())
smdlayers=p.LSET()
for layer in [p.F_Cu,p.F_Paste,p.F_Mask]:smdlayers.AddLayer(layer)
for kind,rows in pads.items():
 f=p.FOOTPRINT(None);f.SetFPID(p.LIB_ID('Wing129',kind));f.SetReference('REF**');f.SetValue(kind);f.SetAttributes(p.FP_SMD)
 f.Reference().SetLayer(p.F_Fab);f.Reference().SetVisible(False);f.Value().SetLayer(p.F_Fab);f.Value().SetVisible(False)
 for row in rows:
  a=p.PAD(f);a.SetNumber(row['number']);a.SetAttribute(p.PAD_ATTRIB_SMD);a.SetShape(p.PAD_SHAPE_CIRCLE if row['shape']=='circle' else p.PAD_SHAPE_RECT);a.SetSize(V(row['width_mm'],row['height_mm']));a.SetPosition(V(row['x_mm'],-row['y_mm']));a.SetLayerSet(smdlayers);f.Add(a)
 io.FootprintSave(str(lib),f)
# One reusable mechanical library footprint; no electrical terminal.
f=p.FOOTPRINT(None);f.SetFPID(p.LIB_ID('Wing129','mounting'));f.SetReference('REF**');f.SetValue('NPTH_2.2mm');f.Reference().SetVisible(False);f.Value().SetVisible(False);f.SetAttributes(p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
a=p.PAD(f);a.SetNumber('');a.SetAttribute(p.PAD_ATTRIB_NPTH);a.SetShape(p.PAD_SHAPE_CIRCLE);a.SetSize(V(2.2,2.2));a.SetDrillSize(V(2.2,2.2));a.SetLayerSet(p.LSET.AllCuMask());f.Add(a);io.FootprintSave(str(lib),f)
provenance={};fixed={}
for name in ['pitch9-16mm','representative21-16mm','representative21-17mm']:
 source=R/'hardware/jitx/wing/generated'/name;spec=json.loads((source/'definition.json').read_text());w=E/'inputs'/name;w.mkdir(parents=True,exist_ok=False)
 provenance[name]={ext:dict(source=str((source/ext).relative_to(R)),sha256=digest(source/ext)) for ext in ['definition.json','placements.csv','nets.csv','bom.csv']}
 b=p.BOARD();b.SetCopperLayerCount(2);b.GetDesignSettings().SetBoardThickness(p.FromMM(spec['thickness_mm']))
 nets={}
 for key in sorted(spec['nets']):
  n=p.NETINFO_ITEM(b,key);b.Add(n);nets[key]=n
 for row in spec['components']:
  f=p.FootprintLoad(str(lib),row['kind']);f.SetFPID(p.LIB_ID('Wing129',row['kind']));f.SetReference(row['reference']);f.SetValue(row['mpn']);f.SetPosition(V(100+row['x_mm'],100-row['y_mm']));f.SetOrientationDegrees(row['rotation_ccw_deg'])
  for a in f.Pads():
   net=row['pins'][a.GetNumber()]
   if net is not None:a.SetNet(nets[net])
  b.Add(f)
 for i,h in enumerate(spec['mounting_holes'],1):
  f=p.FootprintLoad(str(lib),'mounting');f.SetFPID(p.LIB_ID('Wing129','mounting'));f.SetReference('H'+str(i));f.SetPosition(V(100+h['x_mm'],100-h['y_mm']));b.Add(f)
  z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask());z.SetZoneName('mounting keepout '+str(i));z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowPads(True);z.SetDoNotAllowCopperPour(True);z.SetDoNotAllowFootprints(True)
  poly=z.Outline();poly.NewOutline();radius=h['keepout_diameter_mm']/2/math.cos(math.pi/256)
  for j in range(256):
   theta=2*math.pi*j/256;v=V(100+h['x_mm']+radius*math.cos(theta),100-h['y_mm']+radius*math.sin(theta));poly.Append(v.x,v.y)
  b.Add(z)
 def line(x,y,layer):
  a=p.PCB_SHAPE();a.SetShape(p.SHAPE_T_SEGMENT);a.SetStart(V(100+x[0],100-x[1]));a.SetEnd(V(100+y[0],100-y[1]));a.SetWidth(p.FromMM(.05));a.SetLayer(layer);b.Add(a)
 points=spec['outline_mm']
 for i in range(4):line(points[i],points[(i+1)%4],p.Edge_Cuts)
 # Access envelope is mechanical space above the connector, not a copper ban through its own lands.
 x0,y0,x1,y1=spec['connector_cable_access_mm'];pts=[[x0,y0],[x1,y0],[x1,y1],[x0,y1]]
 for i in range(4):line(pts[i],pts[(i+1)%4],p.Dwgs_User)
 text=p.PCB_TEXT(b);text.SetText('GH14 cable/latch access; mechanical reservation');text.SetPosition(V(100+(x0+x1)/2,100-y0+1));text.SetLayer(p.Dwgs_User);text.SetTextSize(V(.7,.7));b.Add(text)
 # Seed full project defaults from established qualification rules, then explicitly pin every routing floor.
 old=R/'hardware/kicad/qualification/issue-115-kicad-routing-tools-escalation-off/evidence/inputs/smoke/main.kicad_pro';pro=json.loads(old.read_text());pro['meta']['filename']='main.kicad_pro'
 rules=pro['board']['design_settings']['rules'];rules.update(min_clearance=.2,min_track_width=.2,min_via_diameter=.6,min_through_hole_diameter=.3,min_via_drill=.3,min_hole_clearance=.2,min_hole_to_hole=.2,min_copper_edge_clearance=.2)
 pro['net_settings']['classes'][0].update(clearance=.2,track_width=.2,via_diameter=.6,via_drill=.3)
 save(w/'main.kicad_pro',pro)
 manager=p.GetSettingsManager();manager.LoadProject(str(w/'main.kicad_pro'));b.SetProject(manager.Prj());p.SaveBoard(str(w/'main.kicad_pcb'),b)
 (w/'fp-lib-table').write_text(f'(fp_lib_table (version 7)(lib (name "Wing129")(type "KiCad")(uri "{lib}")(options "")(descr "Existing project library land geometry")))\n')
 save(w/'pinmap.json',dict(pins={c['reference']:c['pins'] for c in spec['components']},intentional_nc=spec['intentional_nc'],ground_connector_contacts=[str(i) for i in range(1,15) if next(c for c in spec['components'] if c['reference']=='J_WING')['pins'][str(i)]=='GND'],coordinate_transform='KiCad X=100+JSON x; KiCad Y=100-JSON y; CCW unchanged',mounting_keepout_polygon=dict(vertices=256,circumscribed=True,max_radial_excess_mm=2.5/math.cos(math.pi/256)-2.5),cable_access='Mechanical reservation on Dwgs.User; no copper restriction through connector lands.'))
 fixed[name]={x.name:digest(x) for x in w.iterdir() if x.is_file()}
 print(name,flush=True)
save(E/'input-provenance.json',provenance);save(E/'input-hashes.json',fixed)
