"""Build four independent native two-layer boards from Wing Rev.2 definitions.
Run via .issue194-runtime/run /usr/bin/python3 (KiCad 9.0.9 pcbnew).
"""
from pathlib import Path
import sys, json, math, shutil
import pcbnew as p
E=Path(__file__).resolve().parent;R=E.parents[3]
sys.path.insert(0,str(R/'hardware/jitx'))
from wing.rev2 import define_rev2
V=lambda x,y:p.VECTOR2I(round(x*1e6),round(y*1e6))
def save(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
lib=E/'WingRev2.pretty';lib.mkdir(exist_ok=True)
rows=json.loads((E.parent/'issue-129-wing-2layer-routing/evidence/library-pads.json').read_text())
io=p.PCB_IO_KICAD_SEXPR()
def layers(ids):
 out=p.LSET()
 for layer in ids:out.AddLayer(layer)
 return out
for kind,rr in rows.items():
 f=p.FOOTPRINT(None);f.SetFPID(p.LIB_ID('WingRev2',kind));f.SetReference('REF**');f.SetValue(kind);f.SetAttributes(p.FP_SMD)
 f.Reference().SetVisible(False);f.Value().SetVisible(False)
 for row in rr:
  a=p.PAD(f);a.SetNumber(row['number']);a.SetAttribute(p.PAD_ATTRIB_SMD);a.SetShape(p.PAD_SHAPE_CIRCLE if row['shape']=='circle' else p.PAD_SHAPE_RECT);a.SetSize(V(row['width_mm'],row['height_mm']));a.SetPosition(V(row['x_mm'],-row['y_mm']));a.SetLayerSet(layers([p.F_Cu,p.F_Mask] if kind=='testpoint' else [p.F_Cu,p.F_Paste,p.F_Mask]));f.Add(a)
 io.FootprintSave(str(lib),f)

def hole(b,ref,x,y,d):
 f=p.FOOTPRINT(b);f.SetFPID(p.LIB_ID('','NPTH'));f.SetReference(ref);f.SetValue(f'NPTH_{d}');f.Reference().SetVisible(False);f.Value().SetVisible(False);f.SetAttributes(p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
 a=p.PAD(f);a.SetAttribute(p.PAD_ATTRIB_NPTH);a.SetShape(p.PAD_SHAPE_CIRCLE);a.SetSize(V(d,d));a.SetDrillSize(V(d,d));a.SetLayerSet(p.LSET.AllCuMask());a.SetLocalClearance(p.FromMM(.25));f.Add(a);f.SetPosition(V(100+x,100-y));b.Add(f)
def keepout(b,x,y,r,name):
 z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask());z.SetZoneName(name)
 z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowPads(False);z.SetDoNotAllowCopperPour(True)
 poly=z.Outline();poly.NewOutline()
 for i in range(128):
  a=2*math.pi*i/128;v=V(100+x+r/math.cos(math.pi/128)*math.cos(a),100-y+r/math.cos(math.pi/128)*math.sin(a));poly.Append(v.x,v.y)
 b.Add(z)
for pitch in (16,17):
 for side in ('left','right'):
  s=define_rev2(pitch,side);w=E/s['name'];w.mkdir(exist_ok=True)
  b=p.BOARD();b.SetCopperLayerCount(2);b.GetDesignSettings().SetBoardThickness(p.FromMM(1.2))
  nets={}
  for name in sorted(s['nets']):n=p.NETINFO_ITEM(b,name);b.Add(n);nets[name]=n
  for c in s['components']:
   f=p.FootprintLoad(str(lib),c['kind']);f.SetReference(c['reference']);f.SetValue(c['mpn']);f.SetPosition(V(100+c['x_mm'],100-c['y_mm']))
   b.Add(f)
   if c['side']=='bottom':f.Flip(f.GetPosition(),True)
   f.SetOrientationDegrees(c['rotation_ccw_deg'])
   for a in f.Pads():
    name=c['pins'][a.GetNumber()]
    if name is not None:a.SetNet(nets[name])
  for i,h in enumerate(s['mounting_holes'],1):
   hole(b,f'H{i}',h['x_mm'],h['y_mm'],h['diameter_mm']);keepout(b,h['x_mm'],h['y_mm'],2.5,f'Mounting H{i} phi5')
  for i,k in enumerate(s['keys'],1):
   for j,h in enumerate(k['locator_holes'],1):hole(b,f'MH_{i}_{j}',h['x_mm'],h['y_mm'],1.7)
  for i,xy in enumerate(s['outline_mm']):
   other=s['outline_mm'][(i+1)%len(s['outline_mm'])];a=p.PCB_SHAPE();a.SetShape(p.SHAPE_T_SEGMENT);a.SetStart(V(100+xy[0],100-xy[1]));a.SetEnd(V(100+other[0],100-other[1]));a.SetWidth(p.FromMM(.05));a.SetLayer(p.Edge_Cuts);b.Add(a)
  # Front and rear identities, below the key field, inside the reserved connector area.
  for layer in (p.F_SilkS,p.B_SilkS):
   a=p.PCB_TEXT(b);a.SetText(f'WING REV2 {pitch} {side.upper()}');a.SetPosition(V(100+(-37 if side=='left' else 37),125));a.SetLayer(layer);a.SetMirrored(layer==p.B_SilkS);a.SetTextSize(V(.8,.8));a.SetTextThickness(p.FromMM(.12));b.Add(a)
  pro=json.loads((E.parent/'issue-141-wing-power-integrity/cell-inputs/KRT-16-power030/main.kicad_pro').read_text()) if (E.parent/'issue-141-wing-power-integrity/cell-inputs/KRT-16-power030/main.kicad_pro').exists() else json.loads((E.parent/'issue-131-wing-condition-search/evidence/inputs/representative21-16mm/main.kicad_pro').read_text())
  pro['board']['design_settings']['rules'].update(min_clearance=.1,min_track_width=.1,min_via_diameter=.6,min_via_drill=.3,min_through_hole_diameter=.3,min_hole_clearance=.25,min_hole_to_hole=.25,min_copper_edge_clearance=.3)
  default=pro['net_settings']['classes'][0];default.update(name='Default',clearance=.1,track_width=.1,via_diameter=.6,via_drill=.3)
  power=dict(default);power.update(name='Power',track_width=.3)
  pro['net_settings']['classes']=[default,power];pro['net_settings']['netclass_patterns']=[dict(netclass='Power',pattern=n) for n in ('HALL_5V','GND')]
  pro['kicad_routing_tools']={'same_net_pad_clearance':.15}
  save(w/'input.kicad_pro',pro)
  manager=p.GetSettingsManager();manager.LoadProject(str(w/'input.kicad_pro'));b.SetProject(manager.Prj());p.SaveBoard(str(w/'input.kicad_pcb'),b)
  (w/'fp-lib-table').write_text('(fp_lib_table (version 7)(lib (name "WingRev2")(type "KiCad")(uri "${KIPRJMOD}/../WingRev2.pretty")(options "")(descr "Wing project lands")))\n')
  save(w/'definition.json',s);print(s['name'],flush=True)
