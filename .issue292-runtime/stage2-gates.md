# Issue #292 Stage 2 — ENTRY GATE RESULTS (2026-11-19)

Board work NOT started. Gate G1 failed as specified; per the Stage 2
brief ("if either FAILS, stop and report — do not improvise a module
swap") the implementation stops here and the decision returns to
PMO/PO. Gate G2 passed, with material corrections to the study.

## G1 — Module stock: FAIL (UNVERIFIED at every reachable channel)

Requirement: observe TODAY's stock for EYSKDNZWB / ED2840AA2 at 2+
channels, comfortably above prototype qty (5 boards + spares).

Observed 2026-11-19 (worker session, web search + page fetch):
- DigiKey (JP/US): no product/stock figure retrievable for either
  part number.
- Mouser: hosts the Kaga FEI datasheet in its manufacturer library
  (mfr library ID 3800) but no product page / stock figure could be
  retrieved.
- LCSC / JLCPCB: no listing surfaced for either part number
  (consistent with a Japan-domestic B2B module outside the LCSC
  catalogue; cf. Issue #288 where the LCSC API was bot-blocked).
- TME: no listing surfaced.
- Chip1Stop (the Kaga FEI route named in the brief): no product
  page retrievable via search in EN or JP.
- EYSKDNZWB eval board (EBSKDNZWB) shown OutOfStock by an
  aggregator (xonelec) — the only stock-shaped figure found, and
  it is for the eval board, not the module.

Positive context (NOT a stock observation): ED2840AA2 is a current
maker product — datasheet Ver.1.1 dated 2024-02-02, current Nordic
3rd-party module list, Japan MIC cert 005-103104 in the datasheet.
This is exactly the study's risk R1 state: UNVERIFIED, not observed
thin. But the gate as specified requires an observed figure, and
none exists. G1 = FAIL.

Decision options for PMO/PO (worker's list, not a choice):
(a) Accept the G1 risk and proceed: design for ED2840AA2, procure
    via Kaga FEI / Chip1Stop quote at order time, module hand-fit
    if JLCPCB cannot source it.
(b) Prove the channel first: sample purchase (1-5 pcs) before
    layout resumes.
(c) Invoke the study Section 4.3 fallback (MDBT50Q-1MV2 + north
    tab) as a recorded decision — its channels WERE observed in
    Stage 1 (DigiKey Marketplace 35, TME 88-176), at the cost of
    the outline change + D-053 antenna-home note.

## G2 — Model-transition pin compatibility: PASS (design basis corrected)

Design part = **ED2840AA2** (Kaga FEI), datasheet "ED2840AA1/AA2
Data Sheet" Ver.1.1, 2024-02-02, Control KM-AG-A223006 (maker's own
document, retrieved in full this session).

Compatibility EYSKDNZWB -> ED2840AA2:
- Same outline: Taiyo Yuden's own lineup document gives EYSKDNZWB
  9.6 x 12.9 x 1.3 mm MAX; ED2840AA2 datasheet: 9.6 x 12.9 x 1.3 mm,
  38-pin LGA.
- The ED2840AA2 datasheet's own high-voltage-mode reference
  circuit (Section 5.2.2) is captioned "EYS KDN" — the maker
  carries the EYSKDN reference design into the ED2840 document.
- Independent cross-check: a published EYSKDNZWB design (TI E2E
  AGC_IOT2D schematic) labels pins 1 GND, 12 P0.26, 13 GND,
  15 ANT, 16/17 GND, 18 NFC2, 20 VDD, 21 VDDH, 22 DECUSB,
  29 P0.31, 31 P0.03, 32 P0.29, 33 NFC1, 34 RESET — every one
  identical to the ED2840AA2 pin table (KM-BA-A223006). No
  conflicting pin assignment found anywhere.
- Japan certification carries: ED2840 MIC ID 005-103104 (datasheet
  Section 2.2 j-5).

ED2840AA2 pin table (38 pins, from KM-BA-A223006) — design basis:
1 GND(corner 0.55x0.8), 2 VBUS, 3 D-, 4 D+, 5 P0.07, 6 P0.08,
7 GND, 8 P0.01/XL2, 9 P0.00/XL1, 10 P0.04/AIN2, 11 GND(corner),
12 P0.26, 13 GND, 14 OUT_MOD (tie to 15), 15 OUT_ANT (tie to 14),
16 GND(corner), 17 GND(corner), 18 P0.10/NFC2, 19 SWDIO, 20 VDD,
21 VDDH, 22 DECUSB, 23 P0.15, 24 P0.05/AIN3, 25 P0.06,
26 P0.30/AIN6, 27 P0.27, 28 P0.28/AIN4, 29 P0.31/AIN7,
30 P0.02/AIN0, 31 P0.03/AIN1, 32 P0.29/AIN5, 33 P0.09/NFC1,
34 P0.18/RESET, 35 SWDCLK, 36 GND(center 2.8x1.5),
37 NC(corner), 38 NC(corner).
Land pattern (KM-AD-A223006): signal pads 0.4x0.8 (31), corner
pads 0.55x0.8 (6), center pad 2.8x1.5 (1); land = foot pattern.
Antenna rules (datasheet Section 10.1): no copper on any main-
board layer in the antenna routing-prohibited area, no metal in
the antenna space, GND pattern length >=30 mm recommended,
FR-4 assumed. OUT_MOD-OUT_ANT tie as short as possible.

CORRECTIONS to the Stage 1 study (material; apply when work
resumes):
1. **GPIO = 19, not 46.** ED2840AA2 block diagram: "GPIO (19)";
   Nordic's module list also says 19. The study's 46 was wrong
   (that figure belongs to the EB2840-class part). Budget
   re-check vs study Section 1.1: need 15 GPIO / 4 ADC.
   Available: 19 GPIO, all 8 AIN (AIN0-7 on P0.02/03/04/05/28/
   29/30/31). With the LF crystal fitted (below), 17 GPIO free
   >= 15. PASSES, with 2 spare GPIO.
2. **DCDC converter mode NOT supported** (datasheet block
   diagram note *1). The module runs the nRF52840 in LDO mode;
   any #284-model DCDC assumption for the radio must be
   revisited by whoever owns the runtime model. Not a layout
   blocker.
3. **32.768 kHz crystal is EXTERNAL** (P0.00/XL1, P0.01/XL2;
   reference circuit Section 5.2.1: FC-12M / SC-20S class,
   CL 9.0 pF). The study's "internal 32 kHz" claim does not
   hold for the orderable part. Design must fit the crystal +
   2 load caps (or accept RC LFCLK accuracy — crystal
   recommended; footprint it regardless).
4. Normal-voltage mode = VDD and VDDH both to SYS 3.3 V
   (Section 5.2.1) — matches the study's power tree. VBUS feeds
   only the USB regulator; DECUSB needs its decoupling cap per
   the reference circuit. VDD/VDDH/VBUS traces >0.5 mm wide
   (Section 11.2.1); ~100 uF bulk near the module recommended
   for battery operation (Section 11.1).

## State
- No board files created. No tree hardware/kicad/qualification/
  issue-292-wmain/ yet.
- This file + the Stage 2 plan are the only Stage 2 outputs.
- Awaiting PMO/PO decision on G1 (options a/b/c above).
