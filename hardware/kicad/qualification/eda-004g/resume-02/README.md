# EDA-004G resume 02 — pre-route physical DRC STOP

Same branch/PR #86, clean start HEAD
`bf3d7eb56a2d8f82a52aff23e77761f36ee053be`, `2026-10-14T13:07:55Z`.
Prior STOPs, failed files and frozen tables are preserved and never promoted.

This fresh target uses `main-contract-v2.json`, fixed **before generation** from
the preserved source-geometry transcription and all 193 **raw official** pin
definitions, including inheritance. The public-cache fallback is not role truth.
Only AP2112K pin4's observed role differs from failed v1; its old failure stays.
Four symbols, their original correspondence and NC conditions were reused after
individual public API/structured-data verification. No default footprint reuse.

`auxiliary-contract-v2.json` is read-only historical **non-copper comparison**;
generation consumes fresh routing-disabled source. No old routed copper is input,
stripped or copied. Current source matches immutable commit/current main.

Results: four scoped models; raw ERC **0 violations**; individual 193 logical pins,
197 physical pads (167 required/30 NC), 2 NPTH, source poses/layers/outline and
three source-derived USB bond segments checked. Same-number shield lands are joined
by actual copper, not labels. All four Main-shaped synthetic fault cases detected.
557 visible auxiliary primitive parameters match the frozen comparison. Exact
native text glyph equivalence is **unqualified**, not certified by those parameters.

Terminal STOP at `13:40:11Z`: PCB DRC has **61 printing violations** (44 text height,
12 silk overlap,5 silk over copper). They are warnings in raw KiCad output and are
not excluded. Position-only changes cannot fix text-height violations. Defaults
were not suppressed and frozen print size/geometry was not changed to pass.
Core copper/hole/edge target DRC violations were0 in this baseline, but effective
0.20mm injection, DSN/SES and Main routing were **not entered**. Routes **0/0/0**.

`test-checker.py` creates synthetic verification data only, never PCB/router input.
Its coverage is this fixed two-layer geometry; unknown shapes fail, drills are
subtracted from copper, and ambiguous sub-resolution contacts fail. It is not an
accepted general checker or proof of routed-via/spacing qualification.

Library inputs were serialized with public sexpdata `pretty_print=True` without
semantic changes. Fixed KiCad public `PCB_IO_KICAD_SEXPR.FootprintSave` writes
native individual footprints; all49 are registered. The empty-library public
helper failure and original author code remain. Default CAD ref/value ink, absent
from native source, is hidden while every native visible label remains; no DRC
diagnostic rule was suppressed. Independent reader schema/numeric corrections are
logged without generated-file handpatches or oracle edits.

The disappeared tmp environment was re-prepared and hashed. This is **not** full
environment reconstruction qualification. Java/router were prepared but never run.
Time uses the unchanged six-hour cumulative **work frame**, conservatively charging
prior windows2.25h; waiting is separate. The old absolute wall cutoff was an
executor convention, not the Issue's work-hour deadline. No new six-hour allowance.

After STOP, only evidence verification/reporting/submission is permitted. See
[report](../../../../../docs/native-main-routing-qualification.md).

Large official library inputs and upstream Markdown with trailing whitespace are
archived byte-for-byte as gzip. `evidence/exact-archives.json` records original and
archive hashes; expand for read-only inspection, not automatic re-execution.
