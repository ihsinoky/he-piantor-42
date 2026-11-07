# Wing Stage 1: rederive 21 centers from Cantor PCB geometry (#190)

Cantor Classic and Piantor left PCBs agree on all 21 centers, while current Wing uses a different stagger and thumb cluster. Add exact 18/17-axis u coordinates, 16/17 mm center tables, per-key deltas, hole/edge clearances, and proposed definition/placement/#150 CSV replacements. Existing design files are unchanged.

The reanchored centers fit current outlines, but full Jade envelope containment requires wider boards under the stated support policy. Translation alone cannot fix the width. Standard DSA caps collide; narrow caps and source thumb angles remain mechanical decisions before Stage 2.

Validation: independent extraction from both pinned PCBs; original definition/placement/#150 coordinate agreement; deterministic regeneration; 210-pair screening per envelope/angle/pitch; in-memory proposal patch checks. No board relayout, routing, fabrication output, order or payment. Stage 2 requires PO adoption of the documented geometry, rotation and outline conditions.
