"""Seal the native DRC of this exact candidate; a failure is terminal for #173."""
from common import *
import collections
source=E/'inputs/final';drc=E/'preflight.json';data=json.loads(drc.read_text())
ignored={'text_height','silk_overlap','silk_over_copper','via_dangling'}
bad=[v for v in data['violations'] if v['type'] not in ignored]
save(E/'preflight-receipt.json',dict(utc=now(),board_sha256=digest(source/'main.kicad_pcb'),project_sha256=digest(source/'main.kicad_pro'),drc_sha256=digest(drc),pass_preflight=not bad,blocking_violations=bad,type_counts=dict(collections.Counter(v['type'] for v in data['violations'])),expected_unrouted_connections=len(data['unconnected_items']),ignored_print_and_pre_route_via_warnings=sorted(ignored),routing_allowed=not bad,terminal_on_failure=True))
print('Preflight', 'PASS' if not bad else 'FAIL: STOP, no routing',flush=True)
raise SystemExit(1 if bad else 0)
