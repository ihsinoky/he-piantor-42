"""Check evidence consistency separately from the (possibly failed) design gates."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET,gzip
E=Path(__file__).resolve().parent;R=E.parents[3]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def nets(path):
 out={}
 for n in ET.parse(path).getroot().find('nets'):
  name=n.attrib['name'].removeprefix('/')
  if name.startswith('unconnected-'):continue
  out[name]=sorted((x.attrib['ref'],x.attrib['pin']) for x in n.findall('node'))
 return out
before=nets(E/'main/netlist.xml');after=nets(E/'main/netlist-final.xml')
assert before==after,'Schematic repair changed connected-pin netlist'
parity=read(E/'main/drc.json')['schematic_parity']
assert all(x['type']=='net_conflict' and 'unconnected-(' in x['description'] for x in parity)
summary=read(E/'qualification-summary.json');power=read(E/'power-budget.json');res=read(E/'resistance-summary.json')['rows'][0]
assert res['board_sha256']==sha(E/'main/main.kicad_pcb')
assert read(E/'power-extraction-final.json')['PCB_sha256']==res['board_sha256']
assert read(E/'ground-extraction-final.json')['board_sha256']==res['board_sha256']
for q in summary:
 w=E/q['name'];assert q['board_sha256']==sha(w/'main.kicad_pcb');assert q['source_sha256']==sha(R/read(w/'construction.json')['source'])
 assert (w/'main.kicad_pro').read_bytes()==(w/'input.kicad_pro').read_bytes(),'Original project rules changed'
 d=read(w/'drc.json');assert q['native_drc_violations']==len(d['violations']);assert q['native_unconnected']==len(d['unconnected_items'])
 assert not q['invariant_errors'] and not q['cavity_contract_errors']
 if w.name!='main':
  extraction=read(w/'resistance-extraction.json');assert extraction['board_sha256']==q['board_sha256'];assert len(extraction['rows'])==8
  p=next(x for x in power['wing_extractions'] if x['board']==w.name);assert p['board_sha256']==q['board_sha256'];assert all(x['mesh_pass'] for x in p['cases']);assert p['KCL_max_A']<1e-6
  assert q['all_components_B_Cu']
 assert q['full_gate_pass'] is False,'Expected unresolved gate status must not become an adoption pass'
h=read(E/'harness/geometry.json')
for endpoint in h['endpoints']:assert sha(E/'harness'/endpoint['file'])==endpoint['sha256']
assert h['wing_underside_B_mm']==6.7
roof=h['main_roof_screen'];assert abs(roof['B3_nominal_clearance_mm']-roof['allowance_mm']-roof['after_allowance_mm'])<1e-9;assert roof['after_allowance_mm']>=.3
assert h['finished_conductor_spec_mm']['maximum']==200 and h['finished_conductor_spec_mm']['service_reserve_included']==30.2
stock=read(E/'connector/stock.json');assert not stock.get('fallback_browser_observations');assert stock['primary_page_recheck']==read(E/'connector/primary-page-recheck.json')
for name,d in stock['observations'].items():
 f=E/'connector/stock-responses'/(name+'.html.gz')
 if 'response_sha256' in d:assert hashlib.sha256(gzip.decompress(f.read_bytes())).hexdigest()==d['response_sha256']
out=dict(evidence_consistent=True,design_qualification_pass=False,connected_schematic_netlist_unchanged=True,connected_schematic_nets=len(after),native_parity_residuals=len(parity),native_parity_residual_kind='Named generated unconnected nets versus baseline empty PCB nets; disclosed, not counted as a native parity pass',boards={q['name']:q['board_sha256'] for q in summary},library_release='BLOCKED: conservative surface keepout is not verified against current exact no-pattern drawing',stock=stock['verdict'],decisions_sha256=sha(R/'docs/decisions.md'))
(E/'evidence-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
