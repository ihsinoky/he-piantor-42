# Issue #292 Stage 2 — Wireless Main layout (ISP1807-LR)

Tree: `hardware/kicad/qualification/issue-292-wmain/`
Board: `wmain.kicad_pcb` (native KiCad 9, 4 layers, 1.2 mm)
Basis: D-056 (module = Insight SiP ISP1807-LR, outline = Rev.10
exactly, north tab dropped), Stage 1 study
(`.issue292-runtime/wmain-design.md`), Stage 2a re-selection
(`.issue292-runtime/module-selection.md`).

## Gate table (re-route round, 2026-11-19 — all measured on the final board file, SHA-256 `2f0b4526…`)

| Gate | Result |
|---|---|
| ERC (native schematic, 55 parts) | **0 violations** |
| DRC unconnected | **6 items** (deviation 10): module GND pads U1.14+U1.16 as one isolated pair; VBUS 1; SYS_3V3 2; PAD_EN 1; VBAT_SENSE 1. All other nets — every module signal, both Wing links, USB_DM/DP, SWD, RESET_N, ADC_A/B/C — connected |
| DRC shorting_items / tracks_crossing | **0 / 0** |
| DRC severity-all (zone-refilled) | 720 violations total, of which clearance 502 — the population is inherited (≈499 already present in the pre-round board, dominated by the #263-era netclass population and the connector fanout grazes); this round's delta ≈ +3 clearance, +61 copper_edge_clearance (south-band routes), +23 hole_clearance (field/hop vias). Residue classes: silk 20, dangling 35, mask bridge 3, annular 3 — itemised in `.issue292-runtime/gates-final.json` and the round notes |
| D-057 rule area (MODULE_FIELD_FINE) | Rectangle (69.3, 119.05)–(80.9, 128.9) = 11.6 × 9.85 mm = **114.26 mm²**, rule areas on all 4 copper layers + `wmain.kicad_dru` (clearance/track_width min 0.05 mm inside). **Measured in-field minima from board data:** track width **0.050**, track–track **0.066**, track–pad **0.046** (vs no-net NC pads; 0.004 below the 0.05 floor — deviation 11), via-to-copper **0.050**, pad–pad 0.25 (land pitch gap). **148 item pairs** inside the field have clearance < 0.10 mm and are legal only under D-057 (the exception's full footprint) |
| Via-pad audit (different-net, from placed data) | Outside the field: **min 0.100 mm** (pre-existing PAD_DR via ↔ JPAD MP pad) — D-019 floor holds. Inside the field: min **0.054** (ADC_B escape via ↔ U1.7 GND pad), 5 sites in 0.054–0.081, all exception-dependent. Sub-0.125 sites board-wide: 10 |
| Via size audit | Unchanged from the layout round: 5 vias below the 0.60/0.30 project standard (deviation 5). All vias added in this round are 0.60/0.30 standard |
| Trackpad Ø40 keep-out | **0 pads** inside r20 at (100,118); rule area enforced (footprints only — copper under the bay is permitted). DRC items_not_allowed = 2: J2/J3 footprints (pre-existing, deviation 4) |
| Antenna keep-out | **0 tracks / 0 vias** in the strip x 70.3–79.9, y 128.9–137.9 (all layers) — re-verified on the finished board |
| Wing-link census (from board pads) | J2 and J3 both **14/14** as designed: pin 14 = HALL_3V3, pin 8 = MUX_EN0 (J2) / MUX_EN1 (J3), pins 2/4/6 = MUX_OUT_C/B/A, pins 9/10/12 = MUX_A2/A1/A0, odd pins GND, MP no-net — identical signal content to the wireless Matrix/Wing definition |
| Outline delta vs Rev.10 | **0** — Edge.Cuts 14 segments equal as undirected edges (endpoints match to 0.001 mm), re-verified on the finished board; mounting holes at Rev.10 positions |
| Far-Wing rail budget | HALL_3V3 copper is **byte-identical** to the layout-round board (script-verified key-set equality), so the layout-round figure carries over unchanged: on-board ≈0.09 Ω → ≈2.5 mV at 28 mA; FFC lane at the 1.30 Ω acceptance limit adds 36.5 mV; total **≤ 39 mV** against the ≤50 mV class budget |
| Module GND pads | **8 of 10 plane-tied** (pads 1, 7, 18, 21, 23, 24, 25, 31 — taps/chains re-verified in DRC); pads 14+16 tied to each other only (deviation 10). Supersedes the layout-round disposition in deviation 3 |

DRC residue classes not listed above: silk_over_copper 13,
silk_edge_clearance 4, silk_overlap 3 (cosmetic, donor-inherited
silk), track_dangling 1 (MUX_EN1 inner stub, electrically inert),
hole_to_hole 0 after duplicate-via removal.
**(Superseded by the re-route gate table above where the two
differ; the layout-round table is retained in git history.)**

## USB arrangement — comparison and pick

Candidates: (i) bare USB-C on a minimal north mini-tab;
(ii) EZmate-linked daughterboard; (iii) bare connector elsewhere
on the existing outline.

**Pick: (ii).** J4 (Molex Pico-EZmate 781710004, at its Rev.10
pose) stays on Main; USB-C lives on the daughterboard. The
stocked Fly daughterboard (PO owns two) can serve: its recorded
spec is EZmate 781710004 with ESD + VBUS TVS + common-mode
filter + 1 A fuse, and its USB path is data+power pass-through —
exactly what the module's USB (VBUS pin 12, D+ pin 8, D− pin 10)
needs; VBUS is diode-OR'd on Main (D1) so the pack can never be
back-fed. Cost: zero new boards (units on hand). Rework: none on
Main. Freedom: the USB-C side can be re-spun or swapped without
touching Main, and SWD (below) is an independent update path.
(i) loses: it spends the one allowed outline deviation on a
connector that (ii) makes unnecessary. (iii) loses: no legal
spot exists — the south edge is the antenna/PETG zone and the
battery pod mouth, the north edge is the trackpad bay and the
Wing FFC exits.

**Outline consequence of the pick: none. Outline delta = 0**
(no tab). The deviation slot is unspent.

## SWD provision

JSWD = pads-only TC2030-class 6-pin footprint at (113.5, 136.2),
south band, wired VTref(SYS_3V3) / SWDIO / RESET_N / SWDCLK /
GND / NC(SW O unconnected). Justification: zero fitted height,
pogo access with the case open, nothing above it; the assumed
programmer is PO's nRF52840 DK (PCA10056) Debug Out (PO input
2026-11-19). USB is therefore not the sole update path.

## Antenna report

Module at (75.1, 124.85) rot 0 (official frame since the fix
round; the Stage 2 text below the gate table predates it) in the
Stage 1 south-west pocket,
antenna edge facing south toward the PETG zone. Keep-out per
Insight SiP §4.3 (metal exclusion from the antenna edge to the
board edge, all layers): implemented as rule areas on all four
copper layers over x 70.3–79.9, y 128.9–137.9 — the south
boundary is the module body edge (128.85), i.e. the exclusion
starts at the antenna edge itself (maker wording), not at the
pad row. Audit: 0 tracks, 0 vias inside. The GND plane (In1.Cu)
is likewise excluded there by the rule area. ANT_LINK
(OUT_ANT pin 20 → OUT_MOD pin 22) is routed on F.Cu inside the
module's own pad field as the datasheet requires; no external
antenna parts. NFC pins 2/4: no-connect (stated disposition —
NFC is not used; the pins are left unconnected per datasheet
allowance for unused NFC).

## Case fitted check (vs `hardware/case/issue-263-lowdeck-production/`)

Dimensional comparison against the Rev.10 fitted audit basis —
no new 3D run, because every interface dimension is inherited:
- Outline and mounting holes identical to Rev.10 → tray fit
  identical, including the south-straightened outline going
  forward (the wireless case work takes the straightened
  outline; this board's outline equals Rev.10's, whose south
  edge is the reference the straightening was checked against).
- J4 EZmate at the Rev.10 pose → plug mouth geometry identical
  to the fitted-audited Rev.10 (mated height ≈3.0 mm class).
- Module height ≈1.1 mm class (LGA) — below the XFL4020 2.0 mm
  envelope already audited in the tray; confirm the exact
  ISP1807-LR max height from the datasheet §3 drawing at the
  adoption gate (with deviation 1).
- JSWD: flat pads, no component — pogo access with the case
  open; south band, clear of the trackpad bay and the pod zone.
- JBATT (JST GH, 2.9 mm) at the south edge (124, 134.5) over
  the battery pod opening per the Stage 1 south-band note;
  ≈3 mm local height matches the EZmate precedent.
- Trackpad bay: Ø40 keep-out holds (0 pads inside); JPAD FFC
  land at (112.5, 96.8) on the bay's north-east rim.

## Deviations

1. **ISP1807-LR footprint is DERIVED, not maker-verified.**
   §3 pin table fully extracted; the §3 pad-placement / §4.1
   drawings are graphical with no coordinate table in any
   reachable text source, so the land pattern is a JEDEC
   dual-row derivation (0.65 pitch, pads 0.4×0.4; map in
   `.issue292-runtime/isp1807-derived-pads.json`). Consequences
   visible in the gates: 8 pad-to-pad clearances of 0.060–0.085
   inside the module field (below the 0.10 rule, no contact).
   The south NC ring pads 70–78 are OMITTED from the footprint:
   with them present, the south functional row (pins 34–44)
   cannot escape at project rules (inter-row corridor 0.25 mm <
   0.30 mm needed; interstitial via would need ⌀≤0.15 mm).
   **Adoption condition (D-057): replace with Insight SiP
   official CAD and re-run the module-field gates before any
   order.** Precedent: D-043 carried the reconstructed FH12 MP
   land the same way. Package is DRAFT / NOT FOR ORDER.

   **Fix-round status (2026-11-19): FOOTPRINT DISCHARGED —
   RE-ROUTE BLOCKED, PO decision required (deviation 9).**
   **Re-route round (2026-11-19): DISCHARGED IN FULL.** The
   official footprint is in the tree board (this directory,
   SHA-256 `2f0b4526…`): the tree board's U1 was replaced with
   the verified library footprint, pad-number→net assignment
   script-verified identical to the fix-round working board
   (only the 9 added NC pads differ, no net). The module field
   is routed under the D-057 exception (deviation 9 RESOLVED);
   the D-057 adoption condition is therefore met, subject to
   the residuals in deviation 10.
   Insight SiP official CAD was obtained from the maker's own
   file tree (`insightsip.com/fichiers_insightsip/pdf/ble/
   ISP1807/`): Altium library zip (SHA-256 `14fa64eb…`),
   Eagle library zip (`6e9409e1…`), TB gerber zip
   (`ac1dfb31…`), datasheet DS1807 R19 (`6a1fc572…`).
   Provenance and full tables: `.issue292-runtime/official-cad/
   PROVENANCE.md`. Verification, all script-generated:
   (a) geometry triangulated three ways — Altium PcbLib pads
   == Eagle pads == TB top-copper flash cluster, 78/78 pads,
   max error 0.000 mm; (b) pin-function binding three ways —
   datasheet pin table (R19 pp. 9–10), the maker Eagle
   library's connects, and this project's schematic symbol
   agree on all 78 pins (this also exposed a transcription
   error in the Stage 2 study's `design.py` ISP_PINS table —
   shifted by +2 from pin 24; the schematic and board were
   always correct, see PROVENANCE.md correction note);
   (c) pad diff, derived vs official: **same 0, position
   differs 69, size differs 8, added 9 (pads 70–78)** — the
   derived footprint was wrong in both geometry and number
   placement. The library footprint `wmain.pretty/
   ISP1807-LR.kicad_mod` has been regenerated from the
   official Altium library (all 78 pads incl. the south NC
   ring as soldered mechanical pads, maker mask expansion
   0.05 mm) and verified pad-exact on reload. The board swap
   was performed on the working copy
   (`.issue292-runtime/wmain-v28-fp.kicad_pcb`, SHA-256
   `b7629fe9…`): same centre (75.1, 124.85), orientation
   90° → 0° (official frame — pin 1 NW, antenna edge south,
   consistent with §4.3 and the board's antenna strip);
   pad-number→net assignment preserved exactly (script-
   verified against the pre-swap board; only change is the
   added NC pads 70–78, no net). **The tree board in this
   directory is unchanged** (SHA-256 `6afa289a…`, still
   embeds the derived footprint) because the re-route
   cannot be completed under project rules — deviation 9.
   The D-057 condition therefore remains OPEN.
2. **Pin swaps for escape** (design.py, schematic regenerated,
   ERC 0): BTN pin 34 → pin 47 (P0.23); ADC_C pin 44 → pin 42
   (AIN7 — pin 44 is uniquely blocked by functional pad 45);
   PAD_DR pin 29 → pin 50 (P1.06). All are firmware-visible
   only; no signal-content change.
3. **Module GND pads — disposition UPDATED by the re-route
   round (2026-11-19).** With the official footprint, pads 7
   and 18 are now plane-tied (tap via and the south-east F
   chain respectively), joining pads 1, 21, 23, 24, 25, 31 —
   **8 of 10 tied**. Pads 14+16 remain as a pair tied to each
   other but not to the plane (their bridge to pad 18's chain
   is blocked by the VBAT_SENSE escape stub crossing, and no
   via in the NC ring is legal at drill clearances) — carried
   as a residual in deviation 10. The module's 10 GND pads are
   one internal common ground, so the pair is grounded through
   the module in operation.
4. **J2/J3 courtyard tails vs trackpad rule area** (DRC
   items_not_allowed 2): the FH12 courtyard FFC-exit tails
   cross the Ø40 circle; bodies and pads are ≥1.35 mm clear
   of r20 by pad-edge measure. Accepted exception, same class
   as the Rev.10 courtyard behaviour at the bay.
5. **Sub-standard vias** (5 sites, listed in the gate table):
   two 0.45/0.30 hand GND taps (one is the U4.2 via-in-pad —
   plugged/tented per FABRICATION.md) and three router-placed
   0.35–0.40 vias in the module/JSWD funnels. All ≥ JLCPCB
   minima; none is in a current-carrying path.
6. **RPD2.1 ↔ RPD3.1 pad clearance 0.050** (EN0/EN1 pull-down
   0603s placed diagonally at the south edge). Static nets;
   flagged for assembly inspection. A +0.4 mm move of RPD3 was
   tried and reverted (it fouled the EN1 route); a respin with
   official CAD can reposition the pair.
7. **Battery connector changed from the Stage 1 placeholder**:
   JST XH top-entry (6.5 mm) breaks the low deck, so JBATT is
   a JST GH land (1.25 mm pitch, 2.9 mm) per the Stage 1
   study's low-connector intent. LCSC code unverified —
   "verify at quote" in the BOM.
8. **Antenna keep-out boundary interpretation**: exclusion
   measured from the module body edge (128.85), not from the
   antenna pad row — the maker's "from the antenna edge"
   wording. The rule areas on the board encode this.
9. **Official-footprint fanout exceeds the project design
   rules (fix round, 2026-11-19) — RESOLVED by D-057
   (re-route round, 2026-11-19).** PO granted the exception:
   a rule area MODULE_FIELD_FINE covering the footprint plus
   the minimal escape zone — rectangle (69.3, 119.05)–(80.9,
   128.9) = 11.6 × 9.85 mm = **114.26 mm²**, derived from the
   escape geometry in `escapes_005.json` — inside which the
   0.05 mm class is permitted (board rule areas on all four
   copper layers + `wmain.kicad_dru`); outside it D-019
   (0.10/0.10) is unchanged and verified (via-pad floor 0.100
   outside the field). The field was routed with the minimum
   exception that routes: measured minima from the finished
   board are in the gate table (width 0.050, track–track
   0.066, track–pad 0.046, via 0.050; 148 exception-dependent
   pairs < 0.10 mm). JLCPCB manufacturability/cost of the fine
   field is flagged in the quote handoff for confirmation at
   quotation, per D-057. Original deviation text follows.
   With the official land pattern, 0.4 mm pads at 0.65 mm
   pitch leave 0.25 mm streets; a 0.10 mm track at the
   0.10 mm clearance rule (D-019) needs 0.30 mm. Measured
   with an exact-geometry A* (0.05 mm grid, obstacles from
   board data) on the swapped board: the 12 edge nets escape
   at 0.10/0.10, but the 12 interior nets (U1 pads 3, 5, 9,
   13, 15, 17, 19, 27, 33, 47, 50, 56) escape 0/12 at
   0.10/0.10, 5–8/12 at 0.075/0.075 (order-dependent),
   7/12 with 0.05 mm tracks at 0.10 clearance, and 12/12
   only at 0.05/0.05 (escape set recorded in
   `.issue292-runtime/escapes_005.json`). KiCadRoutingTools
   in three configurations (all-net, rip-up retry,
   single-net) fails the same pads identically. The maker's
   own test board (ISP1807_LR_TB_Gerber, measured from the
   GTL) fans the same land pattern out with 0.1 mm tracks
   at field clearances down to ≈0.05 mm — the module's land
   pattern presumes ~0.05 mm-class fanout rules. Options
   for the adoption gate: (a) a module-field rule exception
   (≈0.05 mm class; JLCPCB manufacturability and cost to
   be confirmed at quote — this is below standard-process
   minima), (b) the D-056 fallback module MDBT50Q-1MV2
   (castellated — no LGA fanout; re-opens the north-tab
   outline change D-055 accepted), (c) another direction.
   Until the PO decides, the tree board keeps the derived
   footprint and the package stays DRAFT / NOT FOR ORDER.

10. **Residual unconnected items — 6 (re-route round,
    2026-11-19).** After the field routing, six items remain
    unconnected; each was attacked with layer/waypoint/via
    variants and, for the power nets, width relaxations down
    to 0.15 mm (none drawn — every relaxation attempt failed
    and was discarded, so no sub-design-width copper exists
    for these nets): (a) **module GND pads 14+16** — tied to
    each other; the bridge to pad 18's grounded chain is
    crossed by the VBAT_SENSE escape stub, and no tap via is
    legal inside the NC pad ring (deviation 3); (b) **VBUS**
    — the module-side comp reaches a new via at (88, 119.5),
    but the 0.30 mm band y≈110–120 toward the USB-side comp
    is sealed on F/I2/B by the Wing-link and trackpad-west
    routes; (c) **SYS_3V3 ×2** — the CVCC1/CVCC2 island is
    tied together but not to the main SYS_3V3 network nor to
    the module's SYS_3V3 escape comp (the B-end via row at
    y≈119.3 and the field congestion block all layers at
    0.30 mm); (d) **PAD_EN** — its escape via is trapped on
    B and the F south corridor is sealed; (e) **VBAT_SENSE**
    — its B-side pocket and the far I2 track are separated
    by the sealed y≈112–119 band. These are disclosed for
    the adoption gate: the board as it stands is NOT
    electrically complete. Attempts log:
    `.issue292-runtime/reroute-notes.md`.
11. **Verification tooling note (re-route round).** The
    D-057 `.dru` rules are NOT applied by this environment's
    kicad-cli 9.0.9 DRC (control experiments: a 0.5 mm test
    rule — global, net-scoped, and area-scoped — changed no
    violation counts). The exception was therefore verified
    geometrically from board data (script
    `.issue292-runtime/gates.py`: in-field minima and the
    148-pair exception footprint in the gate table). The
    `.dru` and rule areas ship with the board, so a KiCad
    GUI DRC at the fab/PO side applies them normally. One
    measured in-field clearance, track–pad 0.046 mm against
    no-net NC pads, sits 0.004 mm below the D-057 floor —
    disclosed here rather than hidden in the minimum table.

## Draft adoption line (for PO, at the adoption gate)

**D-058 (draft):** Wireless Main layout (Issue #292) adopted as
the wireless Main baseline: ISP1807-LR module (D-056) with the
**official-CAD footprint** (deviation 1 DISCHARGED), Rev.10
outline unchanged (USB via EZmate daughterboard — the stocked
Fly can serve; outline delta 0), module field routed under
the **D-057 rule exception** (deviation 9 RESOLVED; measured
minima and the 114.26 mm² rule area in the gate table), power
tree per Stage 1 (TPS63070 at 3.3 V, diode-OR USB,
TPS22919-switched HALL_3V3 and trackpad feeds, gated battery
divider), SWD pads (TC2030 class) for the PCA10056 Debug Out.
CONDITIONS: (i) the 6 residual unconnected items (deviation
10) are PO-judged — accept as-is with a documented rework/
re-spin plan, or send back for a further routing round;
(ii) JLCPCB confirms capability/cost for the 0.05 mm-class
field at quotation (quote handoff flags it). The
manufacturing package is DRAFT / NOT FOR ORDER until the PO
adopts.
**History:** the D-057 draft line and its fix-round addendum
(footprint condition open, re-route blocked) are superseded
by this D-058 draft; both conditions they carried are
discharged above.
