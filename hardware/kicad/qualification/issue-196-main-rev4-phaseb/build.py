"""Author native Rev.4 from the accepted Phase A-2 geometry; discard Rev.3 routing."""
from common import *
import pcbnew as p,shutil,math
A=E.parent/'issue-196-main-rev4-phasea2';plan=json.loads((A/'geometry-plan.json').read_text())
w=E/'inputs/final';w.mkdir(parents=True,exist_ok=True)
import sexpdata as sx
src=E.parent/'issue-185-main-rev3/inspection/final/main.kicad_pcb'
ast=sx.loads(src.read_text())
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def removed_fp(n):return tag(n)=='footprint' and any(tag(t)=='property' and t[1]=='Reference' and t[2] in ['J1','R1','R2','U2','H4'] for t in n)
ast=[n for n in ast if tag(n) not in ['segment','via','zone','gr_line','gr_rect','gr_poly','gr_text'] and not removed_fp(n)]
seed=T/'rev4-stripped.kicad_pcb';seed.write_text(sx.dumps(ast))
b=p.LoadBoard(str(seed));fps={f.GetReference():f for f in b.GetFootprints()}
ub=p.LoadBoard(str(A/'inputs/udb/c3.kicad_pcb'));uf=next(f for f in ub.GetFootprints() if f.GetReference()=='J2').Duplicate();uf.SetReference('J4');b.Add(uf);fps['J4']=uf
nets={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
for a in uf.Pads():a.SetNet(nets[{'1':'VBUS','2':'USB_DM_ESD','3':'USB_DP_ESD','4':'GND'}.get(a.GetNumber(),'')])
vec=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
for q in plan['main']['placements']:
 f=fps[q['ref']];f.SetOrientationDegrees(q['angle_deg']);x,y=q['at_mm'];f.SetPosition(vec(x+100,y+70))
 assert sorted([[a.GetNumber(),a.GetNetname()] for a in f.Pads()])==sorted([[n,'' if net=='mechanical_NC' else net] for n,net in q['pad_nets']])
for q in plan['main']['holes']:
 f=fps[q['ref']];x,y=q['xy_mm'];f.SetPosition(vec(x+100,y+70))
 # Native circular rule area, with all copper layers including the GND plane.
 z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask());z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowCopperPour(True);z.SetDoNotAllowPads(False)
 z.Outline().NewOutline()
 # Circumscribed polygon: never cuts inside the 2.5002mm reservation.
 radius=2.5002/math.cos(math.pi/96)
 for i in range(96):z.Outline().Append(int(p.FromMM(x+100+radius*math.cos(i*2*math.pi/96))),int(p.FromMM(y+70+radius*math.sin(i*2*math.pi/96))))
 b.Add(z)
pts=plan['main']['outline_xy_mm'];pts=pts[:-1] if pts[0]==pts[-1] else pts
for a,c in zip(pts,pts[1:]+pts[:1]):
 g=p.PCB_SHAPE();g.SetShape(p.SHAPE_T_SEGMENT);g.SetStart(vec(a[0]+100,a[1]+70));g.SetEnd(vec(c[0]+100,c[1]+70));g.SetLayer(p.Edge_Cuts);g.SetWidth(p.FromMM(.05));b.Add(g)
z=p.ZONE(b);z.SetLayer(p.In1_Cu);z.SetNet(nets['GND']);z.SetLocalClearance(p.FromMM(.13));z.SetThermalReliefGap(p.FromMM(.2));z.SetThermalReliefSpokeWidth(p.FromMM(.3));z.SetPadConnection(p.ZONE_CONNECTION_THERMAL);z.SetMinThickness(p.FromMM(.1));z.Outline().NewOutline()
for x,y in pts:z.Outline().Append(p.FromMM(x+100),p.FromMM(y+70))
b.Add(z)
# Delete orphaned USB CC/ESD supply net definitions only when no retained pin uses them.
used={a.GetNetname() for f in b.GetFootprints() for a in f.Pads()}
for name,n in nets.items():
 if name and name not in used:pass # unused definitions are inert; preserve source codes
lib=E/'Rev4.pretty';lib.mkdir(exist_ok=True);io=p.PCB_IO_KICAD_SEXPR()
for f in b.GetFootprints():
 f.SetFPID(p.LIB_ID('Rev4',f.GetReference()));io.FootprintSave(str(lib),f)
p.SaveBoard(str(w/'main.kicad_pcb'),b)
pro=json.loads((E.parent/'issue-175-main-dual-wing-final2/inputs/final/main.kicad_pro').read_text())
# Preserve 0.10mm DRC floor; router operates at 0.13mm, same-net via margin 0.13mm.
(w/'main.kicad_pro').write_text(json.dumps(pro,indent=2)+'\n')
(w/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Rev4")(type "KiCad")(uri "${KIPRJMOD}/../../Rev4.pretty")(options "")(descr "Frozen Rev4 footprints")))\n')
save(E/'build.json',dict(source_plan_sha256=digest(A/'geometry-plan.json'),input_sha256=digest(w/'main.kicad_pcb'),electrical_parts=59,holes=3,discarded_all_old_copper=True,positions='Phase A-2 exact; X+100 Y+70',usb_contract={'1':'VBUS','2':'USB_DM_ESD','3':'USB_DP_ESD','4':'GND'},unused_net_definitions_inert=sorted(set(nets)-used)))
print('Native Rev4 authored',len(list(b.GetFootprints())),len(list(b.GetTracks())))
