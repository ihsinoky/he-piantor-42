# Issue 244 proposed case changes — study only

Coordinates below use the original #242 upper datum, before translating every
raised part by Δ. The completed assembly files use the original floor datum.
Thus PCB underside/top are Z10+Δ / 11.2+Δ, and the common Wing deck/cover plane
is Z16.2+Δ. The nominal floor and rubber feet stay put. No board is notched.

| Part | Actual study change / remake scope |
|---|---|
| Both trays | Split the original #232 tray at Z3, keep the upper geometry rigid, extrude its exact horizontal section downward by Δ, and translate its lower portion down by Δ. Finally translate the whole result up by Δ. This preserves floor/socket geometry while extending walls and board/fastener supports. Both complete trays must be remade; no stacked lid shim is credited. |
| Wing support posts | Apply the same Z3 split and section extension. The original peg and socket fit translate together, with the upper shank lengthened. All twelve posts must be remade. |
| Main/Fly bosses, Wing plate screw supports, rim and deck seats | Follow the tray extension; raise seats, pilots, upper passages and decks together. Original screw lengths and engagement relative to their raised seats are retained. Original plates, spacers, washers, PCBs and Fly assembly translate rigidly by Δ. |
| Floor splices and feet | Remain at the original floor height. The two splice rows retain Y−8 / 55; move screws from X−5 / 12 to X0 / 15. Remove original elevated splice bosses and add floor-rooted replacements of the original 6.8 mm height; redrill pilots. Existing splice plates need new Ø2.2 clearance holes; old holes remain unused. |
| Lower harness channels | Actual Ø6 R5 cutters following the U; global center Z7, envelope Ø5. U waypoints are (±27,−24) → (±7,−16) → (±7,28) → (±19,28) → (±19,0). Reference turn Y12 releases 32 mm by shortening two legs by 16 mm. |
| North rise and upper passages | Actual projected grooves clear the modeled fourteen OD1 wires by 0.32 mm nominal, with 0.02 mm projection simplification. Global cutter starts Z3.9. Each wire goes from the common lower endpoint through (±(5+off),−18,7), (±(5+off),−5,12.8+Δ+dz), (±(23+off),10,12.8+Δ+dz), then the original outward GH approach and endpoint. The 5/5/4 strand pack uses off −2…2 / dz −1,0,+1. All corners use R5. Exact rounded samples are authoritative. |
| Rim / cover edge | Retain #242 underside trim south of Y−39; fit the cover around retained north rim with 0.30 mm XY clearance. D-037 Fly seat and USB opening follow the raised assembly rigidly, with no local shaving. |
| North cover pillars | Integral Ø8, rooted at global Z1, top Z14.7+Δ. Pillars lengthen by Δ. AF4 ×1.6 nuts at global Z11.5+Δ; side-loading pockets use the actual buffered hexagon plus entry slot. Cut the pocket through both pillar and existing tray material, resolving #242's nut-corner obstruction. M2x6 screws. |
| South retention | Same existing Main H2/H3 sites (±31.89268,64.4), removable POM Ø4.5 / ID2.2 ×3.0 spacers, original washers and M2x10 lid screws. All translate by Δ; no PCB hole or spacer length change. |
| Cover | One 6061-T6 aluminium part, 1.50 nominal, top Z16.2+Δ, underside Z14.7+Δ. Same GH 0.25 mm / Fly 0.40 mm / USB 1.00 mm remaining skins. Pockets open from below; two north and two south countersunk screw heads are flush. The exhaustive audit uses an exact disjoint tile partition; `finish.py` reconstructs and checks a single solid. |
| Rack | Remove the #232 rack completely. No outside-cover cable storage. |

The scripts export these changed trays and posts within the complete assembly.
The routes and pockets are real CSG changes, never collision exemptions.
The result is a candidate: a failed audit rejects the package at that Δ.

The #242 aluminium skin and local fastener stress screens remain applicable
as local calculations because the cover and upper retention geometry translate
rigidly. Longer integral pillars require a new whole-case stiffness assessment;
no physical load or inversion test is implied. Their axial area is unchanged.

Service candidate: disconnect external USB; remove two north M2x6 and two south
M2x10 cover screws; lift the lid and remove the loose south spacers. Main H1
still holds Main. Release GH latches and withdraw the plugs along their outward
axes; disconnect Main EZmate, remove H1 and lift Main. Wing boards and decks
remain fixed. With Main removed, lift/unlace the under-Main U from its open
channel and move its turn from Y28 to Y12, recovering 32 mm on the same connected
harness. Reverse for reassembly, keeping lid loads on supports. A collision in
the assembled candidate prevents certifying this as accessible service reserve.
