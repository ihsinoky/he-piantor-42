# Fix round brief — wireless Main board (Issue #292), from the Codex cross-model review

## Background

A cross-model review (Codex, different model family) of the adopted wireless
Main board file (D-061, SHA-256 6dfbcb954e…) found one major defect plus
several smaller items. The PMO independently re-measured and CONFIRMED the
major defect. Full review report (evidence, coordinates, methods):
`~/workspace/projects/he-piantor-wmain-review/.issue292-runtime/codex-review-report.md`
— read it first; it is your defect list. Review scripts/data are in the same
directory (`codex-measure.py`, `codex-measurements.json`, `codex-drc*.json`).

Worktree: `~/workspace/projects/he-piantor-wmain-fix2`, branch
`issue-292-wmain-fix2`, base origin/main `d3c834d46`. Board tree:
`hardware/kicad/qualification/issue-292-wmain/`.

KiCad tooling: extracted runtime at
`~/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr`
(kicad-cli 9.0.9; pcbnew via system python3 with
`PYTHONPATH=$K/lib/python3/dist-packages`,
`LD_LIBRARY_PATH=$K/lib/x86_64-linux-gnu:$K/lib`). Note: this kicad-cli does
NOT apply `.dru` rules; verify geometrically. pcbnew zone API in this build:
`zone.GetFilledPolysList(layer)`.

## Verification invariants (mandatory)

1. Reproduce the problem before fixing it (for F1: demonstrate the short on
   the unmodified file with your own measurement first).
2. Distrust the first passing test — check it actually exercises the claim
   (for F1 the acceptance test must run on the SAVED file WITHOUT refilling:
   the defect existed precisely because earlier checks refilled a copy).
3. Do not stop at the edit — continue until verification is complete and
   evidenced, per item.

## Fixes to implement

- **F1 (MAJOR) Stale zone fill.** The saved In1.Cu GND fill predates the SWD
  respin: via annuli of RESET_N at (112.9, 133.75) and (108.3, 133.975) and
  SYS_3V3 at (100.5, 134.95) are covered by plane copper in the saved file
  and in the checked-in Gerber (shorts to GND). Refill ALL zones, save the
  board, and:
  - enumerate EVERY geometry change the refill makes anywhere on the board
    (not just the 3 vias — e.g. the JSWD guide-hole overlaps in the review's
    finding 2), with before/after evidence;
  - verify on the reloaded SAVED file: annulus coverage of the 3 vias = 0,
    DRC run WITHOUT refill (shorting items 0, unconnected = the known GND
    pair only), containment gate PASS, ERC 0;
  - regenerate the manufacturing Gerber bundle from the saved file, verify
    byte/geometry consistency, and verify the new In1.Cu Gerber no longer
    covers those annuli;
  - record the new board SHA-256.
- **F2 JBATT value text.** PCB + schematic value says `B2B-XH-A`; the land is
  JST GH (1.25 mm pitch) and the BOM buys BM02B-GHS-TBT. Correct the value
  text to the GH part on both files. Value text only — no connectivity,
  footprint, or land change. ERC must stay 0.
- **F3 Thickness field.** The .kicad_pcb general thickness says 1.600 while
  the stackup sums to 1.200 and FABRICATION.md specifies 1.2 mm. Set the
  general field to 1.200. Verify the stackup sum yourself first.
- **F4 FABRICATION.md prose.** It still calls JSWD "TC2030-class"; the placed
  footprint is TC2050 (D-061). Correct the prose.
- **F5 BOM duplicate.** The per-reference BOM lists JSWD twice (one obsolete
  placeholder entry). Remove the duplicate so the BOM matches the board's
  single JSWD; verify designator sets BOM↔board stay equal.

## Studies / dispositions (measure and propose; change only where stated)

- **S-A TC2050 routing keep-out.** The Tag-Connect drawing's contact-field
  rectangle is entered by 10 F.Cu track segments; closest foreign pair
  0.091 mm vs the drawing's 0.508 mm guidance. Assess the physical
  consequence against the real plug (TC2050-IDC) and the project's own jig
  geometry. IF the foreign tracks can be cleared from the rectangle by
  re-routing strictly inside the SWD work box without moving any pad, via,
  or hole and without touching the field geometry, do it and re-run all
  gates. Otherwise leave routing untouched and write a disposition proposal
  (accept-as-deviation with reasons, or a scoped re-route plan).
- **S-B Trackpad keep-out definition.** Resolve the definition question:
  find the trackpad keep-out as actually defined in the board file (rule
  area) and its intended centre from the case frame (trackpad island centre
  shell (0,48) in the case study frame; the D-053 record). Measure the JSWD
  pads' relation to BOTH definitions and state precisely which definition
  the Stage 2 "0 violations" gate used and whether the D-061 file violates
  the intended one. Disposition proposal only — do NOT move JSWD.
- **S-C Outside-field clearances.** Produce the definitive different-net
  sub-0.100 mm pair list outside the module fine field under the project's
  own definitions (D-019: 0.10 width/clearance). Specifically verify the
  review's three named items: JPAD fanout via-pad 0.0625 (record says
  0.0627, dispositioned), east-side GND via (129.543, 127.33) → RPD1.1 at
  0.075000, PAD_SDA via → JPAD.5 at 0.099249. Classify each: known &
  dispositioned / new. No routing changes in this round for S-C items;
  new items get a disposition proposal.
- **S-D Via census.** Definitive census: project definition (KiCad
  via_diameter check) vs diameter-or-drill-below-0.60/0.30 count (review
  says 23). Itemise any via with drill < 0.30 mm (manufacturing relevance)
  with location and net.
- **S-E Co-located vias + duplicate UUIDs.** The review found 3 sites where
  two vias share a drill centre and 13 routing UUIDs reused by two records.
  Report whether the co-located pairs are same-net (intentional stitching)
  or different-net; disposition note only, no change.

## Out of scope

- No outline change. No module/J2/J3/JPAD footprint change. No netlist change
  beyond F2's value text. No changes to any other board.
- Silk-to-edge / mask-bridge items from the review: itemise in your report
  only; do not edit silkscreen in this round.

## Deliverables

1. The fixed tree on branch `issue-292-wmain-fix2`, checkpoint commits per
   fix, pushed.
2. `.issue292-runtime/fix-report.md`: per item (F1–F5, S-A–S-E) — what was
   done or proposed, before/after measured values, methods, new SHA-256,
   and the full gate results on the final SAVED file (DRC without refill,
   ERC, containment, unconnected set).
3. A REPORT.md fix-round section appended in the board tree (producer
   record), and a DRAFT D-063 decision text in `.issue292-runtime/d063-draft.md`
   (re-adoption of the fixed file, superseding the D-061 board file only;
   configuration unchanged).
4. Draft PR opened against main (title: Issue #292 fix round), with a
   comment on Issue #292 summarising the round.
5. One line appended to
   `~/workspace/goals/he-piantor-42-keyboard-pmo/GOAL.md`.

Working style: write a short plan note first; checkpoint-commit after each
fix; keep scripts and logs in `.issue292-runtime/`; if a fix cannot be made
without breaking an invariant above, STOP that item, record the evidence,
and continue with the others.
