# EDA-004D — bounded converter repair

**CONVERSION_BLOCKED — D1_FOOTPRINT_LIBRARY_ID_COLLISION.** The three known
transformations now pass limited independent object reconciliation, but complete
pre-route acceptance fails. Two different footprints reference `tscircuit:chip`;
the upstream library extractor retains only the first same-named entry. Faithful
library configuration requires an additional footprint identity/export repair.
Issue [#77](https://github.com/ihsinoky/he-piantor-42/issues/77) requires STOP on a
new conversion loss. Real KiCad ERC also still reports disconnected SIG pins.
Smoke routes initial/fresh **0/0**, Main **0**. No next Main evaluation, candidate
switch, backend adoption, Human Gate, merge or manufacturing approval is performed.

The [authority](../hardware/tscircuit/qualification/eda-004d/evidence/authority.json)
contains the actual Issue body. Initial cwd/origin/branch were correct, HEAD,
origin/main and remote main were `6684821a00bc2ebe368dcc78495d013eb5dd47d9`,
with one clean worktree. No applicable repository/ancestor AGENTS.md was found;
downloaded kicadts instructions were read. No branch cleanup or installation of
Codex was performed. Every starting tracked file is protected by SHA-256;
production tscircuit 0.0.2646, frontend qualification pins, earlier evidence,
designs, decisions and CI/workflows remain byte-identical. Only the new EDA-004D
root and this report change; existing historical status remains unchanged.

The [acceptance contract](../hardware/tscircuit/qualification/eda-004d/acceptance.md)
was written before repair/conversion. It retains every duplicate land and the
source local bond, distinguishes two intentional pre-route unconnected nets
from final required-unrouted=0, and requires real ERC, faithful libraries,
effective rules and independent final physical checks before any route.

The [patch](../hardware/tscircuit/qualification/eda-004d/converter.patch) changes
three files in an isolated source copy of converter **0.0.230**, Git
`8dee5b926f5db28800292b46b66a712c71aba055`:

- `AddFootprintsStage.ts` traverses explicit internal source-port connections
  when collecting net candidates. It does not merge different KiCad nets;
  contradictory net assignments and invalid/cross-component references fail.
- `getLibraryId.ts` gives component definitions and instances a shared,
  deterministic, component-specific identifier, avoiding equal-name assumptions.
- `createPinSubsymbol.ts` maps explicitly attributed source pins to KiCad types
  and rejects missing/conflicting semantics. Input/output/passive and supported
  power, bidirectional, NC and output-mode mappings have synthetic unit coverage.

Maintenance would require retaining these three source changes, reviewing
upstream net/schema/symbol APIs, and re-running identity/semantic/failure tests
on any upgrade. This is a qualification patch, not a permanent product dependency
replacement or upstream PR. It does not fix footprint identity, schematic
connection precision or library portability. No further fixes were attempted.

No existing `/tmp/eda004c` environment existed. Original source archive,
source/patch hashes, exact runtime/build locks and same-source kicadts
`f3ea106bdc65ca901e9b23255ad3be0bd2a624ab` build are recorded. npm lifecycle scripts
were disabled; runtime bundling uses the existing locked tsup 8.5.1 without
declaration generation. Node/npm are 24.21.0/11.19.0. KiCad **9.0.9** was recreated
by the existing isolated extraction procedure. No frontend regeneration, Bun
installation, DSN export, router download/launch or SES import was needed.
The unchanged EDA-004C corrected raw was replayed with commit/path/hash provenance;
it is historical input, not fresh generation. Commands, UTC times, numeric exits,
stdout/stderr and generated artifacts were saved before decisions. The final
evaluation script consolidates the two executed capture phases; this distinction
is recorded in `evaluation-sequence.json`.
The regenerated kicadts bundle/declarations exactly match the earlier preserved
raw; `deduplicated-artifacts.json` references those immutable commit/path/hashes
instead of storing another identical large copy. Whitespace-sensitive raw and
the new converter bundle are preserved losslessly compressed.

| Evaluation | Observed result |
| --- | --- |
| Source and limited PCB/schematic object parity | PASS: five electrical lands, duplicate GND networks, one NPTH, position/rotation/size/drill/plating/layers, 20 × 16 mm, two layers/1.2 mm, one 2 mm top GND bond at 0.20 mm, chip pin names/numbers/types and instance references |
| Explicit project fields | Default netclass 0.20 mm clearance/width, 0.60/0.30 mm via and five explicit project rules match; full effective precedence/DSN rules remain unqualified |
| Actual pre-route DRC | Two intentional unconnected records; zero violation errors, two footprint-library warnings; `shorting_items=0`, `solder_mask_bridge=0` |
| Actual synthetic ERC | Three errors: two `pin_not_connected`, one `pin_not_driven`; sixteen warnings: two unconnected endpoints, ten off-grid, four symbol-library issues |
| Libraries | FAIL: none configured; `tscircuit`, `Device`, `Custom` warnings retained. Different U_TX/U_RX geometry shares one footprint library ID; upstream deduplication confirmed by source inspection, not an executed library export |
| Converter unit tests | 15 checks PASS, including deliberate internal-net conflicts, invalid relationships and missing/conflicting electrical attributes |
| Independent saved-data checker | 13 fault replays detected on actual patched positive artifacts, with no generated-file correction |
| Initial / fresh / Main routing | NOT ENTERED / NOT ENTERED / NOT ENTERED; 0 / 0 / 0 attempts |

The historical GND short and solder-mask error disappear with correct pad net
inheritance; this does not establish complete DRC acceptance. Correct OUT/output
and IN/input types make the remaining disconnected source SIG meaningful:
KiCad reports the input is not driven. These connection/off-grid issues were
already observed in EDA-004C and remain unresolved. No warning is excluded or
credited PASS. No explicit schematic/PCB parity CLI flag was run. A real
intentional output/output ERC test is **NOT ENTERED** after STOP; metadata/unit
fault tests are not substituted for it.

The inherited checker has limited per-object coverage: it does not prove actual
schematic connectivity, footprint-library identity, full rule precedence or
physical copper islands/shorts/clearances. Extended read-only assessment exposes
the library identity collision; duplicate rail definitions are also outside the
historical chip-only comparison. Full physical checker qualification, missing-via
faults, DSN/SES/fabrication exports and byte/normalized fresh agreement are
**NOT ENTERED**. All initial/fresh final acceptance metrics are **null**, including
required unrouted, wrong-net physical copper, project-required material DRC and
source/rule parity. Router completion and CLI return code 0 are not acceptance.

The [replay procedure](../hardware/tscircuit/qualification/eda-004d/replay.py)
uses fresh explicitly named directories, retained converter source, unchanged
locks and raw. Its syntax and hashes are checked, but no clean full replay/fresh
confirmation is claimed. APT repositories remain an availability/dependency
closure reproducibility limit; installed package hashes are retained. STOP forbids
further EDA experiments in this execution.

Start was **2026-10-08 19:57:18 UTC** (first exact clock observation). The issue
uses a conservative **0.750 h AI effort estimate**, including reporting,
validation, commit/push/PR and CI reserve, against the 3 h ceiling. Continuous
session wall allowance is its basis, not measured active engineer-hours.
The prior known estimate **1.036 h** is carried forward: known cumulative
**1.786 h**, nominal remainder **14.214 h** under the original 16 h budget.
Prior unquantified reporting/review corrections, human time and fully unattended
time remain unknown/null; exact cumulative effort and exact remainder cannot be
certified. Observed process elapsed overlaps AI work and is not added again.
Experiment cutoff was predeclared with at least 30 minutes reserved for reporting;
the technical STOP occurred well before that cutoff.

Read-only validation checks patch/source/lock/raw hashes, protected starting
bytes, STOP chronology, zero attempts and null final metrics; fault replays and
`git diff --check` are reported separately from qualification. Current PR CI is
recorded in `evidence/ci-record.json` and the PR body: unchanged engineering path
filters skip product KiCad/layout/firmware jobs for this evidence scope. CI
success or SKIPPED is not qualification PASS. PO/PMO owns disposition of this
STOP and any separately authorized native-KiCad trial; no Main advancement is
supported by this result.

The first reporting validation rejected its own pending process record. Its
exit 1, raw traceback and v1 source are retained in `reporting-correction.json`.
The corrected validator permits only its own named active final capture; the
caller verifies that record after completion. This post-STOP reporting correction
does not launch another EDA experiment or change the technical classification.
