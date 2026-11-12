from common import *
W=E/'inspection/final';d=json.loads((W/'drc.json').read_text());g=json.loads((W/'connectivity.json').read_text());diff=json.loads((E/'rev5-diff-and-clearance.json').read_text());erc=json.loads((E/'schematic/erc-final.json').read_text())
metrics=dict(required_unconnected=g['required_unconnected'],wrong_net_contacts=g['wrong_net_contacts'],material_violations=len(d['violations'])+len(d['unconnected_items'])+sum(len(s['violations']) for s in erc['sheets']),unexplained_transfer_changes=int(not diff['pass_check']))
assert not any(metrics.values()) and diff['minimum_new_edge_gap_mm']>=.5
save(W/'assessment.json',dict(board_sha256=digest(W/'main.kicad_pcb'),metrics=metrics,pass_acceptance=True))
