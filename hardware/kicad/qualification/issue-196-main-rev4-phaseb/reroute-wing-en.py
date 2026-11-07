"""Reroute WING_EN with an explicit native via-only keepout over J2.7."""
from common import *
import pcbnew as p,importlib.util,sexpdata as sx,shutil
spec=importlib.util.spec_from_file_location('audit',E/'audit-vias.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
src=E/'inspection/auto02/main.kicad_pcb';ast=sx.loads(src.read_text())
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
net=next(int(n[1]) for n in ast if tag(n)=='net' and n[2]=='WING_EN')
ast=[n for n in ast if not (tag(n) in ['segment','via'] and any(tag(c)=='net' and int(c[1])==net for c in n))]
seed=T/'wing-en-stripped.kicad_pcb';seed.write_text(sx.dumps(ast));b=p.LoadBoard(str(seed));pad=next(pad for f in b.GetFootprints() if f.GetReference()=='J2' for pad in f.Pads() if pad.GetNumber()=='7');g=a.pad_polygon(pad,p.F_Cu).buffer(.13,quad_segs=16)
z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask());z.SetDoNotAllowTracks(False);z.SetDoNotAllowVias(True);z.SetDoNotAllowCopperPour(False);z.SetDoNotAllowPads(False);z.Outline().NewOutline()
for x,y in list(g.exterior.coords)[:-1]:z.Outline().Append(p.FromMM(x),p.FromMM(y))
b.Add(z);w=E/'runs/auto03';w.mkdir(parents=True,exist_ok=True);p.SaveBoard(str(w/'in.kicad_pcb'),b);shutil.copyfile(E/'inputs/final/main.kicad_pro',w/'in.kicad_pro')
# The extra native rule area is a documented design addition, also carried by
# the reference input for the independent routing transfer comparison.
base=p.LoadBoard(str(E/'inputs/final/main.kicad_pcb'));duplicate=z.Duplicate();base.Add(duplicate);p.SaveBoard(str(E/'inputs/final/main.kicad_pcb'),base)
ref=E/'inputs/final/main.kicad_pcb';ref.write_text(ref.read_text().replace(duplicate.m_Uuid.AsString(),z.m_Uuid.AsString()))
args=['--escalation','off','--track-width','0.1','--clearance','0.13','--same-net-pad-clearance','0.13','--via-size','0.6','--via-drill','0.3','--layers','F.Cu','In1.Cu','In2.Cu','B.Cu','--layer-costs','1','-1','1','1','--nets','WING_EN','--keep-input-copper']
save(w/'conditions.json',dict(source_sha256=digest(src),removed_route_net='WING_EN',native_via_keepout_uuid=z.m_Uuid.AsString(),pad_buffer_mm=.13,args=args))
sys.exit(run('auto03',[B/'venv/bin/python3',K/'py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb']+args,cwd=K,timeout=1200))
