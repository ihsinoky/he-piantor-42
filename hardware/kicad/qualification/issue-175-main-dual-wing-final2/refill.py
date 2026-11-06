"""Independent KiCad refill with the pinned input project, never router project rules."""
from common import *
import pcbnew as p,shutil,collections
label=sys.argv[1];source=E/'inputs'/label;raw=E/'runs'/label;w=E/'inspection'/label;w.mkdir(parents=True,exist_ok=True)
assert not (w/'physical-readback.json').exists(), 'Do not overwrite completed refill evidence'
manager=p.GetSettingsManager();manager.LoadProject(str(source/'main.kicad_pro'))
b=p.LoadBoard(str(source/'main.kicad_pcb'));b.SetProject(manager.Prj());assert p.SaveBoard(str(w/'canonical-input.kicad_pcb'),b)
b=p.LoadBoard(str(raw/'out.kicad_pcb'));b.SetProject(manager.Prj());shutil.copyfile(source/'main.kicad_pro',w/'main.kicad_pro');shutil.copyfile(source/'fp-lib-table',w/'fp-lib-table')
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();assert p.SaveBoard(str(w/'main.kicad_pcb'),b)
tracks=collections.Counter();widths=collections.Counter();vias=collections.Counter()
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):vias[f'{p.ToMM(t.GetWidth(p.F_Cu)):g}/{p.ToMM(t.GetDrillValue()):g}']+=1
 else:tracks[b.GetLayerName(t.GetLayer())]+=1;widths[f'{p.ToMM(t.GetWidth()):g}']+=1
save(w/'physical-readback.json',dict(utc=now(),kicad_version=p.GetBuildVersion(),thickness_mm=p.ToMM(b.GetDesignSettings().GetBoardThickness()),copper_layers=[b.GetLayerName(x) for x in b.GetEnabledLayers().CuStack()],tracks_per_layer=dict(tracks),track_width_mm_counts=dict(widths),via_diameter_drill_mm_counts=dict(vias),zones=[dict(net=z.GetNetname(),layer=b.GetLayerName(z.GetLayer()),filled=z.IsFilled(),area_internal=z.CalculateFilledArea()) for z in b.Zones() if not z.GetIsRuleArea()],rule_areas=sum(z.GetIsRuleArea() for z in b.Zones()),original_input_project_used=True,refilled=True))
print('Refilled',label)
