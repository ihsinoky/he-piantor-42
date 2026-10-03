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
