"""Offline acceptance: evidence cross-checks, hashes and authorized path scope."""
from pathlib import Path
import json,hashlib,gzip,csv,zipfile,subprocess,xml.etree.ElementTree as ET
E=Path(__file__).resolve().parent;R=E.parents[3];V=E.parent/'issue-221-main-rev5'
def j(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):return list(csv.DictReader(Path(p).open()))
h=sha(E/'inspection/final/main.kicad_pcb');m=j(E/'manifest.json')
for q in m['files']+m['inputs']:assert sha(R/q['path'])==q['sha256'],q['path']
d=j(E/'inspection/final/drc.json');erc=j(E/'schematic/erc-final.json');assert not d['violations'] and not d['unconnected_items'] and all(not s['violations'] for s in erc['sheets'])
for name in ['main.kicad_sch','main.kicad_pro','review.kicad_sym','sym-lib-table','main.net.xml']:assert (E/'schematic'/name).read_bytes()==(V/'schematic'/name).read_bytes()
s=j(E/'inspection/final/snapshot.json');old=j(V/'inspection/final/snapshot.json');assert s['components']==old['components'] and s['pads']==old['pads'] and s['tracks']==old['tracks'];assert s['rules']==old['rules']
g=j(E/'inspection/final/connectivity.json');assert g['nets_checked']==40 and g['required_unconnected']==g['wrong_net_contacts']==0 and all(n['component_count']==1 for n in g['nets'])
connected={a for n in g['nets'] for c in n['components'] for a in c['pads']};assert connected=={a['ref']+'.'+a['number']+'@'+a['uuid'] for a in s['pads'] if a['net']}
xroot=ET.parse(E/'schematic/main.net.xml');xp={(n.get('ref'),n.get('pin')):net.get('name').removeprefix('/') for net in xroot.findall('.//nets/net') for n in net.findall('node') if not n.get('ref').startswith('#')}
for a in s['pads']:
 if a['number']:assert xp[(a['ref'],a['number'])]==a['net'] if a['net'] else xp[(a['ref'],a['number'])].startswith('unconnected-')
diff=j(E/'rev5-diff-and-clearance.json');assert diff['pass_check'] and diff['rev6_sha256']==h and diff['rev5_sha256']==sha(V/'inspection/final/main.kicad_pcb')
assert diff['all_62_positions_and_angles_identical'] and diff['tracks_unchanged']==1143 and diff['vias_unchanged']==130 and diff['net_changes']==0
assert diff['minimum_new_edge_gap_mm']>=.5 and diff['rev6_outside_rev5_area_mm2']==0
assert len(diff['copper_changes'])==1 and diff['copper_changes'][0]['layer']=='In1.Cu' and diff['copper_changes'][0]['outside_corner_regions_beyond_2nm_mm2']==0
plan=j(E/'geometry-plan.json');assert plan['board_sha256']==h and len(plan['vertices'])==3 and len(s['edges'])==6
for v in plan['vertices']:assert abs(v['interior_angle_deg']-60)<1e-5 and all(abs(x-4)<.000003 for x in v['actual_leg_mm']) and v['face_length_mm']>3.99
adir=E/'inspection/final/audit/via-pad';a=j(adir/'summary.json');pairs=json.loads(gzip.decompress((adir/'all-pairs.json.gz').read_bytes()));assert a['source_sha256']==h
assert len(pairs)==30160 and len({(q['via_uuid'],q['pad_uuid']) for q in pairs})==30160 and min(q['annulus_gap_mm'] for q in pairs)==a['min_annulus_gap_mm']==.145
assert all(q['classification']=='none' and q['annulus_gap_mm']>=.1 for q in pairs)
power=j(E/'power-impact.json');assert power['rev6']['PCB_sha256']==h and power['rev5']['PCB_sha256']==sha(V/'inspection/final/main.kicad_pcb') and power['rev6']['values']['input_loop_ohm']<.05 and power['regulated_far_point_V']>=4.60
assert j(E/'power-budget.json')['board_sha256']==h and j(E/'ground-model-verification.json')['pass_numerics']
for path in ['power-extraction-final.json','ground-extraction-final.json']:
 q=j(E/path);assert q.get('PCB_sha256',q.get('board_sha256'))==h
assert len(j(E/'ground-extraction-final.json')['rows'])==4 and len(j(E/'power-extraction-final.json')['rows'])==16
for name in ['snapshot','native-drc','native-erc','physical-connectivity','via-pad-audit','positive-extraction','ground-extraction','release-gerbers','release-drill','release-paste','release-native-pos','cam-readback']:
 assert j(E/'processes'/name/'record.json')['exit_code']==0,name
cam=j(E/'cam-check.json');frame=j(E/'cpl-frame-check.json');assert cam['board_sha256']==frame['board_sha256']==h and cam['pass_check'] and frame['pass_check']
assert frame['rows']==frame['native_secondary_export_matches']==55 and frame['pairwise_vectors_checked']==1485 and frame['max_axis_error_mm']=='0' and frame['edge_segments']==6
for filename in ['BOM.csv','CPL.csv']:assert (E/'manufacturing'/filename).read_bytes()==(V/'manufacturing'/filename).read_bytes()
archive=E/'manufacturing/main-rev6-fabrication-review.zip';assert sha(archive)==cam['archive_sha256']
with zipfile.ZipFile(archive) as z:
 assert len(z.namelist())==11 and z.testzip() is None
 for q in cam['archive_members']:assert sha(E/'manufacturing/gerber'/q['name'])==q['sha256'] and z.read(q['name'])==(E/'manufacturing/gerber'/q['name']).read_bytes()
assert cam['plane_symmetric_difference_mm2']<1e-8
assert (E/'outline-comparison.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
git=['git','--git-dir='+str(R/'.issue226-runtime/git'),'--work-tree='+str(R)]
changed=subprocess.check_output(git+['diff','--name-only',m['base_commit'],'--'],text=True).splitlines()
allowed={'.issue226-runtime/REPORT.md','docs/decisions.md','docs/findings.md'}
assert all(p in allowed or p.startswith(str(E.relative_to(R))+'/') for p in changed),changed
assert subprocess.check_output(git+['branch','--show-current'],text=True).strip()=='issue-226-main-rev6'
report=dict(status='PASS: all nine data pass conditions; PO adoption/manufacturing gates pending',base_commit=m['base_commit'],board_sha256=h,DRC=0,unrouted=0,ERC=0,independent_nets=40,connectivity_errors=0,via_pad_pairs=30160,via_pad_min_gap_mm=.145,minimum_new_edge_clearance_mm=diff['minimum_new_edge_gap_mm'],footprint_poses_preserved=62,tracks_preserved=1143,vias_preserved=130,input_loop_mOhm=1000*power['rev6']['values']['input_loop_ohm'],farthest_V=power['regulated_far_point_V'],gerber_cpl_rows=55,gerber_cpl_pairs=1485,gerber_cpl_max_error_mm=0,outline_outside_rev5_area_mm2=0,D036_status='proposed',push=False,PR=False,manufacturing_release=False)
(E/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
