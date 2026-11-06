"""Independent saved-board DRC, physical copper graph, transfer and width audit."""
from common import *
import sys,shutil,collections,importlib.util
sys.path.insert(0,str(T/'geometry/lib/python3.12/site-packages'))
import sexpdata as sx
cell,board,tool=sys.argv[1:];source=E/'cell-inputs'/cell;raw=E/'runs'/cell;floor=json.loads((source/'condition.json').read_text())['width_mm']
w=E/'inspection'/cell;w.mkdir(parents=True,exist_ok=False)
metrics=dict(required_unconnected=None,wrong_net_contacts=None,material_violations=None,unexplained_transfer_changes=None)
if not (raw/'out.kicad_pcb').exists():
 save(w/'assessment.json',dict(pass_acceptance=False,metrics=metrics,measured_unconnected=None,reason='No saved routed PCB'));sys.exit(0)
for ext in ['kicad_pcb','kicad_pro']:shutil.copy2(raw/'out.kicad_pcb' if ext=='kicad_pcb' else source/'main.kicad_pro',w/('main.'+ext))
shutil.copy2(source/'fp-lib-table',w/'fp-lib-table')
reader=R/'hardware/kicad/qualification/eda-004g/resume-02/read-pcb.py'
assert run(cell+'-snapshot-input',['/usr/bin/python3',reader,source/'main.kicad_pcb',w/'input-snapshot.json'],timeout=120)==0
assert run(cell+'-snapshot-output',['/usr/bin/python3',reader,w/'main.kicad_pcb',w/'snapshot.json'],timeout=120)==0
rc=run(cell+'-independent-drc',[T/'kicad/usr/bin/kicad-cli','pcb','drc','--format','json','--severity-all','-o',w/'drc.json',w/'main.kicad_pcb'],timeout=180)
assert rc==0
before=sx.loads((source/'main.kicad_pcb').read_text());after=sx.loads((raw/'out.kicad_pcb').read_text())
def inv(tree):return collections.Counter(sx.dumps(n) for n in tree[1:] if not isinstance(n,list) or not n or str(n[0]) not in ['segment','via'])
a,b=inv(before),inv(after);removed=list((a-b).elements());added=list((b-a).elements())
orig=json.loads((w/'input-snapshot.json').read_text());snap=json.loads((w/'snapshot.json').read_text())
semantic_changes={k:dict(before=orig[k],after=snap[k]) for k in orig if k!='tracks' and orig[k]!=snap[k]}
save(w/'transfer-diff.json',dict(nonroute_removed=removed,nonroute_added=added,snapshot_changes=semantic_changes))
tracks=[t for t in snap['tracks'] if t['kind']=='track'];widths=collections.Counter(str(t['width']) for t in tracks)
inpro=json.loads((source/'main.kicad_pro').read_text());outpro=json.loads((raw/'out.kicad_pro').read_text()) if (raw/'out.kicad_pro').exists() else None
def delta(a,b,path=()):
 if isinstance(a,dict) and isinstance(b,dict):
  rows=[]
  for k in sorted(set(a)|set(b)):
   if k not in a or k not in b:rows.append(dict(path=list(path+(k,)),before=a.get(k),after=b.get(k)))
   else:rows.extend(delta(a[k],b[k],path+(k,)))
  return rows
 return [] if a==b else [dict(path=list(path),before=a,after=b)]
project_changes=delta(inpro,outpro) if outpro is not None else []
width_audit=dict(track_width_histogram_mm=dict(widths),minimum_track_width_mm=min(map(float,widths)) if widths else None,tracks_below_pinned=sum(t['width']<(floor if t['net'] in ['HALL_5V','GND'] else .1)-1e-9 for t in tracks),output_project_exists=outpro is not None,output_project_changes=project_changes,output_project_min_width=None if outpro is None else outpro['board']['design_settings']['rules']['min_track_width'])
width_pass=width_audit['tracks_below_pinned']==0
if tool=='KRT':
 width_pass=width_pass and outpro is not None and outpro['board']['design_settings']['rules']['min_track_width']==inpro['board']['design_settings']['rules']['min_track_width']
 if outpro is not None:width_pass=width_pass and outpro['net_settings']['classes']==inpro['net_settings']['classes']
if tool=='FAB':
 ses=sx.loads((raw/'out.ses').read_text())
 def children(n,k):return [x for x in n if isinstance(x,list) and x and str(x[0])==k]
 routes=children(ses,'routes')[0];res=children(routes,'resolution')[0];assert str(res[1])=='um';permm=1000*float(res[2]);network=children(routes,'network_out')[0];paths=[]
 for net in children(network,'net'):
  for wire in children(net,'wire'):
   path=children(wire,'path')[0];paths.append(dict(net=str(net[1]),layer=str(path[1]),width_mm=float(path[2])/permm))
 width_audit.update(ses_paths=paths,ses_resolution=str(res),ses_paths_below_pinned=sum(q['width_mm']<floor-1e-9 for q in paths),minimum_ses_path_width_mm=min((q['width_mm'] for q in paths),default=None))
 width_pass=width_pass and width_audit['ses_paths_below_pinned']==0
width_audit['classes']={}
for label,names,required in [('Power',['HALL_5V','GND'],floor),('Signal',sorted(set(t['net'] for t in tracks)-{'HALL_5V','GND'}),.1)]:
 ts=[t for t in tracks if t['net'] in names]
 width_audit['classes'][label]=dict(nets=names,required_width_mm=required,segments=len(ts),minimum_mm=min((t['width'] for t in ts),default=None),histogram_mm=dict(collections.Counter(str(t['width']) for t in ts)),below_required=sum(t['width']<required-1e-9 for t in ts))
# Audit EVERY project key: only KRT provenance and measured-width records may be added.
# Power-width records must equal the prescribed class widths; all actual settings stay identical.
allowed=[q for q in project_changes if q['path']==['kicad_routing_tools'] and q['before'] is None and set(q['after'])=={'fab_floor_origin','records_rev','power_widths','same_net_pad_clearance'} and q['after']['same_net_pad_clearance']==.1 and q['after']['power_widths']=={'HALL_5V':floor,'GND':floor}]
width_audit['unexplained_project_changes']=[q for q in project_changes if q not in allowed]
width_pass=width_pass and not width_audit['unexplained_project_changes']
vs=[t for t in snap['tracks'] if t['kind']=='via']
width_audit['via_count']=len(vs)
width_audit['via_dimensions']=dict(collections.Counter(str((t['size'],t['drill'])) for t in vs))
width_audit['incorrect_vias']=sum(abs(t['size']-.6)>1e-9 or abs(t['drill']-.3)>1e-9 for t in vs)
width_pass=width_pass and width_audit['incorrect_vias']==0
save(w/'width-audit.json',width_audit)
drc=json.loads((w/'drc.json').read_text());unconnected=len(drc['unconnected_items']);printing={'text_height','silk_overlap','silk_over_copper'};material=[v for v in drc['violations'] if v['type'] not in printing]
# Always measure all four metrics, including on failed candidates.
if True:
 spec=importlib.util.spec_from_file_location('independent',R/'hardware/kicad/qualification/issue-87-native-main-routing/check-main.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 # Same exact conservative broad phase as #129 graph completion.
 import inspect
 code=inspect.getsource(m.connectivity)
 code=code.replace('    parent=list(range(len(copper)))', "    bounds=[a['geometry'].bounds for a in copper]\n    parent=list(range(len(copper)))")
 needle='            z=copper[j]\n'
 assert code.count(needle)==1
 code=code.replace(needle,needle+'            aa,bb=bounds[i],bounds[j]\n            if aa[0]-bb[2]>.000002 or bb[0]-aa[2]>.000002 or aa[1]-bb[3]>.000002 or bb[1]-aa[3]>.000002:continue\n')
 save(w/'graph-method.json',dict(oracle_sha256=digest(R/'hardware/kicad/qualification/issue-87-native-main-routing/check-main.py'),executed_connectivity_source=code,reference_predicates_unchanged=True))
 exec(compile(code,'<conservative-bounds-connectivity>','exec'),m.__dict__)
 graph=m.snapshot_graph(snap);save(w/'copper-graph.json',graph)
 metrics=dict(required_unconnected=sum(v-1 for v in graph['disconnected'].values()),wrong_net_contacts=len(graph['shorts']),material_violations=len(material),unexplained_transfer_changes=len(removed)+len(added))
accept=dict(cell=cell,board=board,tool=tool,metrics=metrics,measured_unconnected=unconnected,independent_material_drc_count=len(material),drc_type_counts=dict(collections.Counter(v['type'] for v in drc['violations'])),width_pass=width_pass,nonroute_snapshot_unchanged=not semantic_changes,pass_acceptance=unconnected==0 and all(v==0 for v in metrics.values()) and width_pass and not semantic_changes,original_project_used_for_drc=True,output_project_audited=True,utc=now())
save(w/'assessment.json',accept);print(json.dumps(accept,indent=2))
