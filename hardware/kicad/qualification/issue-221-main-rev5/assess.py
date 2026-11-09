from common import *
import pcbnew as p
w=E/'inspection/final';d=json.loads((w/'drc.json').read_text());g=json.loads((w/'connectivity.json').read_text());diff=json.loads((E/'rev4-diff.json').read_text());erc=json.loads((E/'schematic/erc-final.json').read_text())
assert not d['violations'] and not d['unconnected_items'];assert all(not s['violations'] for s in erc['sheets']);assert diff['pass_check']
assert g['required_unconnected']==g['wrong_net_contacts']==0
b=p.LoadBoard(str(w/'main.kicad_pcb'));tracks=list(b.GetTracks());conditions=dict(width=all(p.ToMM(t.GetWidth(p.F_Cu) if isinstance(t,p.PCB_VIA) else t.GetWidth())>=.1 for t in tracks),via=all(p.ToMM(t.GetWidth(p.F_Cu))==.6 and p.ToMM(t.GetDrillValue())==.3 for t in tracks if isinstance(t,p.PCB_VIA)),GND_only_In1=not any(not isinstance(t,p.PCB_VIA) and t.GetLayer()==p.In1_Cu for t in tracks))
assert all(conditions.values())
save(w/'assessment.json',dict(board_sha256=digest(w/'main.kicad_pcb'),metrics=dict(required_unconnected=0,wrong_net_contacts=0,material_violations=0,unexplained_transfer_changes=0),pass_acceptance=True,measured_unconnected=0,nets_checked=g['nets_checked'],drc_type_counts={},ERC_violations=0,conditions=conditions,track_count=sum(not isinstance(t,p.PCB_VIA) for t in tracks),via_count=sum(isinstance(t,p.PCB_VIA) for t in tracks)))
