"""Write the review report from saved verification evidence, without editing sources."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent

def run():
 dims={p:json.loads((HERE/f'{p}mm/dimensions.json').read_text()) for p in (16,17)}
 checks={p:json.loads((HERE/f'{p}mm/verification.json').read_text()) for p in (16,17)}
 invariants={p:json.loads((HERE/f'{p}mm/invariants.json').read_text()) for p in (16,17)}
 metrology={p:json.loads((HERE/f'{p}mm/plate-metrology.json').read_text()) for p in (16,17)}
 passed=all(checks[p]['cad_passed'] and invariants[p]['passed'] and metrology[p]['passed'] for p in (16,17))
 table=[]
 for p in (16,17):
  v=checks[p];d=dims[p];brim=max(v['printing'].values(),key=lambda x:max(x['with_5mm_brim_xy_mm']))['with_5mm_brim_xy_mm']
  table.append(f"| {p} mm | {len(v['unexpected_overlaps'])} | {max(x['max_step_mm'] for x in v['palm']):.6f} | {max(x['max_seam_gap_mm'] for x in v['palm']):.6f} | {sum(x['nonmanifold_edges'] for x in v['printing'].values())} | {brim[0]:.3f} × {brim[1]:.3f} |")
 refs='; '.join(f"{p} mm: {len(checks[p]['unqualified_cap_reservation_overlaps'])}" for p in (16,17))
 service=dims[17]['routes'][0]['service_stored_mm'];ref=dims[17]['routes'][0]['integrated_reference_longest_mm']
 channel=[]
 print_rows=[]
 for p in (16,17):
  for part in dims[p]['printing']:
   verified=checks[p]['printing'][part['name']]
   size=' × '.join(f'{v:.3f}' for v in part['size_mm'])
   brim=' × '.join(f'{v:.3f}' for v in verified['with_5mm_brim_xy_mm'])
   print_rows.append(f"| {p} | {part['name']} | {size} | {brim} | {'PASS' if verified['passed'] else 'FAIL'} |")
 for p in (16,17):
  for side,v in checks[p]['passages'].items():channel.append(f"| {p} {side} | {v['original_wall_removed_mm3']:.6f} | {v['removed_floor_mm3']:.6f} | {v['conservative_original_roof_mm']:.3f} |")
 text=f'''# Issue #232 — E-R full-cover Wing plates and receiving case

2026-11-13 · branch `issue-232-full-cover` · dimensions mm · package only.

**Mechanical CAD suite: {'PASS' if passed else 'FAIL — see saved JSON failures'}. Full requested acceptance: NOT established.** The actual keycap
skirt/profile is unavailable, so the ≥0.30 mm physical cap clearance gate cannot
honestly be marked PASS. Every key has a required skirt envelope, and all
remaining physical fit/load gauges are documented. Plate ordering remains a PO
gate. No print, order, push, PR, decision change or prior production-tree change
is included.

## Scope and final inputs

The saved [issue, including the final 2026-11-13 comment](inputs/issue232.json)
supersedes the earlier GH-notch and south-shelf proposals. The two Wing decks
cover the complete D-037 Wing silhouette **including both south shelves**. Their
outer edges follow the case rather than PCB steps. No Wing connector notch,
semicircle or finger opening is present. The central Main/Fly service bay stays
open, as in the source studies: its unchanged Main headers and #235 rises cross
Z16.2 and cannot sit underneath a solid Z16.2 lid. This is the Wing-deck
interpretation of “full cover”; a lid over the central electronics bay would
require changing those inputs. The Fly USB opening remains the D-037 opening.

Sources read: [#230 E-R study](../issue-230-mount-study/REPORT.md),
[#228 D-037 tree](../issue-228-final/README.md),
[#235 round 2](../../kicad/qualification/issue-235-wing-round2/REPORT.md),
[round 3](../../kicad/qualification/issue-235-wing-round2/REPORT3.md), and
D-037/D-038/D-039 in [decisions](../../../docs/decisions.md).
Each pitch's `inputs-sha256.json` binds the original case, source CSVs, Rev.4
native PCBs and Main obstacle data. `invariants.json` also rechecks all source
baseline input hashes. `exports-sha256.json` binds this new tree.

## Plates, shelf support and surface

Four distinct plate parts in two pitch packages are in [16mm](16mm/plate-package/) and
[17mm](17mm/plate-package/). Each contains left/right DXF + STEP, aperture and
tie tables and drawing notes. Material **5052-H32 aluminium 1.50**, accepted
finished thickness **1.45–1.51**; 21 apertures per plate **14.02 nominal,
14.00–14.04 finished**, **R0.20**, **C0.20 underside**; flatness **≤0.10**.
See [drawing notes](plate-package-notes.md). DXF and independent STEP probes in
`plate-metrology.json` check all 84 aperture centres, flat dimensions, corner
radii, lead-ins, tie holes and both Z faces across the four plates.

Plate bottom **Z14.70**, top **Z16.20**. The external rim is 1.00 wide, with its
upper face at Z16.20; plates inset 1.20 leave a nominal straight/curved seam of
0.20. The ledge is at Z14.70. The unchanged two-millimetre perimeter wall gives
nominal 0.80 exterior bearing beneath the plate after the inset. The **whole
original solid south shelf is raised to the ledge datum**, backing the extended
plate across the shelf. There is no new unsupported shelf cantilever. The
original four ties retain each Wing plate; no extra shelf fastener or head is
needed in the palm contact area. The inner service edge is retained by those
ties rather than an overhang that would trap the PCB during drop-in assembly.

Four **3.50 POM spacers (Ø3.8 / Ø2.2)** and four **M2×12** screws with 0.30 nylon
washers replace each Wing's original short screws. Head envelope Ø3.4 ×1.3;
thread core Ø1.6 in the unchanged Ø1.7 pilot, nominal engagement 5.5. Every
head/washer is inside the original PCB outline, outside the south shelf and
original south palm strip; the minimum strip clearance is **11.256 mm** at both
pitches. Inventory: **13 PCB sites** (Main3 + Wing8 + Fly2), **17 screws total**
(8 Wing-stack M2×12 +5 Main/Fly M2×6 +4 splice M2×8). Plate screws reuse the
Wing sites and are not eight extra fixing points.

The measured surface results below come from **exported CAD faces**, not a
physical print. The palm seam is measured within 8 mm of the complete approved
south sweep, including its rounded ends. The measured maximum includes local
corner/offset joins and reaches 0.40, versus the 0.20 straight-seam nominal.
Whole-perimeter maxima are also disclosed separately in JSON.

| Pitch | Unexpected mechanical overlaps | South max step | South max seam gap | STL nonmanifold edges | Largest tray + 5 mm brim |
|---|---:|---:|---:|---:|---:|
{chr(10).join(table)}

No CAD step, proud head or raised corner crosses the palm band. Physical
coplanarity still requires fitting/finishing: at a fixed Z14.70 ledge, accepted
plate thickness alone allows −0.05…+0.01 relative to the nominal rim, before
flatness and print variation. The nominal zero-step result does not certify a
manufactured assembly. Deburr, fit and gauge the actual complete band.

All exported printable parts were reloaded for STEP validity, single-solid
connectivity, STL manifoldness, degeneracy and mesh/BRep volume agreement
(relative error <0.001). The following envelopes include a 5 mm brim on every
XY side and fit the 220 ×220 ×250 print limit. Support-post dimensions are
per piece; twelve are required. Bed translations/orientations are in ASSEMBLY.md.

| Pitch | Part | Part XYZ | XY including brim | Check |
|---|---|---|---|---|
{chr(10).join(print_rows)}

## Floor sockets and posts

Twelve **Ø3.10 ×0.80 blind sockets** end at Z1.20, leaving **1.20 floor**.
The six #230 contacts per Wing are unchanged independently for each pitch/hand;
local and assembly coordinates are copied to `post-positions-left/right.csv`.
The common [post STEP](support-post.step) / [STL](support-post.stl) has **Ø3
shaft**, **Ø4.5 ×0.5 collar**, and Z10.00 contact. The Ø3.15 peg has a 0.60 split
for the source design's 0.025 radial press interference. Its assembly model
shows the peg compressed to Ø3.10; free-state interference is intentional,
not an undisclosed rigid-solid clearance. Qualify a printed fit coupon.

All twelve nominal PCB-contact gaps are **0.000 mm by construction**, within
0–0.02. Actual post tops must be trimmed/shimmed to the four boss seats without
preload. Fresh assembly checks include shafts/collars against the Rev.4 service
bodies and routing. The published native-pad/drill/via rescreen remains
applicable because no post or electrical geometry moves (including 16L round3).

## Underside harness passage and structural reasoning

The mated underside SM14B-GHS-TB envelope includes the #235 0.50 height budget:
bottom Z5.15, floor clearance **3.15**. Exit axes start at Y−35.45/Z8.4; actual
1 mm fanouts join the Ø5 conservative lower bundle at centre Z5, leaving
**0.50 nominal floor clearance**. Fourteen conductors are not replaced by a
single thin electrical wire in the planning model.

The production wall passage uses the **Ø6/R5** sweep around the integrated
#235 route. It is cut from the original D-037 wall, not the floor. The low
waypoints (±27,−24,5), (±7,−16,5), mated exits and Main approach at
(±15.5,43,28.5)/(±15.5,43,18.5) remain. The rise leans to (±7,−19,14), then passes
vertically through the **unchanged rack's 5 mm rail gap** at Y−19. The study's
straight rise at Y−16 collided with the retained rack; that conflict is fixed
here, not exempted from the collision audit.

The rail crossing has a **5 ×4 maximum envelope**, 0.50 clear at each Y edge.
Fourteen ≤1 mm wires fit in 3/4/4/3 rows inside a Ø5 circle and a 4 mm Y strip;
`routing.py` states the packing coordinates. Keep that flat pack with soft
lacing below/above the rails and inspect the clearances. A round Ø5 jacket is
not interchangeable at the rack. The exported section is a conservative
controlled-dressing envelope, not a tolerance-certified cable assembly.

| Pitch / tray | Wall removed, mm³ | Passage removal from Z0–2, mm³ | Conservative original roof above passage |
|---|---:|---:|---:|
{chr(10).join(channel)}

The floor diaphragm, splice load path, mounting bosses and outer walls remain
continuous. Rounded R5 transitions avoid a sharp cable-bearing re-entrant cut;
the passage retains the roof reported above even before added ledge material.
It lies away from screw pilots. Both trays remain one valid connected solid.
The short rounded roof can be bridged or given removable accessible support
in the open cavity; inspect the slicer preview and use a bridge/fit coupon for
the chosen material. This is geometric structural/printing reasoning, not a
load-tested polymer qualification or FEA claim. The only intended new floor
removal is the twelve blind post sockets; material below them is unchanged.

## Connected length, storage and retained Fly

Each exported Wing route has **160.000 mm longest connected conductor** at the
#235 datums. The study reference is **123.395 +30 =153.395 mm**. Integrating the
rack changes the direct reference to **{ref:.3f} mm**, leaving **{service:.3f} mm**
physically dressed service length at 160. The U detour is connected into the
same cable at Z28.5; no disconnected ring is counted as length.

The checked adjustable range is **153.4–170 mm**. Range endpoints are rebuilt
and checked against the Fly; only two elevated horizontal straights vary.
The changing route stays above the inherited cap reservations (0.80 vertical
gap), on its own side of X0, and below the re-dressed Fly loop. At the short
end, service allowance is whatever remains after the integrated reference;
**160 mm is the selected planning length with ≥30 mm service**. This neither
qualifies 200 mm storage nor changes D-033's deferred fabrication decision.
Final cut/contact datums remain for the cable fabricator.

The original Fly 170 mm service loop collided with both new Wing paths.
The **same connected 170 mm cable**, same endpoints and same R5 minimum is
re-dressed at Z32.5 (top33.5), above the Wing cruise envelope. Its Main approach
passes X−3 beside the rack, then moves centrally before the longer Wing screw.
Fly seat, hole spacing, USB opening, mouth recess and plug insertion region have
**0 added /0 removed mm³** in the independent retained-region comparison.
The rack/splices/Main/boards remain in their original positions. D-037's
accepted defective official USB-shell/internal mating-model limit is preserved
and explicitly classified, not repaired or relabelled a strict mating pass.

## Verification boundary and reproduction

[16 mm evidence](16mm/verification.json), [17 mm evidence](17mm/verification.json),
`collision-audit.json`, `invariants.json` and `plate-metrology.json` contain the
complete measurements and every contact classification. The reloaded assembly
audit includes plates, switch housing envelopes, PCB solids, Rev.4 underside
bodies, individual fanouts, stored bundles, Fly, rack, posts and fastening.
Only own connector mating volumes, connected fanout/bundle envelope unions
and the preserved D-037 source internals are intended contacts.

Constituent sweeps within each named GH fanout are one conservative connected
envelope, not separate physical parts. Their internal broadphase pairs are
listed in `self_envelope_pairs` with solid indices and **no measured volume**.
The initial release attempt failed OCCT Common on valid converging sweeps
(16 mm indices 273/284 and 401/404); 1e-7 and 1e-6 fuzzy retries did not repair
the first pair. The final verifier records these same-envelope pairs before
Boolean intersection, preserving all constituent-vs-other-part checks and
failing on any other Boolean error. No collision volume is assumed zero.
This changes audit bookkeeping only; no geometry or D-037/D-038/D-039 invariant
was changed. Failed-attempt and diagnostic logs remain in the runtime folder.

**Actual keycaps remain unqualified.** All 42 keys per pitch have required
Z≥16.60 skirt envelopes (0.40 nominal above plate/case, retaining0.30 after the
0.10 loaded movement allowance). No purchased profile was supplied. At16 pitch,
the inherited17 mm XY reservations also overlap each other/neighbouring switch
envelopes; these are recorded as reference conflicts, not hidden as actual
qualified caps ({refs}). Thus `full_acceptance_passed` remains **false**.
No decision to change key positions, switch seating or plate Z was taken to
make the cap result look successful.

[ASSEMBLY.md](ASSEMBLY.md) gives pre-mating, dressing, physical skirt and palm
gauges, post fit, 1 N differential-deflection ≤0.10, key-to-key spread ≤0.07,
Hall return, inversion and retention checks. None is claimed physically tested.

Run [reproduce.sh](reproduce.sh). It writes only this new tree and
`.issue232-runtime/` scratch; CAD/geometry tools are read-only dependencies.
Checks cover closed meshes, mesh/BRep volume agreement, Ender-3 Pro220×220
including5 mm brim, independent DXF/STEP metrology, retained inputs, all fixing
sites/bosses/pilots, source Main spacing0.30, Fly scope, lower floor and route
range. The manifest can be checked without CAD using `python3 manifest.py`.
The private Git database was initialized in `.issue232-runtime/git`, with the
unmodified checkout as its first commit, followed by this branch's design work.

Release continuation logs are retained outside the deliverable tree in
`.issue232-runtime/verify16-release-final.log`, `verify17-release-final.log`,
`invariants16-release-final.log` and `invariants17-release-final.log`.
The earlier `*-release.log` files ended mid-run and establish no verdict.
The invariant CLI exits nonzero when its saved verdict fails.

## Open PO gates

- **Plate order:** PO authorization remains required; select pitch, qualify
  the stock/process and switch-clip coupon, and review finished dimensions.
- **Case print:** PO pitch selection and print GO remain required. Review
  slicer bridges/supports and qualify post/socket and passage fit coupons.
- **Assembly acceptance:** actual keycap profile/skirt clearance ≥0.30 mm,
  complete south-band step/gap and finish, post contact without preload,
  differential deflection, return/Hall stability, inversion/retention and real
  Fly USB mating remain physical checks. The 16 mm cap reservation conflicts
  require resolution against the selected real caps before qualification.
- **Cable fabrication:** approve final conductor cut/contact datums and length,
  verify the controlled rack flat pack, and decide the deferred D-033 length.
  The 153.4–170 mm route range does not qualify 200 mm storage.
'''
 (HERE/'REPORT.md').write_text(text)
 print('Report written; CAD suite',passed,'; actual cap acceptance unverified')
if __name__=='__main__':run()
