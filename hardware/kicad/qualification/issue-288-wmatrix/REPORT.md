# Issue #288 Stage 2 — Wireless Matrix evaluation board: implementation report

**Status: DRAFT — for PO review. NOT FOR ORDER.**
Board: `wmatrix.kicad_pcb` (this directory), SHA-256
`5baf83c84f938b4acd787bd2694bd3b6434984dcc2c31410396b3081a113d6e7`.
Design source: Stage 1 study (`.issue288-runtime/wmatrix-design.md`),
frozen design table in `.issue288-runtime/plan.md` (Stage 2 section).

## 1. Design summary

The Rev.3 Matrix field (18 sites, two pitches) is carried over unchanged
and re-sensored for the wireless line (D-049):

- **Sensors:** 18x TMAG5253BA3 (TI X2SON-4, DMR land pattern per TI
  drawing DMR0004A: lands 0.22 x 0.40 mm, pin columns ±0.25, rows ±0.70,
  thermal pad tied to GND and soldered). Hall element is package-centred,
  so the Rev.3 site centres are the sensing centres. West section
  16 mm pitch 3x3 (x = 50/66/82), east section 17 mm pitch 3x3
  (x = 117/134/151) — the MS4 pitch decision's evaluation vehicle.
- **Multiplexing:** 3x TMUX1208PWR (groups A/B/C by column pair, as
  Rev.3). Sensor i of a group sits at MUX address i (pins S1..S6);
  address 6 (S7) is tied to GND (offset reference) and address 7 (S8)
  to REF_RAIL = HALL_3V3 / 2 via one shared 10k/10k divider, so firmware
  can correct offset and the LDO-rail vs ADC-reference difference.
  The sensors' EN pins are driven per group (EN_A/EN_B/EN_C); the MUX
  EN pins are tied to the rail (always enabled).
- **MCU:** socketed Seeed XIAO nRF52840 (D-052), hand-fitted after PCBA.
  Frozen pin map: MUX outputs A/B/C -> D0/AIN0, D1/AIN1, D2/AIN4;
  address A0/A1/A2 -> D6/D7/D8; EN_A/EN_B/EN_C -> D9/D10/D3;
  D5 -> status LED; D4 spare (NC). The XIAO 3V3 pin is NC by design
  (separate regulator domains; the REF_RAIL channel exists precisely
  to calibrate that difference). Antenna end faces the south edge,
  with a copper keep-out under the antenna on both layers.
- **Power:** one input node VIN_SRC fed by the board USB-C (bench
  primary; CC1/CC2 5.1k to GND, D+/D-/SBU NC) **or** the NiMH pack on
  J_BATT (JST XH 2-pin) — one source at a time, as the study specifies.
  AO3401A P-MOSFET reverse-polarity protection -> VIN -> AP2112K-3.3
  -> HALL_3V3_SRC -> 0R shunt position (R_SHUNT, current-measurement
  point) -> HALL_3V3, the dedicated sensor rail (sensors + MUX VDD).
- **Measurement access:** all 25 test points from the study are placed
  (6 raw sensor TPs at the donor positions, MUX outputs, address lines,
  rail north/east, per-group EN, VIN_SRC, VIN, 3V3_SRC, REF, 4x GND).
- **Board:** 128 x 80 mm outline (Rev.3), 2 layers, 1.2 mm, signal
  0.10 mm / power 0.30 mm, clearance 0.10 mm, via 0.60/0.30 mm.
  Native KiCad schematic (`wmatrix.kicad_sch`, generated from the
  design data in `.issue288-runtime/s2_design.py`) — the Matrix line's
  inherited JITX no-schematic gap is closed for this board.

## 2. Gate results (all from the placed board data)

| Gate | Result | Evidence |
|---|---|---|
| DRC severity-all | **0 errors, 0 unconnected**, 105 warnings | `drc-s2.json` |
| ERC (native schematic) | **0 violations** | `erc-s2.json` |
| Via-pad audit, different-net | **min 0.1002 mm** (floor 0.10); 0 sites < 0.100; 14 sites < 0.125 target | `via-audit-s2/via-pad-diffnet.json` |
| Field coordinates vs Rev.3 | **max deviation 0.0000 mm** over 18 sensors | `verification-s2.json` |
| Channel assignment | **18/18 + 3 reference rows extracted from placed pads, 0 errors** | `verification-s2.json` |
| Schematic <-> board parity | **260/260 pins, 0 mismatches** (independent netlist export) | `s27_parity.py` run |
| Design-table parity | **0 mismatches** | `verification-s2.json` |
| Hall-rail droop (burst) | **worst 13.66 mV nominal / 16.83 mV at width -20%** (budget 50 mV; worst sensor U_HC0; loads 18x 5 mA + 3x 0.1 mA + divider 0.165 mA) | `rail-droop-s2.json` |
| TMAG5253BA3 stock re-observation | see §4 | — |

DRC warnings (105, none are errors): silk_over_copper 28,
hole_to_hole 32, via_dangling 25, track_dangling 10, copper_sliver 6,
holes_co_located 4. The dangling items are same-net stubs left by the
routing process; they are electrically inert. Silk over copper is the
donor board's inherited class.

Assignment table (extracted from placed pads; full rows in
`verification-s2.json`): group A sensors U_HA0..A5 -> U_MUXA pins
4,5,6,7,12,11 (addresses 0..5), output MUXA_OUT -> XIAO pad 1
(D0, AIN0/P0.02), EN_A -> XIAO pad 10 (D9). Group B -> U_MUXB, output
-> pad 2 (D1, AIN1/P0.03), EN_B -> pad 11 (D10). Group C -> U_MUXC,
output -> pad 3 (D2, AIN4/P0.28), EN_C -> pad 4 (D3). Address lines
A0/A1/A2 -> XIAO pads 7/8/9 (D6/D7/D8). Per group: address 6 -> GND,
address 7 -> REF_RAIL, MUX EN (pin 2) -> HALL_3V3, MUX VSS (pin 3)
-> GND, sensor EP (pad 5) -> GND.

## 3. Deviations and disclosures

No deviation from the Stage 1 study's architecture, field, or
measurement-access list. The following implementation-level items are
disclosed:

1. **TMUX1208 VSS (pin 3) tied to GND.** The Rev.3 donor left pin 3
   unconnected; the datasheet's single-supply hookup ties VSS to GND.
   This follows the frozen design table (it is a deviation from the
   donor board, not from the study).
2. **Via-pad minimum is at the floor.** The different-net minimum is
   0.1002 mm (GND via at KiCad (120.15, 123.55) vs U_MUXC pin 11,
   H_C5_RAW) — above the 0.10 mm floor but with effectively no margin,
   and 13 further sites sit between 0.103 and 0.120 mm (target 0.125).
   All sites are listed with coordinates in
   `via-audit-s2/via-pad-diffnet.json`. Per the PO yardstick this is a
   risk to weigh at adoption, not a pass to celebrate.
3. **One 0.10 mm rail neck.** The MUX-row link C_MUXB pad 1 ->
   U_MUXB pin 2 (the MUX EN tie) is routed at 0.10 mm instead of the
   0.30 mm power width because the MUX pin-field channel admits no
   more. It is a MUX-only branch (<= 0.1 mA class, ~0.04 ohm), not on
   any sensor feed path; the droop gate above already includes it.
4. **One tight track channel.** H_B3_RAW threads between the EN_B via
   at (97.12, 113.45) and a MUX_A2 track at x ~ 97.585 with ~0.115 mm
   clearance on both sides — above the 0.10 mm floor, below the
   0.125 mm target.
5. **J_BATT is hand-fit.** The JST B2B-XH-A (LF)(SN) footprint is
   authored from the JST catalogue, but its LCSC code could not be
   verified at package time (no project precedent; the LCSC search
   route failed and was not retried). It is therefore excluded from
   BOM/CPL and listed as hand-fit in FABRICATION.md, keeping every
   BOM line mapped to a verified LCSC code.
6. **Same-net via-on-pad junctions exist** (e.g. stitching vias on
   test-point pads, a via on the J_BATT pad). The donor Rev.3 audit's
   all-net criterion counts these as overlaps (82 vias); the gate's
   different-net form is what §2 reports. No different-net overlap
   exists, so no POFV is required.
7. **Audit tooling note.** The donor's `audit-via-pads.py` asserts on
   ROUNDRECT pads (the TMAG lands); the run used a local copy extended
   for ROUNDRECT with the sharp-rect approximation, which
   underestimates distance to the real corner-cut copper — i.e.
   conservative for a floor audit (`.issue288-runtime/s31_audit.py`,
   different-net filter in `s31_viapad_diffnet.py`).

## 4. TMAG5253BA3 (C22401868) stock re-observation

Named gate from the study (stock fell 6,314 -> 1,126 on 2026-11-19).
Re-observation at package time (2026-11-19, this session):

- Web search surfaced no LCSC/JLCPCB product page for the part.
- tscircuit's JLCPCB library index (jlcsearch, queried
  2026-11-19 01:04 UTC) lists C22401868 / TMAG5253BA3IQDMRR with
  orderable price breaks ($0.5491 @ 1-9 down to $0.3472 @ 1000+) but
  **exposes no stock figure** (stock: null; category "Global Sourcing
  Parts").
- The LCSC API route is bot-blocked (recorded at Stage 1).

So a fresh numeric count could not be obtained through the available
routes. The last numeric observation stands at **1,126 pcs (Stage 1,
2026-11-19)** = 62 boards' worth, far above the gate's blocker
threshold (stock < 10x the per-board need of 18 = 180). The part
remains listed and orderable. **Recommendation: re-check the numeric
stock on the JLCPCB quote screen before any order** — the quote
handoff (`manufacturing/quote-handoff.md`) says the same.

## 5. Manufacturing package

`manufacturing/`: gerbers + drills (`gerber/`), `BOM-jlcpcb.csv`
(54 placed parts, 12 MPN groups, every line a verified LCSC code;
TMAG5253BA3IQDMRR character-exact, C22401868), `CPL-jlcpcb-gerber-frame.csv`
(gerber frame: Mid X = KiCad X, Mid Y = -KiCad Y, top, KiCad rotation),
`FABRICATION.md`, `quote-handoff.md` — all marked **DRAFT / NOT FOR
ORDER** per the #267 conventions. Hand-fit: XIAO module and J_BATT.

## 6. Draft adoption line (for the PO's decision record)

> D-053 (draft): Adopt the Issue #288 wireless Matrix evaluation board
> (this tree, board SHA-256 5baf83c8...) as the D-049 evaluation
> vehicle: DRC 0 errors / 0 unconnected, ERC 0, field deviation
> 0.000 mm vs Rev.3, via-pad different-net minimum 0.1002 mm (at the
> floor; 14 sites below the 0.125 target, disclosed), Hall-rail droop
> worst 16.83 mV at width -20% vs the 50 mV budget. Manufacturing
> package is DRAFT / NOT FOR ORDER; ordering remains a separate PO
> gate, preceded by a numeric TMAG5253BA3 stock re-check at quote
> time and the D-049 bench evaluation plan.
