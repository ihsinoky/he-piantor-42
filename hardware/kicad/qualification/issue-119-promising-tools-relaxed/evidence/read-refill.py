"""KiCad independent SES transfer, canonical reference, refill and plane readback."""
from helpers import *
import pcbnew as p
import shutil
label,router=sys.argv[1:];source=E/'inputs'/label
raw=E/'runs'/label/router;w=E/'inspection'/label/router;w.mkdir(parents=True,exist_ok=False)
manager=p.GetSettingsManager();manager.LoadProject(str(source/'main.kicad_pro'))
b=p.LoadBoard(str(source/'main.kicad_pcb'));b.SetProject(manager.Prj())
assert p.SaveBoard(str(w/'canonical-input.kicad_pcb'),b)
if router in ['fab','free']:
 assert p.ImportSpecctraSES(b,str(raw/'out.ses'))
 assert p.SaveBoard(str(raw/'out.kicad_pcb'),b)
else:
 b=p.LoadBoard(str(raw/'out.kicad_pcb'));b.SetProject(manager.Prj())
# Raw output retained before the independent refill.
shutil.copyfile(source/'main.kicad_pro',w/'main.kicad_pro')
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity()
assert p.SaveBoard(str(w/'main.kicad_pcb'),b)
zones=[]
for z in b.Zones():
 connected=[]
 for fp in b.GetFootprints():
  for pad in fp.Pads():
   if pad.GetNetCode()==z.GetNetCode():
    connected.append(dict(ref=fp.GetReference(),pad=pad.GetNumber(),uuid=pad.m_Uuid.AsString(),on_plane_layer=pad.IsOnLayer(p.In1_Cu)))
 zones.append(dict(net=z.GetNetname(),layer=b.GetLayerName(z.GetLayer()),filled=z.IsFilled(),filled_area_internal=z.CalculateFilledArea(),same_net_pads=connected))
tracks={b.GetLayerName(i):0 for i in b.GetEnabledLayers().CuStack()};widths={};vias={}
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):
  key=f'{p.ToMM(t.GetWidth()):g}/{p.ToMM(t.GetDrillValue()):g}';vias[key]=vias.get(key,0)+1
 else:
  key=b.GetLayerName(t.GetLayer());tracks[key]=tracks.get(key,0)+1
  key=f'{p.ToMM(t.GetWidth()):g}';widths[key]=widths.get(key,0)+1
# Original libraries only, supplied for DRC's library comparison.
libs={};io=p.PCB_IO_KICAD_SEXPR()
original=p.LoadBoard(str(source/'main.kicad_pcb'))
for fp in original.GetFootprints():
 nickname=str(fp.GetFPID().GetLibNickname());assert nickname
 lib=w/(nickname+'.pretty');lib.mkdir(exist_ok=True);io.FootprintSave(str(lib),fp);libs[nickname]=lib
(w/'fp-lib-table').write_text('(fp_lib_table (version 7) '+''.join(f'(lib (name "{name}")(type "KiCad")(uri "{lib}")(options "")(descr "Original fixed fixture"))' for name,lib in libs.items())+')\n')
save(w/'physical-readback.json',dict(utc=utc(),kicad_version=p.GetBuildVersion(),refill_performed=True,zones=zones,track_width_mm_counts=widths,via_diameter_drill_mm_counts=vias,tracks_per_layer=tracks,In1_signal_tracks=tracks.get('In1.Cu',0)))
