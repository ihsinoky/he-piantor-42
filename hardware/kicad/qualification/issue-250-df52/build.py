"""DF52 study construction. Run under runtime wrapper; baseline inputs read only."""
from pathlib import Path
import pcbnew as p, math, json, shutil, hashlib
from shapely.geometry import Polygon,LineString,Point
E=Path(__file__).resolve().parent; R=E.parents[3]; T=R/'.issue250-runtime'
F='DF52-14S-0.8H_14'; lib=E/'DF52.pretty';lib.mkdir(exist_ok=True)
# Hirose catalogue p3: B=10.4, 0.8 pitch, contact .5x1, nail .9x1.6,
# total land depth 3.22. Origin at land-depth midpoint, as KiCad reference.
s=f'''(footprint "{F}" (version 20241229) (generator "issue250") (layer "F.Cu")
 (descr "Hirose DF52-14S-0.8H(21); catalogue p3; 1.2 mm PCB; .10 mm stencil 100% apertures")
 (attr smd)
 (fp_text reference "REF**" (at 0 -2.5) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))
 (fp_text value "DF52-14S-0.8H(21)" (at 0 3.4) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))
 (fp_rect (start -6.7 -1.26) (end 6.7 1.51) (stroke (width .1) (type default)) (fill none) (layer "F.Fab"))
 (fp_rect (start -7.15 -1.86) (end 7.15 3.09) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))
 (fp_line (start -5.45 -1.85) (end -4.95 -1.85) (stroke (width .15) (type default)) (layer "F.Fab"))
'''
for i in range(14):s+=f' (pad "{i+1}" smd rect (at {-.8*6.5+.8*i:.3f} -1.11) (size .5 1) (layers "F.Cu" "F.Paste" "F.Mask"))\n'
for x in [-6.45,6.45]:s+=f' (pad "MP" smd rect (at {x} .81) (size .9 1.6) (layers "F.Cu" "F.Paste" "F.Mask"))\n'
# Conservative study no-pattern reservation under body, excluding solder lands.
# Exact manufacturer no-pattern release remains a separately reported review gate.
s+=''' (zone (net 0) (net_name "") (layers "F.Cu") (hatch edge .5)
  (connect_pads (clearance 0)) (min_thickness .01) (filled_areas_thickness no)
  (keepout (tracks not_allowed) (vias not_allowed) (pads allowed) (copperpour not_allowed) (footprints allowed))
  (polygon (pts (xy -5.95 -.55) (xy 5.95 -.55) (xy 5.95 1.61) (xy -5.95 1.61))))
)'''
(lib/(F+'.kicad_mod')).write_text(s)
# Passive 14 cavity symbol, two identical mechanical pads mapped to one MP pin.
pins=['HALL_5V','GND','MUX_A0','GND','MUX_A1','MUX_A2','WING_EN','GND','MUX_OUT_A','GND','MUX_OUT_B','GND','MUX_OUT_C','GND','MP']
s='''(kicad_symbol_lib (version 20241209) (generator "issue250")
 (symbol "DF52-14S-0.8H_14" (pin_names (offset 1.016)) (in_bom yes) (on_board yes)
 (property "Reference" "J" (at 0 22.86 0) (effects (font (size 1.27 1.27))))
 (property "Value" "DF52-14S-0.8H(21)" (at 0 20.32 0) (effects (font (size 1.27 1.27))))
 (property "Footprint" "DF52:DF52-14S-0.8H_14" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
 (symbol "DF52-14S-0.8H_14_0_1" (rectangle (start 0 19.05) (end 20.32 -20.32) (stroke (width .254) (type default)) (fill (type background))))
 (symbol "DF52-14S-0.8H_14_1_1"
'''
for i,n in enumerate(pins):
 y=17.78-2.54*i;s+=f' (pin {"no_connect" if n=="MP" else "passive"} line (at -5.08 {y:.2f} 0) (length 5.08) (name "{n}" (effects (font (size 1.27 1.27)))) (number "{i+1 if n!="MP" else "MP"}" (effects (font (size 1.27 1.27)))))\n'
s+=')))';(E/'DF52.kicad_sym').write_text(s)
def xy(v):return [p.ToMM(v.x),p.ToMM(v.y)]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
sources={'main':E.parent/'issue-240-main-rev7/inspection/final/main.kicad_pcb'}
sources.update({w.name:w/'main.kicad_pcb' for w in (E.parent/'issue-235-wing-round2').glob('wing-rev4-*')})
records=[]
parents=[]
for name,src in sources.items():
 w=E/name;w.mkdir(exist_ok=True);b=p.LoadBoard(str(src)); parents.append(b); regions=[]; changes=[]; native_tracks=list(b.GetTracks());parents.extend(native_tracks)
 oldfeet=list(b.GetFootprints());parents.extend(oldfeet)
 for old in oldfeet:
  if old.GetReference() not in ('J2','J3','J_WING'):continue
  f=p.FootprintLoad(str(lib),F);assert f;b.Add(f)
  f.SetReference(old.GetReference());f.SetValue('DF52-14S-0.8H(21)')
  if old.GetLayer()==p.B_Cu:f.Flip(f.GetPosition(),False)
  f.SetPosition(old.GetPosition());f.SetOrientationDegrees(old.GetOrientationDegrees());f.SetPath(old.GetPath())
  f.SetFPID(p.LIB_ID('DF52',F))
  nets={a.GetNumber():a.GetNet() for a in old.Pads()}
  for a in f.Pads():
   if a.GetNumber()!='MP':a.SetNet(nets[a.GetNumber()])
  ang=math.radians(old.GetOrientationDegrees());x,y=xy(old.GetPosition())
  def tr(u,v):return [x+u*math.cos(ang)+v*math.sin(ang),y-u*math.sin(ang)+v*math.cos(ang)]
  regions.append(Polygon([tr(u,v) for u,v in [(-11,-3.3),(11,-3.3),(11,3.3),(-11,3.3)]]))
  changes.append(dict(ref=f.GetReference(),native_origin_mm=xy(f.GetPosition()),angle_deg=f.GetOrientationDegrees(),side=b.GetLayerName(f.GetLayer()),translation_mm=[0,0],rotation_delta_deg=0,old_sha256=sha(src),cavity_nets={a.GetNumber():a.GetNetname() for a in f.Pads()}));b.Remove(old)
 removed=[]
 for t in native_tracks:
  if isinstance(t,p.PCB_VIA):g=Point(xy(t.GetPosition())).buffer(p.ToMM(t.GetWidth())/2)
  else:g=LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2)
  if any(g.intersects(r) for r in regions):removed.append(dict(uuid=t.m_Uuid.AsString(),net=t.GetNetname()));b.Remove(t)
 p.SaveBoard(str(w/'input.kicad_pcb'),b)
 pro=src.with_suffix('.kicad_pro');assert pro.exists();shutil.copyfile(pro,w/'input.kicad_pro');shutil.copyfile(pro,w/'main.kicad_pro')
 (w/'fp-lib-table').write_text('(fp_lib_table (lib (name "DF52") (type "KiCad") (uri "${KIPRJMOD}/../DF52.pretty") (options "") (descr "Issue250 study")))\n')
 rec=dict(name=name,source=str(src.relative_to(R)),source_sha256=sha(src),poses=changes,removed=removed,routing_windows_native_mm=[list(r.exterior.coords) for r in regions]);(w/'construction.json').write_text(json.dumps(rec,indent=2)+'\n');records.append(rec)
(E/'construction.json').write_text(json.dumps(records,indent=2)+'\n')
print([(x['name'],len(x['removed'])) for x in records])
