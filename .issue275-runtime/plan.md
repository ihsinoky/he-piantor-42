# Issue #275 Phase 1 (Stage A) — Main symmetrization DESIGN STUDY plan

Scope: study only. No board files modified. Deliverables: symmetric connector
pose pair recommendation, mounting-hole verdict, flip feasibility (a)-(d),
Wing impact scope, Stage B brief outline, PO figure (fig-sym-tabs.png).

PO decision (2026-11-18, firm): symmetrize Main left-right under the FPC
premise, including mounting holes if achievable. Purpose: same Main board
installable flipped (components facing down).

## Verification extract — measured from the SAVED Rev.9 board file
Source: `hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb`
(parsed by `.issue275-runtime/extract.py` -> `extract.json`; board frame, mm,
KiCad Y-down).

### Connector poses (footprint origin = FH12 body centre reference)
| site | position (x, y) | rotation | layer |
|------|-----------------|----------|-------|
| J2 | (76.048074, 112.073215) | +38.0 deg | F.Cu |
| J3 | (124.254798, 111.823895) | -43.0 deg | F.Cu |
| J4 (Fly, Pico-EZmate) | (100.000, 90.000) | 180.0 deg | F.Cu |

Pad-row check (validates rotation): J2 pad1 (74.103, 109.284) -> pad14
(79.225, 113.286): row angle +38.0 deg, span 6.50mm = 13 x 0.5. J3 pad1
(121.196, 113.309) -> pad14 (125.950, 108.876): row angle -43.0 deg.
Pad numbering runs in mirrored senses: mirror of J2 pad n lands on J3's
pad (15-n) end — consistent with the D-042 amendment record (FFC arrives
k -> 15-k, absorbed in Main's footprint assignment).

### Symmetry axis determination
Axis = **x = 100.000** (board frame), established three independent ways:
1. Outline: south edge y=137.9 spans x 66.1073..133.8927 (100 +/- 33.8927,
   exact); north vertex flat (98..102, 75.7321) centred on 100; north edge
   lines start at (98, 75.7321) / (102, 75.7321).
2. J4 sits exactly on x=100; H1 sits exactly on x=100.
3. H2/H3 are an exact mirror pair about x=100 (see below).
Only the Stage 2d tab regions deviate from mirror symmetry (tab chain
vertices off by up to ~0.4mm), which is the asymmetry under study.

### Mounting holes (all NPTH, drill 2.2mm, no net)
| hole | position | mirror about x=100 | offset |
|------|----------|--------------------|--------|
| H1 | (100.000000, 79.267949) | itself (on axis) | 0 |
| H2 | (68.107317, 134.400000) | (131.892683, 134.400000) = H3 exactly | 0 |
| H3 | (131.892682, 134.400000) | H2 | 0 |

**The mounting-hole pattern is already exactly mirror-symmetric.**
(Per-hole offset = 0.000mm for all three.) Case-side consequence to verify:
tray boss positions in the production case tree must mirror the same way.

### Connector asymmetry (the quantity to eliminate)
Mirror of J2 about x=100: centre (123.951926, 112.073215), rotation -38.0.
Actual J3: centre (124.254798, 111.823895), rotation -43.0.
Delta: centre offset (+0.302872, -0.249320) = 0.392mm; rotation delta 5.0 deg.
Cross-check vs REPORT Stage 2c (case frame): skew J2 22 deg / J3 17 deg —
same 5 deg discrepancy seen from the board edges (120/60 deg).

## Work sequence
1. [done] Verification extract (above) + checkpoint commit.
2. [done] Read REPORT.md Stage 2c/2d + #264 fold record + case production tree
   (tray bosses, FPC channel, Main pocket Z stack) + Fly dimensions.
3. [done] Candidate symmetric pose pairs (a) mirror-J2, (b) mirror-J3,
   (c) meet-in-middle: tab consequences vs D-037 silhouette, fanout room
   from the Rev.9 copper/footprint map, FFC approach, J4/power proximity.
4. [done] Hole verdict (board done; case bosses remain) — collision check for any
   hypothetical hole move is moot if offsets are 0; verify case side.
5. [done] Flip feasibility (a) FFC contact faces, (b) flipped component clearance
   (top-5 heights vs under-Main space), (c) J4/Fly + 170mm cable,
   (d) EN0/EN1-only swap confirmation from pad net assignment.
6. [done] Wing impact scope statement.
7. [done] Stage B brief outline + fig-sym-tabs.png (Rev.9 tabs vs recommended
   symmetric tabs, from measured geometry).
8. [done] stageA-design.md + stageA.json; final compact report. Do NOT push.
