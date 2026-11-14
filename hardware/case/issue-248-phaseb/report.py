"""Current tuning gates; original candidate evidence remains under first-candidate/."""
from common import *
from collections import Counter
GATES=['1 Exhaustive fitted collision','2 Finished conductors ≤200 mm','3 Accessible ~30 mm service','4 Connected Fly 170 / R5 / roof gap','5 USB 30 mm insertion','6 Assumed swept caps after allowances','7 Print envelopes and manufacturing data','8 Fitted preview STEP']
def run():
 # Rechecking source hashes precedes any manifest regeneration.
 for n,h in read(HERE/'inputs-sha256.json').items():assert sha(ROOT/n)==h,('changed design input',n)
 rows={};details=[]
 for pitch in (17,16):
  out=HERE/f'{pitch}mm';get=lambda n:read(out/(n+'.json'))
  a=get('audit');lf=get('length-fly');u=get('usb');c=get('caps');s=get('service');v=get('export-verification');m=get('manufacturing');inv=get('invariants');ret=get('retention-check');cw=get('cap-witnesses');cm=get('collision-map');bl=get('tuning-blockers');hw=get('hardware-inventory')
  ghash=sha(out/'assembly-index.json')
  assert all(d['geometry_sha256']==ghash for d in [a,v,c,cw,cm,ret,bl,lf,u,s,inv])
  assert a['total_pairs']==a['aabb_rejected_pairs']+len(a['intended_pairs'])+len(a['exact_results'])
  assert len(a['exact_results'])==a['exact_candidates'] and cm['complete'] and len(cm['contacts'])==len(a['unexpected_interferences'])
  hits=a['unexpected_interferences'];flyhits=[r for r in hits if 'Fly-170mm' in (r['a'],r['b'])]
  service=a['passed'] and s['geometric_motion_passed'] and inv['passed'] and ret['local_geometry_passed']
  s['accessible_reserve_certified']=service;save(out/'service.json',s)
  passed=[a['passed'],all(r['passed'] for r in lf['conductors']),service,lf['fly']['passed'] and not flyhits,u['passed'],c.get('certified',False) and c['passed'] and not cw['solver_inconsistencies'],v['passed'] and all(r['envelope_passed'] for r in m['parts']),v['preview_exists'] and v['preview_inventory_passed']]
  capmin=min(r['remaining_gap_mm'] for r in c['keys'])
  reasons=[f"{len(hits)} unexpected contacts; {len(a['boolean_errors'])} Boolean errors; exhaustive all-pair audit.",f"Longest finished upper bound {max(r['cut_length_upper_mm'] for r in lf['conductors']):.6f} mm including 3.90 mm Wing / 3.40 mm Main sourced dress-to-tip bounds and 30.20 mm connected reserve; nominal assembly conditions in tail-source.json.",f"Motion {'clear' if s['geometric_motion_passed'] else 'blocked'}; fitted collisions additionally prevent accessible certification.",f"{lf['fly']['length_mm']:.9f} mm, R5; true roof gap {lf['fly']['shell_gap_mm']:.6f} mm; {len(flyhits)} fitted contacts.",'Three continuous 30 mm reservations recomputed.',f"Certified trimmed-face minimum after 0.50 mm allowance: {capmin:.6f} mm; physical Junana skirt test OPEN.",'; '.join(f"{r['part']}: {r['solids']} solids, {r['mesh']['nonmanifold_edges']} nonmanifold edges" for r in v['checks'] if not r['passed']) or 'All nineteen STEP/STL sets independently reloaded with unchanged verifier.',f"Preview reloaded {v['preview_reloaded_solids']} / {v['preview_expected_solids']} constituents."]
  rows[pitch]=['PASS' if r else 'FAIL' for r in passed]
  save(out/'gates.json',dict(status=P['status'],pitch_mm=pitch,gates=[dict(gate=n,passed=p,evidence=e) for n,p,e in zip(GATES,passed,reasons)],all_cad_gates_pass=all(passed),production_release=False,physical_full_press_skirt='OPEN',invariants=inv['passed'],accessible_service_reserve_certified=service))
  vol=sum(p['volume_mm3'] for p in m['parts']);mass=vol/1000*1.27;filament=mass*1.25;cash=[filament/1000*20+2+.8,filament/1000*30+6+2.4];hours=[vol/8/3600*1.5,vol/4/3600*1.5]
  cost=dict(status=P['status'],printed_material_volume_mm3=vol,nominal_PETG_mass_g=mass,filament_including_25_percent_support_waste_g=filament,cash_material_and_new_retention_USD=cash,print_hours_estimate=hours,costed_one_off_USD=[cash[0]+hours[0]+20,cash[1]+hours[1]+20],assumptions='PETG 1.27 g/cm3, 25% waste, USD20–30/kg; shell retainers/inserts USD2–6; eight replacement M2x10 USD0.80–2.40 total; no quote. 4–8 mm3/s, 1.5 travel factor. USD1/machine-hour plus USD20 assembly.',scope='Printed case and new retention plus eight replacement E screws; unchanged electronics/aluminium excluded.')
  save(out/'cost-estimate.json',cost)
  wiretable='\n'.join(f"| {r['side']} | {r['longest_mm']:.6f} | {r['cut_length_upper_mm']:.6f} | {r['cut_length_upper_margin_to_200_mm']:.6f} | {r['dressed_cut_length_upper_mm']:.6f} | {r['dressed_finished_margin_to_164_8_mm']:.6f} | {r['minimum_reserve_mm']:.6f} |" for r in lf['conductors'])
  categories=Counter()
  def cat(n):
   for prefix,label in [('Wire-','conductors'),('plate-screw-','E screws'),('plate-','aluminium plates'),('tray-','trays'),('underside-','Wing underside bounds')]:
    if n.startswith(prefix):return label
   return n
  for h in hits:categories[' / '.join(sorted([cat(h['a']),cat(h['b'])]))]+=1
  muxhits=sum('MUX' in r['a'] or 'MUX' in r['b'] for r in hits)
  strandhits=sum(r['a'].startswith('Wire-') and r['b'].startswith('Wire-') for r in hits)
  contacts='\n'.join(f'- {n}: {count} contacts.' for n,count in categories.most_common()) or '- None.'
  motion='\n'.join(f"- {r['side']}: {len(r['unexpected'])} contacts, {len(r['boolean_errors'])} errors; represented release {r['release_mm']:.2f} mm." for r in s['sides'])
  checks='\n'.join(f"| {r['part']} | {r['solids']} | {r['mesh']['nonmanifold_edges']} | {'PASS' if r['passed'] else 'FAIL'} |" for r in v['checks'])
  local='\n'.join(f"- {r['part']}: distance {r['distance_mm']:.6f} mm; Common {r['common_mm3']:.9f} mm³." for r in get('local-measures')['results'])
  roofconflicts='\n'.join(f"- {r['fixed_part']} / required {r['required_skin_region']} roof: {r['intersection_mm3']:.6f} mm³." for r in bl['fixed_roof_conflicts'])
  details.append(f'''## {pitch} mm current evidence

'''+ '\n'.join(f"- **{n}: {ok}.** {e}" for n,ok,e in zip(GATES,rows[pitch],reasons))+f'''

| Side | Routed max mm | Finished bound mm | Margin to 200 mm | Finished dressed bound mm | Margin to 164.8 reference mm | Connected reserve mm |
|---|---:|---:|---:|---:|---:|---:|
{wiretable}

The 164.8 mm value is a reported Phase A reference, not a binding gate. The 3.40 mm internal tails plus the 0.50 mm Wing dress lead are included in finished and dressed bounds. The 30.20 mm reserve is the difference between connected curves, not a detached length allowance. See [length-fly.json]({pitch}mm/length-fly.json).

Fitted audit: **{a['assembly_solids']} constituents, {a['total_pairs']} unordered pairs**, {a['aabb_rejected_pairs']} AABB exclusions, {len(a['intended_pairs'])} explicitly classified own mates, {a['exact_candidates']} exact Commons, {len(a['boolean_errors'])} operation errors. Intersection threshold remains 1e−6 mm³. [tuning-comparison.json]({pitch}mm/tuning-comparison.json) lists cleared, remaining and new named pairs against the first candidate. Both pitch geometries and all exact candidates were rerun in this tuning round. After E-boss restoration, results are replayed only when both serialized operand hashes, names and constituent indices are unchanged; every changed-tray pair is recomputed. audit-E-restoration-reuse.json binds this proof to preserved parent evidence; verify_package.py independently checks it. No first-candidate PASS is reused. Full names, Common volumes/bounds and all positive contacts are in [audit.json]({pitch}mm/audit.json) and [collision-map.json]({pitch}mm/collision-map.json). Inherited Fly source invalidities remain labelled.

{contacts}

Continuous service-motion results:

{motion}

The swept envelope includes every intermediate translation of each concentric reserve U, plus a 0.020 mm excess. Wing stacks and the other harness remain fitted. Main and its removable hardware, shell caps and own moving harness are excluded as documented in service.json. The fixed legs shorten along their existing loci. A clear reserve-motion result alone cannot certify a harness with fitted fan/upper-route crossings. Individual own-harness motion was not promoted to service certification while those crossings remain. The new route clears every fixed Wing MUX bound ({muxhits} MUX contacts), but still has {strandhits} strand/strand fitted contacts plus the fixed-body contacts listed above; it is not a successful separated-harness qualification.

Hardware: all eight **M2×10** E replacements {'PASS' if hw['all_E_replacements_passed'] else 'FAIL'}. Under-head Z13.85, tip Z3.85, boss top Z7.35: **3.50 mm nominal engagement**, full thread-bearing annulus verified by exact Common (major radius 1.00 / pilot radius 0.85 over Z3.85…7.35), tip **1.85 mm above floor top**, **≥1.20 mm root material** verified with material probes. Washer and head envelope are retained. Existing pilot depths remain recorded per seat. Replacement procurement must preserve the polymer-compatible thread and Ø3.4 ×1.3 mm head envelope; physical retention remains untested. [hardware-inventory.json]({pitch}mm/hardware-inventory.json) lists each seat. New north-head wall relief is below the plateau roof. A stricter engagement check rejected the routing cuts that left only 32.5% of the two north thread-bearing annuli. Exact original source boss material within a named Ø7 region was restored, preserving its pilots and the compressed stack; hardware-inventory.json now requires complete annulus and root material. This adds legitimate wire/boss contacts to the failed routing evidence, rather than weakening the supports. Required-skin contacts are not excused by it.

Certified local distances:

{local}

Caps: all 42 assumed 16×16 mm swept envelopes, Z13.95 to provisional Z24.65, checked against every actual central/strip solid. Common is below 1e−6 mm³ for every pair. The minimum exact trimmed-face distance is **{capmin+.5:.6f} mm**, leaving **{capmin:.6f} mm** after the unchanged 0.50 mm allowance, against a 0.30 mm gate. Face pairs are excluded only by Euclidean AABB lower bounds; finite closest points and their actual face bounds are checked. This bypasses the defective whole-solid inside classifier. [cap-witnesses.json]({pitch}mm/cap-witnesses.json) records faces and points. Physical skirt/full-press test remains OPEN.

Required-skin blockers (independent intersection of the unchanged roof rule and fixed bodies):

{roofconflicts or '- None.'}

These overlaps cannot be removed by underside relief while preserving a full 2.00 mm skin below the settled exterior at the same footprint. The low roof occupies Z11.55…13.55; the aluminium plate occupies Z12.05…13.55. Clearing it requires changed footprint/material ownership, stack or exterior. None is silently changed. Other remaining tray/hardware/strand contacts are still failed and enumerated, not claimed impossible merely because this candidate fails.

Central shell: **{bl['central_shell_components']} solids**. {bl['shell_connection_blocker'] or 'Boundary regularization cancels opposing internal planar sheets; volume preserved within 1e−6 mm³. All detached north tongues are explicitly assigned to an adjoining strip only after a valid volume-preserving single-solid union.'} Exact component separation and footprint component bounds are in [tuning-blockers.json]({pitch}mm/tuning-blockers.json). A disconnected south section is retained in STEP/STL and the print gate fails for it.

| Print | STEP solids | Nonmanifold STL edges | Export verification |
|---|---:|---:|---|
{checks}

The unchanged export checks include STEP validity, single solid, 220×220 mm XY envelope including 5 mm brim, height ≤250 mm, exact STL edge incidence, no degenerate triangles, volume error <0.001, hashes and preview inventory. No mesh welding or discarded solid is used. [export-verification.json]({pitch}mm/export-verification.json), manufacturing STEP/STL/SVG and dimension register correspond to this candidate.

Updated planning cost: {mass:.1f} g nominal PETG; {filament:.1f} g with waste; USD {cash[0]:.2f}–{cash[1]:.2f} case material/new hardware; {hours[0]:.1f}–{hours[1]:.1f} print hours. Including machine time and assembly, USD {cost['costed_one_off_USD'][0]:.2f}–{cost['costed_one_off_USD'][1]:.2f}. Eight M2×10 replacements are newly included; these are assumptions, not quotes.

''')
 table='\n'.join(f'| {n} | {rows[17][i]} | {rows[16][i]} |' for i,n in enumerate(GATES))
 report=f'''# Issue #248 Phase B — tuning continuation

**PROVISIONAL on plateau Z24.65 / unmeasured Junana q=1.50. NOT RELEASED.**

This tuning candidate closes only the gates shown as PASS. It does not complete the requested all-clear wiring/service design. The original first-candidate report and evidence remain byte-preserved in [first-candidate/](first-candidate/REPORT.md). PO comments were reread with `gh issue view 248 --comments`; the continuation snapshot is in sources/issue248-continuation.json.

| Gate | 17 mm primary | 16 mm verification |
|---|---|---|
{table}

## Kept and discarded interrupted work

See [WIP-INVENTORY.md](WIP-INVENTORY.md). Starting at 47f7dd5, uncommitted 17 mm hardware/geometry metadata, cap audit source, boundary regularization and hardware replacement code were inventoried and checkpointed early (aba62a9). M2×10 qualification and the cap audit were kept, rerun and extended to both pitches. The 17 mm shell boundary repair was kept and independently export-verified. Its intermediate two-solid diagnostic is superseded by final geometry diagnostics; the diagnostic is not a final claim. Experimental routes_tuning.py / transport.py remain as rejected development source, not fitted routes. Their fan crossings prevented adoption. Python caches were excluded. Runtime scratch and starting geometry snapshots remain in .issue248-runtime/tuning; no /tmp scratch was used.

Original E-boss regions were restored after a stricter engagement-material audit exposed damage from projected route cuts; the interrupted nominal-only engagement check was insufficient and is superseded. All changed-tray pair and service checks were rerun. The current `routes.py` replaces the early X±27/Y−24 merge with separated outlet lanes through the Wing north corridor, a lower fan into the neck, and concentric reserve turns. The long stored turn was moved from Y22.1 to Y17.1; its released reference is Y2.0, preserving 30.20 mm. This saves routed length. The final audit still rejects unresolved fan/upper-route and fixed-part contacts: no new route is described as qualified on length alone.

## Unchanged inputs and explicit deviations

Deck Z13.55; board undersides Z7.35; plateau Z24.65 provisional q=1.50; slope breaks Y{START:.9f} / Y{TOE:.9f}; boards, aluminium plates and board/plate stack remain unchanged. Existing PCB and plate manufacturing files are byte-checked against inputs-sha256.json before report/manifests regenerate. Actual fitted invariants and the protected south palm band are recomputed. GH remains the connector. Fly remains one connected 170 mm R5 cable. No thinner skin, changed cap, raised deck or changed well is introduced.

Roofs use **2.00 mm normal thickness**; the slope's vertical thickness is {2*math.sqrt(1+M*M):.9f} mm. Main GH blisters retain ceiling/top Z13.20/15.20; Fly Z13.25/15.25; Ø5.10 south openings and north shell retention remain. Case channels are cut only from trays, with the full source floor band restored through Z2 before remaking splice pilots. All local relief is recorded; no gate tolerance is enlarged. Detached north tongues are assigned by explicit geometric adjacency, never a largest-solid filter. The 16 mm south section is not deleted or bridged across a key well.

Length uses a **3.40 mm nominal internal wire upper bound per end**, plus the 0.50 mm Wing external dress lead, from the [JST GH manufacturer drawing](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf), readable repository archival figure on printed page 2. Exact dress-plane definition and derivation are in [tail-source.json](tail-source.json): housing mouth to cut copper end; 5.70 housing axial length minus protected 2.30 mating section. Wing actual mouth is Y−35.45 (#235: header rear −42.60 + seated 7.15); this candidate starts at Y−34.95, so another 0.50 mm is explicitly included. Total unrouted bound is 7.30 mm (Wing 3.90 + Main 3.40). This assumes a correctly seated terminal whose nose does not protrude past the housing mating tip and a wire end that does not invade the mating section. It is a drawing-derived bound, not a measured crimp or a production tolerance guarantee. The 2.10 mm crimp-region and 1.50 mm strip dimensions are not misused as that tail. The 164.8 mm Phase A dressed budget is reported as a reference only. Physical mating, q/skirt/full-press, crimp inspection and retention testing remain OPEN.

## Remaining blockers and service procedure

Wiring remains a failed candidate wherever the exhaustive audit finds strand crossings or fixed-body contacts. Remove USB, shell screws, central cap and strips; disconnect Main GH/EZmate, remove Main and its own hardware, then translate the connected reserve turns north by 15.10 mm. Wing hardware remains fitted. The continuous audit tests that proposal; its blockers are retained in service.json. No accessible-service certification is granted while fitted collisions remain. A further separated fan/upper-path redesign is required; this run does not prove that redesign impossible.

There is also a direct fixed-input roof conflict: the required low skin and unchanged aluminium overlap in material. An underside pocket cannot preserve 2.00 mm skin there. At 16 mm, the settled central surface footprint has a disconnected south component separated by 0.200 mm; a single solid requires revised ownership/footprint or an authorized connection. These constraints are reported explicitly instead of deleting skin, plate or shell material. The full physical Junana skirt test remains OPEN at both pitches.

'''+''.join(details)+'''## Reproduction and integrity

Run `bash hardware/case/issue-248-phaseb/reproduce.sh 17 16` from this worktree with the retained CAD Python environment. Each stage is separate; all scratch and audit checkpoints are under .issue248-runtime. Exact audit reuse is permitted only for the identical geometry index hash. This continuation rebuilds both pitches and reruns all eight gates, independent exports, witnesses and package checks. First-candidate evidence is preserved; new outputs describe the tuning candidate. Run `python3 hardware/case/issue-248-phaseb/verify_package.py` after report generation for input/artifact hashes and independent all-pair coverage. The package remains provisional and unreleased, with the explicitly failed gates above.
'''
 (HERE/'REPORT.md').write_text(report)
 for pitch in (17,16):
  for folder in [HERE/f'{pitch}mm',HERE/f'{pitch}mm/manufacturing']:
   (folder/'PROVISIONAL.txt').write_text(P['status']+'\nAll files in this directory are conditional on plateau_top_z_mm in parameters.json. See ../../REPORT.md and the per-pitch gates before manufacturing.\n')
 inputs=[]
 for pitch in (17,16):
  inputs += [HERE.parent/f'issue-232-final/{pitch}mm/assembly.step',HERE.parent/f'issue-232-final/{pitch}mm/dimensions.json',HERE.parent/f'issue-246-delta6-tuning/packed/delta-6/{pitch}mm/fly-170mm.step',HERE.parent/f'issue-246-delta6-tuning/packed/delta-6/{pitch}mm/measurements.json']
  inputs+=list((HERE.parent/f'issue-232-final/{pitch}mm/plate-package').glob('*'))
 inputs += [HERE.parent/'issue-248-lowdeck-raise/raised-regions-a4.geojson',HERE.parent/'issue-248-lowdeck-raise/tables-a4.json',HERE.parent/'issue-248-lowdeck-raise/b1/mated-gh-assembly-frame.step',HERE.parent/'issue-248-lowdeck-raise/b1/clearances-b1.json',HERE.parent/'issue-246-delta6-tuning/packed/delta-6/17mm/assembly-with-cover.step',HERE.parent/'issue-232-final/geometry.py',HERE.parent/'issue-232-final/build.py',HERE.parent/'issue-232-final/support-post.step',HERE.parent/'issue-232-final/verify.py',HERE.parent/'issue-228-final/base.py',HERE.parent/'issue-238-bay-study/main-inventory.json',ROOT/'hardware/kicad/qualification/issue-235-wing-round2/main-native-obstacles.json',ROOT/'hardware/kicad/qualification/issue-240-main-rev7/inspection/final/main.kicad_pcb',ROOT/'hardware/kicad/qualification/issue-240-main-rev7/connector/JST-current-eGH.pdf']
 inputs += [ROOT/'hardware/kicad/qualification/issue-240-main-rev7/connector/eGH-distributor-copy.pdf',ROOT/'hardware/kicad/qualification/issue-235-wing-round2/REPORT.md']
 inputs+=list((ROOT/'hardware/kicad/qualification/issue-235-wing-round2').glob('wing-rev4-*/routed.kicad_pcb'))
 save(HERE/'inputs-sha256.json',{str(p.relative_to(ROOT)):sha(p) for p in inputs if p.is_file()})
 import importlib.metadata
 versions={}
 for package in ('build123d','cadquery-ocp','shapely','numpy','sexpdata'):
  try:versions[package]=importlib.metadata.version(package)
  except importlib.metadata.PackageNotFoundError:versions[package]='local target dependency; see reproduction environment'
 save(HERE/'toolchain.json',dict(status=P['status'],python=sys.version,packages=versions,scratch=str(RUN)))
 save(HERE/'artifact-sha256.json',{str(p.relative_to(HERE)):sha(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='artifact-sha256.json' and '__pycache__' not in str(p)})
 print('Gate table',rows)
if __name__=='__main__':run()
