"""Independent saved-PCB DRC, route widths and full nonroute semantic differences."""
import runpy,shutil,sys,collections
sys.dont_write_bytecode=True
from pathlib import Path
E=Path(__file__).resolve().parent;globals().update(runpy.run_path(str(E/'prepare-inputs.py')))
# Use the pinned geometry parser independently of KRT.
sys.path.insert(0,str(RT/'geometry/lib/python3.12/site-packages'))
import sexpdata as sx
stage=sys.argv[1];source=E/'inputs'/stage;raw=E/'runs'/stage;w=E/'inspection'/stage;w.mkdir(parents=True,exist_ok=False)
shutil.copyfile(raw/'out.kicad_pcb',w/'main.kicad_pcb');shutil.copyfile(source/'main.kicad_pro',w/'main.kicad_pro')
assert digest(w/'main.kicad_pcb')==digest(raw/'out.kicad_pcb')
assert run(stage+'-read-output',['/usr/bin/python3',OLD/'read-pcb.py',w/'main.kicad_pcb',w/'snapshot.json'])==0
before=sx.loads((source/'main.kicad_pcb').read_text());after=sx.loads((raw/'out.kicad_pcb').read_text())
def inventory(tree,tags=None,exclude=()):return collections.Counter(sx.dumps(n) for n in tree[1:] if not isinstance(n,list) or not n or ((tags is None or str(n[0]) in tags) and str(n[0]) not in exclude))
a=inventory(before,exclude=('segment','via'));b=inventory(after,exclude=('segment','via'))
removed=list((a-b).elements());added=list((b-a).elements())
oldroutes=inventory(before,tags=('segment','via'));newroutes=inventory(after,tags=('segment','via'))
missing=list((oldroutes-newroutes).elements())
snap=json.loads((w/'snapshot.json').read_text());orig=json.loads((source/'snapshot.json').read_text());snapshot_changes={k:dict(before=orig[k],after=snap[k]) for k in orig if k!='tracks' and orig[k]!=snap[k]}
widths=collections.Counter(str(t['width']) for t in snap['tracks'] if t['kind']=='track')
static=dict(tracks=sum(widths.values()),width_mm_counts=dict(widths),minimum_mm=min(map(float,widths)) if widths else None,below_020=sum(v for k,v in widths.items() if float(k)<.2),copper_layers=snap['layers'],vias=sum(t['kind']=='via' for t in snap['tracks']),all_tracks=snap['tracks'])
save(E/f'{stage}-width-inspection.json',static)
diff=dict(nonroute_removed=removed,nonroute_added=added,source_route_records_removed=missing,source_route_records_added=list((newroutes-oldroutes).elements()),snapshot_nonroute_changes=snapshot_changes,raw_output_project_changed=(raw/'out.kicad_pro').exists() and json.loads((raw/'out.kicad_pro').read_text())!=json.loads((source/'main.kicad_pro').read_text()))
def project_delta(a,b,path=()):
 if isinstance(a,dict) and isinstance(b,dict):
  rows=[]
  for key in sorted(set(a)|set(b)):
   if key not in a:rows.append(dict(path=list(path+(key,)),kind='added',after=b[key]))
   elif key not in b:rows.append(dict(path=list(path+(key,)),kind='removed',before=a[key]))
   else:rows.extend(project_delta(a[key],b[key],path+(key,)))
  return rows
 return [] if a==b else [dict(path=list(path),kind='changed',before=a,after=b)]
if (raw/'out.kicad_pro').exists():
 diff['output_project_changes']=project_delta(json.loads((source/'main.kicad_pro').read_text()),json.loads((raw/'out.kicad_pro').read_text()))
save(E/f'{stage}-board-diff.json',diff)
# Supply original footprints for library resolution only. Never alter either PCB.
code='''import pcbnew as p,sys\nfrom pathlib import Path\nw=Path(sys.argv[2]);b=p.LoadBoard(sys.argv[1]);lib=w/'Probe.pretty';lib.mkdir();io=p.PCB_IO_KICAD_SEXPR()\nfor f in b.GetFootprints():io.FootprintSave(str(lib),f)\n(w/'fp-lib-table').write_text(f'(fp_lib_table (version 7) (lib (name "Probe")(type "KiCad")(uri "{lib}")(options "")(descr "Original fixture")))\\n')\n'''
if stage=='main':
 (w/'fp-lib-table').write_text(f'(fp_lib_table (version 7) (lib (name "Qualification")(type "KiCad")(uri "{OLD}/library/Qualification.pretty")(options "")(descr "Original fixture")))\n')
if stage=='smoke':assert run('smoke-library',['/usr/bin/python3','-c',code,source/'main.kicad_pcb',w])==0
assert run(stage+'-independent-drc',[RT/'kicad/usr/bin/kicad-cli','pcb','drc','--format','json','--severity-all','-o',w/'drc.json',w/'main.kicad_pcb'])==0
drc=json.loads((w/'drc.json').read_text());unconnected=len(drc['unconnected_items']);printing={'text_height','silk_overlap','silk_over_copper'};material=[x for x in drc['violations'] if x['type'] not in printing]
metrics=dict(required_unconnected=None,wrong_net_contacts=None,material_violations=None,unexplained_transfer_changes=None)
if unconnected==0:
 import importlib.util
 spec=importlib.util.spec_from_file_location('independent',P/'check-main.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 graph=m.snapshot_graph(snap)
 save(E/f'{stage}-copper-graph.json',graph)
 metrics=dict(required_unconnected=len(graph['disconnected']),wrong_net_contacts=len(graph['shorts']),material_violations=len(material),unexplained_transfer_changes=len(removed)+len(added)+len(missing))
 # Historical checker independently corroborates success; own differences remain enumerated even on failure.
 if not any(metrics.values()) and not snapshot_changes:
  run(stage+'-historical-oracle',['/usr/bin/python3',P/'resume-01/check-import.py',stage,source/'main.kicad_pcb',w/'main.kicad_pcb',source/'snapshot.json',w/'snapshot.json',w/'drc.json',E/f'{stage}-historical-acceptance.json'])
accept=dict(metrics=metrics,measured_kicad_unconnected_items=unconnected,independent_material_drc_count=len(material),drc_type_counts=dict(collections.Counter(x['type'] for x in drc['violations'])),board_diff=diff,static_width_pass=static['below_020']==0,original_project_used_for_drc=True,pass_acceptance=unconnected==0 and all(x==0 for x in metrics.values()) and static['below_020']==0 and not snapshot_changes)
save(E/f'{stage}-independent.json',accept)
if stage=='smoke':save(E/'smoke-gate.json',dict(pass_=accept['pass_acceptance'],**{'pass':accept['pass_acceptance']},utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),metrics=metrics))
print(json.dumps({k:v for k,v in accept.items() if k!='board_diff'},indent=2))
