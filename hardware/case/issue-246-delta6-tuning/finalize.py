"""Bind the completed study evidence and regenerate its reviewable report."""
from pathlib import Path
import json,hashlib,shutil
H=Path(__file__).resolve().parent;R=H.parents[2]
read=lambda p:json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def main():
 runs=[]
 for p in sorted((H/'packed').glob('delta-*/*mm'),reverse=True):
  if not (p/'gates.json').exists():continue
  d=read(p/'measurements.json');a=read(p/'audit.json');m=read(p/'metrology.json');g=read(p/'gates.json');sv=read(p/'service.json');iv=read(p/'invariants.json')
  assert a['all_pairs_enumerated'] and a['all_exact_candidates_completed'] and not a['early_stop']
  if g['all_gates_pass'] and (p/'assembly-with-cover-REJECTED.step').exists():(p/'assembly-with-cover-REJECTED.step').replace(p/'assembly-with-cover.step')
  runs.append((p,d,a,m,g,sv,iv))
 assert runs
 lines=['# Issue 246 — Delta 6 flush-cover tuning','', 'Study only. Production geometry, baseline, decisions and the 200 mm qualification bound are unchanged. [Assignment](issue246.json).','']
 for p,d,a,m,g,sv,iv in runs:
  lines.append(f"**{d['pitch_mm']} mm pitch: {'PASS — all six CAD study gates' if g['all_gates_pass'] else 'FAIL — remaining constraints below'}.** Delta=6; common top Z22.2 mm.")
 if not any(d['pitch_mm']==16 for p,d,a,m,g,sv,iv in runs):lines.append('16 mm has not been evaluated; it is required only after a fully passing 17 mm candidate.')
 lines+=['','These verdicts use the #244 CAD acceptance scope. They do not certify physical load/inversion tests, manufacturing tolerances, supplier bend ratings or a finished electrical harness. The inherited whole-panel/load and defective official USB internal-shell limitations remain. No production release, push, PR or order is made.','','## Tuned route and conductor bound','',
 'The route is fourteen continuous OD1 R5 sweeps per side, from each original Wing exit to its original Main GH endpoint. Each sweep includes the entry, U, return, rise and GH approach. There is no chord shortcut, detached reserve or unmodeled length. The parallel lower pack uses a 4/3/4/3 hex arrangement at 1.01 mm centers, with all strands retained alongside the nominal OD5 shared envelope. The furthest hex center is 2.0042 mm from its axis (maximum radial material extent 2.5042 mm); the Ø6 case channel accommodates it. The full union, not the nominal bundle alone, is audited. Upper offsets use a 5/5/4 pack with 1.05 mm spacing; its lowest/highest dz are −1.05/+1.05 mm. This removes the inherited common-point convergence and exact pack tangencies. The index-to-endpoint mapping is retained on both sides.', '',
 'Coordinates in measurements.json precede the final +6 mm Z translation. The lower center is global Z7; U waypoints are X±27/Y−24 → X±7/Y−16 → X±7/Y22.1 → X±19/Y22.1 → X±19/Y0. Individual lower paths include the saved hex-pack X/Z offsets. Each return then goes through X±(5+off)/Y−18/global Z7; the rise reaches Y−7/global Z18.8+dz; the traverse reaches X±(23+off)/Y8 at that height; the retained outward GH approach and endpoint follow. All joins, including lower-to-return, use R5. Exact full-conductor waypoints, samples and lengths are authoritative; upper_samples_mm supplies the partial reference curves used to cut the grooves.', '',
 '| Pitch | Side | Longest mm | Shorter reference mm | Minimum per-wire release mm | Margin to 200 mm | Connected envelope |',
 '|---:|---|---:|---:|---:|---:|---|']
 for p,d,a,m,g,sv,iv in runs:
  for w in d['wings']:
   q=m['wings'][w['side']]
   lines.append(f"| {d['pitch_mm']} | {w['side']} | {w['longest_conductor_mm']:.6f} | {w['reference_conductor_mm']:.6f} | {min(w['per_conductor_reserve_mm']):.6f} | {200-w['longest_conductor_mm']:.6f} | valid={q['valid']}, solids={q['solids']} |")
 lines+=['', 'The reference moves the same U turn from Y22.1 to Y7. Every corresponding conductor releases 30.2 mm. Accessible service is certified only where gate 2 passes. The verifier independently reconstructs rounded 3D lengths analytically and checks all fourteen, including the reference. The 200 mm limit is applied to the longest complete centerline, not to an average. No added termination or manufacturing allowance is claimed beyond the saved endpoints: a finished harness must satisfy the same ≤200 mm bound. The route meets that bound in CAD, so the conditional overlength Vfar exception is not invoked and no D-033/Rev.7 decision is relaxed.','',
 'The delivered connected cable envelope is the exact union of the full conductor sweeps and the nominal lower bundle. Exact sequential Fuse starts with the lower envelope; left wires are fused 13→0, right 0→13. Each merge must remain valid, one solid and nondecreasing in volume. The deterministic order addresses OCCT numerical failure; no fuzzy Boolean tolerance or contact exemption is introduced. All individual constituents remain in the collision audit. For 16 mm the placed conductor/bundle BReps are byte-identical to 17 mm, so metrology reuses the hash-verified connected unions; the verifier checks every constituent hash and the delivered STEP hash. The complete 16 mm collision audit is performed independently.','',
 '## Full fitted audit and gates','',
 '| Pitch | Solids | All pairs | AABB rejected | Intended | Exact | Unexpected | Boolean errors |',
 '|---:|---:|---:|---:|---:|---:|---:|---:|']
 for p,d,a,m,g,sv,iv in runs:lines.append(f"| {d['pitch_mm']} | {a['assembly_solids']} | {a['total_pairs']} | {a['aabb_rejected_pairs']} | {len(a['intended_pairs'])} | {a['exact_candidates']} | {len(a['unexpected_interferences'])} | {len(a['boolean_errors'])} |")
 lines+=['', 'The 17 mm constituent count falls from #244’s 456 to 427 because fourteen entry plus fourteen upper pieces per side become fourteen full conductors (28 fewer in total), and the detached right-tray sliver is machined away (one fewer). No retained part is dropped. The #244 `reason` and `audit` functions are unchanged; the verifier compares their syntax trees. Every unordered constituent pair, including retained/retained pairs and every cover tile, is enumerated. All non-intended positive-AABB pairs receive OCCT Common; errors never count as clear. The volume threshold stays 1e−6 mm³. Inherited source internals, same cable/own terminations, clearance-reservation overlaps and nominal own nut/thread contacts retain exactly the #244 classifications. finish.py reconstructs a valid single cover and verifies its volume against the exact disjoint partition.', '',
 '| Pitch | 1 Zero contacts | 2 Accessible ≥30 mm | 3 Fly 170 mm | 4 USB insertion | 5 Retention/service | 6 ≤200 mm |',
 '|---:|---|---|---|---|---|---|']
 for p,d,a,m,g,sv,iv in runs:lines.append(f"| {d['pitch_mm']} | "+' | '.join('PASS' if x else 'FAIL' for x in g['gates'].values())+' |')
 for p,d,a,m,g,sv,iv in runs:
  if a['unexpected_interferences']:
   lines+=['',f"Remaining binding contacts at {d['pitch_mm']} mm (all bounds in final datum):",'', '| Parts | mm³ | X bounds | Y bounds | Z bounds |','|---|---:|---|---|---|']
   for c in read(p/'collision-map.json'):
    lo,hi=c['overlap_bounds_mm'];lines.append(f"| {c['a']} / {c['b']} | {c['volume_mm3']:.9f} | "+' | '.join(f'{x:.4f}…{y:.4f}' for x,y in zip(lo,hi))+' |')
  if not sv['pass_clearance']:
   for q in sv['sides']:lines.append(f"Service binding measurements at {d['pitch_mm']} mm, {q['side']}: `{q['unexpected_contacts']}`.")
 lines+=['','## Accessible service and retention','',
 '1. Disconnect external USB. Remove the two north M2x6 and two south M2x10 cover screws. Main H1 continues to hold Main while the cover is lifted.',
 '2. Lift the lid and remove the two loose south POM spacers. Release both GH latches, withdraw the plugs along the outward mating axes, disconnect Main EZmate, then remove H1/its washer and lift Main. Wing boards, posts and decks remain fitted.',
 '3. Through the now open Main aperture, unlace the inner U leg and slide the lower turn north from Y22.1 to Y7 in the service relief. The outer leg remains under the Wing; the new relief permits this horizontal retraction without lifting the Wing. Recover 30.2 mm into the disconnected Main end of each same harness. The reference route is the shortened dressed portion of that same cable, not a replacement shorter harness.',
 '4. Reverse the procedure, dress the U back to Y22.1, engage all latches, replace Main H1 and the loose spacers, and ensure lid load bears on supports before tightening its four flush screws.', '',
 'service.json checks a conservative envelope of the entire continuous U retraction, including its fixed entry and both legs, against every retained constituent after that disassembly. The R5 cap swept continuously in Y fills the strip between its start/end graphs; the longest U includes all fixed legs. The footprint has 0.152 mm additional XY allowance for curve sampling/simplification, and is extruded through the full global Z4.5…9.5 OD5 slab. This is conservative relative to a round bundle. The case cut adds a further 0.1 mm XY and Z clearance. No retained body is exempted because it obstructs service. Full cable continuity and per-wire reserve are checked separately; a failed closed audit or motion clearance fails service.', '',
 'The four-retainer arrangement, hole locations, 3 mm POM spacers, AF4×1.6 captured north nuts, M2x6/M2x10 screws, 3.8 mm south thread engagement and local 10 N screens are inherited from #244/#242. At 5 N per active retainer, screw tension is 2.49 MPa, nut-roof stress 0.82 MPa, south thread shear 0.42 MPa. Nominal 0.25 mm aluminium skin gives 0.051 mm deflection / 87.1 MPa in the local screen; minimum 0.22 mm gives 0.074 mm / 112.5 MPa. These are local calculations, not whole-cover FEA or physical inversion acceptance. The new service cut is remote from the four retention sites. Each completed tray must be valid and one solid.', '',
 '## Actual case changes and cover','',
 '- Retain the coordinated #244 Delta=6 remake: both full trays and twelve Wing posts are split at original Z3 and extended to raise PCB/deck/rim seats by 6 mm while keeping the floor and feet. Main Rev.7 and Wing Rev.4 are unchanged. The common top is 22.2 mm (16.2+6), using the same datum as #244.',
 '- Keep #244 splice relocations X−5/12 → X0/15 at Y−8/55, floor-rooted bosses, and redrilled splice plates; old clearance holes remain unused. Keep the OD6 R5 lower channels, now following the Y22.1 U.',
 '- Move rise Y−5 → Y−7 and traverse Y10 → Y8, retaining X±(5+off)/X±(23+off). Cut projected upper grooves with radius 0.82 mm from global Z3.9 to Z20.9 (formerly Z19.9). The 0.02 mm projection simplification stays unchanged. This physically removes the prior high tray contacts.',
 '- Cut the continuous service-relief footprint with an additional 0.1 mm XY margin through global Z4.4…9.6. The nominal floor is retained. Before this cut the retraction envelope intersected left/right trays by 28.117/26.415 mm³; [saved evidence](evidence/service-before-relief.json).',
 '- Remove the obsolete right splice-boss sliver using the explicit box X8.5…9.3, Y−10.6…−8.8, global Z8.9…9.7. This removes the measured ~0.026 mm³ detached fragment. No arbitrary largest-solid filtering is used.',
 '- Keep #244 north nut hex/side-slot cuts through pillar and surrounding tray, south removable spacers and rim trim. Fit the north cover edge with 0.30 mm clearance while protecting D-037 above the Z3 extension.',
 '- Keep one machined 6061-T6 aluminium cover, 1.50 mm nominal, underside global Z20.7, flush top Z22.2. GH/Fly/USB pockets retain 0.25/0.40/1.00 mm skins. Machine with the top supported; release the perimeter, deburr and inspect skin/flatness. There is no rack or exterior storage.', '',
 '| Pitch | Tray | Valid / solids | Print XYZ incl. 5 mm XY brim | Fits 220×220×250 |',
 '|---:|---|---|---|---|']
 for p,d,a,m,g,sv,iv in runs:
  for side,q in m['printing'].items():lines.append(f"| {d['pitch_mm']} | {side} | {q['valid']} / {q['solids']} | "+' × '.join(f'{x:.2f}' for x in q['with_5mm_brim_xy_mm']+[q['z_mm']])+f" mm | {q['within_220x220x250']} |")
 lines+=['', 'The 6 mm height cost and complete tray/post remake scope follow #244. Reuse its planning allowance: one-off cover US$85–290, batch of ten US$25–80 each, retention US$1–4/set. No supplier quotation is claimed. Fly remains one connected OD2 R5 sweep of exactly 170 mm, original endpoints intact, volume 170π within 0.001 mm³. All of it is included in the fitted audit. USB shell/overmold/exit reservations each cover a continuous 30 mm insertion; the raised protected seat/opening is separately compared against the original above the Z3 extension. Lower floor/splice-hole geometry is intentionally changed as in #244; it is not certified unchanged. No physical insertion trial is implied.', '',
 '## Evidence and reproduction','']
 for p,d,a,m,g,sv,iv in runs:
  rel=p.relative_to(H)
  lines.append(f"- **{d['pitch_mm']} mm:** [audit]({rel}/audit.json), [all solids]({rel}/assembly-index.json), [contact map]({rel}/collision-map.json), [measurements]({rel}/measurements.json), [metrology]({rel}/metrology.json), [service sweep]({rel}/service.json), [D-037 invariants]({rel}/invariants.json), [gates]({rel}/gates.json); [top PNG]({rel}/top-view.png)/[SVG]({rel}/top-view.svg), [sections PNG]({rel}/sections.png)/[SVG]({rel}/sections.svg). Changed tray, cable, Fly, cover and fitted assembly STEP exports are in the same folder.")
 lines+=['', 'The section drawing is a YZ projection of the true rounded paths, not an X-constant section. Exact 3D intersections govern the verdict. Exploratory local screenings in evidence/ are not substitutes for the completed final all-pairs audits.', '',
 'Run `bash hardware/case/issue-246-delta6-tuning/reproduce.sh 6 17`; only after it fully passes, run the same command with `6 16`. The wrapper separates Boolean build, STEP export and audit into fresh processes to bound peak memory, then performs metrology/invariants and checks the continuous service motion, then evaluates all gates. `--audit-only --resume` reuses only hash-matched runtime BReps/results. Run `bash hardware/case/issue-246-delta6-tuning/present.sh` to regenerate drawings, report and hashes and run the independent verifier. CAD_PYTHON and GEOMETRY_SITE defaults are in reproduce.sh. The wrapper also sets the temporary, Matplotlib and font-cache directories under .issue246-runtime/; no scratch goes outside .issue246-runtime/.', '',
 'A first 16 mm attempt stopped on memory before export/audit; the completed run uses the fresh-process pipeline. No interrupted audit is treated as a pass. All scratch, BReps, discarded candidates, logs and private Git are under .issue246-runtime/. The private repository begins with checkout snapshot `33bd2d8` and records only this study in its work commit on issue-246-delta6-tuning. Input/artifact hashes and the independent coverage/rounded-length verifier bind the evidence. No production/baseline/decision file is changed.']
 (H/'REPORT.md').write_text('\n'.join(lines)+'\n')
 evidence=H/'evidence'
 for p,d,a,m,g,sv,iv in runs:
  for prefix in ('tuned','service','metrology','invariants'):
   src=R/f'.issue246-runtime/{prefix}-{d["pitch_mm"]}.log'
   if src.exists():shutil.copyfile(src,evidence/src.name)
 inputs=[H.parent/'issue-244-height-search'/n for n in ('REPORT.md','study.py','finish.py','check-invariants.py','CASE-REVISION.md')]
 inputs += [H.parent/'issue-244-height-search/delta-6/17mm'/n for n in ('audit.json','measurements.json','collision-map.json','metrology.json')]
 inputs += [H.parent/'issue-232-final'/n for n in ('geometry.py','verify.py')]
 inputs += [H.parent/'issue-228-final/base.py',H.parent/'issue-240-bay-cover/study.py',H.parent/'issue-240-bay-cover/routes.py',H.parent/'issue-242-bay-final/mechanics.json',H.parent/'issue-238-bay-study/main-inventory.json',R/'docs/decisions.md',R/'hardware/kicad/qualification/issue-235-wing-round2/main-native-obstacles.json',R/'hardware/kicad/qualification/issue-240-main-rev7/inspection/final/main.kicad_pcb']
 for p,d,a,m,g,sv,iv in runs:
  pitch=d['pitch_mm'];inputs += [H.parent/f'issue-232-final/{pitch}mm/assembly.step',H.parent/f'issue-228-final/{pitch}mm/dimensions.json',H.parent/f'issue-238-bay-study/{pitch}mm-measurements.json',H.parent/f'issue-198-final/{pitch}mm/dimensions.json']
  inputs += [R/rel for rel in read(H.parent/f'issue-232-final/{pitch}mm/inputs-sha256.json') if (R/rel).is_file()]
 save(H/'inputs-sha256.json',{str(p.relative_to(R)):sha(p) for p in set(inputs)})
 save(H/'artifact-sha256.json',{str(p.relative_to(H)):sha(p) for p in H.rglob('*') if p.is_file() and p.name!='artifact-sha256.json'})
 print('Report and manifests written for',[(d['pitch_mm'],g['all_gates_pass']) for p,d,a,m,g,sv,iv in runs])
if __name__=='__main__':main()
