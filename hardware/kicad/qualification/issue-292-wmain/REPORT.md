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

## Gate table — completion round (2026-11-19; board SHA-256 `509e52a7…`)

The completion round closed all 6 residual unconnected items of
deviation 10 by routing only, inside the existing rules (D-019
outside the field; the D-057 exception only inside
MODULE_FIELD_FINE). **No outline expansion was used**
(deviation 12). All gates re-run on the final file:

| Gate | Result |
|---|---|
| ERC (native schematic, unchanged) | **0 violations** |
| DRC unconnected | **0** — deviation 10 closed item-by-item (see its updated text). Per-net pad census from board data: GND pair tied via the new plane tap; VBUS, SYS_3V3, PAD_EN, VBAT_SENSE each a single component |
| DRC shorting_items / tracks_crossing | **0 / 0** |
| DRC severity-all (zone-refilled, same fill method for both boards) | **722** total on the final board vs **729** on the pre-round board by this method (the re-route round's own fill method counted 720 on the pre-round board — method difference, disclosed). Every severity class is **count-identical** to the pre-round board (clearance 502 = the inherited population; hole_clearance 42; copper_edge_clearance 114) except dangling, which improved: track_dangling 20→17, via_dangling 15→11 |
| D-057 exception footprint | In-field minima **unchanged**: width 0.050, track–track 0.066, track–pad 0.046, via-to-copper 0.050. Exception-dependent pairs 148 → **155** (+7, all ≥ 0.050: 3× new VBAT_SENSE B tracks vs the pre-existing MUX_EN0 via at the field's east edge, 0.050–0.074; 3× new SYS_3V3 I2 tracks vs the pre-existing SWDIO via, 0.065–0.080; 1 pair re-distanced) |
| Via-pad audit (corrected rotated-rect geometry) | Outside field min **0.100** (unchanged); inside field min **0.0536**; sub-0.125 site list **identical** to the pre-round board — no new sites from this round's copper |
| New-copper clearance audit (this round's tracks/vias vs all other-net copper, geometric) | Outside field min **0.100** (VBAT_SENSE via (81.75, 122.85) vs SYS_3V3, I2 — at the D-019 floor); inside field min **0.050** (SYS_3V3 I2 segment vs SWDIO via — at the D-057 floor). One construction artifact found and fixed: the PAD_EN via at (84.35, 119.05) measured 0.0975 to HALL_PWR_EN copper on I2 (raster quantization); nudged to **(84.30, 119.10)**, all-layer clearance ≥ 0.130, endpoints retargeted |
| Trackpad Ø40 keep-out | **0 pads** inside r20 at (100,118) (unchanged; no footprints added) |
| Antenna keep-out | **0 tracks / 0 vias** in the strip x 70.3–79.9, y 128.9–137.9 — re-verified |
| Wing-link census | J2/J3 pad-net maps **identical** to the pre-round board (14/14 each) |
| Outline delta vs Rev.10 | **0** — Edge.Cuts edge set of the final board equals both the pre-round board and Rev.10 exactly (undirected edges). No expansion (deviation 12) |
| Far-Wing rail budget | HALL_3V3 copper identical to the pre-round board (key-set equality) → ≤39 mV figure carries over |
| Module GND pads | **10 of 10 plane-tied** (pads 14+16 tied by the new tap via — deviation 3 updated) |

Method note (repeats deviation 11): kicad-cli 9.0.9 DRC in this
environment does not apply the `.dru` rules, so the D-057
exception was again verified geometrically from board data
(`.issue292-runtime/gates.py`, `audit_completion.py`,
`audit_new_copper.py`, `field_pairs.py`).

## Gate table — edge-fix round (2026-11-19; board SHA-256 `26072619…`, supersedes `509e52a7…`)

A PO review of the final 2D drawings found copper sticking out
beyond the board outline. The adopted board file was defective
(deviation 13): exact-geometry enumeration found **72 unique
copper items crossing the Edge.Cuts outline** (87 item-layer
instances) plus 59 unique items closer than the 0.5 mm edge
clearance — all introduced by the wireless design (Rev.10's
baseline has exactly 2 CLOSE items, neither present here). The
completion round's DRC report had listed the 114
copper_edge_clearance violations inside its 722 "dispositioned"
total without item-level review; this round enumerated,
fixed, and re-gated item by item. **Fix method: re-routing
only** — the west-dent outline fill was evaluated against the
case record and rejected with evidence (deviation 13); the
outline is unchanged.

| Gate | Result |
|---|---|
| **Copper containment (NEW gate, `checks/copper_containment.py`)** | Adopted board: **FAIL** (87 crossing instances). Fixed board: **PASS — 0 crossings, 0 touchings**, 35 CLOSE instances = 17 unique items, each dispositioned in deviation 13 |
| ERC (native schematic, unchanged) | **0 violations** |
| DRC unconnected | **2** — both GND, both item-dispositioned in deviation 13 (CVCC2.2 pad; module GND pads U1.14+U1.16 as one pair). This supersedes the completion round's "10 of 10 / unconnected = 0": its plane tap for pads 14+16 sat in copper the edge re-route had to displace, and no legal replacement site exists (attempts enumerated in deviation 13). All signal nets — every module signal, both Wing links, USB, SWD, trackpad — are single-component |
| DRC shorting_items | **0** (one short introduced mid-round by a re-stitch via — PAD_SDA via vs JPAD.5 pad — was found by DRC and fixed by relocating the via to (111.58, 95.75)) |
| DRC severity-all (zone-refilled) | **704** total on the final tree board (clearance 502 = the inherited population of the #263 netclass defect; copper_edge_clearance **17** = exactly the 17 dispositioned CLOSE items, count-matched against the containment enumeration) |
| Antenna keep-out | **0 tracks / 0 vias** in the strip — re-verified after fixing a PAD_SCL inner-layer detour through the strip that the re-route had introduced (deviation 13) |
| Trackpad Ø40 keep-out | **0 pads** inside r20 at (100,118) |
| Wing-link census | J2/J3 **14/14 each**, identical to the completion round (pin 8 = MUX_EN0/EN1, pin 14 = HALL_3V3, MP no-net) |
| Via-pad audit (true pad shapes) | In-field min **0.0537** (MUX_A0 via ↔ U1.65 NC pad — the completion round's site, unchanged); no new sub-0.10 sites outside the D-057 field and the JPAD fanout rect (worst there 0.0627, this round's relocated PAD_SDA via ↔ JPAD.3 pad, inside the 0.05-class fanout rect) |
| In-field minima (re-measured per layer) | Track width 0.050; all track–track and via-to-copper pairs ≥ 0.050 **except two item-dispositioned pairs** (deviation 13): MUX_A0 F track ↔ U1.7 GND pad **0.0413** (track–pad) and GND stitch via (70.85, 121.35) ↔ MUX_A0 I2 track **0.0424**. ADC_B V2 drill-to-copper **0.2000** vs the 0.25 netclass default — item-dispositioned (the adopted board violates that figure 52× board-wide) |
| Outline delta vs Rev.10 | **0** — vertex sets equal; max vertex deviation 0.00002 mm (file serialization rounding). Dent fill **rejected**: fitted-frame case seam west of the dent measures 0.559 mm (rising to ~2.0 mm), the USB corridor needed the edge ≥ 2.41 mm further west — a fill is not case-compatible (deviation 13) |
| Module GND pads | **8 of 10 plane-tied** (as the re-route round; pads 14+16 dispositioned in deviation 13). New stitches this round: via-in-pad at U1.31 (78.70, 121.50) and U1.7 (71.55, 124.55); Q1.2 and JPAD.2 gained plane vias; JPAD.6's plane via retained |
| Manufacturing package | Regenerated from the final file (BOM/CPL 55 rows, consolidated 32; gerbers + drill re-exported). Still **DRAFT / NOT FOR ORDER** |
| PO drawings | Regenerated (`wmain-2d-topview.png`, `wmain-2d-zoom-module.png`, `wmain-2d-zoom-service.png`); annotation overlays (trackpad circle, south band, antenna rectangle) are now **clipped to the board outline** |

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
   round (2026-11-19), and CLOSED by the completion round
   (2026-11-19).** With the official footprint, pads 7
   and 18 are now plane-tied (tap via and the south-east F
   chain respectively), joining pads 1, 21, 23, 24, 25, 31 —
   **8 of 10 tied**. Pads 14+16 remain as a pair tied to each
   other but not to the plane (their bridge to pad 18's chain
   is blocked by the VBAT_SENSE escape stub crossing, and no
   via in the NC ring is legal at drill clearances) — carried
   as a residual in deviation 10. The module's 10 GND pads are
   one internal common ground, so the pair is grounded through
   the module in operation.
   **Completion round:** a plane tap via placed on the pair's
   existing F bridge track at **(74.6, 124.65)** (0.60/0.30)
   ties the pair directly to the I1 plane. Measured from board
   data before placement: clearance to other-net copper
   F 0.106 / I1 0.413 / I2 0.145 / B 0.413 mm, drill-edge to
   nearest other via 0.712 mm — legal at D-019 everywhere (the
   earlier "no legal tap via" conclusion had probed the NC
   ring interior, not the bridge track itself). **10 of 10
   GND pads are now plane-tied** (DRC unconnected 0).
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
    2026-11-19) — ALL CLOSED by the completion round
    (2026-11-19); DRC unconnected = 0.** Each blocker was
    reproduced from board data (component census) before
    routing, and each closure was proven from the final board
    data (per-net pad census + DRC), not from router exit
    status. As-built closures, all at the nets' design widths
    with no frozen structure touched (module-field routing,
    Wing census geometry and outline untouched):
    (a) **module GND pads 14+16** — plane tap via on the
    pair's F bridge at (74.6, 124.65); measured all-layer
    clearances ≥ 0.106 (deviation 3 updated). The F bridge to
    pad 18 remains blocked by the VBAT_SENSE stub, as
    recorded; the tap makes it unnecessary.
    (b) **VBUS** — a 0.30 mm **F.Cu bridge, 6.90 mm, 0 vias**,
    from the module-side comp at its via (88, 119.5) north
    through the y≈110–120 band at x≈87–88 to the USB-side
    comp. The band was sealed at the corridors the re-route
    round tried; an F corridor at x≈87.2–87.8 was open at
    full width.
    (c) **SYS_3V3 ×2** — island↔main: 0.30 mm bridge
    13.59 mm / 3 vias (via (81.4, 113.65), (82.1, 111.7),
    (82.1, 109.75)) from the island via (74, 116.75) to
    COUT2.1's network; module comp↔main: 0.30 mm bridge
    16.24 mm / 2 vias ((84.25, 121.55), (83.5, 117.65)) from
    the module comp's B trunk end (79.65, 119.35) to the
    (former) island's B diagonal. The net is one component
    (all 15 pads).
    (d) **PAD_EN** — 0.10 mm route 30.05 mm / 2 vias: B from
    the escape via (77.4, 119.35) east, via at (84.30,
    119.10) (nudged from the raster's (84.35, 119.05) for a
    0.0975→≥0.130 I2 clearance fix — see the completion gate
    table), I2/B to via (99.95, 132.5), up into the F trunk.
    (e) **VBAT_SENSE** — 0.10 mm route 22.80 mm / 4 vias,
    predominantly an I2 trunk: from the module comp's B end
    (80.6, 125.45) via (81.75, 122.85), (83.0, 121.55),
    (84.3, 112.7), (83.6, 109.0) to the far comp's I2 track
    at (85.6, 105.5). (Item count: the re-route round's list
    (a)–(e) carries SYS_3V3 twice, i.e. 6 DRC items.)
    Original re-route-round text: after the field routing,
    six items remained unconnected; each was attacked with
    layer/waypoint/via variants and, for the power nets,
    width relaxations down to 0.15 mm (none drawn — every
    relaxation attempt failed and was discarded). Attempts
    log: `.issue292-runtime/reroute-notes.md`; completion
    routes: `.issue292-runtime/route-*.json`, method
    `.issue292-runtime/gaproute.py`.
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
    **Completion round addendum:** the same tooling caveat
    applies; geometric verification was repeated on the final
    board. The 0.046 mm track–pad item was **not touched** by
    this round's routes and re-measures **0.0457 mm** in the
    final audit — carried as-is, per the round's brief. The
    exception footprint is now 155 pairs (completion gate
    table).
12. **Outline expansion — authorized (PO, 2026-11-19) but
    NOT USED (completion round).** The PO authorized
    expanding the outline into the available case margin for
    items that could not close by routing, with the south
    antenna band excluded. All 6 items of deviation 10 closed
    by routing only, so **expansion used = 0.00 mm in every
    direction; the final outline delta vs Rev.10 is 0**
    (Edge.Cuts edge sets equal, verified in the completion
    gate table). No case-side margin was consumed, so no
    board-to-wall clearance changed and no case-record
    measurement was needed; the trackpad Ø40 keep-out and the
    Wing census geometry are likewise untouched.
13. **Edge defect — copper outside the board outline in the
    D-058-adopted board file (SHA-256 `509e52a7…`), fixed by
    re-routing; D-058 AMENDED: configuration unchanged, board
    file superseded by SHA-256 `26072619…`.** Found by PO
    review of the final 2D drawings ("copper is sticking out
    beyond the outline — is this really final?"). Exact-geometry
    enumeration (KiCad shapes + shapely, cross-validated against
    DRC: all 114 DRC copper items contained in the enumeration,
    0 missed) found **131 unique flagged items: 72 CROSSING,
    59 CLOSE (< 0.5 mm), 0 TOUCHING** (167 item-layer instances).
    Clusters: west dent / module fanout 102, north-west shoulder
    13, north-tab east shoulder / JPAD 8, east slant 7, south
    edge 1. Root cause: the escape machinery's field box (west
    edge x = 69.6) was never intersected with the board outline;
    near the dent vertex (71.064, 122.387) the outline sits at
    x ≈ 69.7–71.1, so the box-edge exits and their beyond-field
    corridor (x ≈ 68.4–69.6) lay outside the board — some west
    tracks were fully external (up to 1.41 mm beyond the
    boundary). The completion round's DRC had the evidence
    (114 copper_edge_clearance violations) inside a
    class-dispositioned total; no item-level review was done.
    That review gap is the process defect; the containment gate
    below is the countermeasure.
    **Fix, per cluster** (preference order: re-route ≥ 0.5 mm
    where achievable → dent fill if case-compatible →
    item-level disposition):
    - *West dent / module fanout (102 items):* full re-route of
      the fanout inside the outline — module escapes now leave
      the pad field southward on F inside the grid, hop layers
      in the southern strip / NW tab via fields, and run north
      on I2/B through the pad column's x-range (the dent vertex
      pinches the west strip to 0.136 mm, so no track passes it
      at 0.5 mm edge clearance). Two escapes (LED_DRV, ADC_B)
      closed on second-opinion (Codex) routes applied verbatim
      and re-verified geometrically. 75 GND items lost as
      collateral during the re-route were key-matched against
      the adopted board and restored (20 pruned where they
      overlapped new routes).
    - *Dent fill — REJECTED with evidence:* in the #275 fitted
      frame (replication reproduced the recorded seam 0.5593 mm
      / overlap 0 exactly), the free gap west of the dent is
      0.559 mm on the north segment, 1.99–2.11 mm on the south
      segment; the USB corridor needed the edge ≥ 2.41 mm
      further west. A full straight fill moves the edge 5.02 mm
      at the dent vertex — beyond the gap; a partial fill gains
      ~0–1.4 mm while consuming the seam. Not case-compatible;
      **outline delta = 0** (deviation 12's authorization again
      unused).
    - *N / T / E / S clusters (29 items):* component nudges
      (CIN1, CIN2, CVS, RRST, RPD1, RPD3, CFC, JPAD, TP1 —
      cumulative deltas in the round log) and via/track vertex
      moves; final non-west flagged count = 0 before
      dispositions.
    - *Incidents inside the round, all closed:* a PAD_SCL
      inner-layer detour through the antenna strip (introduced
      by a restore) was cut and re-stitched via the south-east
      I2 mesh — final strip count 0; a PAD_SDA via placed by a
      re-stitch shorted JPAD.5's pad — relocated to
      (111.58, 95.75), DRC shorting = 0; a dangling GND stub
      west of JPAD was identified as Q1.2's stitch and restored
      with its via at (107.40, 97.05).
    **Remaining item-level dispositions** (no class waivers):
    - *CLOSE items (17 unique; measured distance to the
      outline, mm):* GND via (70.850, 121.350) **0.0334** —
      U1.1's stitch via, the adopted board's own geometry
      restored verbatim; the tightest item on the board, flagged
      for the order gate (milling tolerance can reach the
      annulus; it is a GND stitch via, not a signal). GND track
      (71.600, 121.350)→(70.850, 121.350) **0.2334** — same
      stitch. U1.1 pad **0.4364**, U1.2 pad **0.1362**, U1.4 pad
      **0.2745** — module LGA pads, fixed by the official
      footprint. COUT2.2 pad **0.1789** — adopted placement; a
      +0.35 mm nudge was tried and reverted (created shorts);
      north is the edge, south is blocked by MUX_OUT vias.
      RPD1.2 pad **0.4864** — two-sided constraint (CHOUT
      adjacency vs the east slant) after three nudges. Adopted
      GND stitches: track (93.500, 83.975)→(93.280, 84.796)
      **0.0744** + via (93.280, 84.796) **0.1944** (north edge);
      track (131.825, 128.000)→(132.071, 128.918) **0.1548** +
      via (132.071, 128.918) **0.2508** (east slant); via
      (115.750, 100.475) **0.1637** + track (114.800, 100.475)→
      (115.750, 100.475) **0.3136** (JPAD east); via
      (85.128, 99.059) **0.2160** + track (85.800, 98.388)→
      (85.128, 99.059) **0.3660**; via (128.675, 122.998)
      **0.2318** + track (128.200, 122.175)→(128.675, 122.998)
      **0.3817**. (One 0.3414 mm item seen in a mid-round DRC
      does not exist in the final enumeration — it was a
      transient segment removed by the PAD_SCL/LED rework.)
    - *Unconnected GND (2 DRC items):* **CVCC2.2** — its
      adopted via site (72.75, 117.78) is occupied by the
      re-routed USB_DM via; every alternative (via-in-pad,
      north-west hop, east hop at (72.75, 118.35) / (73.35,
      118.35)) is blocked on at least one layer by
      MUX_A0/USB_DM/MUX_A1/SYS_3V3 copper. CVCC1 remains tied;
      the pad is a decoupling-capacitor ground. **Module GND
      pads U1.14 + U1.16** (tied to each other) — the completion
      round's tap via conflicts with VBAT_SENSE's re-routed
      staircase and via (75.45, 125.20); the y-125.56 thread,
      the y-124.325 street, via-in-pad at three offsets, and a
      VBUS jog shift were all attempted and geometrically
      blocked (VBAT_SENSE, VBUS, MUX_A2, BTN items). The pads
      rely on the module's internal GND plane continuity; the
      other 8 module GND pads are plane-tied, including both
      0.8 × 0.8 west pads and U1.18 in the same row. Both items
      are carried to the order gate as accepted residuals of
      this fix, replacing the completion round's "10 of 10"
      line.
    - *In-field sub-floor pairs (2):* MUX_A0 F descent track ↔
      U1.7 GND pad **0.0413** (track–pad; the descent is centred
      in a 0.18 mm channel between the pad and USB_DP's via —
      both neighbours re-measured ≥ 0.050 after corridor
      balancing) and GND stitch via (70.85, 121.35) ↔ MUX_A0 I2
      track **0.0424** (via-to-copper). Same class as deviation
      11's adopted 0.046 track–pad item, 0.004–0.009 lower,
      created by the forced re-route out of the illegal west
      geometry.
    - *ADC_B drill-to-copper **0.2000*** (V2 (75.90, 120.30)
      drill vs the PAD_DR dogleg) vs the 0.25 hole_clearance
      netclass default — inside the D-057 field; DFM
      confirmation at quotation, like the D-057 items. The
      adopted board violates the 0.25 figure 52× board-wide.
    **New hard gate:** `checks/copper_containment.py` (this
    tree) fails if any copper shape crosses or touches the
    outline; it reproduces the defect on the adopted file
    (87 crossing instances, FAIL) and passes the fixed file
    (0 / 0). **D-058 amendment:** the adopted configuration is
    unchanged in every particular (module, power tree, USB
    arrangement, census, outline); only the board file was
    defective and is superseded — SHA-256 `509e52a7…` →
    `26072619…`. The D-058 condition (ii), JLCPCB confirmation
    of the 0.05 mm-class field at quotation, is unchanged and
    now also covers the ADC_B drill item above.

## Draft adoption line (for PO, at the adoption gate)

**D-058 (draft):** Wireless Main layout (Issue #292) adopted as
the wireless Main baseline: ISP1807-LR module (D-056) with the
**official-CAD footprint** (deviation 1 DISCHARGED), Rev.10
outline unchanged (USB via EZmate daughterboard — the stocked
Fly can serve; **final outline delta = 0** — the PO-authorized
expansion of deviation 12 was not needed), module field routed
under the **D-057 rule exception** (deviation 9 RESOLVED;
measured minima and the 114.26 mm² rule area in the gate
table), power tree per Stage 1 (TPS63070 at 3.3 V, diode-OR
USB, TPS22919-switched HALL_3V3 and trackpad feeds, gated
battery divider), SWD pads (TC2030 class) for the PCA10056
Debug Out. **The board is electrically complete: DRC
unconnected = 0** (completion round, 2026-11-19 — deviation
10 CLOSED). CONDITIONS: ~~(i) the 6 residual unconnected
items (deviation 10) are PO-judged~~ **DISCHARGED by the
completion round**; (ii) JLCPCB confirms capability/cost for
the 0.05 mm-class field at quotation (quote handoff flags
it) — the sole remaining condition. The manufacturing
package is DRAFT / NOT FOR ORDER until the PO adopts.
**History:** the D-057 draft line and its fix-round addendum
(footprint condition open, re-route blocked) are superseded
by this D-058 draft; both conditions they carried are
discharged above.

## SWD respin — TC2050 conversion (2026-11-20; awaits D-061)

PO decision 2026-11-20: convert JSWD from the TC2030-NL-class
6-pad field to Tag-Connect's official **TC2050** footprint.
Scope was the SWD field ONLY. The same session's outline
extension / JBATT relocation was **stopped at the margin gate**
(`.issue292-runtime/margin-budget.md` on this branch): with the
real Wing Rev.6 outlines placed in the case frame, Main's north
diagonals face the Wings across a 2.00 mm FFC channel; the
balanced extension is capped at d = 1.0 mm and no JBATT site
exists. **JBATT stays at the south edge; its cable drape is
fixed case-side (Issue #296). Outline delta = 0 (Edge.Cuts
verified item-identical, 14/14).**

### The new field

- Footprint `wmain:TC2050-IDC-NL`, from the maker's own
  datasheet drawing **DWG TC2050-IDC-NL-FP REV A (12/2/10)**,
  cross-checked against the KiCad library footprint — max
  disagreement 0.001 mm (rounding). Provenance:
  `.issue292-runtime/tc2050/PROVENANCE.md`.
- 10 contact pads Ø0.7874 mm, **no solder paste** (datasheet
  note 3 — the old TC2030 field had paste; corrected), and the
  **3 alignment NPTH Ø0.9906 mm** the old field omitted.
- Placed centre **board (110.5, 135.99), rotation +1.35°** —
  case frame (+10.5, 148.39). The desk-study centre
  (111.5, 136.2) does not survive the official footprint: its
  east-south hole left a 0.189 mm web to the outline and its
  east-north hole drilled the In2.Cu PAD_SCL jog. The shift
  (−1.0, −0.21) plus the rotation keep all three holes clear of
  PAD_SCL and MUX_EN0 with **no drill contact** (residual
  clearances +0.04…+0.10 mm vs the 0.25 mm hole-clearance
  floor — inherent to the maker hole pattern against the
  pre-existing In2.Cu tracks; moving those tracks is outside
  this respin's invariants). RPD2/RPD3 clear the field by
  ~4.1 mm, the plug body by ~1.5 mm. Top face; usable in-case
  with the cover off and on the bench, as before.
- **Signal mapping = Cortex 10-pin debug order** (cable is
  straight-through, datasheet sheet 2): 1 VTref→SYS_3V3,
  2 SWDIO, 3 GND, 4 SWDCLK, 5 GND, 6 SWO→NC, 7 KEY→NC,
  8 TDI→NC, 9 GNDDetect→GND, 10 nRESET→RESET_N.
- **Cable correction to the study record:** the plain
  TC2050-IDC-NL terminates in a 0.1″ 2×5 IDC, which does NOT
  mate with the nRF52840 DK. The chain is **DK debug-out →
  TC2050-IDC-NL-050-ALL (1.27 mm Cortex end) → board**, no
  adapter. (Study §E.2's table conflated the two variants.)
- Escapes re-routed inside the field box only: SYS_3V3 via a
  south-edge F.Cu channel + B.Cu return to the existing run;
  SWDIO/SWDCLK on F.Cu 0.1 mm; GND pads 3/5 via the south
  channel, pad 9 via a Ø0.45 via in the In2 window; RESET_N
  via B.Cu jog + Ø0.45 up-via. Pads 6/7/8 carry no tracks.

### Gate results (respin)

| Gate | Baseline (D-058 board) | After respin |
|---|---|---|
| Copper containment | PASS | **PASS** (SE hole CLOSE note 0.489 mm web) |
| ERC | 0 | **0** |
| DRC total (drc2 method) | 704 / 2 unconnected | **709–711 / 2 unconnected** (see note) |
| DRC shorting_items | 0 | **0** |
| Unconnected | CVCC2.2 GND; module GND pair | **identical pair** (item-diff verified) |
| Pad audit vs maker geometry | — | **max error 0.0000 mm** (10 pads + 3 holes) |
| Footprint census | 55 | 55; **only JSWD moved** |
| Track census outside field box | — | **0 diffs** |
| Edge.Cuts | — | **identical (14/14 items)** |

DRC delta, itemised (in-field): annular_width +2 and
via_diameter +2 = the two Ø0.45/0.3 vias (same class as the
design's existing Ø0.45 GND-via precedent); via_dangling +2 =
the SYS_3V3 (112.2,133.3) and GND (115.72,135.565) vias whose
F.Cu stubs were deleted with the old field — both remain
connected on inner/back layers (unconnected pair unchanged
proves it); items_not_allowed +1 = the field's NW corner
intrudes ≤~1.0 mm into the TRACKPAD_KEEP_OUT rim — the field
is planar (pads + holes, zero height), which is what the
keep-out protects against, and J2/J3 already carry the same
class at the same keep-out; hole_clearance: +2 listed (maker
holes vs the new SYS_3V3 B.Cu route, +0.14 / +0.07, no
contact), −2 net class change; two further no-contact
proximities (W hole × PAD_SCL +0.06, E-N hole × MUX_EN0
+0.04) are at this build's DRC reporting threshold and flip
between runs. **Note on totals:** this KiCad build's DRC
reporting of marginal pairs is run-unstable — three runs of
the identical final file gave 709/709/711, with the variance
confined to far-field fine-field decomposition items; the
load-bearing results (shorting 0, unconnected identical,
containment PASS) are stable in every run. No new violation
classes.

### Manufacturing

Gerbers + drill regenerated (28 files, same set);
`wmain-gerber.zip` rebuilt. CPL: only the JSWD row changed
(new position/rotation). **BOM: no purchasable line changes**
— JSWD is a pad/hole field with no part; its two descriptive
placeholder rows were renamed TC2030-IDC-NL → TC2050-IDC-NL.
Package remains DRAFT / NOT FOR ORDER. The JLCPCB quote
re-run stays an order-stage item (the ≈$139 quote of
2026-11-19 predates both the edge fix and this respin).

## Adoption (final)

**D-061 (adopted by PO 2026-11-20; recorded in
`docs/decisions.md`):** Wireless Main SWD respin adopted:
JSWD converted to the official Tag-Connect TC2050 footprint
(10 pads Ø0.79mm on a 1.27 × 1.27mm grid, no paste, 3
alignment holes Ø0.99mm) at board (110.5, 135.99) rot
+1.35°, Cortex pin order, cable = TC2050-IDC-NL-050-ALL
from the PCA10056 debug-out. Outline, JBATT and all other
features unchanged from the D-058 board (SHA-256
`26072619…` → `6dfbcb954e57b1a19fdbbf526f956c00c3c59a756c1a60b7a5e2e4ebf095ecd7`).
D-061 also adopts the standing guideline: the TC2050
footprint is the standard SWD pad field for future ARM
boards, and the standard DIY jig head is a Mill-Max
855-22-010-10-001101 integrated block + 3 guide pins.
The outline extension / JBATT relocation examined in the same
round is **not adopted** (margin gate: 2.00 mm Wing FFC
channel); JBATT's cable management is a case-side item for
Issue #296.
