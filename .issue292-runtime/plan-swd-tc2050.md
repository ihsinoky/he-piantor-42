# Issue #292 wireless Main — SWD-ONLY respin (TC2050) — plan

PO decision 2026-11-20: convert the SWD pad field to TC2050.
Outline extension / JBATT relocation is DEAD (margin gate, see
margin-budget.md: north diagonals face the Wing boards across a
2.00 mm FFC channel; N-TAB region is 100% Wing board). JBATT
stays south; the case-side cable fix goes to Issue #296.

Branch: issue-292-wmain-rev2 (tip 3f3d8240f, margin commits on top
of the D-058 record chain). Tree:
hardware/kicad/qualification/issue-292-wmain/
Baseline board SHA-256: 260726192947a090... (edge-fixed D-058)

## Scope — ONLY the SWD field changes

- JSWD today: TC2030-IDC-NL_Pads at board (113.5, 136.2), 6 SMD
  pads 3x2 @1.27, pad D0.787: VTref=SYS_3V3, SWDIO, RESET_N,
  SWDCLK, GND, NC. No SWO. NO alignment holes (maker's TC2030-NL
  footprint has 3x D0.99 NPTH) — deviation recorded in study E.1.
- New: Tag-Connect OFFICIAL TC2050 footprint (maker's published
  spec/CAD, not derived), centre board (111.5, 136.2) per the
  margin round's desk verification: field X 108.57..114.43,
  Y 135.17..137.23 contains ONLY JSWD's own 4 escape tracks
  (SYS_3V3 / SWDIO / SWDCLK / RESET_N); RPD2/RPD3 clear ~3.1 mm;
  head body clears ~1.25 mm. Smallest shift from that centre if
  the official geometry forces one; report any shift.
- Mapping MUST follow the TC2050-IDC cable's fixed pin order
  (maker's footprint/cable datasheet) so DK debug-out (10-pin
  1.27 Cortex) -> TC2050-IDC-NL -> board works with NO adapter.
  Unused pins (SWO etc.) = NC or GND exactly per maker guidance,
  cited. Signals unchanged; no SWO net exists or is added.
- HARD INVARIANTS: outline byte-identical; JBATT + all else
  unmoved; module fine-field untouched; Wing census untouched.
  Anything outside the field needing change -> STOP + report.

## Stages

0. [ ] this plan + checkpoint commit
1. [ ] Baseline gates re-run on UNMODIFIED board: containment,
       ERC, DRC (JSON, full violation list saved for the diff)
2. [ ] Official TC2050 footprint obtained from Tag-Connect
       (datasheet/CAD), provenance saved; KiCad footprint built
       from it verbatim (pads + alignment/retention holes)
3. [ ] Symbol/schematic: JSWD pins remapped to the TC2050 pad
       numbers (part of the field definition); ERC stays 0
4. [ ] Board edit: swap footprint at (111.5, 136.2), re-route
       the 4 escapes to their existing nets, nothing else moves
5. [ ] Re-verification: containment PASS; ERC 0; DRC diff vs
       baseline list (no new classes; deltas itemised;
       unconnected = exactly the 2 known GND items); pad-level
       audit vs the maker's file (count/positions/holes, max err);
       case-frame position + accessibility line
6. [ ] Gerbers + manufacturing package regenerated; BOM delta
       stated (expected: none — pad field, no part); REPORT
       gains a respin section
7. [ ] Push + Draft PR (title: SWD TC2050 respin; body: cable
       chain, margin-gate record, gate deltas, D-061 pending,
       quote re-run = order-stage item). NO order placed.

Adoption = D-061, recorded by PMO after PO review. This worker
does NOT write the decision.
