# Issue #252 — Candidate C (mid-harness connector) adoption study

Worker: Muse (PMO session), 2026-11-16. Method: fitted repaired audit
(the #248 audit_repair standard), uniform repair budget per height
(2 passes, 900 s / 40 evals per pass, the #248 frontier method).
All Z provisional on the Junana q = 1.50 assumption where the #248
design is inherited (plateau Z24.65 at the 13.55 deck).

## Verdict

**Candidate C is NOT ADOPTABLE at any of the three deck heights
studied (plate top Z13.55 / 15.0 / 16.2).** The carrier PCB itself is
fully designed and qualified (DRC 0 / ERC 0, pin mapping verified
numerically), the electrical addition passes with margin
(Vfar 4.779 V vs the 4.60 V target), stock passes, and the service
concept works mechanically — but the two-segment routing does not
reach a fitted-clean state at the uniform repair budget: gate 1
(fitted collision audit) remains at **571 / 535 / 489**
unexpected contacts (17 mm pitch) against a requirement of 0.
The binding problem is the Wing segment's fan/hairpin zone in the
central bay — the same zone that defeated candidate A in #248 —
now shared with a carrier board that the low pins' hairpins also
strike. This is a routing-convergence result at the sanctioned
budget from a constructed seed, not a proof that no fitted route
exists; it is, however, the same evidence standard that closed
#248, and on that standard candidate C does not qualify. The Δ+6
design (D-041) remains the only qualified low-risk path; candidate
C's carrier work is preserved here for any future restart.

## 1. Candidate C as studied

Each Wing harness is split in two by a carrier PCB in the central
bay carrying 2× JST SM14B-GHS-TB back-to-back (JC1 faces the Wing
segment, JC2 the Main segment), wired pin-k to pin-k — a pure 1:1
pass-through; D-024 cavity numbering is invariant end-to-end.
Service: shells off → unplug both pairs at the carrier → unscrew
and remove the carriers (2 screws each) → lift the Wing out WITH
its short segment attached → Main segment removable from the Main
side. No extraction slack is needed at the Wing plug; no connected
slide-service (the gate-3 requirement change PO approved for
candidate A on 2026-11-15, in carrier form).

Fixed frame honoured throughout: Main Rev.7 / Wing Rev.4
byte-unchanged; GH connectors and D-024 invariant; #248 low-deck
case at plate Z13.55 primary (plateau Z24.65 provisional), PO slope
lines, seam rule, printed PETG shells; wire OD1 / AWG28 class,
R ≥ 5 continuously certified by the strict build; F-015 precedent
applied to the Fly model defect; Ender-3 Pro envelopes; aluminium
plates per D-038.

## 2. Carrier PCB (WP1) — qualified

Tree: `hardware/kicad/qualification/issue-252-carrier/`
(carrier.kicad_sch / carrier.kicad_pcb / carrier.kicad_sym /
carrier.kicad_pro, footprint = the project's qualified GH asset
under connector/Carrier.pretty/, inspection/ = DRC + ERC reports,
netlist, pad table).

- 2 layers, outline 29 × 35 mm (assembly X 3..32, Y −8..27), both
  headers SM14B-GHS-TB(LF)(SN) (LCSC C265343):
  - JC1 (Wing-facing), TOP face, mates toward −X; plug tails row
    along Y at assembly X = 21.0, wire Z = 16.45.
  - JC2 (Main-facing), BOTTOM face, mates toward +Y; plug tails row
    along X at assembly Y = 20.0, wire Z = 10.65.
  (Tail geometry from the #248 B1 dimensioned mated-GH model:
  tail = origin + u_k·row + 5.55·axis, wire at face ± 2.10.)
- **Pin mapping — verified numerically** from the built board
  (inspection/pad-table.json): JC2 sits flipped on the bottom face
  (its cavity row reverses against a top-face placement) and JC1 is
  rotated 180° in plan (its row also reverses); the two reversals
  cancel, pad positions land exactly on the model's cavity
  coordinates, and both headers are netted P<k>_<function> per
  D-024, so Wing cavity k → Main cavity k for all k = 1..14,
  derived from the physical presentation of each header (the
  round-4 / D-032 discipline), never assumed. GND cavities keep
  separate nets on the carrier — no joining anywhere; the carrier
  is a pure pass-through.
- On-carrier routing: the two headers' pad orders are reversed
  relative to each other; a single via row south of both headers
  absorbs the reversal (B.Cu verticals from JC2, F.Cu staircase to
  JC1 — planar by construction). Power/return nets 0.50 mm,
  signals 0.30 mm, vias 0.60/0.30 (project standard via).
- **DRC: 0 violations, 0 unconnected** (0.10 mm clearance class,
  D-019/D-021). **ERC: 0 errors, 0 warnings.** Netlist export
  confirms JC1.k ↔ JC2.k on every net.
- Mounting: FIXED seat — two printed posts (Ø7) per carrier rise
  from the tray floor to the board underside at assembly
  (4.5, −6) and (28.3, −6); M2 screws through the board's Ø2.2
  holes. Justification: unplug extraction (~6 mm along each axis)
  must react against a fixed carrier; a floating carrier would
  push the extraction load into the opposite segment's plug.
  Case delta, ledgered in §6.
- Manufacturing note: both headers are SMD. Recommendation =
  **hot-plate hand assembly** on the project's existing reflow
  setup (2 parts, no fine-pitch devices; JLCPCB PCBA would add an
  Extended-part feeder fee and setup for a 2-part board). The part
  is the same C265343 already qualified on Rev.7/Rev.4.

## 3. Routing (WP2) — gate 1 fails at all heights

Construction: per side, Wing segment = [Wing outlet B0/B1,
corridor, rise top (the #248 design_r15 skeleton), 3 free points,
on-axis approach, carrier W tail]; Main segment = [carrier M tail,
on-axis run (6–12 mm, per-pin), 1–2 free points, P, G, Main ep
(the round-9 on-axis stations)]. Free points seeded per strand by
a buildability search against the strict R5 build
(split_corners + rounded); the Wing segment's fan is a per-pin
staggered hairpin (west run north of the tail row, south leg,
east axis join) because the incumbent fan's exit momentum
(≈155° hook at its last point) cannot turn west into the carrier.
Repair: per-segment Gauss-Seidel fitted repair (frontier method),
acceptance = local fitted count down, else ≥2 % volume down.

Fitted repaired-audit results (both counters agree exactly at
13.55: the fast counter and the canonical fitlib18 Scorer both
give WW 333, WF 238/242):

| plate top | WW | WF @17 | WF @16 | **gate 1 @17 / @16** | longest segment |
|---|---|---|---|---|---|
| Z13.55 | 333 | 238 | 242 | **571 / 575 FAIL** | 121.88 mm |
| Z15.0 (Δ+1.45) | 299 | 236 | 240 | **535 / 539 FAIL** | 123.33 mm |
| Z16.2 (Δ+2.65) | 246 | 243 | 247 | **489 / 493 FAIL** | 121.67 mm |

Seed (pre-repair) gate 1 at 13.55 was 600/602 — two passes bought
only ~5 %: gains are whole-segment shifts, there is no convergence
trend toward 0, and the SegM units were barely reached (the pass
ordering spends the budget on the worse SegW units first). Height
helps WW (333 → 299 → 246 across the three heights) and WF not
at all (238 → 236 → 243) —
the residual is topological, not clearance-driven, exactly as in
the #248 frontier study.

Residual structure @17 (13.55, WF families): carrier board 64,
aluminium plates 56, shells 30, trays 20, Wing PCBs 20, MUX
underside bounds 18, Main GH drawing bounds 12, switch envelopes
8, seat posts 8, strips 2. Two named findings:

- **The carrier board is the largest single WF family (64).**
  The seed's Z-ladder (0.35 mm/pin) dips the low pins' hairpins
  to Z ≈ 13.5–14.1 where they cross the carrier board's Z band
  (12.75–14.35) inside its footprint (SegW-01 × board 17.8 mm³).
  A production route must hold every hairpin ≥ board top + 0.5;
  that is a seed-design fix, recorded here — it was not applied
  mid-study because the uniform-budget method forbids reseeding
  between passes.
- **The 2 known POM skin residuals of #248 are NOT inherited:**
  no POM pair appears in this candidate's audit at either pitch
  (the segments do not traverse the low_south skin the way the
  incumbent route did). Nothing is carried as a named residual;
  every contact above counts against the candidate.

Gate 2 (lengths): PASS at all heights — longest finished segment
121.88 mm (13.55) / 123.33 mm (15.0) vs the 200 mm per-segment
bound; worst end-to-end (SegW + SegM, one strand) 165.06 mm.

## 4. Service qualification (gate 3, adapted) — concept sound, not certifiable on an unqualified route

Evaluated on the best-effort 13.55 design (gate3_results.json);
because gate 1 fails, no motion result here certifies — the
readings show the concept's mechanics, not a qualification.

- Shells off: vertical sweep clears from +5 mm (0 hits at
  +5/+10/+25, both pitches); at +2 mm the shell slope grazes
  high SegW wires (26 hits) — removal wants the first 5 mm of
  lift kept vertical and slow, as with #248 round 18.
- Unplug W pair (−X, 3/6 mm): length conservation HOLDS
  (rebuilt path never needs to grow > 0.05 mm — the segment's
  own curvature feeds the extraction). Contact counts (196/198)
  are the fitted state's pre-existing contacts of the moved
  wires, not new motion-induced classes. Several moved wires
  fail the strict R5 rebuild at full extraction (the model holds
  downstream waypoints fixed; a real wire redistributes its
  bends) — recorded as a model limitation, and one more reason
  certification needs a fitted-clean route first.
- Unplug M pair (+Y, 3/6 mm): 0 hits over the wires that build,
  length conservation holds; same rebuild caveat.
- Wing lift-out with segment (carriers still seated): grazes at
  +5 (12–13 hits incl. Wing × carrier board, 648.6 mm³ left) —
  **procedure amended: unscrew and remove the carriers before
  lifting the Wings** (they are 2-screw parts sitting in the
  open bay; with them removed the lift path is the #248 one).
  At +20 both sides are fully clear (0 hits) even with carriers
  seated.
- Main segment removal: clear at +20 (0 hits); +5 shows only
  ≤0.03 mm³ grazes against the fitted state's own contacts.
- Fly 170 storage and USB insertion: unaffected by the carrier
  (the Fly cable and opening are bodies in the audit set; no
  carrier body intersects the USB sweep) — inherited PASS from
  #248 on the unchanged case geometry.

## 5. Electrical (WP3) — PASS

Real extraction from the built carrier + fitted segment lengths
(electrical.py / electrical.json). Per-element model, stated:
GH mated-pair contact 30 mΩ (JST GH initial maximum); crimp
5 mΩ per termination (allowance, labelled); carrier traces from
the built board (Cu 1 oz; HALL_5V net 22.38 mΩ incl. via
allowance; signal nets up to ~86 mΩ — irrelevant, they feed
high-impedance MUX/ADC inputs); wire AWG28 213 mΩ/m at the
fitted finished lengths. Loop = HALL_5V line + six GND returns
in parallel (7/6 factor), worst strand (right, strand 12:
SegW 121.88 + SegM 43.18 = 165.06 mm end-to-end).

| quantity | baseline (D-033 200 mm, 2 pairs) | candidate C (4 pairs + carrier) |
|---|---|---|
| harness loop | 143.0 mΩ | 253.8 mΩ |
| Δ loop | — | +110.8 mΩ |
| Vfar @127 mA/Wing | 4.792958 V (Rev.7 qualified) | **4.7789 V** |
| margin to 4.60 V target | +193 mV | **+179 mV — PASS** |

The split costs +110.8 mΩ of loop (two extra mated pairs +
carrier traces, partly offset by much shorter wire: 165 mm
end-to-end vs the 200 mm baseline). Even at the full 200 mm
wire bound the candidate would hold ≈4.777 V.

Main-copper targets are board targets and are stated separately
(the #167 lesson — they are NOT netted against the harness):
Rev.7 extraction common 49.491 / J2 branch 20.961 / J3 branch
43.051 mΩ against the ≤50 mΩ targets — unchanged by candidate
C, which touches no board.

## 6. Case-delta ledger

- ADDED: carrier seat posts, 2 per carrier (Ø7, tray floor to
  carrier underside Z12.75) at assembly (4.5, −6) and (28.3, −6)
  per side — printed with the trays. The carrier board outline
  and its header/plug envelopes are new fitted bodies (audited).
- UNCHANGED: trays (otherwise), E-R posts, shells (central +
  north strips), PO slope lines and seam rule, plateau height,
  Main Rev.7 / Wing Rev.4 boards, aluminium plates, Fly seat +
  170 mm cable storage, USB opening, Ender-3 Pro envelopes.

## 7. Stock + cost (WP4) — checked 2026-11-16

Quantities: the task brief's per-keyboard figures (+2 headers,
+2 plugs, +28 crimps) describe ONE split. A keyboard has two
harnesses, hence **two carriers**: the keyboard totals are
**+4 headers, +4 housings, +56 crimps, +2 carrier PCBs** of one
design. Both figures are stated wherever they matter.

| part | source / date | stock | need (keyboard) |
|---|---|---|---|
| SM14B-GHS-TB, LCSC C265343 | JLCPCB live check 2026-11-13 (project record) | overseas 1,859 + presale 1,196 | +4 |
| GHR-14V-S housing | DigiKey (crawl 2026-11-06) 4,549 @ $0.18; Farnell (2026-11-13) 940; LCSC carries it, code not confirmed in this check | thousands in distribution | +4 |
| SSHL-002T-P0.2, LCSC C189897 | LCSC fresh fetch 2026-11-16: InStock, $0.0066 ref; 2026-10-27 crawl: 578,200 | ≥ 578 k class | +56 |

All pass the project's ≥10× stock guideline for the added
quantities. (The header figure is the project's own most recent
live check; this session's web search did not surface a fresher
LCSC page for C265343 — flagged, not hidden.)

Cost delta per keyboard at quote level (2 splits), PO priority
order — cost first:
- carrier blanks ×2 ≈ $1–2 (29×35 mm 2-layer, small batch)
- headers ×4 ≈ $0.5–0.9; housings ×4 ≈ $0.7 (@ $0.18);
  contacts ×56 ≈ $0.4–0.7 (@ $0.0066–0.0128)
- assembly: hot-plate hand labour (existing capability, no
  vendor fee); crimping +56 terminations = hand-crimp labour
  class (LCSC custom cable is an MOQ-1 alternative)
- **parts total ≈ $3–5 per keyboard** — inside round 13's
  +$6–12/unit class estimate once labour class is counted.
Cost is NOT the blocker for candidate C; routing convergence
is. Backtracking risk: adopting C would have respun nothing
(boards unchanged) but would have frozen a harness definition
(D-033) around an unqualified route — the dominant risk, and
the reason for the negative verdict. Freedom: C preserved all
board/case options; that virtue does not offset gate 1.

## 8. Gate table (adapted #248 set, 13.55 unless noted)

| gate | result |
|---|---|
| 1 fitted collision (repaired audit) | **FAIL** — 571 @17 / 575 @16 (15.0: 535/539; 16.2: 489/493) |
| 2 finished lengths ≤200 mm/segment | PASS — longest 121.88 mm; end-to-end 165.06 mm |
| 3 carrier service (shells off → unplug → carrier removal → lift-out) | NOT CERTIFIABLE on an unqualified route; mechanics sound (§4) |
| 4 Fly 170 storage | PASS (inherited, unchanged geometry; Fly is an audit body, no carrier interference) |
| 5 USB insertion | PASS (inherited; carrier outside the sweep) |
| 6 keycap sweep (Junana, assumed envelopes) | OPEN — inherited; physical measurement still PO-side |
| 7 print envelopes / manufacturing data | PASS for the case (unchanged); carrier DRC 0 / ERC 0 (§2) |
| 8 fitted preview STEP | NOT PRODUCED — no qualified assembly exists to preview |

## 9. Draft decision text (NOT applied — docs/decisions.md untouched)

D-033 amendment (draft): "…the 200 mm harness length bound
applies per harness as manufactured. A mid-harness split
(candidate C, Issue #252) was evaluated and NOT adopted
(2026-11-16): the carrier design is qualified but the
two-segment routing did not reach a fitted-clean state at any
of Z13.55/15.0/16.2 under the uniform repair budget; the
single-piece 200 mm harness remains the only qualified
definition."

New decision (draft) — D-042: "Candidate C (mid-harness GH
carrier) — REJECTED for adoption (Issue #252, 2026-11-16).
Carrier PCB qualified (DRC/ERC 0, pin mapping verified);
electrical addition +110.8 mΩ loop, Vfar 4.779 V (PASS);
stock/cost pass (≈$3–5/keyboard parts). Rejection ground is
gate 1 only: fitted contacts 571 @Z13.55 (535 @15.0, 489 @16.2)
after the uniform repair budget, dominated by the Wing-segment
fan/hairpin zone and carrier-board strikes from the seed's
Z-ladder. Do not re-propose without a route concept that keeps
the Wing segment's fan out of the carrier board's Z band and a
fitted-clean seed. The Δ+6 case (D-041) and single-piece
harness remain the baseline."

## 10. Open items

- Junana MX physical measurement (q, installed skirt at full
  travel, swept width) — OPEN, inherited from #248 (PO-side).
- If candidate C is ever restarted: fix the SegW seed first
  (hairpins ≥ carrier top + 0.5 everywhere; fan Z-ladder
  independent of the board band), and give SegM repair priority
  parity (the pass ordering starved it here).
- GHR-14V-S LCSC code unconfirmed (distribution stock is
  ample via DigiKey/Farnell regardless).

## Sources (this tree)

sources/: fitlib252.py / fitlib252h.py (geometry + carrier
model), repair252.py (fitted repair), count_full.py,
gate3_252.py, electrical.py + electrical.json, design_seed /
design_state / design_state_h1.45 / design_state_h2.65 (design states),
full_count_s0.0 / s1.45 / s2.65 (fitted counts), scorer_final.json
(canonical Scorer cross-check at 13.55), gate3_results.json.
Carrier tree: hardware/kicad/qualification/issue-252-carrier/.
