"""Current Round 3 report, preserving the complete preceding tuning report."""
from common import *
from collections import Counter

def category(n):
 for pre,label in [('Wire-','conductors'),('plate-screw-','E screws'),('plate-','aluminium plates'),('tray-','trays'),('underside-','Wing underside bounds')]:
  if n.startswith(pre):return label
 return n

def categories(a):
 return Counter(' / '.join(sorted([category(r['a']),category(r['b'])])) for r in a['unexpected_interferences'])

def render(rows):
 from report import GATES
 text='''# Issue #248 Phase B — Round 3 continuation

**PROVISIONAL on plateau Z24.65 / unmeasured Junana q=1.50. NOT RELEASED.**

## Round 3 results

The plate-boundary seam rule supersedes the tuning round's shell/plate ownership. The entire preceding report is preserved below and its evidence is frozen in [tuning-round/](tuning-round/REPORT.md); first-candidate evidence is also retained. Current results below supersede earlier current-candidate statements. Restart WIP disposition is recorded in [ROUND3-WIP-INVENTORY.md](ROUND3-WIP-INVENTORY.md), checkpoint cdc2085.

| Gate | 17 mm | 16 mm |
|---|---|---|
'''
 text+='\n'.join(f'| {n} | {rows[17][i]} | {rows[16][i]} |' for i,n in enumerate(GATES))+'\n\n'
 repair=read(HERE/'route-repair-attempts.json')
 assert repair['fitted_route_sha256']==sha(HERE/'routes-round3.json')
 text+=f"**Routing remains unresolved.** The finite local-repair screen examined {repair['screened_admissible_variants']} admissible waypoint variants with R5, positive stored/released tangent slack, finished length including 7.30 mm tails ≤200 mm, and connected 30.20 mm reserve. The three shortlisted changes were individually tested by exact Common against the 16 mm fitted assembly: "
 text+=', '.join(f"{r['conductor']}: {len(r['contacts'])} contacts" for r in repair['exact_probes']['rows'])
 text+=". All three remain blocked by fixed bodies and strands; the attempts also introduce tray/POM contacts. They are rejected and the frozen fitted round-3 route is retained. Full attempted waypoints, constraint checks and exact contacts are in [route-repair-attempts.json](route-repair-attempts.json). A separated fan/height-transition redesign is still required. This bounded unsuccessful search does not prove a compliant route impossible. No overlap exemption, thinner skin, shortened reserve or length waiver is used.\n\n"
 text+='''Deck Z13.55, slope lines, plateau Z24.65, 2.00 mm normal skin, unchanged boards/aluminium, M2×10 E screws, GH/Fly blister dimensions and Ø5.10 south openings remain binding. Tail-source.json supplies 3.40 mm/end plus the 0.50 mm Wing dress lead: 7.30 mm added to every routed conductor. The 164.8 mm value remains a reported reference. Physical Junana skirt/full-press and retention tests remain OPEN.

Tray route relief is an explicit conservative union of the projected conductor paths, buffered 0.87 mm and cut through their common height interval (clamped at Z2). This replaces overlapping per-strand Boolean tools; it may remove additional tray material within that reservation. The actual channel polygon and height are recorded in measurements.json. Initial floor restoration precedes splice remaking; the redundant post-pilot floor fuse is omitted because it produced invalid coincident topology. The final exact Common checks the complete original Z0…2 floor band, excluding only the authorized relocated pilot holes. Source floor, E thread-bearing support material and dedicated shell pillars are restored before the independent material, engagement, palm-band, fitted and print audits. Shell skin and aluminium are not cut by these channels.

'''
 for pitch in (17,16):
  out=HERE/f'{pitch}mm';get=lambda n:read(out/(n+'.json'))
  a=get('audit');s=get('seam');bl=get('tuning-blockers');lf=get('length-fly');service=get('service');v=get('export-verification');hw=get('hardware-inventory');inv=get('invariants');caps=get('caps');g=get('gates')
  old=read(HERE/'tuning-round'/f'{pitch}mm/audit.json');before=categories(old);after=categories(a)
  comparison=dict(geometry_sha256=sha(out/'assembly-index.json'),baseline='tuning-round/'+str(pitch)+'mm/audit.json',baseline_sha256=sha(HERE/'tuning-round'/f'{pitch}mm/audit.json'),categories=[dict(category=k,tuning=before[k],round3=after[k]) for k in sorted(before.keys()|after.keys())])
  save(out/'round3-comparison.json',comparison)
  text+=f'### Round 3 — {pitch} mm\n\n'
  text+=f"Exhaustive audit: {a['assembly_solids']} constituents, {a['total_pairs']} unordered pairs; {a['aabb_rejected_pairs']} AABB exclusions, {len(a['intended_pairs'])} explicit own mates, {a['exact_candidates']} exact Commons, {len(a['boolean_errors'])} Boolean errors. Threshold stays 1e−6 mm³. All gates bind to assembly-index.json; no prior PASS certifies changed operands.\n\n"
  if (out/'tray-seating-relief.json').exists():
   seat=get('tray-seating-relief');reuse=get('audit-E-restoration-reuse')
   text+=f"Final tray seating removes {sum(r['removed_volume_mm3'] for r in seat['changes']):.9f} mm³ only from trays north of the protected palm band. The two shell/tray contacts clear to zero Common. Shell, plate, POM and wire operands are byte-identical across that change. The full unordered-pair audit is re-enumerated; {reuse['reused_pair_count']} exact current-round results are reused only when both serialized operand hashes, names and indices match. Every changed-tray pair is recomputed. The independent package verifier replays that proof; all service/material/export gates rerun on the new index. Seam proof rebinding likewise verifies every unchanged shell/plate operand. See tray-seating-relief.json and audit-E-restoration-reuse.json.\n\n"
  text+='| Collision category | Tuning | Round 3 |\n|---|---:|---:|\n'+'\n'.join(f'| {k} | {before[k]} | {after[k]} |' for k in sorted(before.keys()|after.keys()))+'\n\n'
  text+='| Side | Longest finished mm | Routed mm | Connected reserve mm | Minimum radius mm |\n|---|---:|---:|---:|---:|\n'
  for w in lf['conductors']:text+=f"| {w['side']} | {w['cut_length_upper_mm']:.6f} | {w['longest_mm']:.6f} | {w['minimum_reserve_mm']:.6f} | {min(r['minimum_bend_radius_mm'] for r in w['all_conductors']):.6f} |\n"
  text+=f"\nFly: {lf['fly']['length_mm']:.9f} mm, R5, exact roof gap {lf['fly']['shell_gap_mm']:.6f} mm. USB sweep: {'PASS' if get('usb')['passed'] else 'FAIL'}. Sourced tails and per-wire geometry are in [length-fly.json]({pitch}mm/length-fly.json).\n\n"
  text+=f"**Seam geometry:** shell ownership ends at the full unchanged aluminium blank silhouette, including apertures; no shell is allowed inside plate apertures. Nominal horizontal gap and overlap are both 0 mm. Actual shell/plate Common maximum {max(r['common_mm3'] for r in s['shell_plate_contacts']):.9f} mm³; ownership maximum {max(r['plate_silhouette_overlap_mm3'] for r in s['ownership_material']):.9f} mm³. Full 2.00 mm normal skin check {'PASS' if s['skin_passed'] else 'FAIL'}; maximum missing required material {max(r['missing_required_skin_mm3'] for r in s['required_skin']):.9f} mm³. Slope vertical skin is {2*math.sqrt(1+M*M):.9f} mm.\n\n"
  text+='| Seam region | Length mm | Shell top minus plate top mm |\n|---|---:|---|\n'
  for r in s['seams']:text+=f"| {r['region']} | {r['length_mm']:.6f} | {r['shell_minus_plate_top_step_range_mm'][0]:.6f} … {r['shell_minus_plate_top_step_range_mm'][1]:.6f} |\n"
  text+=f"\nExact seam lines, trimmed boundary-distance witnesses (explicit [0, upper] intervals at ≤0.000001 mm for nominally coincident boundaries), and removed ownership regions are in [seam.json]({pitch}mm/seam.json). The central footprint is the component containing the declared bay datum (0,20); disconnected outer south perimeter regions are explicitly outside ownership, not discarded by volume ranking. No bridge crosses a well. Central shell: **{bl['central_shell_components']} solid(s)**. {bl['shell_connection_blocker'] or 'Single solid under the seam rule.'}\n\n"
  for r in bl['central_shell_separations']:text+=f"- Central solids {r['solids']}: exact gap {r['gap_mm']:.9f} mm.\n"
  if bl['fixed_roof_conflicts']:
   text+='\nFixed bodies intersecting the full required 2.00 mm skin (an underside pocket here removes required material):\n\n| Fixed body | Roof region | Common mm³ |\n|---|---|---:|\n'
   for r in bl['fixed_roof_conflicts']:text+=f"| {r['fixed_part']} | {r['required_skin_region']} | {r['intersection_mm3']:.9f} |\n"
   text+='\nThese residual contacts require a further explicit footprint, exterior or fixed-stack change. The seam rule is applied; no skin pocket or additional footprint exception is used to hide them.\n'
  text+='\nContinuous service motion (caps and Main removed, Wing hardware fitted):\n\n'
  for r in service['sides']:text+=f"- {r['side']}: {len(r['unexpected'])} contacts, {len(r['boolean_errors'])} errors; release {r['release_mm']:.6f} mm.\n"
  text+='\nThe remaining continuous-motion blockers are tray contacts (the fitted route itself has no tray contact); the translating reserve envelope is therefore not clear even after the caps/Main removal procedure:\n\n'
  for side in service['sides']:
   for r in side['unexpected']:
    text+=f"- {side['side']} strand {r['wire']:02d} / {r['part']}: {r['volume_mm3']:.9f} mm³.\n"
  text+=f"\nAccessible service is {'certified' if service['accessible_reserve_certified'] else 'NOT certified'}. The envelope covers every intermediate reserve-turn translation plus 0.020 mm allowance. Own moving harness is excluded as in the tuning method; fitted crossings remain independently disqualifying. See [service.json]({pitch}mm/service.json).\n\n"
  text+=f"E screws full engagement/root: {'PASS' if hw['all_E_replacements_passed'] else 'FAIL'}. Board/plate stack, protected palm and complete source floor band: {'PASS' if inv['passed'] else 'FAIL'}. Certified cap check: {'PASS' if caps['passed'] else 'FAIL'}. Independent manufacturing reload: {sum(r['passed'] for r in v['checks'])}/19 parts; preview {v['preview_reloaded_solids']}/{v['preview_expected_solids']} constituents.\n\n"
  shellcheck=next(r for r in v['checks'] if r['part']=='shell-central')
  text+=f"**{pitch} mm central-shell manufacturing verdict: {'PASS' if shellcheck['passed'] else 'FAIL'}** — STEP valid={shellcheck['valid']}, {shellcheck['solids']} solid(s), {shellcheck['mesh']['nonmanifold_edges']} nonmanifold STL edges. This shell-specific verdict does not waive any other part's manufacturing failure.\n\n"
  for r in v['checks']:
   if not r['passed']:
    text+=f"Manufacturing blocker **{r['part']}**: independently reloaded STEP valid={r['valid']}, {r['solids']} solid(s), STEP volume delta {r['step_volume_delta_mm3']:.9g} mm³; STL has {r['mesh']['nonmanifold_edges']} nonmanifold edges and {r['mesh']['degenerate_triangles']} degenerate triangles. Source validity or a manifold STL cannot substitute for a valid STEP reload.\n\n"
  if (out/'tray-step-diagnostics.json').exists():
   text+=f"Rejected serialization repair attempts and the invalid splice-boss face are recorded in [tray-step-diagnostics.json]({pitch}mm/tray-step-diagnostics.json). No validity check is relaxed.\n\n"
  for r in a['invalid_solids']:
   text+=f"Inherited constituent **{r['name']}** is invalid: {len(r.get('invalid_faces',[]))} invalid faces, bounds {r['bounds']}; diagnostic fix valid={r.get('diagnostic_fix_valid')}, volume delta {r.get('diagnostic_fix_volume_delta_mm3')} mm³. It remains a gate-1 blocker. Face areas/bounds are recorded in audit.json.\n\n"
  text+='Remaining failed gates and evidence:\n\n'
  for r in g['gates']:
   if not r['passed']:text+=f"- **{r['gate']}**: {r['evidence']}\n"
  if not s['skin_passed']:text+='- Required skin material is missing; see per-region exact volume checks in seam.json. No skin waiver is granted.\n'
  text+='\nFull named fitted blockers and intersection bounds are in audit.json / collision-map.json; exact roof blockers and shell separations are in tuning-blockers.json. A failed route is not proof that a compliant route is impossible.\n\n'
 text+='''## Round 3 reproduction

Run `bash hardware/case/issue-248-phaseb/reproduce.sh 17 16` with the retained CAD Python environment. All runtime scratch is in `.issue248-runtime/`. Every gate, independent STEP/STL reload, preview constituent count, collision witness and package hash/coverage check is rerun. Metrology runs length, USB, continuous service and invariants as separate processes; caps_only supplies the independent certified cap audit. This bounds memory and checkpoints completed sections without changing their geometric checks. Geometry ownership and full required skin are additionally checked by seam.py. Authorized openings are subtracted with the exact CAD cylinders: Ø5.10 south through-holes, Ø2.20 north through-holes and Ø4.00 north counterbores only over their top 1 mm. The preliminary inscribed-polygon masks falsely left circular slivers in the required material and are preserved under per-pitch evidence/; the collision/material thresholds are unchanged. No mesh welding, discarded in-footprint solid, changed collision threshold or strand-overlap exemption is used.

## Preserved tuning report (historical evidence)

'''
 text+=(HERE/'tuning-round/REPORT.md').read_text()
 return text
