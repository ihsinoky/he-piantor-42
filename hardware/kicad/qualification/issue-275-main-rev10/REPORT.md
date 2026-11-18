# Issue #275 — Main Rev.10 symmetrization + flip support: REPORT

Status: DRAFT for PO adoption gate (draft line D-046 at the end).
Worker: Muse (PMO-dispatched), 2026-11-18. Design basis: Stage A
study (`.issue275-runtime/stageA-design.md`, commits aa70c814d /
3f3f14495). PO decision (2026-11-18): symmetrize Main under the FPC
premise, mounting holes included if achievable; flip-installation
is the purpose; GH conversion is a LATER stage gated on the
geometric cable check, not part of this round.

## 1. Change set

### Main Rev.10 (tree: issue-275-main-rev10/main-rev10)
- J3 site BIT-IDENTICAL to Rev.9 (footprint + all pads verified by
  census; resistance extraction bit-identical, §3).
- J2 site moved to the Stage A candidate-(b) pose — the exact
  mirror of J3: footprint centre (75.745202, 111.823895), rotation
  +43.0°. Signal-pad deviation vs mirrored J3 = 1e-06 mm under the
  k -> 15-k correspondence (the mirrored cable presents the row
  reversed; per-number pad-net assignments are identical, verified
  in Stage A). MP pads are NC mechanicals; the footprint is chiral
  in its MP tabs, lands swept clear in Stage A.
- Outline: left tab chain replaced by the exact mirror of the
  right chain (mirror operator (x,y) -> (200-x, y), nm-exact).
  14 line segments, no arcs; the Rev.9 J2 dive-corner R0.50 fillet
  on its 0.1739 mm stub is GONE. Polygon valid, area 2644.24 mm2,
  mirror-completeness verified element-by-element.
- Mounting holes UNCHANGED (Stage A: already exactly symmetric —
  H1 on axis, H2/H3 mirror pair with 0.000 offset; no case boss
  changes).
- Fanout re-route, confined to J2's own 9 nets: wide rip of the
  old fanout (F.Cu segments of the 9 nets within 8 mm of the old
  centre — the first build's narrower pad-rect rip left chain
  fragments that shorted the moved pads: 7 DRC shorts, reproduced
  and diagnosed in B2), then the project router (KRT) with ALL
  surviving copper locked (additions only), sequential single-net
  fixup for MUX_A1 (first pick of the field — in the joint run a
  KRT-added MUX_OUT_C escape sealed pad 10's exit slot), MUX_OUT_C
  + GND second; dead-copper cleanup (2 orphaned vias, one dead
  MUX_OUT_B spur, one MUX_A1 In2 stub shortened to its junction).
  Track changes beyond 11 mm from the old J2 centre: 4 segments,
  all on the 9 nets' own route corridors (boundary re-draws with
  identical or continuation geometry; see gates evidence).
- Schematic byte-identical to Rev.9 (md5 fa754bee... both).

### Wing Rev.6 final notch pair (tree: issue-270-wing-rev6)
- Right variants (16R/17R): Stage 2e boards imported BYTE-EXACT
  from the Issue #273 worktree (board md5 70f11a71... /
  d86e22bc..., verified after import). The J3 tab is unchanged by
  Rev.10, so the 2e right notch stands; nothing was re-derived.
- Left variants (16L/17L): notch chain = EXACT MIRROR (case
  x -> -x) of the saved right chain (Stage 2e 7-element
  construction), built by the 2e full-outline-rebuild method;
  mirrored chain endpoints land exactly on the Rev.5 left ring
  (distance 0.0). Non-outline census identical; fill delta
  confined (outside-band 0.00000 mm2). Left packages regenerated
  and re-verified (DRAFT).

### Case (tree: hardware/case/issue-263-lowdeck-production)
- See §5 (pocket delta adopted; tray relief updated; flipped J4
  disposition).

## 2. Main gates (Rev.10 vs Rev.9, same invocation class as #270)

| metric | Rev.9 | Rev.10 |
|---|---|---|
| DRC unconnected | 0 | 0 |
| copper-graph unconnected | 0 | 0 |
| wrong-net contacts (graph) | 0 | 0 |
| DRC shorting items | 0 | 0 |
| ERC | 0 | 0 |
| via-pad minimum | 0.1596 | 0.1596 |
| via-pad below 0.10 | 0 | 0 |
| track dangling | 5 | 5 (identical population) |
| via dangling | 0 | 0 |
| phantom clearance (netclass defect) | 500 | 428 (shrunk) |
| copper_edge_clearance | 4 | 2 |
| ZIF pad-to-outline J2 / J3 | 1.632 / 1.6361 | 1.6361 / 1.6361 |
| F.Cu copper-to-outline min | 0.3226 | 0.4414 |

Evidence: `.issue275-runtime/gates-rev9.json`, `gates-rev10.json`,
`erc-rev10.json`. The phantom population is the known Main
project netclass defect (0.2 mm Default only); the criterion is
non-growth vs the same-invocation Rev.9 baseline — it shrank.

## 3. Resistance extraction + Vfar (both branches)

Pipeline: the #263 extractors, calibrated first on Rev.9 — the
Rev.9 run reproduces the Rev.8 "final" extraction EXACTLY
(U5->J2 119.68, U5->J3 249.69, VBUS 4.79 mOhm at 125 C / factor
0.8), so Rev.9 copper = Rev.8 copper for this metric and the
published system figures carry over.

- J3 (untouched): positive path 249.69 mOhm, GND return delta
  +0.02 mOhm — bit-identical class. Vfar(J3) = 4.754 V (as
  published for Rev.9) — reproduced by construction.
- J2 (re-routed): positive path 119.68 -> 175.42 mOhm
  (+55.74); GND return delta +0.02 mOhm (regulator reference
  terminal). dVfar = -0.127 A x 0.0558 Ohm = -7.1 mV.
  Vfar(J2) = 4.770 - 0.007 = 4.763 V >= 4.60 V — PASS.
  J2's loop (published accounting) rises 114.2 -> ~169.9 mOhm,
  still well under J3's 240.9: J3 remains the binding branch,
  exactly the Stage A premise for choosing candidate (b).

## 4. Wing gates (per variant, #263 yardsticks)

| variant | material DRC | unconnected | wrong-net | via-pad min |
|---|---|---|---|---|
| 17L (new) | 0 | 0 / 0 | 0 | 0.1252 |
| 16L (new) | 0 | 0 / 0 | 0 | 0.1032 |
| 17R (2e, imported) | 0 | 0 / 0 | 0 | 0.1252 (2e record) |
| 16R (2e, imported) | 0 | 0 / 0 | 0 | 0.1063 (2e record) |

Seam vs Main Rev.10 (fitted pose, from saved boards): 0.5593 mm
at both pitches, both sides; overlap 0. Floor 0.55 — PASS.

## 5. Case deltas + fitted audits

Case deltas are recorded in the production tree
(hardware/case/issue-263-lowdeck-production/README.md, Issue #275
section):

- Tray pocket relief for the Rev.10 tabs: left 6.305 mm3 / right 6.305 mm3 (both pitches; the right reproduces the Rev.9 figure since the right tab is unchanged, the left becomes its mirror — superseding the Rev.9 pair 6.521 / 6.305). Computation: case-delta-275 (production-tree audit-rerun/).
- Flipped-installation pocket (ADOPTED): 1.0 mm under the
  power-stage field, case X -6..+13, Y 28..48 (floor Z0.60).
  Measured on the audit body set (both pitches identical): the
  pocket box removes exactly 380.00 mm3 of tray and touches no
  other body. It restores the flipped power-field residual from
  0.60 mm to 1.60 mm. Nominal remaining web 0.60 mm (design floor
  1.60 mm; the audit body set models the floor at 2.00,
  conservative) — production note for the case-print gate.
- No pocket or channel for the flipped Fly cable is adopted
  (J4 disposition below).

Fitted audits (method: #264 bundle — fitlibF.bodies_at(17, -2.65)
body set, audit_static CTRL paths and sheet model w=10.2 t=0.25,
Main ZIF envelopes as the Rev.10 mirror pair at the #264 study
centres; containment disposed by the channel-corridor test, as in
#264: cable plan footprint outside the corridor must be 0).
Evidence: .issue275-runtime/audit275-{normal,flipped,j4flip}.json
+ logs, c23-check.log.

NORMAL pose (Type A fold plan):
- Gate 1 (cable vs non-tray bodies): right side ZERO contacts.
  Left side: one graze — Main-study-C23 envelope, 0.488 mm3
  (sheet slices the envelope's west face 0.94 mm at the plateau
  z-band). Root cause, verified by re-test: the study ZIF
  envelope sits ~1.4 mm from the as-built connector centre (a
  pre-existing offset of the #264 lineage, both sides); with the
  approach re-run to the as-built Rev.10 J2 centre the contact
  falls to 0.016 mm3 (a corner touch). The original hand-tuned
  CTRL_L (superseded here by the exact mirror) swung ~1 mm
  further west at the same stations. Classified: marginal
  envelope graze, build watch item — the sheet is flexible and
  the envelope is a conservative box; not a route blocker.
- Tray pairs: cable/tray overlap volume 290.409 mm3 (both sides,
  vs tray-left body), plan footprint outside corridor 0.000 mm2.
  The overlap is contact with the channel support form INSIDE
  the corridor — the same class the #264 containment argument
  disposes (the body-set tray models the channel form solid).

FLIPPED pose (Type D cable: same 5-fold plan, z flattened to the
underside mouth plane 2.95; Main bodies flipped about the slab
centre; pocket A cut; service consequence recorded below):
- Gate 1: left side ZERO contacts. Right side: two sub-mm3
  grazes — a case joint screw (0.503 mm3; the sheet's bend corner
  sweeps the screw's upper end at (14.2..15.8, -8.8..-7.2,
  z 2.82..3.08)) and the flipped C23 envelope (0.049 mm3;
  0.03 mm z-touch at the envelope corner). Both are
  envelope-corner contacts of the conservative sheet model
  against fixed bodies; the flexible sheet dresses around them.
  Classified: marginal grazes, recorded — gate 1 is not a
  literal 0 on this side.
- Tray pairs: overlap 246.904 mm3 (both sides), plan outside
  corridor 0.000 mm2 — same within-corridor form-contact class
  as the normal pose. Identical results with the normal-profile
  and flat-profile channel cuts: the flipped run needs NO
  separate tray variant; the normal trays serve both poses.
- Component clearance (Stage A figures, confirmed by the body
  set): flipped underside plane Z4.70 vs tray floor Z1.60 =
  3.10 mm free; tallest flipped parts C26/C27/C28 2.5 mm ->
  residual 0.60 mm, restored to 1.60 mm by pocket A; L1 2.1 ->
  1.00; FH12 2.0 -> 1.10; J4 header 1.55 -> 1.55.
- SERVICE CONSEQUENCE: in the flipped pose the FH12 actuators
  face the tray. Cable (un)locking requires lifting the Main
  board off its mounts first; the Wing-side actuators remain
  accessible as in the normal pose. Recorded for the build guide.

FLIPPED J4 / Fly cable — NAMED RESIDUAL (sub-item stopped per
the Stage B stop rule; not forced):
- The flipped plug itself fits: it hangs to Z2.80 over the plain
  floor (1.20 mm clear); its only audit contact is its own
  mating header envelope (the engagement volume, expected).
- The attempted escape geometry (flat bundle 4.5 x 1.2, plan
  loop west, southbound leg in a candidate west channel, hop
  over the left FFC sheet) FAILS the audit: the hop's descending
  transition contacts the left FFC sheet (5.385 mm3), and the leg
  needs a new tray channel along its whole run. Any west-side
  southbound path must cross the left FFC sheet's plan exactly
  once, and the sheet's S-curve leaves no transition window on
  the south side; the alternative vertical fold-back at the plug
  needs a sub-1 mm bend radius for the EZmate wire bundle
  (available z-span 4.10 mm vs 2 x 1.2 mm strands + bend
  allowance). Evidence: audit275-j4flip.json.
- Disposition: flipped installation is qualified for the Wing
  FFC links; the USB/Fly connection in the flipped pose is
  unresolved and would need its own case/cable study. This does
  not block the D-046 adoption: the normal pose (the order
  configuration) is unaffected, and flip remains available for
  the Wing-link geometry it was adopted for.

## 6. Draft adoption line

D-046 (DRAFT — PO decision): Adopt Main Rev.10 (symmetric
connector sites; J2 mirrored onto J3) and the Wing Rev.6 final
notch pair (Stage 2e right + mirrored left) as the order-baseline
board pair for the low-deck FPC configuration, superseding Main
Rev.9 (D-044) and closing the Wing Rev.6 adoption deferred there
(draft D-045 is subsumed). The production case gains the
flipped-installation pocket under the power-stage field
(1.0 mm, case X -6..+13, Y 28..48) and the Rev.10 tray reliefs.
Flipped installation is qualified for the Wing FFC links with a
Type D cable (opposite-face contacts; EN0/EN1 swap absorbed in
firmware); the flipped Fly/USB connection is the named residual
(§5) and does not block adoption. Order release remains a
separate PO gate.
