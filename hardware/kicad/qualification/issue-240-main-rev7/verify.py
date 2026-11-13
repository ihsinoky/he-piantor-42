"""Offline gate and hash verification for the frozen Main study candidate."""
import json,hashlib
from pathlib import Path
E=Path(__file__).resolve().parent
read=lambda p:json.loads((E/p).read_text())
sha=lambda p:hashlib.sha256((E/p).read_bytes()).hexdigest()
b=sha('inspection/final/main.kicad_pcb');d=read('inspection/final/drc.json');erc=read('schematic/erc-final.json');c=read('inspection/final/connectivity.json');a=read('inspection/final/audit/via-pad/summary.json');r=read('resistance-summary.json')['rows'][0];p=read('power-budget.json');i=read('invariants.json')
assert not d['violations'] and not d['unconnected_items'] and not d['schematic_parity']
assert all(not sheet['violations'] for sheet in erc['sheets'])
assert c['required_unconnected']==0 and c['wrong_net_contacts']==0
assert a['source_sha256']==b and a['violates_0p10']==0 and a['min_physical_gap_mm']>=.1
assert r['board_sha256']==p['board_sha256']==i['candidate_sha256']==b
assert r['input_positive_ohm']+r['input_GND_ohm']<=.05 and r['all_loop_targets_met_in_model']
assert p['six_return_worst']['farthest_V']>=4.60
assert i['outline_unchanged'] and i['mounts_unchanged'] and i['J4_unchanged'] and i['D024_pin_order_unchanged']
for name in ['positive-extraction','ground-extraction','snapshot','native-drc','native-erc','physical-connectivity','via-pad-audit']:
 assert read(f'processes/{name}/record.json')['exit_code']==0
print('Main electrical gates PASS; connector-local routing exception remains disclosed in REPORT.md')
