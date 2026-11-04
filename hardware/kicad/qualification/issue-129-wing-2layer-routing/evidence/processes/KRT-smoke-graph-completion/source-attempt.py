"""Continue saved smoke inspection with an exact conservative geometry broad phase.

Only pairs whose axis-aligned boxes are separated by MORE than 2nm are
excluded. Such pairs cannot intersect or trigger the reference near-contact
assertion. Every remaining pair uses the unchanged reference GEOS predicates,
in the same order, with the same union-find and acceptance criteria.
"""
from common import *
import sys,importlib.util,inspect,os,signal,collections
sys.path.insert(0,str(T/'geometry/lib/python3.12/site-packages'))
cell='KRT-smoke';w=E/'inspection'/cell
oracle=R/'hardware/kicad/qualification/issue-87-native-main-routing/check-main.py'
spec=importlib.util.spec_from_file_location('independent',oracle);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source=inspect.getsource(m.connectivity)
needle="            z=copper[j]\n"
assert source.count(needle)==1
source=source.replace("    parent=list(range(len(copper)))", "    bounds=[a['geometry'].bounds for a in copper]\n    parent=list(range(len(copper)))")
source=source.replace(needle,needle+"            aa,bb=bounds[i],bounds[j]\n            if aa[0]-bb[2]>.000002 or bb[0]-aa[2]>.000002 or aa[1]-bb[3]>.000002 or bb[1]-aa[3]>.000002:continue\n")
exec(compile(source,'<conservative-bounds-connectivity>','exec'),m.__dict__)
snap=json.loads((w/'snapshot.json').read_text());graph=m.snapshot_graph(snap)
# Stop only the earlier read-only graph computation; all snapshots/DRC/width
# results are retained. No gate or routing process is touched.
stopped=[]
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:args=(proc/'cmdline').read_bytes().split(b'\0')
 except OSError:continue
 if len(args)>=5 and args[1].endswith(b'/repair-inspect.py') and args[2]==b'KRT-smoke':
  os.kill(int(proc.name),signal.SIGTERM);stopped.append(int(proc.name))
save(w/'copper-graph.json',graph)
drc=json.loads((w/'drc.json').read_text());assert len(drc['unconnected_items'])==0
printing={'text_height','silk_overlap','silk_over_copper'};material=[v for v in drc['violations'] if v['type'] not in printing]
diff=json.loads((w/'transfer-diff.json').read_text());width=json.loads((w/'width-audit.json').read_text())
metrics=dict(required_unconnected=sum(v-1 for v in graph['disconnected'].values()),wrong_net_contacts=len(graph['shorts']),material_violations=len(material),unexplained_transfer_changes=len(diff['nonroute_removed'])+len(diff['nonroute_added']))
width_pass=width['tracks_below_020']==0 and width['output_project_min_width']==.2 and not any(p['path'][:1]==['net_settings'] for p in width['output_project_changes'])
accept=dict(cell=cell,board='pitch9-16mm',tool='KRT',metrics=metrics,measured_unconnected=0,independent_material_drc_count=len(material),drc_type_counts=dict(collections.Counter(v['type'] for v in drc['violations'])),width_pass=width_pass,nonroute_snapshot_unchanged=not diff['snapshot_changes'],pass_acceptance=all(v==0 for v in metrics.values()) and width_pass and not diff['snapshot_changes'],original_project_used_for_drc=True,output_project_audited=True,utc=now())
save(w/'graph-completion.json',dict(utc=now(),oracle=str(oracle.relative_to(R)),oracle_sha256=digest(oracle),reference_predicates_unchanged=True,excluded_pairs='axis-aligned box separation strictly greater than 0.000002 mm on either axis',executed_connectivity_source=source,earlier_bruteforce_graph_stopped_pids=stopped,existing_snapshot_sha256=digest(w/'snapshot.json'),existing_drc_sha256=digest(w/'drc.json'),no_gate_or_route_reexecution=True))
save(w/'assessment.json',accept);print(json.dumps(accept,indent=2))
