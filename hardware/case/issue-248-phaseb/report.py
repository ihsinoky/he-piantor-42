"""Gate aggregation and review report, with explicit failures and cost arithmetic."""
from common import *
from collections import Counter
GATES=['1 Exhaustive fitted collision','2 Conductors and dressed target','3 Accessible ~30 mm service','4 Connected Fly 170 / R5 / roof gap','5 USB 30 mm insertion','6 Assumed swept caps after allowances','7 Print envelopes and manufacturing data','8 Fitted preview STEP']
def run():
 rows={};details=[];costs={}
 for pitch in (17,16):
  out=HERE/f'{pitch}mm';a=read(out/'audit.json');lf=read(out/'length-fly.json');u=read(out/'usb.json');c=read(out/'caps.json');s=read(out/'service.json');v=read(out/'export-verification.json');m=read(out/'manufacturing.json');d=read(out/'measurements.json');inv=read(out/'invariants.json')
  assert a['geometry_sha256']==sha(out/'assembly-index.json')==v['geometry_sha256']
  assert a['total_pairs']==a['aabb_rejected_pairs']+len(a['intended_pairs'])+a['exact_candidates']
  assert len(a['exact_results'])==a['exact_candidates']
  hits=a['unexpected_interferences'];flyhits=[r for r in hits if 'Fly-170mm' in (r['a'],r['b'])]
  fitted=a['passed'];motion=s['geometric_motion_passed'];service=fitted and motion and inv['passed']
  gate=[fitted,all(r['passed'] for r in lf['conductors']),service,lf['fly']['passed'] and not flyhits,u['passed'],c['passed'],v['passed'] and all(p['envelope_passed'] for p in m['parts']),v['preview_exists']]
  manufacture_failures='; '.join(f"{r['part']}: {r['solids']} solids, {r['mesh']['nonmanifold_edges']} nonmanifold STL edges, relative volume error {r['mesh']['volume_relative_error']:.9g}" for r in v['checks'] if not r['passed'])
  cap_reason=f"Minimum reported after 0.50 allowance {min(r['remaining_gap_mm'] for r in c['keys']):.6f} mm; physical skirt gate OPEN"
  if pitch==17 and not c['passed']:cap_reason+='; kernel reports zero distance with witnesses outside shell bounds, so no physical-contact or clearance verdict is certified'
  reasons=[f"{len(hits)} unexpected contacts; {len(a['boolean_errors'])} Boolean errors; see audit.json",f"Outlet routes pass, but crimp tails are unsourced. Conservative 5.70 mm/end bound: L {lf['conductors'][0]['cut_length_upper_mm']:.6f}, R {lf['conductors'][1]['cut_length_upper_mm']:.6f} mm; full/dressed limits unclosed",f"30.20 mm represented; motion {'clear' if motion else 'blocked'}; accessible certification requires fitted audit and invariants",f"{lf['fly']['length_mm']:.9f} mm; gap {lf['fly']['shell_gap_mm']:.6f}; {len(flyhits)} other fitted contacts",'Three continuous 30 mm reservations; see usb.json',cap_reason,'Independent STEP/STL failures: '+manufacture_failures if not v['passed'] else '19 STEP/STL/drawing sets independently reloaded; all envelopes checked','fitted-assembly-PROVISIONAL.step']
  rows[pitch]=['PASS' if g else 'FAIL' for g in gate]
  save(out/'gates.json',dict(status=P['status'],pitch_mm=pitch,gates=[dict(gate=n,passed=g,evidence=r) for n,g,r in zip(GATES,gate,reasons)],all_cad_gates_pass=all(gate),production_release=False,physical_full_press_skirt='OPEN',invariants=inv['passed'],accessible_service_reserve_certified=service))
  printed=sum(p['volume_mm3'] for p in m['parts']);mass=printed/1000*1.27;filament=mass*1.25
  cash=[filament/1000*20+2,filament/1000*30+6];hours=[printed/8/3600*1.5,printed/4/3600*1.5]
  cost=dict(status=P['status'],printed_material_volume_mm3=printed,nominal_PETG_mass_g=mass,filament_including_25_percent_support_waste_g=filament,filament_assumed_USD_per_kg=[20,30],retention_hardware_allowance_USD=[2,6],cash_material_and_new_retention_USD=cash,print_hours_estimate=hours,assumptions='PETG density 1.27 g/cm3; solid CAD volume; 25% support/waste; 4–8 mm3/s with 1.5 travel factor. Planning assumptions, no supplier quote.',costed_one_off_USD=[cash[0]+hours[0]+20,cash[1]+hours[1]+20],costed_basis='USD1/machine hour + USD20 assembly/finishing allowance; electricity included in machine allowance',scope='two trays, twelve remade posts, two splices, central shell, two strips, new shell retention; unchanged aluminium plates, boards, switches, caps, cables and reused standard hardware excluded')
  costs[pitch]=cost;save(out/'cost-estimate.json',cost)
  pairs=Counter(tuple(sorted([r['a'],r['b']])) for r in hits)
  failed='\n'.join(f'- **{n}: FAIL.** {reason}' for n,ok,reason in zip(GATES,gate,reasons) if not ok)
  group=Counter()
  for r in hits:
   aa,bb=r['a'],r['b']
   def cat(n):
    if n.startswith('Wire-'):return 'conductors'
    if n.startswith('plate-'):return 'aluminium plates / their fitted hardware'
    if n.startswith('tray-'):return 'trays'
    if n.startswith('Main-study-'):return 'Main component bounds'
    if n.startswith('underside-'):return 'Wing underside bounds'
    return n
   group[' / '.join(sorted([cat(aa),cat(bb)]))]+=1
  top='\n'.join(f'- {name}: {count} constituent contacts' for name,count in group.most_common())
  wtext='\n'.join(f"| {r['side']} | {r['longest_mm']:.6f} | {r['cut_length_upper_mm']:.6f} | {r['cut_length_upper_margin_to_200_mm']:.6f} | {r['dressed_longest_mm']:.6f} | {r['dressed_cut_length_upper_mm']:.6f} | {r['minimum_reserve_mm']:.6f} |" for r in lf['conductors'])
  env='\n'.join(f"| {p['name']} | {p['solids']} | {'yes' if p['valid'] else 'no'} | {' × '.join(f'{x:.3f}' for x in p['with_5mm_brim_xyz_mm'])} |" for p in m['parts'])
  servicehits='\n'.join(f"- {r['side']}: {len(r['unexpected'])} motion contacts, {len(r['boolean_errors'])} Boolean errors; `service.json` lists every part/wire." for r in s['sides'])
  details.append(f'''## {pitch} mm evidence

{failed or 'All eight CAD gates pass.'}

| Side | Outlet route max mm | Full cut upper bound mm | Bound margin to 200 | Routed dressed max mm | Dressed cut upper bound mm | Represented reserve mm |
|---|---:|---:|---:|---:|---:|---:|
{wtext}

Collision audit: **{a['assembly_solids']} physical constituents, {a['total_pairs']} unordered pairs**, {a['aabb_rejected_pairs']} AABB rejects, {len(a['intended_pairs'])} explicit own-mate pairs, {a['exact_candidates']} completed exact Commons. Threshold stays 1e−6 mm³. No early stop. {len(a['boolean_errors'])} Boolean errors. Full pair results and all witnesses by constituent name are in [{pitch}mm/audit.json]({pitch}mm/audit.json). Positive component-bound overlaps are listed separately, as in #246; they do not disappear from the evidence. Inherited official Fly source invalidities remain labelled, and never justify a new case or wire collision.

Contact categories:

{top or '- None.'}

Continuous service motion:

{servicehits}

Fly: one valid connected swept solid, **{lf['fly']['length_mm']:.9f} mm**, R5, volume error {lf['fly']['volume_error_mm3']:.9f} mm³ against 170π, minimum true shell distance **{lf['fly']['shell_gap_mm']:.6f} mm**. Its fitted contacts with other bodies are separately applied to gate 4. USB results enumerate all three shell/overmold/exit reservations and their full 30 mm travel. Caps: all 42 assumed 16 mm swept envelopes are tested against the actual shells, strips and blisters with a 0.50 mm combined allowance; the solver reports worst remaining gap **{min(r['remaining_gap_mm'] for r in c['keys']):.6f} mm**. For 17 mm, zero-distance witnesses outside the central shell's bounds make this an **uncertified kernel result**, not proof of a physical cap contact. `cap-witnesses.json` preserves the inconsistent points. The physical skirt/full-press gate also remains open.

| Print | Solids | Valid | XYZ including 5 mm XY brim, mm |
|---|---:|---|---|
{env}

STEP/STL meshes are independently reloaded in [{pitch}mm/export-verification.json]({pitch}mm/export-verification.json), including edge manifoldness, degeneracies and volume agreement. A multi-solid print remains failed even when its bounding envelope fits. Each print has an SVG drawing and the numerical dimension register. All geometry is in assembly coordinates; translate each print's lowest Z to the bed in the slicer. The fitted preview is [{pitch}mm/fitted-assembly-PROVISIONAL.step]({pitch}mm/fitted-assembly-PROVISIONAL.step).

Planning cost for the **printed case set plus new retention**: {mass:.1f} g nominal PETG, {filament:.1f} g with support/waste; **USD {cash[0]:.2f}–{cash[1]:.2f}** material/hardware cash allowance. Estimated printer time {hours[0]:.1f}–{hours[1]:.1f} h. With USD1/machine-hour and USD20 assembly/finishing allowance: **USD {cost['costed_one_off_USD'][0]:.2f}–{cost['costed_one_off_USD'][1]:.2f}**. These are arithmetic planning allowances, not quotes, and do not include a rerun of a rejected design. Unchanged aluminium plates and electronics are excluded. [{pitch}mm/cost-estimate.json]({pitch}mm/cost-estimate.json) records every assumption.
''')
 table='\n'.join('| '+n+' | '+rows[17][i]+' | '+rows[16][i]+' |' for i,n in enumerate(GATES))
 report=f'''# Issue #248 Phase B — production-intent GH low deck / raised keyless case

**PROVISIONAL: every CAD, mesh, drawing, audit, dimension and cost in this tree is conditional on the single named `plateau_top_z_mm = {TOP:.2f}` parameter, based on unmeasured Junana q=1.50. NOT RELEASED.** The latest Issue #248 comments, including PO's GH Phase B GO, were read first and are frozen in [sources/issue248-go.json](sources/issue248-go.json). GH stays; DF52/SH are not reopened. All prior study trees remain untouched. This package delivers fitted candidates and the complete audit, including failed gates; it does not convert a failed audit into approval to manufacture.

| Gate | 17 mm primary | 16 mm verification |
|---|---|---|
{table}

The physical full-press Junana skirt-to-plate test remains **OPEN** at both pitches. The provisional q is not a measured cap height or a production tolerance bound. Read the failed-gate blockers below before using manufacturing files.

## Geometry, material ownership and invariants

Plate top is Z13.55; Main and Wing PCB undersides remain Z7.35. Main Rev.7 and Wing Rev.4, GH placements, aluminium plate shape/thickness and the board-to-plate stack are preserved by rigid translation −2.65 from #232. The case floor remains at Z0, nominal floor top Z2. Trays and all twelve E/R support posts are remade by removing the neutral Z3…5.65 band; upper seats move down 2.65 while floor and post sockets remain. Floor-level splices, screws and rubber feet stay at their original floor datum. `invariants.json` compares the fitted boards/plates and the continuous south palm band against their source. No input PCB or aluminium manufacturing file is edited.

The slope exterior is one plane between **Y{START:.9f} and Y{TOE:.9f}**, with straight X-parallel breaks. The 18 mm wells remain; outer/palm/thumb margins stay at plate height. North strips end at the start line. A4's overlapping plateau/strip polygons are a surface union; B assigns common material to the strips, rather than physically superposing printed parts. Small north wall tongues are assigned to the adjoining strip only after a zero-distance, valid single-solid union check. All original material is retained unless explicitly identified as an obsolete detached tray rim nib. The 16 mm disconnected south shell section is retained and reported; it is not silently discarded or joined through a key well.

Nominal PETG walls and **normal** roof thickness are 2.00 mm. Consequently the slope's vertical thickness is {2*math.sqrt(1+M*M):.9f} mm: {2*math.sqrt(1+M*M)-2:.9f} more underside intrusion than B0's 2 mm vertical study skin. This is an explicit implementation interpretation of the requested 2 mm roof; the A4 exterior plane and datums are unchanged. It is applied to clearance audits, rather than borrowing B0's clearance verdicts.

Both Main GH projections use the B1 drawing-bounded seated header/plug model, ceiling **Z13.20**, top **Z15.20**, maximum rise 1.65. These are nominal manufacturer drawing bounds, not unpublished moulding cavities or certified production maxima. The baseline Fly storage uses ceiling **Z13.25**, top **Z15.25**, maximum rise 1.70. Blister blend masks extend 0.50 mm north under the already higher slope to recover true 0.30 mm clearance with the normal 2 mm skin; this does not raise the specified blister tops or alter the exterior slope plane. Walls stand outside the obstacle +0.30 clearance footprint. South screw/spacer openings are **Ø5.10** at **(−31.892683,64.40)** and **(+31.892683,64.40)**; the adopted right hardware's 1e−6 mm asymmetry is retained in the hardware, not substituted for the requested hole centre. Those screws retain Main, not the shell.

The case uses #246's X−5/12 → X0/15 splice-screw relocation at Y−8/55, with lower floor-rooted Ø7 bosses, top Z5.50 and Ø1.70 pilots. Changed splices keep their original print pattern and gain the new Ø2.20 clearance holes. Case-only grooves follow the dedicated wires with 0.87 mm projected radius; the wire solids remain exact R5 sweeps. Subtractions never alter a PCB or plate. Routing can isolate obsolete rim nibs; `geometry-finish.json` records their explicit regions, bounds and removed volume. Topology repair is accepted only when valid and volume change <1e−6 mm³. No tolerance is enlarged and no arbitrary largest-solid filter is used.

## Retention and service design

The central shell uses **two independent north M2 retainers at (±8,−30)**. Each has a floor-rooted Ø6 pillar ending at Z22.65, a 2.8 mm heat-insert pilot over its top 4 mm, a 2.2 mm shell clearance and 4.0 mm head recess. The nominal low-head screw envelope is Ø3.6 × 1.0, under-head length 4 mm, with 3 mm engagement into the insert. Procurement must meet that envelope; no supplier quote or validated insert pull-out value is claimed. The south Ø5.10 openings carry no retention load.

Each strip bears on the unchanged keyless north deck through its 2 mm perimeter walls. Two 2 mm tabs per strip at Y−40/−23 extend X8…14 (mirrored left), below the central roof with 0.30 mm clearance. Open-bottom slots let the central shell lift vertically. Upward strip loads pass through the captured tabs into the central roof, its north screws, inserts, pillars and tray floor. Downward roof loads pass through walls to the deck/rim and through the north pillars; south rim contact must be assessed with the collision evidence. The two-retainer local 10 N screen gives 5 N per screw, about 2.49 MPa on a nominal Ø1.6 screw section. This is not whole-shell bending, tab fatigue, insert pull-out or physical inversion qualification; fitted contacts and disconnected geometry prevent release where reported.

Service: disconnect external USB; remove the two north shell screws and lift the central cap; lift the two independent strips. Wing boards, plate screws, posts and spacers remain fitted. Release Main GH latches and withdraw along their outward mating axes; disconnect Main EZmate, remove Main's own H1 and south hardware/loose spacers, then lift Main. Retain the Fly cable in its dressed storage pose. Access each connected U through the open Main bay and move its turn continuously Y22.1→7.00, recovering 30.20 mm into the disconnected Main end. Reverse this procedure, redress the U to Y22.1, seat the caps and tighten their north screws. This is the proposed procedure: only the gate table can certify its fitted/motion feasibility.

The dedicated route has fourteen OD1 conductors per side, horizontal Wing Z5.75 and Main Z10.65 outlet dress axes, R≥5 throughout, no detached reserve; the curves end at nominal outlet dress planes. Outlet axes are nominal paths inside the drawing-bounded faces, not measured individual GH cavity centres. The 4/3/4/3 lower pack sits at Z4.90 in the Main bay, rises north of Main inside the central neck, then traverses at nominal Z14.80 with separated upper offsets. **Deviation from the first-pass packing suggestion:** reserve is stored below Main at Y7…22.1, south of the north neck, rather than above the deck near Y25…45. This saves routed length and avoids allocating the same volume to two high loops. **Length gate blocker:** the internal wire tip/crimp reference planes are not dimensioned by the bounded outlet model. The earlier routed lengths omit those tails. A deliberately conservative 5.70 mm per end, using B1's plug tip-to-wire-end bound, produces 201.151412 / 202.169482 mm full cut bounds and 170.951412 / 171.969482 mm dressed cut bounds. Both the full and dressed qualifications therefore remain failed; the routed-only margins are not claimed as finished-conductor margins. No terminal length is silently set to zero. It is not claimed accessible merely because 30.20 mm is represented. The service audit uses a continuous filled cap-motion strip for every strand with 0.020 mm excess envelope, and checks retained Wing stacks, case, the other harness and the dressed Fly cable.

## Failed gates and full evidence

Every unexpected fitted pair and Boolean error is retained in each pitch's `audit.json`; motion blockers are in `service.json`; USB blockers in `usb.json`; cap witnesses in `caps.json`. The unmodified aluminium plate and 2 mm slope/low roofs are audited as separate bodies. Any overlapping material remains a failed gate; it is not waived as a mating contact. This exposes whether the settled exterior, full roof thickness and unchanged plate can coexist at the slope-to-deck transition. No plate notch, reduced skin, smaller cap, shorter cable or higher deck is introduced to conceal a failure.

'''+''.join(details)+'''
## Files and reproduction

Both pitch directories contain the fitted STEP, manufacturing STEP/STL/SVG for all nineteen printed parts, a dimension register, connected service-motion STEP envelopes, and raw gate evidence. PROVISIONAL is embedded in manufacturing filenames, STEP labels, STL headers and drawings. Plate drawings/manufacturing remain the unchanged D-038 package in #232; they are not reissued as printed plates. `parameters.json` is the single plateau-height authority. `artifact-sha256.json` binds this report, scripts and outputs; `inputs-sha256.json` binds all source CAD, layouts and PCB inputs. The runtime git contains checkpoint commits; no push, purchase or production release is performed.

Run `bash hardware/case/issue-248-phaseb/reproduce.sh 17 16` from the worktree with the existing CAD Python environment. All scratch, source BRep caches, audit checkpoints and logs stay in `.issue248-runtime/`; no `/tmp` scratch is used. Each stage is separate to bound memory. Exact audits checkpoint progress and resume only when the geometry-index hash matches. Do not reuse any PASS from a prior geometry or prior study. The independent export verifier and full-pair accounting are part of the final run.
'''
 (HERE/'REPORT.md').write_text(report)
 for pitch in (17,16):
  for folder in [HERE/f'{pitch}mm',HERE/f'{pitch}mm/manufacturing']:
   (folder/'PROVISIONAL.txt').write_text(P['status']+'\nAll files in this directory are conditional on plateau_top_z_mm in parameters.json. See ../../REPORT.md and the per-pitch gates before manufacturing.\n')
 inputs=[]
 for pitch in (17,16):
  inputs += [HERE.parent/f'issue-232-final/{pitch}mm/assembly.step',HERE.parent/f'issue-232-final/{pitch}mm/dimensions.json',HERE.parent/f'issue-246-delta6-tuning/packed/delta-6/{pitch}mm/fly-170mm.step',HERE.parent/f'issue-246-delta6-tuning/packed/delta-6/{pitch}mm/measurements.json']
  inputs+=list((HERE.parent/f'issue-232-final/{pitch}mm/plate-package').glob('*'))
 inputs += [HERE.parent/'issue-248-lowdeck-raise/raised-regions-a4.geojson',HERE.parent/'issue-248-lowdeck-raise/tables-a4.json',HERE.parent/'issue-248-lowdeck-raise/b1/mated-gh-assembly-frame.step',ROOT/'hardware/kicad/qualification/issue-240-main-rev7/inspection/final/main.kicad_pcb']
 inputs+=list((ROOT/'hardware/kicad/qualification/issue-235-wing-round2').glob('wing-rev4-*/routed.kicad_pcb'))
 save(HERE/'inputs-sha256.json',{str(p.relative_to(ROOT)):sha(p) for p in inputs if p.is_file()})
 save(HERE/'artifact-sha256.json',{str(p.relative_to(HERE)):sha(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='artifact-sha256.json' and '__pycache__' not in str(p)})
 print('Gate table',rows)
if __name__=='__main__':run()
