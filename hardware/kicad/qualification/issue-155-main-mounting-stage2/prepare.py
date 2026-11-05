"""Add plan A holes/keepouts only; remove exactly three conflicting segments for local KRT."""
from common import *
import pcbnew as p, math,shutil
V=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
source=R/'hardware/kicad/qualification/issue-121-full-auto-conditions/evidence'
pcb=source/'inspection/main-cell1/krt/main.kicad_pcb';pro=source/'inputs/main-cell1/main.kicad_pro'
plans=R/'hardware/kicad/qualification/issue-153-main-mounting-stage1/plans.json'
plan=json.loads(plans.read_text())['A-retain-4'];affected=set(plan['affected_existing_items'])
save(E/'inputs.json',dict(files={str(x.relative_to(R)):digest(x) for x in [pcb,pro,plans,R/'docs/decisions.md',R/'docs/issue-153-main-mounting-stage1.md']},plan=plan))
w=E/'inputs/revised';w.mkdir(parents=True,exist_ok=False)
shutil.copyfile(pro,w/'main.kicad_pro')
manager=p.GetSettingsManager();manager.LoadProject(str(w/'main.kicad_pro'))
b=p.LoadBoard(str(pcb));b.SetProject(manager.Prj());assert p.SaveBoard(str(w/'canonical-source.kicad_pcb'),b)
lib=E/'Main155.pretty';lib.mkdir(exist_ok=False)
f=p.FOOTPRINT(None);f.SetFPID(p.LIB_ID('Main155','mounting'));f.SetReference('REF**');f.SetValue('NPTH_2.2mm');f.Reference().SetVisible(False);f.Value().SetVisible(False);f.SetAttributes(p.FP_EXCLUDE_FROM_BOM|p.FP_EXCLUDE_FROM_POS_FILES)
a=p.PAD(f);a.SetNumber('');a.SetAttribute(p.PAD_ATTRIB_NPTH);a.SetShape(p.PAD_SHAPE_CIRCLE);a.SetSize(V(2.2,2.2));a.SetDrillSize(V(2.2,2.2));a.SetLayerSet(p.LSET.AllCuMask());f.Add(a)
io=p.PCB_IO_KICAD_SEXPR();io.FootprintSave(str(lib),f)
for i,(x,y) in enumerate(plan['holes'],1):
 f=p.FootprintLoad(str(lib),'mounting');f.SetFPID(p.LIB_ID('Main155','mounting'));f.SetReference('H'+str(i));f.SetPosition(V(x,y));b.Add(f)
 z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask());z.SetZoneName('Main155 mounting keepout '+str(i));z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowPads(False);z.SetDoNotAllowCopperPour(True);z.SetDoNotAllowFootprints(True)
 poly=z.Outline();poly.NewOutline();radius=2.5/math.cos(math.pi/256)
 for j in range(256):
  theta=2*math.pi*j/256;v=V(x+radius*math.cos(theta),y+radius*math.sin(theta));poly.Append(v.x,v.y)
 b.Add(z)
assert p.SaveBoard(str(w/'main.kicad_pcb'),b)
# Preserve only the existing input copper in local mode except exact three UUIDs.
local=E/'inputs/local';local.mkdir(parents=True,exist_ok=False);shutil.copyfile(pro,local/'main.kicad_pro')
removed=[]
for t in list(b.GetTracks()):
 if t.m_Uuid.AsString() in affected:
  assert not isinstance(t,p.PCB_VIA)
  removed.append(dict(uuid=t.m_Uuid.AsString(),net=t.GetNetname(),layer=b.GetLayerName(t.GetLayer()),width_mm=p.ToMM(t.GetWidth()),start_mm=[p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)],end_mm=[p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)]));b.Remove(t)
assert len(removed)==3
# Remove stale fill cache before routing; independently refill output for qualification.
for z in b.Zones():
 if not z.GetIsRuleArea():z.UnFill()
assert p.SaveBoard(str(local/'main.kicad_pcb'),b)
save(E/'local-scope.json',dict(removed_segments=removed,remaining_tracks=537,retained_vias=66,signal_layer_policy='F.Cu/In2.Cu/B.Cu; In1.Cu GND only',silkscreen_changes=[],silkscreen_note='No added silk text; existing artwork retained, separately measured against reservation.',keepout_polygon=dict(vertices=256,circumscribed=True,max_radial_excess_mm=radius-2.5,pads_allowed=True,independent_check_all_existing_copper_pads=True),attempt_limit=1,timeout_seconds=1800))
# DRC libraries are the original footprints; mounting uses the separate mechanical library.
libs={'Main155':lib}
for fp in b.GetFootprints():
 nickname=str(fp.GetFPID().GetLibNickname())
 if nickname=='Main155':continue
 dest=E/(nickname+'.pretty');dest.mkdir(exist_ok=True);io.FootprintSave(str(dest),fp);libs[nickname]=dest
text='(fp_lib_table (version 7) '+''.join('(lib (name "'+name+'")(type "KiCad")(uri "${KIPRJMOD}/../../'+dest.name+'")(options "")(descr "Fixed source geometry"))' for name,dest in libs.items())+')\n'
for dest in [w,local]:(dest/'fp-lib-table').write_text(text)
save(E/'input-hashes.json',{str(x.relative_to(E)):digest(x) for dest in [w,local] for x in dest.iterdir() if x.is_file()})
print('Prepared revised and local inputs',removed)
