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
