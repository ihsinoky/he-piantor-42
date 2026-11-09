"""Offline artifact acceptance: substantive cross-file checks, no CAD writes."""
from pathlib import Path
import csv,gzip,hashlib,itertools,json,math,subprocess,xml.etree.ElementTree as ET,zipfile
E=Path(__file__).resolve().parent;R=E.parents[3];V=E.parent/'issue-196-main-rev4-phaseb'
def j(path):return json.loads(Path(path).read_text())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def csvread(path):return list(csv.DictReader(Path(path).open()))
manifest=j(E/'manifest.json')
assert all(sha(R/q['path'])==q['sha256'] for q in manifest['files'])
assert all(sha(R/q['path'])==q['sha256'] for q in manifest['inputs'])
board=E/'inspection/final/main.kicad_pcb';h=sha(board);snap=j(E/'inspection/final/snapshot.json')
drc=j(E/'inspection/final/drc.json');erc=j(E/'schematic/erc-final.json');assert not drc['violations'] and not drc['unconnected_items'] and all(not s['violations'] for s in erc['sheets'])
for name in ['final-native-drc','final-native-erc','power-extraction','ground-extraction','rev4-positive-reextract','rev4-ground-reextract','cam-readback','physical-connectivity']:
 assert j(E/'processes'/name/'record.json')['exit_code']==0,name
for path in ['inspection/final/assessment.json','inspection/final/audit/via-pad/summary.json','land-check.json','paste-via-check.json','export-provenance.json','cam-check.json','cpl-frame-check.json']:
 q=j(E/path);assert q.get('board_sha256',q.get('source_sha256'))==h,path
assessment=j(E/'inspection/final/assessment.json');assert assessment['pass_acceptance'] and not any(assessment['metrics'].values())
graph=j(E/'inspection/final/connectivity.json');assert graph['nets_checked']==40 and graph['required_unconnected']==graph['wrong_net_contacts']==0 and all(q['component_count']==1 for q in graph['nets'])
diff=j(E/'rev4-diff.json');assert diff['rev5_sha256']==h and diff['rev4_sha256']==sha(V/'inspection/final/main.kicad_pcb') and diff['pass_check']
assert diff['changed_footprints']==['J4'] and diff['changed_vias']==0 and diff['removed_tracks']==3 and diff['added_tracks']==11
graphpads={pad for net in graph['nets'] for group in net['components'] for pad in group['pads']}
assert graphpads=={q['ref']+'.'+q['number']+'@'+q['uuid'] for q in snap['pads'] if q['net']}
assert diff['changed_logical_pins']==0 and diff['logical_netted_pins']==199 and diff['all_62_positions_and_angles_preserved']
assert set(diff['changed_copper_nets'])=={'VBUS','GND','USB_DM_ESD','USB_DP_ESD'}
auditdir=E/'inspection/final/audit/via-pad';pairs=json.loads(gzip.decompress((auditdir/'all-pairs.json.gz').read_bytes()));summary=j(auditdir/'summary.json');vias=j(auditdir/'all-vias.json');pads=j(auditdir/'pads.json')
assert len(vias)==130 and len(pads)==232 and len(pairs)==30160
assert len({(q['via_uuid'],q['pad_uuid']) for q in pairs})==30160
assert {q['via_uuid'] for q in pairs}=={q['uuid'] for q in vias} and {q['pad_uuid'] for q in pairs}=={q['uuid'] for q in pads}
assert min(q['annulus_gap_mm'] for q in pairs)==summary['min_annulus_gap_mm']==.145
assert all(q['annulus_gap_mm']>=.1 and q['classification']=='none' and q['common_layers'] for q in pairs)
assert all(q['min_annulus_gap_mm']==min(p['annulus_gap_mm'] for p in pairs if p['via_uuid']==q['uuid']) for q in vias)
paste=j(E/'paste-via-check.json');assert paste['vias_checked']==130 and paste['via_copper_overlaps_paste']==paste['drill_overlaps_paste']==0
# XML independently checks every connected and NC native pad. Power flags are nonphysical.
root=ET.parse(E/'schematic/main.net.xml');xp={(n.get('ref'),n.get('pin')):net.get('name').removeprefix('/') for net in root.findall('.//nets/net') for n in net.findall('node') if not n.get('ref').startswith('#')}
pcb={(q['ref'],q['number']):q['net'] for q in snap['pads'] if q['number']}
assert len(pcb)==226
for key,net in pcb.items():assert xp[key]==net if net else xp[key].startswith('unconnected-'),key
J4={key[1]:net for key,net in pcb.items() if key[0]=='J4'};assert J4=={'1':'VBUS','2':'USB_DM_ESD','3':'USB_DP_ESD','4':'GND'}
assert j(E/'schematic-repairs.json')['ERC_rules_disabled']==[]
assert j(E/'land-check.json')['routing_in_nonrecommended_body_area']==[]
# Assembly and coordinates: every non-J4 BOM row is inherited verbatim.
bom=csvread(E/'manufacturing/BOM.csv');old={q['Designator']:q for q in csvread(V/'manufacturing/BOM.csv')};cpl=csvread(E/'manufacturing/CPL.csv');frame=csvread(E/'manufacturing/CPL-jlcpcb-gerber-frame.csv')
assert len(bom)==len(cpl)==len(frame)==55
for q in bom:
 if q['Designator']=='J4':assert q['Comment']=='781710004' and q['LCSC Part #']=='C588524' and q['Footprint']=='Rev5:J4'
 else:assert q==old[q['Designator']],q
lookup={q['ref']:q for q in snap['components']}
for a,b in zip(cpl,frame):
 assert all(a[k]==b[k] for k in ['Designator','Layer','Rotation']) and a['Layer']=='top'
 p=lookup[a['Designator']];x=float(b['Mid X'][:-2]);y=float(b['Mid Y'][:-2]);assert abs(x-p['position'][0])<=1e-6 and abs(y+p['position'][1])<=1e-6 and float(a['Rotation'])==p['angle']
 assert abs(float(a['Mid X'][:-2])+62.107318-x)<=1e-6 and abs(float(a['Mid Y'][:-2])-137.9-y)<=1e-6
cam=j(E/'cam-check.json');assert cam['pass_check'] and cam['BOM_CPL_parts']==55 and cam['via_drills']==130 and cam['holes']==3 and cam['plane_symmetric_difference_mm2']<1e-8
archive=E/'manufacturing/main-rev5-fabrication-review.zip';assert sha(archive)==cam['archive_sha256']
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==11
 assert set(z.namelist())=={q['name'] for q in cam['archive_members']}
 for q in cam['archive_members']:assert z.read(q['name'])==(E/'manufacturing/gerber'/q['name']).read_bytes() and q['sha256']==sha(E/'manufacturing/gerber'/q['name'])
f=j(E/'cpl-frame-check.json');assert f['rows']==f['native_secondary_export_matches']==55 and f['pairwise_vectors_checked']==1485 and f['max_axis_error_mm']=='0'
power=j(E/'power-impact.json');assert power['rev5']['PCB_sha256']==h and power['rev4']['PCB_sha256']==sha(V/'inspection/final/main.kicad_pcb')
for label,boardhash in [('final',h),('rev4-reference',power['rev4']['PCB_sha256'])]:
 pos=j(E/f'power-extraction-{label}.json');gnd=j(E/f'ground-extraction-{label}.json');assert pos['PCB_sha256']==gnd['board_sha256']==boardhash and len(pos['rows'])==16 and len(gnd['rows'])==4
 assert {(q['max_triangle_area_mm2'],q['track_width_factor']) for q in gnd['rows']}=={(.03,1),(.03,.8),(.0075,1),(.0075,.8)}
for key in power['delta_ohm']:assert abs(power['delta_ohm'][key]-(power['rev5']['values'][key]-power['rev4']['values'][key]))<1e-12
assert power['rev5']['values']['input_loop_ohm']<.05 and power['input_loop_meets_50mOhm_model']
assert power['regulated_far_point_V']>=4.60 and round(power['regulated_far_point_V'],3)==round(power['rev4_regulated_far_point_V'],3)
assert power['upstream_500mA_classification_changes']==0 and len(power['upstream_sensitivity'])==15
assert j(E/'ground-model-verification.json')['pass_numerics']
# All original tracked paths outside the authorized changes remain byte-identical.
git=['git','--git-dir='+str(R/'.issue221-runtime/git'),'--work-tree='+str(R)]
changed=subprocess.check_output(git+['diff','--name-only','227eb17a','--'],cwd=R,text=True).splitlines()
allowed={'.issue221-runtime/REPORT.md','docs/decisions.md','docs/project-status.md','docs/issue-221-main-rev5.md'}
assert all(q in allowed or q.startswith('hardware/kicad/qualification/issue-221-main-rev5/') for q in changed),changed
assert subprocess.check_output(git+['branch','--show-current'],text=True).strip()=='main-rev5-ezmate'
assert not j(E/'recovery-inventory.json')['mismatches']
report=dict(status='PASS: implementation and data qualification; PO/assembly/manufacturing gates pending',base_commit='227eb17a',branch='main-rev5-ezmate',board_sha256=h,manifest_sha256=sha(E/'manifest.json'),manifest_files_checked=len(manifest['files']),DRC_violations=0,ERC_violations=0,unconnected=0,physical_nets_checked=40,wrong_net_contacts=0,via_pad_pairs=30160,via_pad_min_gap_mm=.145,via_pad_violations=0,changed_footprints=['J4'],changed_vias=0,changed_tracks={'removed':3,'added':11},input_loop_ohm=power['rev5']['values']['input_loop_ohm'],input_loop_delta_ohm=power['delta_ohm']['input_loop_ohm'],regulated_farthest_V=power['regulated_far_point_V'],BOM_CPL_assembled_parts=55,Gerber_CPL_max_error_mm=0,Gerber_CPL_relative_pairs=1485,zip_members=11,protected_original_paths_changed=[],D035_status='提案',physical_cable_polarity_measurement='pending; mandatory before Main first power',manufacturing_release=False,push=False,PR_created=False,order_placed=False)
(E/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
