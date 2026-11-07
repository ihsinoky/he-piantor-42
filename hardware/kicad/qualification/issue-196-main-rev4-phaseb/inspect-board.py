"""Independent original-project refill, DRC, physical graph and transfer check."""
from common import *
import pcbnew as p,shutil,collections,sexpdata as sx
label=sys.argv[1] if len(sys.argv)>1 else 'auto01';raw=E/'runs'/label;w=E/'inspection'/label;w.mkdir(parents=True,exist_ok=True)
source=E/'inputs/final'
manager=p.GetSettingsManager();manager.LoadProject(str(source/'main.kicad_pro'))
b=p.LoadBoard(str(source/'main.kicad_pcb'));b.SetProject(manager.Prj());p.SaveBoard(str(w/'canonical-input.kicad_pcb'),b)
b=p.LoadBoard(str(raw/'out.kicad_pcb'));b.SetProject(manager.Prj())
for name in ['main.kicad_pro','fp-lib-table']:shutil.copyfile(source/name,w/name)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();p.SaveBoard(str(w/'main.kicad_pcb'),b)
assert run(label+'-drc2',[B/'kicad/usr/bin/kicad-cli','pcb','drc','--format','json','--severity-all','-o',w/'drc.json',w/'main.kicad_pcb'])==0
reader=R/'hardware/kicad/qualification/eda-004g/resume-02/read-pcb.py'
assert run(label+'-snapshot2',['/usr/bin/python3',reader,w/'main.kicad_pcb',w/'snapshot.json'])==0
assert run(label+'-graph2',['/usr/bin/python3',E/'connectivity.py',label])==0
# Router is authorized to author all tracks/vias. Compare every nonroute node;
# only actual zone fill cache, not design settings, is normalized.
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def clean(n):
 if not isinstance(n,list):return n
 if tag(n)=='fill':n=[x for x in n if str(x)!='yes']
 return [clean(x) for x in n if tag(x) not in ['filled_polygon','fill_segments','filled_areas_thickness']]
def inv(path):return collections.Counter(sx.dumps(x) for x in clean(sx.loads(path.read_text()))[1:] if tag(x) not in ['segment','via'])
a=inv(w/'canonical-input.kicad_pcb');c=inv(w/'main.kicad_pcb');removed=list((a-c).elements());added=list((c-a).elements());save(w/'transfer-diff.json',dict(removed=removed,added=added,route_changes_authorized='all tracks and vias; no placement, pin, outline or zone rule changes',source_sha256=digest(source/'main.kicad_pcb'),output_sha256=digest(w/'main.kicad_pcb')))
d=json.loads((w/'drc.json').read_text());g=json.loads((w/'connectivity.json').read_text());printing={'text_height','silk_overlap','silk_over_copper'};material=[v for v in d['violations'] if v['type'] not in printing]
metrics=dict(required_unconnected=g['required_unconnected'],wrong_net_contacts=g['wrong_net_contacts'],material_violations=len(material),unexplained_transfer_changes=len(removed)+len(added))
tracks=list(b.GetTracks());conditions=dict(width=all(p.ToMM(t.GetWidth())>=.1 for t in tracks),via=all(p.ToMM(t.GetWidth())==.6 and p.ToMM(t.GetDrillValue())==.3 for t in tracks if isinstance(t,p.PCB_VIA)),GND_only_In1=not any(not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.In1_Cu for t in tracks))
save(w/'assessment.json',dict(metrics=metrics,pass_acceptance=all(x==0 for x in metrics.values()) and not d['unconnected_items'] and all(conditions.values()),measured_unconnected=len(d['unconnected_items']),nets_checked=g['nets_checked'],drc_type_counts=dict(collections.Counter(v['type'] for v in d['violations'])),conditions=conditions,track_count=sum(not isinstance(t,p.PCB_VIA) for t in tracks),via_count=sum(isinstance(t,p.PCB_VIA) for t in tracks)))
print(json.dumps(json.loads((w/'assessment.json').read_text()),indent=2))
