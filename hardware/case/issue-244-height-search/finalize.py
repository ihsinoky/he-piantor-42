"""Write the study verdict from completed evidence and bind inputs/artifacts."""
from pathlib import Path
import json, hashlib, shutil
H=Path(__file__).resolve().parent; R=H.parents[2]
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d): p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def main():
 runs=[]
 for p in sorted(H.glob('delta-*/*mm'),key=lambda p:(float(p.parent.name[6:]),int(p.name[:-2]))):
  if not (p/'audit.json').exists():continue
  d=read(p/'measurements.json'); a=read(p/'audit.json'); m=read(p/'metrology.json'); inv=read(p/'invariants.json')
  assert a['all_pairs_enumerated'] and a['all_exact_candidates_completed'] and not a['early_stop']
  cable_ok=all(v['valid'] and v['solids']==1 for v in m['wings'].values())
  fly_hits=[v for v in a['unexpected_interferences'] if 'Fly-170mm' in (v['a'],v['b'])]
  gates={'1_zero_interference':a['interference_zero'], '2_accessible_service':a['interference_zero'] and cable_ok and all(w['represented_reserve_mm']>=30 for w in d['wings']), '3_fly_connected_storage':d['fly']['solid_count']==1 and abs(d['fly']['connected_length_mm']-170)<1e-6 and not fly_hits, '4_USB_insertion':d['usb_pass'] and inv['fly_scope_unchanged'], '5_retention':a['interference_zero'] and all(x['valid'] and x['solids']==1 for x in d['case_deltas'])}
  save(p/'gates.json',dict(gates=gates,all_gates_pass=all(gates.values()),scope='CAD study; no physical load or service test'))
  runs.append((p,d,a,m,inv,gates))
 assert runs
 passed=[d['delta_mm'] for p,d,a,m,i,g in runs if all(g.values())]
 title='No passing Delta established' if not passed else f'Minimum evaluated passing Delta: {min(passed):g} mm'
 text=f'''# Issue 244 — coordinated case-height and rise-route study

**{title}.** Study only; production geometry, baseline and decisions remain unchanged.
The saved Issue #244 assignment is [issue244.json](issue244.json).
'''
 if not passed:
  assert any(d['delta_mm']==10 and d['pitch_mm']==17 and not all(g.values()) for p,d,a,m,i,g in runs)
  text+='''
Both requested 17 mm candidates have complete covered-assembly audits. Delta=10
fails, so the requested stop condition applies. No 16 mm evaluation or downward
refinement is justified by these rejected packages. This rejects the evaluated
routes/case changes; it does not prove that every possible redesign at 10 mm is
impossible. There is no minimum passing Delta or passing-design drawing to report.
The drawings below document the measured rejected designs.
'''
 text+='''
## Design and coordinate convention

[CASE-REVISION.md](CASE-REVISION.md) gives the complete proposed case-change list.
Both trays and all twelve Wing posts are remade. Their original upper geometry
is split at Z3 and raised with the boards, supports, rim and decks; the section
is extended to the retained lower floor. The common cover/deck top is 16.2+Delta.
No PCB is cut or moved in XY. Main Rev.7 and Wing Rev.4 remain fixed inputs.

The redesigned rises differ from #242: the OD5 lower U has global centre Z7,
X±7/±19 and turn Y28. Fourteen OD1 wires per side return inward to
X±(5+off), Y−18 at Z7, then rise near X±(5+off), Y−5 to
Z12.8+Delta+dz before traversing toward X±(23+off), Y10 and the GH
approaches. The 5/5/4 pack uses off −2…2 and dz −1/0/+1. R5 rounded
curves, not waypoint chords, control geometry. Per-conductor rounded samples,
lengths and endpoints are in each measurements.json. There is no rack or exterior
storage. OD6 lower channels and buffered upper grooves are real case cuts.
Splice screws move from X−5/12 to X0/15 at both original Y rows. Hexagon-shaped
north nut pockets cut through both pillar and surrounding tray material.

**Cable coordinates in measurements.json are before the final Delta translation**;
add Delta to their Z values. Assembly indices, contact bounds and STEP exports
are in the final floor datum. The reported total height is the requested common
top datum 16.2+Delta, not a new claim about foot/keycap overall envelope height.

## Per-candidate full audit and gates

| Delta | Pitch | Top height | Solids | All pairs | AABB rejected | Intended | Exact candidates | Unexpected | Boolean errors |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
'''
 for p,d,a,m,i,g in runs:
  text+=f"| {d['delta_mm']:g} | {d['pitch_mm']} | {d['total_height_mm']:.1f} | {a['assembly_solids']} | {a['total_pairs']} | {a['aabb_rejected_pairs']} | {len(a['intended_pairs'])} | {a['exact_candidates']} | {len(a['unexpected_interferences'])} | {len(a['boolean_errors'])} |\n"
 text+='''
Every unordered constituent pair is enumerated, including retained/retained pairs.
AABB rejection only removes pairs with no positive overlap. Every remaining
non-intended pair gets OCCT Common; errors never count as clear. Tolerance is
1e−6 mm³. Cover tiles are a disjoint exact CSG partition; finish.py reconstructs
one valid machinable cover and checks its volume against the partition.
Same connected cable envelopes, own connector terminations, documented inherited
source internals and cover partition boundaries have explicit intended-pair
records. Enlarged Main component clearance reservations and nominal own
nut/thread contacts are separately retained in audit.json, as in #242.
No unexpected contact is exempted just because a previous study had it.

| Delta / pitch | 1: interference zero | 2: accessible ≥30 mm | 3: Fly 170 mm storage | 4: D-037 insertion | 5: retention acceptance |
|---|---|---|---|---|---|
'''
 for p,d,a,m,i,g in runs:
  text+=f"| {d['delta_mm']:g} / {d['pitch_mm']} | "+' | '.join('PASS' if v else 'FAIL / not established' for v in g.values())+' |\n'
 text+='''
## Measured binding contacts

All unexpected pairs, including repeated constituent contacts, are in each
collision-map.json with exact Boolean intersection bounds. Volumes are per pair;
their sum is not the unique collision volume. The remaining Wing PCB contacts show that this inward-rise redesign still
clips the fixed board footprint at its rounded transition. Merely deepening
the cavity with these waypoints does not yield zero interference; no geometric
claim that all alternative rise locations are impossible is made.
The following table groups pairs
only for readability, showing the largest constituent overlap and the bounding
union of their exact contacts. The complete maps remain authoritative.

| Delta / pitch | Parts | Pairs | Largest mm³ | Contact X mm | Contact Y mm | Contact Z mm |
|---|---|---:|---:|---|---|---|
'''
 for p,d,a,m,i,g in runs:
  groups={}
  for c in read(p/'collision-map.json'):groups.setdefault((c['a'],c['b']),[]).append(c)
  for (an,bn),cs in groups.items():
   lo=[min(c['overlap_bounds_mm'][0][k] for c in cs) for k in range(3)]; hi=[max(c['overlap_bounds_mm'][1][k] for c in cs) for k in range(3)]
   text+=f"| {d['delta_mm']:g} / {d['pitch_mm']} | {an} / {bn} | {len(cs)} | {max(c['volume_mm3'] for c in cs):.9f} | "+' | '.join(f'{x:.4f}…{y:.4f}' for x,y in zip(lo,hi))+' |\n'
 text+='''
## Connected length, service and USB

| Delta / pitch | Side | Longest represented conductor mm | Shorter reference mm | Represented reserve mm | Cable union valid / solids |
|---|---|---:|---:|---:|---|
'''
 for p,d,a,m,i,g in runs:
  for w in d['wings']:
   q=m['wings'][w['side']]
   text+=f"| {d['delta_mm']:g} / {d['pitch_mm']} | {w['side']} | {w['longest_conductor_mm']:.6f} | {w['reference_conductor_mm']:.6f} | {w['represented_reserve_mm']:.6f} | {q['valid']} / {q['solids']} |\n"
 text+='''
The U reference turns at Y12 instead of Y28, shortening two legs by 16 mm
and releasing 32 mm on the same harness; no detached loop or unmodeled cable
is credited. Fourteen entry fanouts, the shared lower bundle and fourteen rising
wires are union-tested; the table records validity and solid count. A failed
union does not certify one connected manufactured cable, and the original
audited conservative envelope export is retained in that case. The raw union
volume in metrology.json is an algorithm diagnostic for failed unions, not a
certified physical material volume; a negative mass or multiple solids is not
accepted as continuity evidence. R5/OD1/OD5 remain
study assumptions, not manufacturer-qualified bend or tolerance specifications.
These longer redesigned paths also exceed the fixed Rev.7 qualification's
200 mm conductor bound (see table); no electrical requalification or silent
relaxation of that bound is made.
A colliding assembly cannot certify accessible service from length arithmetic.

Proposed access procedure:

1. Disconnect external USB. Remove two north M2x6 and two south M2x10 cover
   screws. Main H1 remains installed while the cover is lifted.
2. Lift the lid and remove the two loose south POM spacers.
3. Release GH latches, withdraw each plug along its outward mating axis,
   disconnect Main EZmate, then remove H1 and lift Main. Wing boards/decks stay fixed.
4. Lift/unlace the now open under-Main U and move its turn from Y28 to Y12,
   recovering 32 mm. Reverse to reassemble, checking channel dressing and ensuring
   the cover bears on supports. This is a candidate procedure, not a successful
   service demonstration for a rejected design.

Fly is represented by one connected OD2 R5 sweep of exactly 170 mm, original
EZmate endpoints retained, volume 170π within 0.001 mm³. No segment is shortened
or detached. Its full fitted-case contacts enter the exhaustive audit. Each
USB shell/overmold/cable-exit reservation covers a continuous 30 mm insertion;
measurements.json records any overlap with actual case, lid, cables and hardware.
The protected D-037 seat/opening is separately compared above the Z3 extension,
undoing the uniform Delta translation. The deeper floor region is intentionally
changed and is not certified unchanged. The inherited defective official USB
internal-shell model limitation remains; no physical insertion test is implied.

## Cover, retention, print envelope and cost of Delta

6061-T6 aluminium cover, 1.50 mm nominal, underside 14.7+Delta, flush top
16.2+Delta. Underside pockets retain 0.25 mm GH, 0.40 mm Fly and 1.00 mm USB
skins. Fit the perimeter around retained north rim with 0.30 mm clearance.
Two north M2x6 countersunk screws load captured AF4×1.6 nuts in integral OD8
pillars rooted at global Z1. Two south M2x10 screws use existing Main H2/H3
bosses and washers through removable POM OD4.5/ID2.2×3 mm spacers. No board
hole or spacer length changes; nominal south engagement remains 3.8 mm.
Nuts enter through actual side slots before closure. All screw heads are flush.

The #242 local screens remain applicable to the translated upper details:
at the stated 10 N lid load, nominal 0.25 mm aluminium skin deflection 0.051 mm,
stress 87.1 MPa; 0.22 mm minimum skin gives 0.074 mm / 112.5 MPa. Per-retainer
5 N gives screw tension 2.49 MPa, nut-roof stress 0.82 MPa and south thread
shear 0.42 MPa. These are local study calculations from
[mechanics.json](../issue-242-bay-final/mechanics.json), not whole-panel FEA,
layer-strength qualification or a physical inversion test. Pillar length increases
with Delta; no full-case stiffness pass is inferred. A disconnected tray fragment
or an interference is a retention failure despite acceptable local stress screens.
Machine pockets with the top face supported, then release the perimeter and
inspect minimum skin, flatness and deburring. A one-layer printed roof is not selected.

| Delta / pitch | Part | Valid | Solids | Print XYZ incl. 5 mm XY brim, mm | Fits 220×220×250 |
|---|---|---|---:|---|---|
'''
 for p,d,a,m,i,g in runs:
  for side,q in m['printing'].items():
   dims=q['with_5mm_brim_xy_mm']+[q['z_mm']]
   text+=f"| {d['delta_mm']:g} / {d['pitch_mm']} | tray-{side} | {q['valid']} | {q['solids']} | "+' × '.join(f'{x:.2f}' for x in dims)+f" | {q['within_220x220x250']} |\n"
 text+='''
Delta=6 costs 6 mm additional common-top height (22.2 mm); Delta=10 costs
10 mm (26.2 mm). Both complete trays and twelve support posts must be remade;
this is not a lid shim. Plates, boards, spacers and the Fly assembly translate
rigidly; splice plates require new clearance holes. Increased wall/pillar material
and print time are additional to the full replacement print cost. No new supplier
quote is claimed. Reuse the #242 planning allowance: one-off machined cover
US$85–290, batch of ten US$25–80 each, retention parts US$1–4 per set.
The basis was 1–2 shop hours at US$60–120/h plus US$25–50 stock/fixture/finish.
The cover thickness/pocket process stays the same as Delta grows; the main
height cost is the case remake and taller keyboard, not thicker cover stock.

## Artifacts and reproduction

'''
 for p,d,a,m,i,g in runs:
  rel=p.relative_to(H)
  text+=f"- **Delta {d['delta_mm']:g}, {d['pitch_mm']} mm:** [audit]({rel}/audit.json), [contact map]({rel}/collision-map.json), [measurements]({rel}/measurements.json), [metrology]({rel}/metrology.json), [invariants]({rel}/invariants.json), [gates]({rel}/gates.json); [top PNG]({rel}/top-view.png) / [SVG]({rel}/top-view.svg), [sections PNG]({rel}/sections.png) / [SVG]({rel}/sections.svg).\n"
 text+='''
The routing section is a YZ projection, not an X-constant clearance section;
exact 3D intersections determine the verdict. STEP files deliver changed trays,
Wing cables, Fly storage and the single cover, plus the covered rejected assembly.

Run `bash hardware/case/issue-244-height-search/reproduce.sh 6 17` and similarly
`10 17`. Each rebuilds and audits all pairs, then performs metrology and protected
region comparison. `--audit-only --resume` reuses only hash-matched runtime BReps.
Run `python3 hardware/case/issue-244-height-search/drawings.py`, then
`finalize.py` and `verify.py` to regenerate presentation/hash verification.
The CAD_PYTHON/GEOMETRY_SITE overrides are documented in reproduce.sh.
The first metrology attempts in delta logs stopped on an assumption that rejected
Wing envelopes must union successfully. The completed metrology logs record
their actual failed union results; the verifier checks that these cannot pass
the service gate. No geometry or all-pairs audit was changed by that diagnostic
handling correction.
All scratch, BReps, logs and private Git live under `.issue244-runtime/`; nothing
uses `/tmp`. Completed logs are copied into evidence/. The private Git starting
snapshot and study commit permit checking that only this study directory changed.
A verifier PASS certifies consistent evidence, not a feasible assembly.
No production/baseline/decision edit, push, PR, fabrication release or order occurs.
'''
 (H/'REPORT.md').write_text(text)
 evidence=H/'evidence';evidence.mkdir(exist_ok=True)
 for p,d,a,m,i,g in runs:
  log=R/f'.issue244-runtime/delta{d["delta_mm"]:g}-{d["pitch_mm"]}.log'
  if log.exists():shutil.copyfile(log,evidence/log.name)
  metlog=R/f'.issue244-runtime/metrology{d["delta_mm"]:g}-{d["pitch_mm"]}.log'
  if metlog.exists():shutil.copyfile(metlog,evidence/metlog.name)
 inputs=[H.parent/'issue-228-final/base.py',H.parent/'issue-240-bay-cover/routes.py',R/'docs/decisions.md',H.parent/'issue-242-bay-final/REPORT.md',H.parent/'issue-242-bay-final/mechanics.json',H.parent/'issue-232-final/geometry.py',H.parent/'issue-232-final/verify.py',H.parent/'issue-240-bay-cover/study.py',H.parent/'issue-238-bay-study/main-inventory.json',R/'hardware/kicad/qualification/issue-235-wing-round2/main-native-obstacles.json',R/'hardware/kicad/qualification/issue-240-main-rev7/inspection/final/main.kicad_pcb']
 for p,d,a,m,i,g in runs:
  pitch=d['pitch_mm']
  inputs += [H.parent/f'issue-232-final/{pitch}mm/assembly.step',H.parent/f'issue-228-final/{pitch}mm/dimensions.json',H.parent/f'issue-238-bay-study/{pitch}mm-measurements.json',H.parent/f'issue-198-final/{pitch}mm/dimensions.json']
  for rel in read(H.parent/f'issue-232-final/{pitch}mm/inputs-sha256.json'):
   if (R/rel).is_file():inputs.append(R/rel)
 save(H/'inputs-sha256.json',{str(p.relative_to(R)):sha(p) for p in set(inputs)})
 save(H/'artifact-sha256.json',{str(p.relative_to(H)):sha(p) for p in H.rglob('*') if p.is_file() and p.name!='artifact-sha256.json'})
 print(title)
if __name__=='__main__':main()
