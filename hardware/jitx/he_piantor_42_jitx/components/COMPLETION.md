# EDA-002C1 Component Completion Records

## Component task: AP2112K-3.3TRG1

**Task:** `component-ap2112`
**Primary source:** Diodes Incorporated AP2112, DS39724 Rev. 2-2 (June 2017),
pages 2 (SOT25 pin descriptions) and 14 (SOT25 outline and suggested pad
layout), https://www.diodes.com/assets/Datasheets/AP2112.pdf.
**Secondary references:** `parity/m1-parity-contract.json`,
`../sensor-test/bom.csv`, and permitted lookup-only `parts2jitx-lcsc C51118
--pinout`; all agree on VIN/GND/EN/NC/VOUT ordering.
**Footprint source:** JITX `SOT23_5` generator parameterized with the
manufacturer's SOT25 body, span, pitch, lead length, and lead width. The
SOT25 has no exposed pad.
**Interface notes:** Physical pin 4 is represented as the `NC` port and mapped
to pad 4. This task creates no M1 circuit, nets, reference-designator
identity, placement, or routing.

### Component check

```text
Source: Diodes Incorporated AP2112 DS39724 Rev. 2-2 (June 2017), pp. 2 and 14
Identity: AP2112K_3_3TRG1 — mpn "AP2112K-3.3TRG1"; manufacturer, U prefix,
          C51118 metadata, and datasheet URL set on the class
Pins: 5 ports / 5 physical pads — VIN, GND, EN, NC, VOUT all present; NC kept
Landpattern: SOT23_5 + SOTLeadProfile; 5 pads; body 2.70–3.00 x 1.50–1.70 x
             0.35–0.50 mm, span 2.90–3.10 mm, pitch 0.95 mm, lead
             0.35–0.55 x 0.10–0.20 mm from datasheet p. 14
Library defaults: JITX SOT-23-5 pad construction only; source dimensions are
                  explicitly supplied. Density level: C, installed default;
                  manufacturer states no IPC density preference.
Value / BOM: n/a (IC) — value is asserted unset in a JITX test
No-field walk: fixed 3.3 V / 600 mA regulator rating documented in module docstring
Provenance: NONE
Checks: unittest 2 passed; non-dry build status: ok via
        `uv run jitx build he_piantor_42_jitx.component_test_designs.AP2112K3V3TestDesign`;
        ruff format/check clean for touched files
Verdict: complete
```

## JITX code review — `he_piantor_42_jitx/components/power/`

**Reviewer:** jitx-code-review (same-model self-critique)
**Scope:** `power/diodes_ap2112k_3_3trg1.py`,
`component_test_designs.py`, and `tests/test_ap2112k_3_3trg1.py`
**Rule sources read:** `jitx` workflow rules, JITX architectural-patterns
guidance, and the JITX component-modeler guidance.

### CRITICAL

None.

### WARNING

None.

### NOTE

- `diodes_ap2112k_3_3trg1.py:54` uses explicit `PadMapping` even though
  declaration order would map correctly. This is intentional: the required
  test verifies each physical SOT25 pin-to-pad mapping directly.

### Summary

CRITICAL: 0 | WARNING: 0 | NOTE: 1

**Verdict (self):** ready-for-review
**Verdict (acceptance):** accept
**Notes:** Other manufacturer components are not accepted by this record; see
`../../component-sources.md` for their separate STOP evidence.

## Component tasks: TPS22919DCKR, TMUX1208PWR, DRV5055A3QDBZR, and ABM8-272-T3

**Tasks:** `component-tps22919`, `component-tmux1208`, `component-drv5055`,
and `component-abm8`.
**Primary sources:** TI TPS22919 SLVSEN5B p. 3 plus DCK0006A 4214835/D pp. 1-2;
TI TMUX1208 SCDS389C p. 3 plus PW0016A 4220204/B pp. 1-2; TI DRV5055
SBAS640C p. 3 plus DBZ0003A 4214838/F pp. 1-2; Abracon ABM8 revised
2020-07-29 p. 2. URLs and document identifiers are recorded in
`../../component-sources.md`.
**Footprint source:** JITX `SOT23_6`, dual-column `SOIC`, and `SOT23_3`
generators, respectively, parameterized from the TI package drawings; a
project-authored public JITX `Landpattern` with Abracon's recommended pads for
ABM8. No EasyEDA/LCSC or community footprint geometry was used.

### Component check

```text
Identity: TPS22919DCKR/C2149796, TMUX1208PWR/C494728,
          DRV5055A3QDBZR/C266128, and ABM8-272-T3/C20625731; literal MPN,
          manufacturer, refdes prefix, and datasheet URL are class metadata
Pins: 6/6, 16/16, 3/3, and 4/4 ports/pads; tests assert each explicit
      physical pin-to-pad map. TPS NC/QOD and TMUX NC are retained.
Landpattern: TI body/lead ranges are transcribed in the three generator calls.
             ABM8 has four 1.30 x 1.05 mm pads at 2.30 x 1.75 mm pitch,
             explicitly positioned and bottom-view mapped from Abracon p. 2.
Library defaults: generator pad construction only; all manufacturer package
                  body, span, pitch, lead-length, and lead-width inputs given.
                  The manufacturers state no density preference.
Value / BOM: n/a (IC/crystal); component values remain deliberately unset.
Provenance: NONE
Checks: targeted unittest 4 passed; non-dry builds status: ok via
        TPS22919TestDesign, TMUX1208TestDesign, DRV5055TestDesign, and
        ABM8TestDesign; ruff check clean for all new files.
Verdict: complete
```

## JITX code review — newly accepted EDA-002C1 components

**Reviewer:** jitx-code-review (same-model self-critique)
**Scope:** the four component modules above, their build harnesses, and
`tests/test_ti_m1_components.py` / `tests/test_abm8_272_t3.py`.
**Rule sources read:** `jitx/SKILL.md`, JITX architectural-patterns guidance,
the component-modeler guidance, and the JITX code-review checklist.

### CRITICAL

None.

### WARNING

None.

### NOTE

- **explicit-physical-map** at
  `power/texas_instruments_tps22919dckr.py:56`,
  `switches/texas_instruments_tmux1208pwr.py:69`,
  `sensors/texas_instruments_drv5055a3qdbzr.py:52`, and
  `crystals/abracon_abm8_272_t3.py:43` — explicit `PadMapping` is retained
  to make physical-pin verification direct; it is not a parallel model.

### Summary

CRITICAL: 0 | WARNING: 0 | NOTE: 1

## Reopened component tasks — RP2040, USBLC6-2SC6, TYPE-C-31-M-12, W25Q16JVUXIQ

**Task:** EDA-002C1 manufacturer-component completion candidate, 2026-10-03.
**Primary sources:** manufacturer package drawings and complete pin maps below;
resolved URLs and acquisition evidence are in `../../component-sources.md`.
**Footprint sources:** exact recommended manufacturer copper for RP2040/HRO;
manufacturer dimensions plus parameterized JITX SOT23_6/SON for ST/Winbond.
**Boundary:** five accepted components/tests preserved. No top-level M1 circuit,
placement, routing, DRC, manufacturing preparation, EVT-002 or D-014 changes.
No `hardware/layout/**`, EasyEDA, LCSC or community footprint geometry consumed.

### Component check — RP2040

```text
Source: Raspberry Pi RP2040 datasheet build 3184e62-clean (2025-02-20);
        printed p. 607 package, p. 608 Recommended PCB Footprint,
        p. 611 RP2040 QFN-56 package pinout, pp. 612-614 pin tables.
Identity: RP2040 — manufacturer Raspberry Pi, mpn RP2040, C2040,
          U prefix and official datasheet URL set and structurally checked.
Pins: 57 physical pads / 57 ports; all 30 GPIOs, six IOVDD, two DVDD,
      TESTEN, XIN/XOUT, SWCLK/SWDIO, RUN, ADC_AVDD, VREG_IN/VREG_VOUT,
      USB_DM/USB_DP/USB_VDD, six QSPI and exposed GND individually mapped.
      GPIO26 = physical 38 ADC0. No M1-only partial device or net assignments.
Landpattern: project-authored RP2040Landpattern using public SMDPad;
             56 perimeter pads + exposed pad; width .20, pitch .40,
             left/right length .875 and center magnitude 3.4375;
             top/bottom length 1.175 and center magnitude 3.2875;
             7.75 outer span, 5.40 row extent, 3.20 x 3.20 center GND.
             Manufacturer footprint supplied directly, not a generic QFN.
Library defaults: standard SMDPad mask/paste generation from SampleSubstrate;
                  copper dimensions explicitly supplied, no IPC density choice.
Value / BOM: n/a (IC) — value is None asserted.
No-field walk: 7 x 7 mm package, ADC aliases and TESTEN disposition in docstring.
Provenance: NONE; copper numbers trace to the manufacturer footprint.
Checks: 2 structural tests PASS; pyright 0 errors/warnings; real non-dry
        `uv run jitx build he_piantor_42_jitx.component_test_designs.RP2040TestDesign`
        status: ok. Full-suite and format/lint evidence below.
Verdict: complete manufacturer model; accepted candidate pending PMO.
```

### Component check — USBLC6-2SC6

```text
Source: STMicroelectronics USBLC6-2, DS4260 Rev 7 (December 2021);
        p. 1 Functional diagram (top view), p. 12 SOT23-6L mechanical data.
        https://www.st.com/resource/en/datasheet/usblc6-2.pdf
        Exact family PDF read through official web PDF reader; curl transport
        timeouts do not prevent manufacturer data verification. Reader extract
        cached in ignored .sources/st-manufacturer-reader.txt.
Identity: USBLC6_2SC6 — STMicroelectronics, USBLC6-2SC6, C7519,
          U prefix and resolved exact-part official datasheet URL.
Pins: 6 ports / 6 pads; 1 IO1_1, 2 GND, 3 IO2_1, 4 IO2_2, 5 VBUS,
      6 IO1_2 individually mapped and structurally tested; no exposed pad.
Landpattern: SOT23_6, RectanglePackage width E=1.50-1.75,
             length D=2.80-3.05, height A=.90-1.45 mm;
             SOTLeadProfile span H=2.60-3.00, pitch e=.95,
             SOTLead length L=.30-.60, width b=.30-.50 mm.
Library defaults: generator's IPC SmallGullWingLeads copper construction;
                  explicit density C, manufacturer states no IPC preference.
                  Generated lands .95 x .42 mm, column span 2.35 mm,
                  .95 pitch and all placements pinned by structural test.
                  ST's separate recommended lands are not claimed reproduced;
                  authorized manufacturer-dimensions-plus-generator method A.
Value / BOM: n/a (IC) — value is None asserted.
No-field walk: two data lines plus VBUS protection, no exposed pad in docstring.
Provenance: NONE; all package inputs from mechanical data; IPC lands identified.
Checks: 1 structural test PASS; pyright 0 errors/warnings; real non-dry
        `uv run jitx build he_piantor_42_jitx.component_test_designs.USBLC6TestDesign`
        status: ok.
Verdict: complete manufacturer model; accepted candidate pending PMO.
```

### Component check — HRO TYPE-C-31-M-12

```text
Source: HRO official product page 726 -> PDF Download -> four-sheet family
        drawing; exact PART NO. TYPE-C-31-M-12, dated 2020-12-08, PDF p. 4.
        Use Recommended P.C.B Layout (component side) and pin table on that
        sheet; source page/direct URL are in component-sources.md and module.
Identity: TYPE_C_31_M_12 — HRO, TYPE-C-31-M-12, C165948, J prefix, exact URL.
Pins: 16 contact terminals sharing 12 lands, plus four plated shell stakes;
      13 semantic ports explicitly map 16 copper pads (SHIELD maps all stakes).
      A1_B12/A12_B1 GND; A4_B9/A9_B4 VBUS; A5/B5 CC1/CC2;
      A6/B6 D+; A7/B7 D-; A8/B8 SBU1/SBU2; no electrical nets assigned.
      Two locating NPTHs are physical features, not fake electrical ports.
Landpattern: project-owned Landpattern/SMDPad/THPad/NPTHPad;
             8 narrow .30 x 1.14 lands at +/- .25/.75/1.25/1.75;
             4 wide .60 x 1.14 lands at +/- 2.40/3.20 mm;
             center y=1.07 from locator datum, height=1.64-.50;
             upper shell .90 x 2.00 copper / .60 x 1.70 plated slots;
             lower shell .90 x 1.70 copper / .60 x 1.40 plated slots;
             shell x=+/-4.325, rows y=.50/-3.68 (4.18 separation);
             2 NPTH diameter .60, x=+/-2.89, y=0.
             Drawing's PCB layout positional/dimensional tolerance +/- .05;
             copper authored at stated nominal dimensions, not invented ranges.
Library defaults: substrate mask expansion; plated stakes explicitly no paste;
                  copper and drill shapes supplied directly, no IPC density.
Value / BOM: n/a (connector) — value is None asserted.
No-field walk: body 8.94 x 7.35, 5A/20V, PCB edge y=-4.15 and pin functions
               recorded in docstring; M-12A/B/C not substituted.
Provenance: NONE; derived coordinates include explicit datum arithmetic.
Checks: 1 structural test PASS (all contacts, shell slots, NPTHs, maps);
        pyright 0 errors/warnings; real non-dry
        `uv run jitx build he_piantor_42_jitx.component_test_designs.HROTestDesign`
        status: ok.
Verdict: complete manufacturer model; frozen geometry differs (see manifest).
        Component-modeling PASS is not full M1 geometric-parity acceptance.
```

### Component check — W25Q16JVUXIQ

```text
Source: Winbond W25Q16JV Rev J (May 28, 2026), printed p. 5 pin map,
        p. 67 8-Pad USON 2x3x0.6-mm^3 (Package Code UX), pp. 72-73 ordering.
        Official index/download chain and exact PDF URL in component-sources.md.
Identity: W25Q16JVUXIQ — Winbond, literal exact MPN, C2843335,
          U prefix, official URL; UX/I/Q ordering verified from manufacturer.
Pins: 8 signal pads + exposed metal, 9 ports; exact map:
      1 CS, 2 QSPI_SD1, 3 QSPI_SD2, 4 GND, 5 QSPI_SD0,
      6 QSPI_SCLK, 7 QSPI_SD3, 8 VCC; exposed pad mapped separately to EP.
      No EP net assignment or assumption about internal electrical connection.
Landpattern: SON(num_leads=8), explicit density C, body D=2.90-3.10,
             E=1.90-2.10, A=.50-.60 mm; lead span D=2.90-3.10,
             pitch .50 BSC, L=.40-.50, b=.20-.30 mm.
             Exposed land .20 x 1.60, stated nominal D1 x E1;
             source D1=.15-.25 and E1=1.55-1.65 mm also recorded in manifest.
Library defaults: IPC SmallOutlineNoLeads generator copper construction;
                  explicit C, manufacturer states no density preference or
                  recommended PCB lands. Dimensions-plus-generator method A.
                  Actual signal lands .7118034 x .22, column span 2.7881966,
                  .50 pitch, positions and EP pinned by structural tests.
Value / BOM: n/a (IC) — value is None asserted.
No-field walk: 16 Mbit, 2.7-3.6V, -40..85C, QE=1 Q suffix documented.
Provenance: NONE; all package inputs from exact UX drawing; IPC lands identified.
Checks: 1 structural test PASS; pyright 0 errors/warnings; real non-dry
        `uv run jitx build he_piantor_42_jitx.component_test_designs.W25Q16TestDesign`
        status: ok.
Verdict: complete manufacturer model; frozen land choices differ (see manifest).
        Component-modeling PASS is not full M1 geometric-parity acceptance.
```

## JITX code review — four reopened component models

**Reviewer:** jitx-code-review (same-model self-critique).
**Scope:** `components/mcu/raspberry_pi_rp2040.py`,
`components/protection/st_usblc6_2sc6.py`,
`components/connectors/hro_type_c_31_m_12.py`,
`components/memory/winbond_w25q16jvuxiq.py`, `component_test_designs.py`,
`tests/test_remaining_components.py`.
**Rule sources read:** installed `jitx/SKILL.md`,
`jitx/references/architectural-patterns.md`, `jitx-component-modeler/SKILL.md`,
`jitx-code-review/SKILL.md`, and its `references/checklist.md`.

### CRITICAL

None in the final implementation. No reflected name navigation, string-keyed
construction model, protected framework access, mutable module-level model,
free-function mutation, dynamically defined JITX class or manual refdes.

### WARNING

None in the final implementation. The earlier property aliases were removed
after the real build detected duplicate structural ports. Port/pad inventory
accessors are now methods, and a real build verifies each final structure.

### NOTE

- **explicit-physical-map** at `mcu/raspberry_pi_rp2040.py:169` and
  `connectors/hro_type_c_31_m_12.py` (`PadMapping` in `__init__`) — dictionaries
  are keyed by actual Port objects, not synthesized strings. Rule citation:
  installed `jitx/SKILL.md`, structural-collection convention (referenced,
  not copied into this repository).
  Ownership check: each component owns its manufacturer physical map; its
  landpattern owns pads. Component callers use public pad members/methods.
  No framework internals or duplicated navigation algorithms are used.
- **source-parity-difference** at `connectors/hro_type_c_31_m_12.py:11` and
  `memory/winbond_w25q16jvuxiq.py` (landpattern definition) — source-grounded
  geometry differs from frozen M1 geometry. This is documented in the manifest
  and requires PMO reconciliation before full parity acceptance. No silent
  geometry substitution was accepted.

### Summary

CRITICAL: 0 | WARNING: 0 | NOTE: 2.
**Verdict (self):** ready-for-review.
**Verdict (component modeling):** 9/9 PASS / accepted candidate.
**Verdict (M1 geometry parity):** not established; explicit differences for PMO.

**Shared checks:** locked sync PASS; unittest discovery 12/12 PASS; separate
EDA-002C0 bootstrap graph-export test PASS; new-module pyright clean; ruff
format/check PASS; frozen `m1:verify` all checks PASS; `git diff --check` PASS.
The five accepted models/tests, frozen tscircuit source/verifier, layout tree,
parity contract, `uv.lock`, package/runtime versions and D-014 are unchanged.
EDA-002C2 is next / unblocked and remains unstarted; EVT-002 remains unstarted.
