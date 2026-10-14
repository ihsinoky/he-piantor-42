# EDA-004F — headless schematic qualification

**SMALL_SCHEMATIC_CANDIDATE_PASS**, proposed evaluation record in [Draft PR #84](https://github.com/ihsinoky/he-piantor-42/pull/84) under
[Issue #83](https://github.com/ihsinoky/he-piantor-42/issues/83).
The configured small schematic passed KiCad **9.0.9** ERC and independent
pin/connectivity reconciliation; both intentional faults were detected, a resistor
value change was isolated, and regeneration from an empty directory preserved
semantics. **Initial acceptance was FAIL:** six library-configuration warnings.
The retained configuration correction yielded zero errors, warnings or exclusions
without changing the schematic, contract, library, generator or ERC severities.
This qualifies a candidate for this small schematic path only. Main, PCB transfer,
routing, spacing, manufacturing, method adoption and Human Gates are **NOT ENTERED**.
PMO reviews the evidence; PO decides subsequent direction. No further experiment
is authorized by this report.

## Authority, history and first hypothesis

Start **2026-10-13 22:13:36 UTC**, cwd `/workspaces/he-piantor-42`, branch
`eda-004f-headless-schematic-qualification`, HEAD
`3ed5558855c7d95951ea4a728f755707061279b4`, clean worktree: all matched PO's
instruction. The [latest Issue snapshot](../hardware/kicad/qualification/eda-004f/evidence/issue83.json)
was read with repository workflow, path history, D-014–D-018, EDA-004E report,
alternate-backend plan, project status and Dashboard README. No AGENTS.md was found.

Earlier direct KiCad work repeatedly required format repairs (PO supplement);
original writer commands/root causes remain partly unknown. EDA-004E proved
small-board PCB I/O/parity, but stopped at two unexpected DRC warnings and did not
identify a public pinned headless schematic authoring path. These facts and all
prior decisions/evidence are retained. The changed mechanism here is an existing
external schematic library's public creation/save API, followed by actual pinned
KiCad inspection and an independent expected pin table. First falsifiable
hypothesis: KiCad 9.0.9 reads its unmodified generated schematic and correctly
interprets the contracted pin roles and connectivity. No own schematic writer,
fork, private API, post-generation string replacement or GUI was used.

## Fixed source, environment and maintenance boundary

[kicad-sch-api source](https://github.com/circuit-synth/kicad-sch-api/tree/505bca23e91cf3fa6e3b66976e529e775eada3ba)
is pinned to **505bca23e91cf3fa6e3b66976e529e775eada3ba**, retained as a
[Git archive](../hardware/kicad/qualification/eda-004f/evidence/library-source.tar.gz).
Distribution metadata is **0.5.6**; module `__version__` says **0.5.5** and
`VERSION_INFO` says 0.4.0. The commit is the authority, not these inconsistent
labels. License: MIT, retained with source. This is **external**, not a KiCad
official API. README claims KiCad 7/8 compatibility; source defaults and reference
files mention 9.0, but inspected upstream CI does not install a 9.0.9 executable.
Those claims/references were not counted as qualification. Full upstream test
suite was not run.

Public calls used: `SymbolLibraryCache(enable_persistence=False)`,
`discover_libraries`, documented public `set_symbol_cache` (also used by upstream
tests), `create_schematic`, `components.add`, `get_component_pin_position`,
`wires.add`, `add_label`, `no_connects.add`, `save`. No library-internal fields are
accessed. [Research and open issue snapshot](../hardware/kicad/qualification/eda-004f/evidence/research.json)
record multi-unit detection/grid limitations, mirror/custom-symbol roundtrip,
rotated-pin coordinates, global-label serialization and bounding-box reports.
These are upstream reports, not independently reproduced failures in this fixture.
The tested scope is single unit, rotation 0, official symbols and local labels.

Python **3.14.2** ran the library (actual version also in the install report).
Package requires Python >=3.10; its classifiers enumerate 3.10–3.12. The resolved
runtime dependencies were captured before first generation, with package versions,
download URLs and SHA-256 in the
[install report](../hardware/kicad/qualification/eda-004f/evidence/pip-install-report.json).
[requirements-lock.txt](../hardware/kicad/qualification/eda-004f/requirements-lock.txt)
records those exact distributions/hashes; the library itself is pinned separately
by its source archive. MCP/fastmcp and their broad dependency tree are installed
because upstream requires them; no server/provider is used. Isolated build used
upstream `setuptools>=68`/`wheel`: their exact temporary build versions were not
retained. Runtime fixture reproduction succeeded; a fully locked build/rebuild of
all environment dependencies is **not** established.

No previous `/tmp/eda004d` or `/tmp/eda004e` installation survived. The unchanged
EDA-004D installer prepared `/tmp/eda004f`, with evidence redirected into this
trial. Binary and binding probes identify **9.0.9**, package SHA-256
`b7e6d33867631dc44385067b703b4c39eadede2037a260790b19495fe17e43f0`.
Official `kicad-symbols 9.0.9~ubuntu24.04.1` came from the same PPA;
three complete official `.kicad_sym` files are retained unchanged inside lossless
gzip wrappers, with the
CC-BY-SA 4.0 license and design exception. Package/input hashes and CLI
configuration are in [preparation.json](../hardware/kicad/qualification/eda-004f/evidence/preparation.json).
APT dependency availability remains mutable. Capture unsets DISPLAY and
WAYLAND_DISPLAY; no virtual display/GUI or major-version switch was used.

## Frozen contract and independent inspection

[contract.json](../hardware/kicad/qualification/eda-004f/contract.json) and its
SHA-256 were frozen **before first generation**. The oracle was manually recorded
from official symbol definitions, independently of generated library outputs:

| Reference / definition | Pin → electrical role → expected connection |
| --- | --- |
| U1 / 74xGxx:74LVC1G04 | 1 NC/no_connect; 2 input/INPUT; 3 power_in/GND; 4 output/SIGNAL; 5 power_in/VCC |
| U2 / 74xGxx:74LVC1G04 | 1 NC/no_connect; 2 input/SIGNAL; 3 power_in/GND; 4 output/intentional NC; 5 power_in/VCC |
| R1 / Device:R, 10k | 1 passive/VCC; 2 passive/INPUT |
| R2 / Device:R, 1k | 1 passive/SIGNAL; 2 passive/GND |
| #FLG01 / power:PWR_FLAG | 1 power_out/VCC, declares supplied power |
| #FLG02 / power:PWR_FLAG | 1 power_out/GND, declares supplied return |

Six symbols / 16 pins, four named connections, three explicit NC markers.
Signal inputs/outputs and power types are preserved; only resistor pins are
passive. Flags describe the fixture's external supply intent, not a workaround
that disables electrical checks. R1 pulls INPUT up; U1 drives SIGNAL/U2 input;
R2 loads SIGNAL to GND. No product power design is implied.

KiCad XML export supplies part identity, values, library pin tables, actual
pin roles and net membership for **four physical parts / 14 pins**. KiCad omits
virtual power flags from PCB netlists. The independent generic S-expression
reader additionally checks all six source symbols/16 pins, wire endpoints/local
label connectivity and NC marker placement, including flags. It uses `sexpdata`
plus stdlib XML and does not import the generation library. Its geometry scope is
explicitly the unrotated stub/local-label fixture; no general schematic or PCB
connectivity verifier is claimed. KiCad's electrical ERC independently validates
supplied power and signal semantics.

## Individual outcomes and initial failures

| Trial | KiCad 9.0.9 result | Independent result / acceptance |
| --- | --- | --- |
| First normal generation/read/export | Generation/export exit 0; ERC exit **5**, six `lib_symbol_issues` warnings, electrical errors 0 | **Initial acceptance FAIL**, raw warning report retained |
| Same normal file, corrected configuration | ERC exit **0**, zero violations across errors/warnings/exclusions | Identity/value/pins/roles/nets/NC **PASS**, configured normal acceptance PASS |
| Required input U2.2 disconnected | ERC exit **5**, `pin_not_connected` and `pin_not_driven`, both at U2.2 | Source and XML detect U2.2 net loss; planned detection **PASS** |
| U2.4 connected to U1.4 on SIGNAL instead of NC | ERC exit **5**, `pin_to_pin` at both output pins | Source/XML detect U2.4 wrong net and lost NC marker; planned detection **PASS** |
| R1 10k → 12k | ERC exit **0**, zero violations | **PASS**, only R1 value changes; same identities/pins/roles/connections/NC |
| Normal regenerated from initially empty directory | ERC exit **0**, zero violations | **PASS**, identical normalized semantic record; raw file changes only UUID occurrences |

Every process command, cwd, environment, timeout, timestamps, exit status,
stdout/stderr and output artifact hashes is retained under
[evidence/processes](../hardware/kicad/qualification/eda-004f/evidence/processes/).
Raw streams are losslessly gzip-wrapped; recorded hashes apply to decompressed
bytes. Normal and fault schematics, XML, ERC JSON and reconciliation remain raw
outputs. Read-only raw/UUID-normalized diffs are retained (nonempty diffs losslessly gzip-wrapped): fresh has 58 UUID
occurrences per file and no other byte difference; value trial differs only in
the R1 value after UUID normalization. No schematic bytes were repaired.

Three preparation/configuration failures are disclosed in
[corrections](../hardware/kicad/qualification/eda-004f/evidence/preparation-corrections.json):
obsolete official GitHub master caused a symbol-download 404; the PPA package
uses `LICENSE.md` instead of the expected Debian `copyright`; standalone
schematic CLI did not use the neighboring project `sym-lib-table` without a
project. The last was corrected by registering the **byte-identical** table in
isolated `XDG_CONFIG_HOME/kicad/9.0/sym-lib-table`, then rerunning ERC on the
**same schematic hash**. This was an environment configuration correction,
not a format repair or warning suppression. Initial failure remains FAIL;
expectations/severities/exclusions were never changed. Generator had no post-first
creation correction. No semantic/format/negative-detection stop condition occurred.
Experiments ended on completion at **22:20:14 UTC**; no additional trial followed.

## Scope, effort and submission

For Main, missing evidence includes all actual component models and pin mappings,
RP2040/USB/power/ADC/interface semantics, model/library fidelity, hierarchy and
multi-unit/rotated/mirrored behavior, project configuration and authoritative
source migration, schematic-to-PCB parity, routing with effective 0.20 mm checks,
fabrication handoff and environment reconstruction. The small fixture cannot
qualify those. Maintenance requires pinned external library/dependency versions,
exact official symbols, CLI library configuration and independent parity checks;
upstream known issues and inconsistent version metadata increase that burden.
No effort estimate for Main or adoption decision is asserted.

The 2-hour issue window includes preparation, analysis, documentation and
submission; experiment cutoff was 23:53:36 UTC with final 20 minutes reserved.
Investigation ended within the 20-minute guidance (estimated sequence timestamp).
Actual process durations and exact clock observations are distinct from active
engineer-hours. KiCad re-preparation measured **53.009 s** from package download
through version/binding probes; library installation measured **25.244 s**, partly
overlapping that preparation. The [effort ledger](../hardware/kicad/qualification/eda-004f/evidence/effort-ledger.json)
uses a conservative **0.750 h AI effort allowance**, including publication/CI
reserve, **not measured active engineer-hours**. Carry forward **2.536 h** from
EDA-004E: known cumulative estimate **3.286 h**, nominal remainder **12.714 h** of
original 16 h; historical unquantified review/report/human effort remains unknown.
No budget reset. Process elapsed overlaps session work and is not added twice;
fully unattended time is unknown. The existing KiCad re-preparation and library
installation each have measured process records; empty-directory regeneration
reuses that environment and is not a full environment rebuild.

Evidence replay/hash verification, Dashboard JavaScript syntax and latest-record
substitution, baseline diff whitespace/scope checks and preservation of all old
artifacts are required submission checks. CI filters/conditions are unchanged;
product jobs skipped under those filters provide **no technical acceptance**.
Saved evidence replay and all raw hashes passed. Dashboard syntax and a Node VM
DOM substitution check passed; a literal current-ID reference found by the first
substitution test was corrected in data. No real-browser visual test is claimed
(the Dashboard structure/rendering code was unchanged). A staged whitespace check
found unified-diff context indentation; the diff was losslessly gzip-wrapped,
without altering source or generated files. Actual PR-head CI observation is
recorded in the PR. Commit/push and Draft PR
complete submission; merge, adoption and Human Gate remain PO actions.
