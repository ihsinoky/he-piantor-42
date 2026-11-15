"""Minimum assignment correction of the frozen final round-3 parametric paths."""
import copy,json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
old=json.loads((H/'round3/routes-round3.json').read_text());new=copy.deepcopy(old)
new['before']=[];new['after']=[];deviations=[]
for i in range(14):
 lane=13-i
 before=copy.deepcopy(old['before'][lane]);after=copy.deepcopy(old['after'][lane])
 after[-2:]=copy.deepcopy(old['after'][i][-2:])
 new['before'].append(before);new['after'].append(after)
 deviations.append(dict(right_pin=i+1,left_pin=14-i,frozen_physical_lane=lane+1,unchanged_before_waypoints=len(before),unchanged_after_indices=list(range(len(after)-2)),changed_after_indices=[len(after)-2,len(after)-1],old_main_approach=old['after'][lane][-2:],corrected_main_approach=after[-2:]))
new.pop('search_diagnostic')
new['provenance']='Frozen round-3 final parametric paths: retain every physical Wing lane and its complete reserve and return-fan interior; replace only final Main outlet-axis waypoint and endpoint using the corrected same-numbered cavity assignment. No path optimization, tray relief change, pack or reserve movement.'
def save(name,value):(H/name).write_text(json.dumps(value,indent=2)+'\n')
save('routes-round6.json',new)
save('assignment-deviations-round6.json',dict(source='round3/routes-round3.json',stored_y_mm=10,released_y_mm=-5.1,centre_x_mm=17.4,right_half_deviations=deviations,left_half='Mirror right-half lanes; left pin = 15 - right pin. All 28 endpoint approach edits explicitly enumerated by this correspondence.',affected_geometry_per_strand=dict(unmodified='complete inlet path, reserve arc, return path through after vertex3, and position of vertex4',modified='Main approach vertices5/6; straight edges4→5 and5→6; R5 fillets at vertices4/5; tangent trim at vertex4 on edge3→4. Vertex4 stays at its frozen position. R5 and OD1 unchanged.',indexing='zero-based after-array indices; both sides explicitly identified by right_pin/left_pin')))
