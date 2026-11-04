"""Create allowed stackup changes; refuse to invent a GND net in fixed smoke."""
from common import *
import pcbnew as p
import sexpdata as sx
import collections
def children(t,tag):return [x for x in t if isinstance(x,list) and x and str(x[0])==tag]
def one(t,tag):
 x=children(t,tag);assert len(x)==1,(tag,len(x));return x[0]
expected={'main':'46676e57e9618940a33c5e298244e97aaec61498a87aa7c58a264e444fc71e20','smoke':'3f70465774f577ffe803f88de017004d164f045e6415ade22766a461a2454bec'}
results={}
for stage in ['main','smoke']:
 src=R/'hardware/kicad/qualification/issue-115-kicad-routing-tools-escalation-off/evidence/inputs'/stage
 w=E/'inputs'/stage;w.mkdir(parents=True,exist_ok=False)
 assert sha(src/'main.kicad_pcb')==expected[stage]
 assert sha(src/'main.kicad_pro')=='a5bc2aea160cc9a8b3035f77f0167c26a1de7ffdb749740c94fb7a9e9a3c87d5'
 import shutil
 shutil.copyfile(src/'main.kicad_pcb',w/'original.kicad_pcb')
 for n in ['original','main']:shutil.copyfile(src/'main.kicad_pro',w/(n+'.kicad_pro'))
 before=sx.loads((w/'original.kicad_pcb').read_text())
 nets=[str(n[2]) for n in children(before,'net') if str(n[2])]
 # Text-local addition leaves every footprint, pad, net, edge, track and UUID untouched.
 text=(w/'original.kicad_pcb').read_text()
 text=text.replace('(0 "F.Cu" signal)','(0 "F.Cu" signal)\n\t\t(4 "In1.Cu" power)\n\t\t(6 "In2.Cu" signal)',1)
 # Copper 4*0.035 + dielectrics .18/.70/.18 = 1.20 mm (mask excluded).
 stack='''(stackup
 (layer "F.Cu" (type "copper") (thickness 0.035))
 (layer "dielectric 1" (type "prepreg") (thickness 0.18) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "In1.Cu" (type "copper") (thickness 0.035))
 (layer "dielectric 2" (type "core") (thickness 0.70) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "In2.Cu" (type "copper") (thickness 0.035))
 (layer "dielectric 3" (type "prepreg") (thickness 0.18) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
 (layer "B.Cu" (type "copper") (thickness 0.035))
 (copper_finish "HASL") (dielectric_constraints no))'''
 text=text.replace('(setup','(setup\n'+stack,1);(w/'main.kicad_pcb').write_text(text)
 manager=p.GetSettingsManager();manager.LoadProject(str(w/'main.kicad_pro'))
 b=p.LoadBoard(str(w/'main.kicad_pcb'));b.SetProject(manager.Prj())
 assert b.GetCopperLayerCount()==4 and b.GetLayerType(p.In1_Cu)==p.LT_POWER
 available={str(n) for n in b.GetNetsByName()}
 has_gnd='GND' in available
 if has_gnd:
  z=p.ZONE(b);z.SetLayer(p.In1_Cu);z.SetNetCode(b.FindNet('GND').GetNetCode());z.SetLocalClearance(p.FromMM(.2));z.SetMinThickness(p.FromMM(.2))
  z.SetThermalReliefGap(p.FromMM(.2));z.SetThermalReliefSpokeWidth(p.FromMM(.2))
  # A full board-bounding polygon; KiCad clips fill to the exact unchanged outline.
  box=b.GetBoardEdgesBoundingBox();o=z.Outline();o.NewOutline()
  for x,y in [(box.GetX(),box.GetY()),(box.GetRight(),box.GetY()),(box.GetRight(),box.GetBottom()),(box.GetX(),box.GetBottom())]:o.Append(x,y)
  b.Add(z);b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
  assert z.IsFilled() and z.HasFilledPolysForLayer(p.In1_Cu)
  assert p.SaveBoard(str(w/'saver-roundtrip.kicad_pcb'),b)
  # KiCad normalizes inverted paste rectangles on save. Transplant ONLY the
  # generated zone into the original text-local stackup edit so all other AST
  # records remain exactly identical, including paste drawing representation.
  saved=sx.loads((w/'saver-roundtrip.kicad_pcb').read_text())
  generated_zones=children(saved,'zone');assert len(generated_zones)==1
  (w/'main.kicad_pcb').write_text(text.rstrip()[:-1]+'\n'+sx.dumps(generated_zones[0])+'\n)\n')
  b=p.LoadBoard(str(w/'main.kicad_pcb'));b.SetProject(manager.Prj())
 # Export is readback only, never routing.
 assert p.ExportSpecctraDSN(b,str(w/'raw.dsn'))
 after=sx.loads((w/'main.kicad_pcb').read_text())
 def inv(t,excluded=()):return collections.Counter(sx.dumps(x) for x in t[1:] if not isinstance(x,list) or not x or str(x[0]) not in excluded)
 removed=list((inv(before,('layers','setup','zone'))-inv(after,('layers','setup','zone'))).elements())
 added=list((inv(after,('layers','setup','zone'))-inv(before,('layers','setup','zone'))).elements())
 # Native saver may add empty embedded_fonts as a serialization default; keep explicit.
 assert not removed and not added,(stage,removed,added)
 oldsetup=one(before,'setup');newsetup=one(after,'setup')
 assert inv(oldsetup,('stackup',))==inv(newsetup,('stackup',))
 assert [str(n[2]) for n in children(after,'net') if str(n[2])]==nets
 zones=[dict(net=z.GetNetname(),layer=b.GetLayerName(z.GetLayer()),filled=z.IsFilled(),filled_area_internal=z.CalculateFilledArea()) for z in b.Zones()]
 results[stage]=dict(original_pcb_sha256=sha(w/'original.kicad_pcb'),original_project_sha256=sha(w/'original.kicad_pro'),four_layer_pcb_sha256=sha(w/'main.kicad_pcb'),project_unchanged=sha(w/'main.kicad_pro')==sha(w/'original.kicad_pro'),native_net_names=nets,has_GND=has_gnd,footprints=len(children(after,'footprint')),pads=sum(len(children(f,'pad')) for f in children(after,'footprint')),original_segments=len(children(before,'segment')),non_layer_setup_zone_changes=dict(removed=removed,added=added),setup_difference_only_stackup=True,zones=zones,zone_requirement_pass=has_gnd and len(zones)==1 and zones[0]['net']=='GND' and zones[0]['filled'],layers=[dict(name=b.GetLayerName(i),role='power' if b.GetLayerType(i)==p.LT_POWER else 'signal') for i in [p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]],thickness_mm=p.ToMM(b.GetDesignSettings().GetBoardThickness()))
save(E/'native-equivalence.json',dict(utc=utc(),inputs=results,stackup_assumptions=dict(copper_mm=[.035]*4,dielectric_mm=[.18,.70,.18],total_mm=1.2,mask_excluded=True,material='FR4',epsilon_r=4.5,loss_tangent=.02,qualification_only_not_vendor_stackup=True)))
print(json.dumps(results,indent=2))
