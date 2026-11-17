# Issue 264 — Stock FFC, folded, as the cable for the adopted FPC architecture

**Verdict: REALISABLE at plate Z10.90 (the adopted D-042 height), with named
conditions.** A stock Molex Premo-Flex FFC (152660149, 152 mm, Type A),
folded on a 3D-printed jig into the #261 route, passes the fitted contact
audit (gate 1) with zero unexpected contacts in the nominal configuration
and in both length/placement sensitivity configurations, passes the service
motions (gate 3) with one named residual, and passes the electrical target
on both the assumed and the pessimistic lane cross-section. The paper
guarantee for the cable's lane resistance stays open BY DESIGN (PO's
acceptance, 2026-11-17): it is closed physically by the post-purchase
measurement procedure in §6, whose acceptance threshold has ~13x margin
over the expected reading. Cost per keyboard drops from the custom FPC's
$50–150/iteration class to ≈$10–18 first iteration (two cables + jig
prints) and ≈$6–12 per re-iteration.

## 1. What was asked, what is frozen

PO (2026-11-17): D-042 adopted the FPC architecture with a CUSTOM FPC; on
cost grounds PO asked whether a STOCK (ready-made) FFC, folded to follow
the bent plan path, can realise the same configuration — accepting that
the electrical guarantee cannot be closed on paper (it will be closed by
measuring the purchased cable) — with a 3D-printed folding jig as part of
the method. Boards stay exactly as in #261: Wing Rev.5 / Main Rev.8 ZIF
poses from the #261 placement spec (Wing ZIF underside at the former GH
site, entry centreline Z2.95; Main ZIFs top, NW-facing, entry centreline
Z6.90; plate top Z10.90). The cable change must not move the connectors.

Why stock FFC was killed in round 13 / B3, and what changed: (1) shape —
a stock cable is straight, the route is bent; ANSWERED by the fold plan
(§3). (2) Lane resistance unspecified; ANSWERED partially on paper (§6:
passes on assumed AND pessimistic cross-sections because the loop is
contact-dominated) and closed physically by measurement. (3) Actuator
access — unchanged from #261 (the ZIFs are the #261 FH12-class selection;
service procedure is #261's, re-audited in §5).

## 2. Cable selection

**Selected: Molex Premo-Flex FFC 152660149** — 14 circuits, 0.50 mm
pitch, **Type A (same-side contacts)**, length 152.00 mm, cable thickness
0.27 mm, tin-plated contacts, 0.5 A/contact, Active production status.
Same-family Type A lengths: 102 mm (15266-0145), 127 mm, 152 mm
(152660149), 203 mm (15266-0153). The 152 mm length is the only one that
fits the length budget (§3): the route consumes ≈153 mm of strip at the
nominal fold setting, absorbed by the S-pair fold position over the
cable's 148–156 mm delivery window; 127 mm cannot reach, 203 mm leaves
≈50 mm unabsorbable inside the audited geometry.

Connector compatibility: the cable's contact zone matches the FH12-class
0.5 mm ZIF selected in #261 (FH12-14S-0.5SH(55)); tail thickness 0.27 mm
sits inside the FH12 adaptive band 0.30±0.05 mm.

**Contact-face bookkeeping (decides Type A vs Type D, and the connector
variant).** FH12-14S-0.5SH(55) is the BOTTOM-contact variant (the
top-contact variant is FH12A-...). A bottom-contact ZIF's springs face
the board side it is mounted toward:
- Wing Rev.5: ZIF on the underside → springs face world UP → the cable's
  contacts must face UP at the Wing tail.
- Main Rev.8: ZIF on top → springs face world DOWN → contacts face DOWN
  at the Main tail.
Required net face change along the cable: UP → DOWN = an ODD number of
folds. The fold plan has FIVE folds (§3) — odd — so a Type A cable
(same-side contacts) presents its contact face UP at the Wing end and
DOWN at the Main end. **No board-side delta: FH12-14S-0.5SH(55) stands
at all four sites, exactly as #261 selected.** (Had the fold count been
even, the fix would have been the Type D opposite-side variant of the
same family, not a connector change.)

**Conductor mapping.** Transporting the conductor-order vector through
the five fold reflections (computed, both sides): the net mapping is a
pure REVERSAL, cable position k at the Wing ↔ position 15−k at the Main,
on both sides. This is absorbed by the board respin exactly as #261
already assigns pin order at the four footprints to the arriving lane
order. **Binding note for Issue #263:** with this cable, the Main
footprints assign D-024 signal k to the position the Wing delivers as
15−k (equivalently: number the Main ZIF pads in the arriving order).

## 3. Fold plan

Route (right side; left is the plan mirror). Centreline vertices are in
`path-vertices.csv`; the plan drawing is `plan-view.png`. The strip runs:
Wing tail (27.0, −38.5, z 2.95) → F_A at (25.2, −15.0) → F_B at
(11.37, −22.0) → flat to (11.44, −19.0) → climb to the Main-deck level
z 6.90 at (12.48, −11.0) → long straight run north → F_S1 (180° fold-back)
at (14.08, 24.4) → southbound leg at z 7.22 → F_S2 (180°) at (13.00, 0.43)
→ northbound leg at z 7.54 → F_V7 at (14.41, 30.60) → Main mouth
(20.92, 38.24, z 6.90) → Main tail (22.6, 40.0).

| fold | at | turn | former radius | doubled zone |
|---|---|---|---|---|
| F_A | (25.2, −15.0) | 112.5° | R2 (jig pin) | 6 mm patch under the sheet |
| F_B | (11.37, −22.0) | 119.6° | R2 | 6 mm patch under |
| F_S1 | (14.08, 24.4) | 180° | R2 end pin | the southbound leg itself (stack layer 2) |
| F_S2 | (13.00, 0.43) | 180° | R2 end pin | the northbound leg (stack layer 3) |
| F_V7 | (14.41, 30.60) | 37.7° | R2 | 14 mm patch under |

Face state along the cable (C = contact face): C faces UP at the Wing
tail; each fold flips it: after F_A down, F_B up, F_S1 down, F_S2 up,
F_V7 down = DOWN at the Main tail. ✓ (§2 requirement.)

Length absorption: fixed parts (Wing tail→F_B 39.1 mm; F_S2→Main tail
42.5 mm) + the run/F_S1/F_S2 middle. The F_S1 fold position is the
absorber: strip consumption ≈153.2 mm at S1 y=24.4, changing ≈2 mm per
1 mm of S1 travel. Detents (set on the jig after measuring the delivered
cable): cable 148 → S1 y 21.8; 150 → 22.8; 152 → 23.8; 154 → 24.8;
156 → 25.8. The audit's nominal run sits at S1 y=24.4 (a 153.2 mm unit);
the sensitivity runs bracket S1 y=21.8-equivalent and 26.4 (beyond the
156 extreme) at maximum width/patch allowances (§5).

The S-pair stack: three layers at z centres 6.90 / 7.22 / 7.54 (real
0.27 mm strip + inter-layer clearance in the 0.32 mm model), stack top
7.70 — 1.7 mm below the plate underside (9.40). No unmodelled loops:
the entire 152 mm is the audited polyline.

Fold placement tolerance: ±0.5 mm class, set by the jig (§4); folded
into the audit as the sensitivity configurations (width 10.4 vs nominal
9.6, patch 0.35 vs 0.30, S1 at both extremes).

## 4. Folding jig (PO's addition)

Design deliverables: `sources/jig-right.step`, `sources/jig-right.stl`,
`sources/jig-slider.step` (left jig = mirrored print). One jig per side.

- Base plate 42 × 98 × 6 mm with the plan path as a 10.0 mm wide,
  2.85 mm deep groove (the strip registers in the groove; the groove IS
  the fold-position datum).
- Former pins R2.0 (the design fold radius) at F_A, F_B, F_V7 and at the
  F_S2 end of the stack run; the strip is folded around the pin, so the
  fold line and radius are set by the pin, not by hand.
- Stack fences (two 46 mm walls) along the S-pair run keep the three
  layers registered while folding the 180° pair.
- F_S1 former = a sliding block on a rail along the run, with five
  detent notches (cable lengths 148/150/152/154/156 per §3). The
  operator measures the delivered cable, sets the block to the detent,
  folds.
- Wing-tail end stop (the tail tip butts at the T0 datum) and a Main-end
  tip target pocket at T1: after folding, both tails must sit at their
  datums — that is the per-fold verification, together with "strip
  seated in the groove along its whole length".
- Folding order: register Wing tail at the stop → lay and fold F_A →
  F_B → climb and run → fold F_S1 back (layer 2 southbound between the
  fences) → fold F_S2 (layer 3 northbound) → fold F_V7 → check the Main
  tail lands in its target pocket. Folds are one-time: a mis-folded
  cable is not re-folded at the same line (consumable cost ≈$4, §7).
- Print: PETG, Ender-3 Pro envelope (42 × 98 × 11 mm ≪ 220 × 220);
  solid-equivalent 24.6 cm³ ≈ 31 g, ≈15 g at production settings
  (walls + 20% infill). The audit geometry uses the jig's R2 fold radii
  and detent positions (§5).

## 5. Fitted audit (plate Z10.90, pitch 17)

Machinery inherited from #261/#248 (fitlibF bodies at s=−2.65, repaired
vol_pair, HIT 0.005 mm³). Model allowances: sheet width 9.6 (real ≈9.0 +
placement), thickness 0.32 (real 0.27), fold patches +0.30 below the
sheet, roll boxes at the 180° folds; case delta = the formed channel in
the tray along the folded path (width 11.4, relieved 0.225 below /
0.30 above the local sheet incl. stack and patch zones), as #261.
Method note: the cable and channel are audited as box compounds with
exact Commons (no fuse operations — see §8); tray pairs are evaluated
against the uncut tray with the channel volume subtracted exactly.

[RESULTS TABLE - to fill]
