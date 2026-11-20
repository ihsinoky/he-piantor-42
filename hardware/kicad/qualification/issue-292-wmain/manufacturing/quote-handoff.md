# Wireless Main — JLCPCB quote handoff (D-058 ADOPTED 2026-11-19; order NOT placed)

Upload together: a zip of this directory's `gerber/` contents,
`BOM-jlcpcb.csv` and `CPL-jlcpcb-gerber-frame.csv`.

**Status:** the wireless Main was **adopted as D-058** (PO decision
2026-11-19). **No order has been placed** — ordering is a separate
PO gate. Final board SHA-256
`260726192947a0903e6e3a9268877f3b77868542bcaec29d4777eaa49f9b0689`
— this **supersedes** the D-058-adopted board file
(`509e52a7…`, which had copper crossing the board outline at the
west dent; fixed by the edge-fix round, see REPORT deviation 13;
configuration unchanged). Unconnected items **2**, both GND and
both item-dispositioned in REPORT deviation 13 (CVCC2.2 pad;
module GND pads U1.14+U1.16 as one pair); all signal nets are
single-component. Outline identical to Rev.10 (the PO-authorized
outline expansion was not needed, 0.00 mm used). The gerber zip
in this directory was regenerated from the fixed board.

**Quote obtained 2026-11-19 (quote only, cart left empty):**
partial total **USD 76.81** (PCB $8.00 + PCBA $68.81) for the 34
items selectable in the quote flow. Adding U1 at the pre-order
price below gives a full-equivalent of **≈ USD 139 / 5 boards
excl. shipping and tax**. (This quote was run against the
superseded board file; the edge-fix changed routing only —
outline, parts and CPL are unchanged — so the figures are
expected to carry, but the quote must be re-run on the fixed
board's package at order time regardless.)

## ⚠ Order-stage DFM note — 0.05 mm module field (D-057)

The ISP1807-LR module field (rule area MODULE_FIELD_FINE,
11.6 × 9.85 mm = 114.26 mm² around the module at board coords
x 69.3–80.9, y 119.05–128.9) is routed at the **0.05 mm class**
under design decision D-057. Measured minima inside the field:
track width 0.050 mm, track–track 0.066 mm, track–pad 0.046 mm
(one pair, against an unconnected pad; re-measured 0.0457 mm),
via-to-copper 0.050 mm. The rest of the board is at the D-019
rules (0.10/0.10 mm).

At the 2026-11-19 quote, the JLCPCB quote flow accepted the
gerbers silently at the standard price, and the standalone
JLCDFM tool flags the fine field as "Danger" — but it flags this
board's standard 0.10 mm features identically (its default
thresholds are conservative), so neither result confirms
manufacturability. **The fine field is confirmed only at the
post-order engineering review.** Treat that review as the real
DFM gate when an order is placed; a price/lead-time impact, if
any, will surface there.

## Final BOM state (order-prep round, 2026-11-19)

Both BOMs (55 designators / 32 consolidated lines) now carry
verified LCSC codes for every placeable line and agree
line-for-line. Codes assigned this round (all verified against
the listing/datasheet, stock observed 2026-11-19):

- RFB1 49.9k → **C23184**, RFB2 16.0k → **C4210** (quote-verified;
  the site auto-matches were a through-hole resistor and a
  USD 327 relay — never accept auto-matches on these lines)
- 1uF 0603 ×5 → **C15849** (Samsung CL10A105KB8NNNC, Basic)
- 22uF 0805 ×4 → **C45783** (Samsung CL21A226MAQNNNE, Basic)
- 10nF 0603 → **C1589** (Samsung CL10B103KB8NNNC)
- 6.8k ×3 → **C23212**, 4.7k ×2 → **C23162**, 1M ×2 → **C22935**
  (UNI-ROYAL 0603, Basic)
- Q1 2N7002 → **C8545** (JSCJ, SOT-23, Basic; pinout matches)
- DLED green 0603 → **C12624** (KENTO KT-0603G). **Polarity
  check at quote:** board pad 1 = anode, pad 2 = cathode;
  confirm the JLCPCB library pin 1 = anode, else set the CPL
  rotation for DLED to 180°.
- D1/D2 → **C255588** Nexperia PMEG4020ER,115. The "ER" suffix
  is the package variant: per Nexperia AN10808, **R = SOD123W
  (CFP3)** flat-lead; the P variant (SOD128, 4 mm pitch) does
  NOT fit this board's SOD-123 land. Land fit verified (toe
  overhang ≤0.05 mm at the tolerance corner only); pin 1 = K,
  pin 2 = A matches the board. Second source: TECH PUBLIC
  PMEG4020ER **C19268150** (the part the 2026-11-19 quote
  matched).
- JBATT → **C161690** JST BM02B-GHS-TBT(LF)(SN), GH top-entry
  2P 1.25 mm. Board land measured: 2 SMD pads 0.6 × 1.7 mm at
  1.25 mm pitch, outline 5.9 × 4.4 mm — fits the GH body
  (5.75 mm wide, 4.25 mm deep). Caveat: the board land has no
  reinforcement-tab pads (the JST recommended layout includes
  them), so retention is by the two signal solder joints only.
  The quote's auto-match (through-hole XH C19272845) does NOT
  fit — do not use it.
- **SW1 = DO NOT PLACE (hand-fit at bring-up).** The land is a
  generic 2-pad tact provision (pads 1.2 × 1.8 mm at ±1.6 mm,
  outline 5.2 × 3.0 mm), not a specific part; no stocked part's
  3.2 mm terminal pitch could be verified from a published
  drawing. Intended class: 3 × 4 × 2 mm 2-pin turtle tact
  (e.g. YIZHI YZA-009 C49108621) — verify against the physical
  part before any future placement.
- No-part rows (H1–H3 NPTH, JPAD FFC land, JSWD pads, TP1–TP5)
  stay codeless by design.

## U1 module sourcing options (ISP1807-LR-RS, LCSC C5264268)

JLCPCB/LCSC shelf stock is **0** (pre-order part). Choose at the
order gate:

1. **JLCPCB Pre-order (C5264268):** USD **12.2283 ea** observed
   2026-11-19 (= $61.14 / 5 boards), estimated lead ~28 days.
2. **DigiKey purchase + JLCPCB consignment:** DigiKey
   1786-1019-1-ND (cut tape) / 1786-1019-2-ND (tape & reel).
   DigiKey JP, observed 2026-11-17: stock 13,850; CT 50+
   ¥2,249.60, TR 500 ¥1,837.90; small quantities ≈ ¥2,000–2,300
   per piece excl. tax/shipping. Confirm JLCPCB consignment
   form requirements (reel/tray; a Digi-Reel may be needed for
   cut tape) at order time.
3. **Hand-fit fallback:** buy the module retail and solder at
   bring-up with the SWD/continuity procedure in
   FABRICATION.md.

## Order-stage checklist

1. Post-order engineering review = the fine-field DFM gate (above).
2. DLED polarity confirmation at the matching screen (above).
3. Decide the U1 sourcing path (above) before placing the order.
4. Re-verify stock for all coded lines on the order day; use the
   BOM codes — re-check every auto-match against them.
