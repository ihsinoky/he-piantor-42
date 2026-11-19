# Issue #292 Stage 2 — Wireless Main layout (ISP1807-LR)

Tree: `hardware/kicad/qualification/issue-292-wmain/`
Board: `wmain.kicad_pcb` (native KiCad 9, 4 layers, 1.2 mm)
Basis: D-056 (module = Insight SiP ISP1807-LR, outline = Rev.10
exactly, north tab dropped), Stage 1 study
(`.issue292-runtime/wmain-design.md`), Stage 2a re-selection
(`.issue292-runtime/module-selection.md`).

## Gate table (all measured on the final board file)

| Gate | Result |
|---|---|
| ERC (native schematic, 55 parts) | **0 violations** |
| DRC unconnected | 3 items, all module GND pads U1.7 / U1.14 / U1.18 (disposition D3 below); every signal and power net connected |
| DRC shorting_items / tracks_crossing | **0 / 0** |
| DRC clearance (0.10 rule) | 11 — 8 are derived-footprint pad gaps at U1 (deviation 1), 1 is RPD2.1↔RPD3.1 at 0.050 (D6), 2 are hand-tap grazes ≥0.025 with no contact |
| Via-pad audit (different-net, from placed data) | **min 0.100 mm** = the 0.10 floor; sub-0.125 sites: 2 — PAD_DR via ↔ JPAD MP pad 0.100, GND tap via ↔ U2 SW_B pad 0.120 |
| Via size audit | 5 vias below the 0.60/0.30 project standard: 0.45/0.30 ×2 (hand GND taps, annular 0.075), 0.40/0.25 ×1 and 0.35/0.20 ×2 (router-placed in the module/JSWD funnels, annular 0.075). All ≥ JLCPCB minima; listed for the adoption gate (D5) |
| Hole clearance (0.25 rule) | 22 items, actual 0.200–0.245 — drill-to-copper margins of the dense funnels; no drill intersects copper |
| Copper edge clearance (0.50 rule) | 43 items — dominated by the FH12 GND band vias/stubs in the pad-to-outline band (Rev.10 precedent: its own GND web occupies the same band; Rev.10 count under its project settings was 4) |
| Trackpad Ø40 keep-out | **0 pads** inside r20 at (100,118); rule area enforced (footprints only — copper under the bay is permitted, the pad sits above the board). DRC items_not_allowed = 2: J2/J3 courtyard FFC-exit tails cross the circle; pad-edge clearance to r20 measured ≥1.35 mm (D4) |
| Antenna keep-out | **0 tracks / 0 vias** in the strip x 70.3–79.9, y 128.9–137.9 (all layers, rule areas on the board) |
| Wing-link census (from board pads) | J2 and J3 both 14/14 as designed: pin 14 = HALL_3V3, pin 8 = MUX_EN0 (J2) / MUX_EN1 (J3), pins 2/4/6 = MUX_OUT_C/B/A, pins 9/10/12 = MUX_A2/A1/A0, odd pins GND, MP no-net — identical signal content to the wireless Matrix/Wing definition |
| Outline delta vs Rev.10 | **0** — Edge.Cuts 14 segments equal as undirected edges (endpoints match to 0.001 mm); mounting holes at Rev.10 positions |
| Far-Wing rail budget | On-board HALL_3V3 copper to J2.14 ≈ 0.09 Ω (55 mm of 0.30 mm track) → ≈2.5 mV at the 28 mA design burst; FFC lane at the inherited 1.30 Ω acceptance limit adds 36.5 mV; total ≤ 39 mV against the ≤50 mV class budget (Stage 1 basis). Lane acceptance unchanged |

DRC residue classes not listed above: silk_over_copper 13,
silk_edge_clearance 4, silk_overlap 3 (cosmetic, donor-inherited
silk), track_dangling 1 (MUX_EN1 inner stub, electrically inert),
hole_to_hole 0 after duplicate-via removal.

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

Module at (75.1, 124.85) rot 90 in the Stage 1 south-west pocket,
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
2. **Pin swaps for escape** (design.py, schematic regenerated,
   ERC 0): BTN pin 34 → pin 47 (P0.23); ADC_C pin 44 → pin 42
   (AIN7 — pin 44 is uniquely blocked by functional pad 45);
   PAD_DR pin 29 → pin 50 (P1.06). All are firmware-visible
   only; no signal-content change.
3. **Module GND pads U1.7 / U1.14 / U1.18 are not plane-tied
   on the board.** The module's 10 GND pads are one internal
   ground; the other 7 are plane-tied (incl. three 0.45–0.60
   hand taps). The three remaining pads sit in escape funnels
   where every via/stub attempt fouled a neighbour net
   (attempts recorded in the runtime notes). Disposition:
   grounded through the module's internal common ground.
   Revisit with the official CAD (deviation 1), whose pad
   geometry may open a funnel.
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

## Draft adoption line (for PO, at the adoption gate)

**D-057 (draft):** Wireless Main layout (Issue #292) adopted as
the wireless Main baseline: ISP1807-LR module (D-056), Rev.10
outline unchanged (USB via EZmate daughterboard — the stocked
Fly can serve; outline delta 0), power tree per Stage 1
(TPS63070 at 3.3 V, diode-OR USB, TPS22919-switched HALL_3V3
and trackpad feeds, gated battery divider), SWD pads (TC2030
class) for the PCA10056 Debug Out. CONDITION: the derived
ISP1807-LR footprint (deviation 1) must be replaced with
Insight SiP official CAD and the module-field gates re-run
before any fabrication order; the manufacturing package is
DRAFT / NOT FOR ORDER until then.
