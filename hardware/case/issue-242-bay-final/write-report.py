"""Write the final gate verdict from completed audit evidence, never a partial run."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def read(p):return json.loads(p.read_text())
def main():
 ds={p:read(HERE/f'{p}mm/measurements.json') for p in (16,17)}
 audits={p:read(HERE/f'{p}mm/audit.json') for p in (16,17)}
 for a in audits.values():assert a['all_pairs_enumerated'] and a['all_exact_candidates_completed'] and not a['early_stop']
 assert all(a['unexpected_interferences'] for a in audits.values())
 rows=[];bindings=[]
 for p,a in audits.items():
  rows.append(f"| {p} | {a['assembly_solids']} | {a['total_pairs']:,} | {a['aabb_rejected_pairs']:,} | {len(a['intended_pairs'])} | {a['exact_candidates']} | {len(a['unexpected_interferences'])} | {len(a['boolean_errors'])} |")
  for side in ('left','right'):
   hits=[r for r in a['unexpected_interferences'] if {r['a'],r['b']}=={'wing_'+side,'Wing-'+side+'-upper'}]
   assert hits
   r=max(hits,key=lambda r:r['volume_mm3'])
   bindings.append(f"| {p} | {side} | {len(hits)} | {r['a_solid']} / {r['b_solid']} | {r['volume_mm3']:.9f} |")
 wings=[]
 for w in ds[17]['wings']:wings.append(f"| {w['side']} | {w['longest_conductor_mm']:.6f} | {w['reference_conductor_mm']:.6f} | {w['represented_reserve_mm']:.6f} | 0 |")
 maps=[]
 for p in (16,17):
  for r in read(HERE/f'{p}mm/collision-map.json'):
   lo,hi=r['overlap_bounds_mm']
   maps.append(f"| {p} | {r['a']} / {r['b']}[{r['b_solid']}] | {r['volume_mm3']:.9f} | {lo[0]:.4f}…{hi[0]:.4f} | {lo[1]:.4f}…{hi[1]:.4f} | {lo[2]:.4f}…{hi[2]:.4f} |")
 mech=read(HERE/'mechanics.json');s=mech['skin_screen'][0];st=mech['skin_screen'][1]
 report=f'''# Issue 242 — final flush Z16.20 bay-cover routing study

2026-11-14. **INFEASIBLE for the evaluated dedicated routing/case revision.**
The completed exhaustive audit measures cable penetration of the invariant Wing
Rev.4 PCBs. No zero-interference covered assembly or accessible service reserve
is certified. **The [PO update of 2026-11-14](https://github.com/ihsinoky/he-piantor-42/issues/242#issuecomment-6857066008)
withdraws the stop-if-failed bound. This current-height collision map feeds a
separate follow-on search for the minimum height increase Δ that satisfies all
gates, preserving one flush Wing-deck/cover plane.**
This is a conclusive failed acceptance result, not a mathematical claim that
every imaginable routing in a redesigned case is impossible. The follow-on must account for greater overall keyboard height and the cost
of remaking the case. No height search is performed in this close-out. No production geometry, baseline, decisions or electronics
are changed; no order, push or PR is made.

The starting [Main Rev.7 candidate](../../kicad/qualification/issue-240-main-rev7/REPORT.md)
is fixed exactly, including its disclosed electrical routing-scope exception.
Its electrical pass is not used as evidence of mechanical fit. The Wing Rev.4
boards and D-024 cavity-to-same-cavity wiring/six independent returns are fixed.

## Dedicated design and binding measurement

This round replaces the #232 elevated/rack route rather than fitting that route
beneath a lid. The rack is absent. Each side enters through the original Wing
connector fanout, uses a **connected OD5 lower U at Z5**, then fourteen OD1 rising
conductors to the outward-facing Rev.7 GH plug. The new U uses X±7 and X±23,
turning at Y38 with R5. Case material is actually removed for **OD6 lower
channels** and new upper grooves. Both splice screw rows move from X−5/12 to
X0/15, retaining Y−8/55. All these changes appear in exported study tray solids,
not collision exemptions. See [case-revision delta list](CASE-REVISION.md).

The outside-edge rise from (±23,8,5) toward the individual upper points near
(±31,18,12.8) **passes through the Wing board at Z10…11.20**. A tray groove cannot
remove this board obstruction. The exact BRep audit measures the following
constituent intersections; numbers are physical envelope overlaps, not a
projection or insufficient aggregate free volume:

| Pitch | Wing | Intersecting rising constituents | PCB / wire solid index | Largest single overlap mm³ |
|---|---|---:|---|---:|
{chr(10).join(bindings)}

The authoritative complete contact lists are in [16mm/audit.json](16mm/audit.json)
and [17mm/audit.json](17mm/audit.json). Additional contacts are all retained in
those files; none is hidden to make the above four measurements the only failures.
Constituent volumes must not be summed as a unique assembly collision volume.
Resolving these particular board crossings would require a different route;
case carving, more cable length, a stronger skin or screw relocation cannot
make the evaluated rise fit. The final-round acceptance therefore fails.

## Collision map for the height-variable follow-on

Every remaining unexpected contact is listed below. Coordinates are in the
source assembly datum, millimetres; bounds are those of the actual Boolean
intersection, not the larger part bounds. Wire indices distinguish the fourteen
upper conductors. Per-pair volumes are not a union volume. The machine-readable
[16mm map](16mm/collision-map.json) and [17mm map](17mm/collision-map.json)
include repeated measurements using the audit's OCCT settings; repeat volume
agreement is checked within0.0001mm³ (the rejection threshold stays1e−6mm³).

| Pitch | Parts / constituent | Overlap mm³ | X range mm | Y range mm | Z range mm |
|---|---|---:|---|---|---|
{chr(10).join(maps)}

The28 board/rise contacts occupy Z10.0…11.2. The two lower-bundle/plate-screw
contacts sit at Z4.50…7.2441 near X±5.2/Y1.1. The two north captive nuts interfere
with their tray/pillar material at Z11.5…13.1 near X±10/Y−30: a4.2mm rectangular
slot does not clear every corner of the modeled AF4 hexagonal nut. These are
additional retention fit failures, not accepted thread engagement.

The map identifies current occupied space; neither maximum penetration nor
volume alone determines minimum Δ. Raising only the lid cannot resolve a fixed
Wing PCB crossing or nut/pillar contact. The next round must evaluate the
coordinated case/deck/routing changes and all gates, keeping the common flush
upper plane. This report makes no claim about a feasible Δ or a new route.

Both changed trays are valid connected single solids. The protected D-037 Fly
region comparison passes within0.0001mm³. The separate below-Z1.199 floor
comparison is **not unchanged** (about5.443mm³ added per half from floor-rooted
support geometry); this is disclosed case geometry, not an unchanged-floor claim.

## Complete all-pairs audit

| Pitch | Solid constituents | All unordered pairs | AABB rejected | Explicit intended pairs | Exact candidates | Positive unexpected overlaps | Boolean errors |
|---|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

**Enumeration and exact-candidate processing are complete at both pitches. No
early-stop result supplies this verdict.** The source STEP is reloaded, original
cables/rack/coarse Main obstacles are replaced, and all retained-versus-retained,
retained-versus-new and new-versus-new pairs enter the same audit. It does not
inherit a fixed-part fit certificate from #232. Bounding boxes reject only
pairs with no positive volumetric overlap. Every other non-exempt pair receives
OCCT Common; exact results, errors and labels are recorded individually. The
volume reporting threshold is1e−6 mm³; a Boolean error is never a zero result.

Every solid index and its bounds are delivered in `assembly-index.json`.
[verify.py](verify.py) independently enumerates every unordered index pair and
proves that the AABB rejects, explicit intended pairs and exact results cover
the complete set without duplication. It also verifies input/artifact hashes.
A verifier PASS means the **negative evidence is consistent**, not a feasible lid.

The completed audit also separates28 Main component **clearance-reservation**
overlaps (independently enlarged XY envelopes, not measured physical body
collisions) and2 own nut/screw mating contacts (0.001291773mm³ each). They
remain recorded in `clearance_reservation_overlaps` and
`measured_intended_contacts`; the32 unexpected contacts exclude those categories.

Only same connected conservative cable-envelope constituents, cover partition
boundaries, own connector termination volumes and the documented D-037 Fly
source internals are classified as intended. These reasons and index pairs are
explicit. Nominal screw cores fit their pilots; no blanket fastener exclusion
conceals contacts. Nonphysical cap gauges and USB insertion gauges are not
installed assembly parts; actual cap-profile qualification remains the inherited
#232 limitation. USB gauges are independently swept below. No such limitation
is needed to establish the measured cable/PCB failure.

The cover is audited as a disjoint10mm tile partition to bound Boolean cost.
`cover-solid.py` independently reconstructs the one-piece cover and checks valid
single-solid topology and volume equality with the audited partition. This is
one physical cover, not a kit of tiles. `cover-metrology.json` records agreement.
All faces on its exterior top are Z16.20, including nominal flush screw heads;
all pockets open from below. Perimeter fitting around retained Fly-area rim
obstructions changes the cover edge, not the D-037 opening or top datum.

## Connected cable length, storage and service

| Harness | Longest represented conductor mm | Shorter R5 route, same family mm | Extra represented path mm | Unmodeled length mm |
|---|---:|---:|---:|---:|
{chr(10).join(wings)}

These lengths are below the fixed Rev.7 electrical qualification's200mm wire
bound. They are study path lengths, not released contact/cut dimensions. The
fourteen entry fanouts, common lower bundle and fourteen terminal fanouts form
one connected cable envelope per side. Shared fanout/bundle transition length
is subtracted once. No detached ring is credited. R5/OD1/OD5 are inherited
routing assumptions, not manufacturer-certified bend/tolerance specifications.

The reference U turns at Y22 instead of38; shortening each of its two straight
legs by16mm releases exactly32mm. This is a physically modeled geometric
reserve rather than160mm minus a straight endpoint chord. **It is not a PASS
for accessible service**: the colliding rise prevents an assembled/serviceable
harness. No full service configuration is certified just from length arithmetic.

The intended service sequence is concrete and keeps both Wing plates fixed:

1. Power off and unplug external USB; remove the two north M2x6 lid screws and
   two south M2x10 screws at the existing Main H2/H3 sites. The remaining Main
   H1 screw holds Main while the lid is removed.
2. Lift the lid vertically clear of its underside pockets; remove the two loose
   south POM spacers. No bracket remains over Main to trap the PCB.
3. Release both GH latches and withdraw the housings along their outward mating
   axes; do not pull conductors. Unplug Main EZmate before moving Main.
4. Remove Main H1 screw and lift the now disconnected Main vertically. Its three
   mounts/position and all Wing boards remain unchanged. The under-Main U paths
   are then open from above, not buried in a closed tunnel or under a Wing deck.
5. Lift/unlace either U and move its turn from Y38 toY22 to release32mm of that
   same cable; reverse the sequence for dressing, ensuring the cover bears on
   supports rather than wires. Fly service additionally releases its EZmate and
   two original seat screws; the D-037 seat is unchanged.

This procedure explains what must be unplugged and lifted and how the reserve
would be exposed; the failed collision gate prevents claiming it works on the
as-modeled assembly. No physical service demonstration is implied.

**Fly stock170mm** is retained in full as one valid solid/one connected OD2 R5
sweep, with original two EZmate endpoints. Its length is170.000000mm; volume is
170π within0.001mm³. No segment is omitted, shortened or detached. The stored
upper cruise axis is Z14.60/top15.60, beneath its pocket ceiling15.80. Per-pitch
waypoints and2001 samples are in measurements.json. The connected storage
solid is delivered as `fly-170mm.step`. Whether it is collision-free is evaluated
against the full assembly in the same exhaustive audit, not assumed from volume.

## Cover material, support and cost

Selected study material: **6061-T6 aluminium**,1.50 nominal. The GH pocket retains
#240's **ceiling Z15.95/depth1.25/skin0.25**, allowing0.20 over its Z15.75 mated
reference-plus-mounting reservation. Fly pocket skin is0.40; USB shell pocket
skin1.00. Main remains at topZ11.20. No rigid connector height or board placement
is reduced to obtain these figures.

Printed polymer is not selected for a0.25mm roof: it is approximately one FDM
layer and very flexible over the7.75mm pocket span. With a stated2GPa modulus,
the same10N strip screen predicts {mech['polymer_nominal_skin_deflection_mm']:.2f}mm deflection.
For aluminium, E69GPa and a conservative240MPa yield screening input give
**{s['ten_newton_deflection_mm']:.3f}mm deflection / {s['ten_newton_bending_stress_MPa']:.1f}MPa stress**
at nominal0.25mm, using a simply supported21.35mm-wide strip across7.75mm.
At an accepted minimum0.22mm skin the same screen gives
{st['ten_newton_deflection_mm']:.3f}mm / {st['ten_newton_bending_stress_MPa']:.1f}MPa.
These are local beam calculations, not full-panel FEA or a physical load test.
See [mechanics.py](mechanics.py) / [mechanics.json](mechanics.json).
Material context: [NIST6061-T6 reference](https://srd.nist.gov/NSRDS/NSRDS-NBS-61-V.pdf);
[Protolabs5052-H32 comparison](https://www.protolabs.com/media/iw0mfa0k/datasheet-sm-aluminum5052-h32.pdf).
The latter's typical properties do not qualify this machined skin by analogy to
Wing plates. Aluminium improves the local skin screen; it does not fix routing.

Manufacturing proposal: support the whole top face on sacrificial backing,
machine the underside pockets before releasing the perimeter, then deburr and
inspect skin thickness/flatness. No unsupported0.25mm FDM membrane, glued ledge
or unbounded heat-insert pullout is the proposed retention mechanism.

North retention uses **two M2x6 countersunk screws and AF4×1.6 captive nuts** in
integral OD8 pillars, topZ14.70. Each nut loads a1.6mm roof/remaining3.8mm lateral
ligament section, then the pillar and2mm tray floor. Under a stated10N lid pull,
assuming only two sites react, each takes5N: screw core tension
{mech['screw_tension_MPa']:.2f}MPa; nut-roof stress {mech['nut_roof_stress_MPa']:.2f}MPa,
versus a stated3MPa printed-part screening allowance. Side-loading slots permit
nut installation before closing; no bonded root is credited.

South retention uses **two M2x10 countersunk screws**, replacing Main H2/H3's
M2x6 pair without moving or drilling the board. Two **POM OD4.5/ID2.2×3mm spacers**
span Z11.70…14.70 over the original washers. Compression runs from lid through
spacer/washer/PCB to the original boss; tension runs through the screw into that
boss, nominal3.8mm engagement. A half-circumference thread shear screen gives
{mech['south_boss_thread_shear_area_mm2']:.2f}mm² and {mech['south_boss_thread_screen_stress_MPa']:.2f}MPa at5N.
Removing these two screws and spacers releases Main for service. The case
revision therefore has a specified mechanical load path and removable parts,
but **complete load/service qualification is not asserted**: a local fastener/
skin screen cannot qualify a colliding assembly or the entire pocketed panel.
Gate5 is not marked PASS by calling these calculations a physical test.

**Budget, not supplier quotations:** one-off pocketed cover approximately
**US$85–290** (1–2 shop hours at$60–120/h plus$25–50 stock/fixture/finish);
10-piece batch planning$25–80 per cover. Screws/nuts/spacers approximately$1–4
per set; tray revision net material is small, but a full replacement tray print
still costs its full filament and machine time. Printed-polymer material alone
would be inexpensive, roughly$1–3 for a small cover, but does not close the thin
skin/load issue here. No purchase, vendor quote, production case revision or
fabrication release is implied.

## Gates and reproduction

- **1 — zero interference:** FAIL by the exact Wing PCB/rising-wire measurements;
  both complete exhaustive audits are delivered.
- **2 — accessible ≥30mm per Wing:** NOT ESTABLISHED.32mm is connected and
  represented per side, with the above access procedure; a colliding assembly
  cannot certify usable reserve.
- **3 — connected stock Fly170mm:** full length/connected storage solid is
  established; all contacts against its neighbors remain visible in the audit.
  This does not rescue the failed combined assembly.
- **4 — D-037 external USB insertion:** {'PASS at both pitches' if all(d['usb_pass'] for d in ds.values()) else 'FAIL; see per-pitch swept reservations'} using the
  continuous30mm shell/overmold/cable-exit reservations with the lid fitted.
  The protected Fly seat/opening region is independently compared against the
  source case in `invariants.json`. The accepted D-037 defective official
  USB-shell/internal mating-model limitation remains; no new strict internal
  mating pass or physical USB test is invented.
- **5 — manufacturable retention/service:** defined parts, dimensions and load
  screens are delivered; complete structural/service acceptance is not achieved.

[Top view PNG](top-view.png) / [SVG](top-view.svg),
[pocket and retention sections PNG](sections.png) / [SVG](sections.svg),
[routing section PNG](section-routing.png) / [SVG](section-routing.svg).
The routing section is explicitly a YZ projection, not an X=constant clearance
section. Exact3D intersections, not that projection, establish failure.

Run `bash hardware/case/issue-242-bay-final/reproduce-all.sh` to regenerate both
pitches, audit **every pair**, reconstruct the single-solid cover, check retained
regions, write drawings/report and verify hashes. A pitch alone uses
`bash hardware/case/issue-242-bay-final/reproduce.sh 17` (or16). Default runs
rebuild and audit afresh. The close-out reused completed same-geometry audits,
without rebuilding or searching new routes. Earlier `audit-final16/17.log` files
stop mid-run and describe a superseded461-constituent model; `complete16/17.log`
finish the455-constituent geometry (62 raw hits,0 errors). The later
`audit-classified16/17.log` complete all the same candidates and separate those
hits into32 unexpected,28 reference reservations and2 own mating contacts.
Their `audit.json` and matching runtime index hashes are the verdict evidence.
The stale script error after `AUDIT COMPLETE` in complete logs occurred after
the audit verdict; the current reproduction script no longer contains that
truncated command. No incomplete audit supplies a verdict or requires a new
geometry run. Completed diagnostic logs are preserved under `evidence/`. `--audit-only --resume` is only for same-geometry runtime
checkpoints; geometry hashes must match. There is no reject-known/early-stop
mode. CAD_PYTHON and GEOMETRY_SITE can override the documented read-only CAD
Python/build123d0.13/OCP/Shapely2.2/sexpdata environment. System Python supplies
matplotlib. `python3 .../verify.py` checks saved evidence without CAD.

All scratch, process logs, BRep caches and the private Git database stay under
`.issue242-runtime/`. Its first commit snapshots the input checkout; work is
committed on `issue-242-bay-routing`. `inputs-sha256.json` binds source assemblies,
board and reference files; `artifact-sha256.json` binds this deliverable tree.
The private Git comparison confirms there are no production/baseline/decision
edits. Interrupted diagnostic runs do not supply acceptance evidence; only the
completed `audit.json` files do. The required feasible assembly was not
achieved, so the existing revision is rejected; the height-variable follow-on remains open.
'''
 (HERE/'REPORT.md').write_text(report)
if __name__=='__main__':main()
