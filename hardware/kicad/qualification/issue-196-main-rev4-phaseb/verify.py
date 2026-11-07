"""Final hash-bound acceptance and independent arithmetic checks (Python stdlib)."""
from pathlib import Path
import json,hashlib,csv,math,zipfile,statistics,re,xml.etree.ElementTree as ET
E=Path(__file__).resolve().parent;R=E.parents[3]
def read(name):return json.loads((E/name).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
board=E/'inspection/final/main.kicad_pcb';digest=sha(board);checks={}
a=read('inspection/final/assessment.json');assert a['pass_acceptance'] and all(v==0 for v in a['metrics'].values());assert a['nets_checked']==40 and a['via_count']==130 and a['track_count']==1135
assert not read('inspection/final/drc.json')['violations'] and not read('inspection/final/drc.json')['unconnected_items'];checks['four_metrics']=a['metrics']
g=read('inspection/final/connectivity.json');assert g['nets_checked']==40 and g['required_unconnected']==g['wrong_net_contacts']==0
transfer=read('inspection/final/transfer-diff.json');assert not transfer['removed'] and not transfer['added'] and transfer['output_sha256']==digest
v=read('inspection/final/audit/via-pad/all-vias.json');assert len(v)==130 and all(q['passes_0p10'] and q['classification']=='none' and q['min_annulus_gap_mm']>=.125 for q in v)
summary=read('inspection/final/audit/via-pad/summary.json');assert summary['source_sha256']==digest and summary['copper_pads']==232
vals=[q['min_annulus_gap_mm'] for q in v];dist=read('via-distribution.json');assert dist['min_mm']==min(vals)==.145 and dist['p50_mm']==statistics.median(vals) and sum(q['count'] for q in dist['distribution'])==130;checks['via_minimum_mm']=min(vals)
for name in ['design-check.json','paste-via-check.json','cam-check.json','power-budget.json','resistance-summary.json']:
 d=read(name);d=d['rows'][0] if name=='resistance-summary.json' else d;assert d['board_sha256']==digest,(name,d['board_sha256'],digest)
assert read('design-check.json')['pass_check'] and read('design-check.json')['logical_pins']==226
assert read('paste-via-check.json')['via_copper_overlaps_paste']==read('paste-via-check.json')['drill_overlaps_paste']==0
r=read('resistance-summary.json')['rows'][0];assert r['all_loop_targets_met_in_model'] and r['rail_common_loop_ohm']<=.05 and all(q<=.05 for q in r['branch_loop_ohm'].values());checks['resistance_mOhm']=[r['rail_common_loop_ohm']*1000]+[q*1000 for q in r['branch_loop_ohm'].values()]
for kind,key in [('power','PCB_sha256'),('ground','board_sha256')]:assert read(kind+'-extraction-final.json')[key]==digest
assert read('ground-model-verification.json')['pass_numerics'] and read('copper-equivalence.json')['same_copper'] and read('copper-equivalence.json')['final_board_sha256']==digest
p=read('power-budget.json');rows=list(csv.DictReader((E/'power-sensitivity.csv').open()));assert len(rows)==96
for row in rows:
 T=float(row['temperature_C']);I=float(row['Wing_A']);nr=int(row['return_conductors']);wire=1.7241e-8*.2/(.0804e-6)*(1+.00393*(T-20));rh=(wire+2*.05)*(1+1/nr)
 assert abs(float(row['each_conductor_path_m'])-.2)<1e-12 and abs(float(row['wire_ohm'])-wire)<1e-12 and abs(float(row['harness_loop_ohm'])-rh)<1e-12
 far=5.096-.050-2*I*(r['rail_common_loop_ohm']+.25)-I*(r['branch_loop_ohm'][row['branch']]+rh)-float(row['wing_drop_V']);assert abs(float(row['farthest_V'])-far)<1e-12
worst=min(float(q['farthest_V']) for q in rows if q['design']=='True' and int(q['return_conductors'])==6);assert worst>=4.60 and abs(worst-p['six_return_worst']['farthest_V'])<1e-12;checks['worst_200mm_127mA_V']=worst
bom=list(csv.DictReader((E/'manufacturing/BOM.csv').open()));cpl=list(csv.DictReader((E/'manufacturing/CPL.csv').open()));ledger=list(csv.DictReader((E/'main-bom.csv').open()));assert len(bom)==len(cpl)==55 and len(ledger)==59
assert {q['Designator'] for q in bom}=={q['Designator'] for q in cpl};byref={q['ref']:q for q in ledger};assert byref['J4']['lcsc']=='C160404' and byref['C25']['lcsc']=='C1525' and all(ref not in byref for ref in ['J1','R1','R2','U2']) and all(ref in byref for ref in ['R3','R4'])
cam=read('cam-check.json');assert cam['pass_check'] and cam['plane_symmetric_difference_mm2']<1e-8
archive=E/'manufacturing/main-rev4-fabrication-review.zip';assert sha(archive)==cam['archive_sha256']
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None and len(z.namelist())==11
 for q in cam['archive_members']:assert hashlib.sha256(z.read(q['name'])).hexdigest()==q['sha256']==sha(E/'manufacturing/gerber'/q['name'])
assert read('export-provenance.json')['board_sha256']==digest
for name in ['inspection/final/main.kicad_pro','schematic/main.kicad_sch','manufacturing/quote-handoff.md','manufacturing/cam-review.png']:assert (E/name).is_file()
report=R/'docs/issue-196-main-rev4-phaseb.md';text=report.read_text();assert digest in text and 'D-033' in text and 'supersede' in text and text.rstrip().endswith('**Phase B の実施・成果物コミットまで完了。ここで停止する。**')
assert '| Main board | Rev.4 |' in (R/'docs/project-status.md').read_text() and '## D-033 ' in (R/'docs/decisions.md').read_text()
for path in [report,E/'README.md']:
 for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
  if '://' in target or target.startswith('#'):continue
  assert (path.parent/target.split('#')[0]).exists(),(path,target)
manifest=read('manifest.json');actual={str(q.relative_to(E)):sha(q) for q in E.rglob('*') if q.is_file() and q.name not in ['manifest.json','verification.json']};assert actual==manifest['files']
assert manifest['documents']=={str(q.relative_to(R)):sha(q) for q in [report,R/'docs/decisions.md',R/'docs/project-status.md']}
assert not list(E.rglob('*.kicad_prl')) and not list(E.rglob('*.pyc'))
checks['files_hashed']=len(actual);checks['board_sha256']=digest
(E/'verification.json').write_text(json.dumps(dict(pass_check=True,checks=checks),indent=2)+'\n');print(json.dumps(dict(PASS=True,checks=checks),indent=2))
