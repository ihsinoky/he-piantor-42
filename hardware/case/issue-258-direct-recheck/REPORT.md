# Issue #258 — No-carrier low-deck re-examination (direct GH Wing→Main)

Completion study. The low deck **without** a carrier board was already
deeply studied in Issue #248 (rounds 1–18 + frontier sweep) and Issue
#253 (N2 north relocation). Two no-carrier combinations had never
actually been run; this issue runs exactly those two and closes the
coverage map. **No carrier board anywhere in this issue.** Boards,
connector choice and harness wire spec are unchanged throughout.

Uniform method (both tracks): fitted REPAIRED audit of
`issue-248-phaseb` (target 0 unexpected contacts), round-9 route
topology, round-18 repair machinery, frontier-uniform budget
(2 seed candidates where applicable, 2 repair passes of 900 s / 40
evals, slack build 900 s). All Z in the phase-B frame (Z0 = underside
of the tray floor slab); plate top 13.55 = the #248 low deck.

---

## Track 1 — N3: bay-facing Wing connector

### Pose (as formulated in Issue #253, never routed there)

J_WING (SM14B-GHS-TB, underside) rotated **in place** about its Rev.4
anchor (case frame (±27.0, −41.0)) so the mating axis points toward
the bay: right +90° CCW (exit direction +Y → −X), left −90° CW (exit
→ +X). No outline extension (t = 0 class, per the #253 round-2
rotated-in-place finding); every other placement byte-identical.

Derived geometry (case frame, right; left mirrors):

| quantity | Rev.4 (south) | N3 (bay-facing) |
|---|---|---|
| pad row | Y −42.85, X 35.125 → 18.875 | X 28.85, Y −32.87 (pin 1) → −49.12 (pin 14) |
| exit face | Y −34.95 | X 20.95 (7.90 proud of the pad row, toward the bay) |
| exit points (Z 5.75) | (35.125−1.25i, −34.95) | (20.95, −32.87−1.25i) |

The native→case transform was verified before routing: a pure
rotation (no reflection) mapping all 14 native pads onto the case row
with 0.000 mm error, and the U_MUX_C / U_MUX_B / U_HC1 centres onto
their phase-B case bounds exactly. D-024 cavity correspondence
follows the physical presentation: cavity n faces GH pin n with the
plug inserted from the bay side; the harness machinery's left side
(mirror j = 13−i of the right design, the round-4 verified
convention) is consistent with this presentation.

### Fanout screen (KRT re-route at Rev.4 yardsticks, KiCad DRC)

| variant | DRC violations | unconnected | blocking items |
|---|---|---|---|
| 17 mm right | 7 | 4 | **short**: J_WING pad 14 (GND) overlaps test pads TP_W_H5V (HALL_5V) and TP_H_DIAG_RAW (H_C0_RAW). **edge**: pad 3 across Edge.Cuts, clearance 0.000 mm |
| 17 mm left | 5 | 2 | **short**: J_WING pad 1 (HALL_5V) overlaps TP_H_DIAG_RAW. **edge**: pad 12 across Edge.Cuts |
| 16 mm right | 7 | 8 | same two classes as 17R |
| 16 mm left | 8 | 3 | same two classes as 17L (+ GND track edge items) |

(Remaining DRC classes — solder-mask bridges between the overlapping
pads, silk warnings — are consequences/bystanders of the two blocking
classes.)

### Verdict — fanout cannot close on any variant; Track 1 stops here

The blockers are **placement-level**, not router residuals: rotating
the connector in place sweeps its 16.25 mm pad row across the B.Cu
test-pad field (TP_W_H5V / TP_H_DIAG_RAW) at one end and across the
slanted board edge at the other. No routing can cure a pad that sits
on another part's pad or outside the outline, and the brief fixes all
other placements and the t = 0 pose. The harness stage (gate table at
plate 13.55) was therefore **not run** — the pose is not board-feasible.

Residual note: the #253 formulation also mentioned placing the
connector at an extension tab's inner corner. That pose needs the
outline extension (3.0–3.9 mm tab class) and is **outside** this
track's pose class; it remains unrun (see coverage statement).

---

## Track 2 — Thinned GH stack × direct route

### Stack (Issue #255's GH-compatible levers applied to the #248 stack)

| element | #248 stack | Track 2 | note |
|---|---|---|---|
| tray floor slab | 2.00 | **1.60** | ribbed per #255; modelled as the fuse band −0.40…−0.60 (frontier EXTEND convention, conservative in the band) |
| M2 tie length | M2×12 class | **M2×10** | already qualified in #248 (boss-root bound 12.90 → 10.90, non-binding) |
| free gap (PCB underside → highest underside point) | 0.50 | **0.30** | J_WING band top stays the binding underside point |
| Hall-effect reservation | as fitted | **unchanged** | #255's reduction touches the sensing keep-out, so it was NOT taken (brief condition) |
| **B (PCB underside)** | 7.35 | **6.75** | = 7.35 − 0.40 (floor, carried by the ties) − 0.20 (gap) |
| **plate top** | 13.55 | **12.95** | = B + 6.20 (invariant stack) |
| keytop (provisional) | 24.65 (13.55 + 11.10) | **24.05** | plate + 11.10; Junana q = 1.50 still UNMEASURED |

Route-side consequences: stations/rise −0.60; the tray channel is
floor-anchored, so the corridor point drops only by the floor delta
(Z 5.10 → 4.70); floor-top hardware (splices, joint screws) −0.40;
shells/plateau −0.60 with the keytop. Connector pose: Rev.4 baseline
(south-facing) — Track 1's fanout did not close, so the N3 pose was
not available to this track.

### Gate table (fitted repaired audit; seed = round-18 M shifted −0.60)

| gate | result |
|---|---|
| 1 — unexpected contacts, taut | **FAIL**: 92 (17 mm) / 96 (16 mm) = WW 2 + WF 90 / 94. WW residual is the round-18 pair Wire-05×Wire-06 (0.52 mm³/side); WF bodies are the fan-region set (Wing PCB, plate, R0/R2 switch envelopes, U_MUX_B/C reservations, trays, Main GH drawing bounds) |
| 1 — stored (max-slack assembly) | **FAIL**: 86 / 90 |
| 2 — finished length ≤ 200 | PASS: longest taut 106.47; stored adds at most the max slack delta 14.48 |
| 3 — service (unplug-first) | **FAIL**: storable slack vs the 30.2 mm target — min 0.06 / median 5.27 / max 14.48 mm; extraction Part A min s_max = **0.0** (strands 2, 8, 9 cannot move at all) |
| 4 / 5 — Fly 170 / USB | no contacts against the Fly cable body or the USB reference body in the taut audit (moot — gate 1 fails) |
| 7 — print envelopes | unchanged (floor thinning is internal) |

### Verdict — NO material change

Side-by-side with the frontier-uniform numbers at the un-thinned
stack (Issue #248 frontier, same budget class):

| design | taut gate-1 (17/16) | stored gate-1 | slack Δ min/med/max | Part A min s_max |
|---|---|---|---|---|
| plate 13.55 (frontier) | 90 / 92 | 88 / 90 | 0.03 / 5.29 / 14.50 | 0.0 |
| **plate 12.95 thinned (this track)** | **92 / 96** | **86 / 90** | **0.06 / 5.27 / 14.48** | **0.0** |
| plate 16.2 (frontier, for scale) | 65 / 69 | — | — | — |

The extra ≈0.6 mm of under-PCB room and the 0.40 mm thinner floor
change nothing that matters: gate-1 stays in the low-90s, the
storable-slack distribution is numerically almost identical to
13.55, and extraction still locks at 0 mm on the same strands. The
binding mechanism is the fan/neck geometry in the XY plane (fixed by
the corridor, the keyfield envelopes and the Main GH stations), not
the vertical budget — consistent with the frontier finding that deck
height helps only up to 16.2 mm and never closes.

---

## Coverage statement — the no-carrier low deck

Every no-carrier combination examined so far, with its best fitted
result (gate-1 unexpected contacts, 17/16 mm, unless noted):

| combination | where | best fitted result |
|---|---|---|
| South GH (Rev.4 pose), decks 13.55 / 15.0 / 16.2 / 17.5 / 19.0 / 20.5 / 22.2 (tray architecture) | #248 rounds 1–18 + frontier | 96/98 at 13.55 (round 18); frontier taut 90/92 at 13.55, 65/69 at 16.2 — **no height passes**; service slack impossible at 30.2 mm, unachievable ≈14 mm |
| South GH + thinned stack (floor 1.60, gap 0.30, M2×10), plate 12.95 | **#258 Track 2** | 92/96 taut, 86/90 stored — FAIL |
| N2 north GH (in-place, t = 0), plate 13.55 | #253 rounds 1–2 | fanout nearly clean (1–3 unconnected class), harness FAIL: R5 climb reach ≈4.9 mm vs 4.86 mm to the silhouette; fan contacts remain |
| N3 bay-facing GH (in-place, t = 0), plate 13.55 | **#258 Track 1** | **fanout FAIL on all 4 variants** (placement collisions: test-pad field + board edge); harness not run |
| Wing-side SH + direct (arithmetic only) | #255 | plate 11.55 arithmetic via SH+carrier — harness qualification open, and its carrier premise is out of scope here (carrier) |

**Remaining unexamined no-carrier cells at deck height ≤ 16.2 —
exactly two:**

1. **N3 with an outline extension** (connector at the tab's inner
   corner, the other half of #253's N3 formulation): needs a case/
   outline change of the 3.0–3.9 mm tab class; outside Track 1's
   t = 0 pose class.
2. **N2 at deck heights above 13.55**: N2 was only ever run at
   13.55, where it missed on a ≈0.04 mm-class reach margin on one
   strand pair; a taller deck shortens the R5 climb, so 15.0–16.2 mm
   is genuinely untested. (Its fan contacts at 13.55 were of the same
   family that persists at every height in the south study, so the
   prior is poor — but it has not been run.)

Everything else in the no-carrier space at ≤ 16.2 mm is now closed,
and every closed cell fails. The only fully qualified low-deck-adjacent
design remains the adopted Δ+6 case (D-041, plate 22.2, separated-lane
architecture of Issue #246) — a different case architecture, not a
cell of this map.

## Draft decision text (for PO adoption; NOT entered in docs/decisions.md)

> **D-0xx (draft) — N3 bay-facing Wing connector: rejected at fanout.**
> Rotated in place (t = 0), the SM14B-GHS-TB pad row collides with the
> B.Cu test-pad field and crosses the board edge on all four Rev.4
> variants (Issue #258 Track 1). The pose is not board-feasible
> without moving other placements or extending the outline.
>
> **D-0xx (draft) — Thinned GH stack does not rescue the direct low
> deck.** Floor 1.60 + gap 0.30 + M2×10 (plate 12.95) leaves the
> fitted audit at 92/96 unexpected contacts with extraction locked at
> 0 mm (Issue #258 Track 2) — materially identical to plate 13.55.
> The no-carrier low deck is closed except the two cells named in the
> #258 coverage statement (N3-with-tab; N2 above 13.55).

## Sources

`sources/` — `build_n3.py` (N3 input builder + transform
verification), `n3_exits.json`, `drc-n3-<variant>.json` (fanout DRC
evidence), `track_lib.py` / `run_track1.py` / `run_track2.py` /
`finish_track2.py` (harness drivers), `result_track2.json` (full
Track 2 record incl. per-strand Part A). Track 1's harness driver was
written but not run (fanout stop rule). Runtime logs:
`.issue258-runtime/track2.log`, `track2_finish.log`.
