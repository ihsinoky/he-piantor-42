from pathlib import Path
import pcbnew as p,shutil,json
E=Path('hardware/kicad/qualification/issue-221-main-rev5');V=E.parent/'issue-196-main-rev4-phaseb';W=E/'inspection/final';W.mkdir(parents=True,exist_ok=True)
for name in ['main.kicad_pro','fp-lib-table']:shutil.copyfile(V/'inspection/final'/name,W/name)
lib=E/'Rev5.pretty';lib.mkdir(exist_ok=True)
src=(E/'sources/molex-kicad-official.kicad_mod').read_text()
# Rectangular manufacturer-sized lands also match the established independent reader.
src=src.replace('smd roundrect','smd rect').replace(' (roundrect_rratio 0.25)','').replace('(pad MP ', '(pad "" ')
(lib/'J4.kicad_mod').write_text(src)
b=p.LoadBoard(str(V/'inspection/final/main.kicad_pcb'));old=next(f for f in b.GetFootprints() if f.GetReference()=='J4')
f=p.FootprintLoad(str(lib.resolve()),'J4');f.SetReference('J4');f.SetValue('781710004');f.SetFPID(p.LIB_ID('Rev5','J4'))
f.SetPath(old.GetPath());f.SetPosition(old.GetPosition());f.SetOrientation(old.GetOrientation())
for a in f.Pads():
 if a.GetNumber():a.SetNet(b.FindNet({'1':'VBUS','2':'USB_DM_ESD','3':'USB_DP_ESD','4':'GND'}[a.GetNumber()]))
f.Reference().SetVisible(False);f.Value().SetVisible(False)
b.Remove(old);b.Add(f)
# Neck .60mm to y92.65, then widen outside the connector body.
# Remove two obsolete tiny GND stubs, retain every remote copper item.
for t in list(b.GetTracks()):
 if t.m_Uuid.AsString() in ['7f76d834-0815-4626-a391-8d8207bb3050','f4f81ea7-a3fd-4fa9-a8f6-707032ae6815','ab730888-87d3-42ae-bb44-27b7f2fb2c21']:b.Remove(t)
def route(net,points,width):
 for a,c in zip(points,points[1:]):
  t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(round(a[0]*1e6),round(a[1]*1e6)));t.SetEnd(p.VECTOR2I(round(c[0]*1e6),round(c[1]*1e6)));t.SetWidth(round(width*1e6));t.SetLayer(p.F_Cu);t.SetNet(b.FindNet(net));b.Add(t)
route('VBUS',[(101.8,91.875),(101.8,92.65)],.6)
route('VBUS',[(101.8,92.65),(101.8,94.5),(101.5,94.8),(101.5,95.4)],1.1)
route('GND',[(98.2,91.875),(98.2,92.65)],.6)
route('GND',[(98.2,92.65),(98.2,94.7),(98.1,94.8)],1.1)
route('USB_DM_ESD',[(100.6,91.875),(100.6,95.1),(100.5,95.2)],.1)
route('USB_DP_ESD',[(99.4,91.875),(99.4,95.1),(99.5,95.2)],.1)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();p.SaveBoard(str(W/'main.kicad_pcb'),b)
# Preserve non-J4 footprint libraries, add the exact J4 custom library.
(W/'fp-lib-table').write_text('(fp_lib_table\n(lib (name Rev4)(type KiCad)(uri "${KIPRJMOD}/../../../issue-196-main-rev4-phaseb/Rev4.pretty")(options "")(descr ""))\n(lib (name Rev5)(type KiCad)(uri "${KIPRJMOD}/../../Rev5.pretty")(options "")(descr ""))\n)\n')
print('Board saved')
