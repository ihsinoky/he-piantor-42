"""Concrete free-space pre-mating fixture, independent of installed case seating.
Wing held above tray before insertion: plug slides horizontally north 8 mm.
Exports three plug poses and the complete reserved insertion prism.
"""
from pathlib import Path
import json
from build123d import Box,Pos,Compound,export_step
E=Path(__file__).resolve().parent;out=E/'case';out.mkdir(exist_ok=True)
rows=[]
for side,sgn in [('left',-1),('right',1)]:
 # Nominal mated drawing envelope at underside Z10 translated up 25 mm.
 # .5 mm allowance in each outside direction; lowest Z30.15 during mating.
 shapes=[Pos(sgn*27,-39.025+delta,32.575)*Box(19.75,8.15,4.85) for delta in (8,4,0)]
 corridor=Pos(sgn*27,-35.025,32.575)*Box(19.75,16.15,4.85)
 export_step(Compound(children=[*shapes,corridor]),out/f'pre-mating-{side}.step')
 rows.append(dict(side=side,held_pcb_underside_z_mm=35,approach_direction_assembly=[0,-1,0],insertion_travel_mm=8,poses_y_offsets_mm=[8,4,0],minimum_reserved_z_mm=30.15,source_case_cap_top_z_mm=25.2,nominal_overhead_gap_mm=4.95,mated_final_underside_z_mm=10,mode='mate above/outside tray; cable dressed before seating; no installed latch access claimed'))
(out/'mating-procedure.json').write_text(json.dumps({'power':'off','poses':rows,'sequence':['Join empty tray halves first; leave Main plugs free.','Hold Wing with underside accessible above tray at underside Z35 or outside tray.','Check L/R and cavity 1; push GHR-14V-S housing horizontally north through 8 mm approach until latch clicks, holding housing rather than wires.','Dress fourteen 1 mm maximum wires through the modeled horizontal fanout into the lower channel; retain slack away from mounting supports.','Lower prewired Wing to underside Z10 while feeding Main end through central bay; seat four mounts and six E-R posts.','Fasten Wing, then mate Main J2/J3 from above. Install the full-cover plate and switches afterward.','For service, power off, disconnect Main and lift Wing before depressing the underside latch.'],'limits':['Pre-mating clearance is a free-space fixture model; PCB held by edges, no keys/plate fitted.','Straight-down seating motion with dressed flexible wires is an assembly procedure, not a rigid-body motion certification.','Use study wall-passage proposal; original tray still blocks the installed harness.']},indent=2)+'\n')
