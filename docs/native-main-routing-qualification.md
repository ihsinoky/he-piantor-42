# EDA-004G — native Main routing qualification

**CONVERSION_BLOCKED / ERC_UNQUALIFIED — Stage 1 STOP.**
[Issue #85](https://github.com/ihsinoky/he-piantor-42/issues/85) authorized the
non-product `RepresentativeMain strategy=3` evaluation. Complete Main pin-model
coverage was not established in the selected pinned-library/public-API reuse
path. No Main schematic or PCB was generated; no routing was launched.
Main initial/confirmation counts are **0/0**, small transport trials **0**.
All Main acceptance metrics are **null**, not zero or PASS.

This is a **partial prerequisite evaluation and submitted STOP report**. It is
not Main routing failure, proof of general tool incapability, adoption, a Human
Gate, or authorization to start product design. PMO/reviewer is ChatGPT; PO is
the user. Codex implemented/evaluated and made the execution stop; PMO reviews
the evidence and PO owns acceptance and any subsequent investment decision.

## Authority, initial state and changed hypothesis

At **2026-10-14 01:17:56 UTC**, cwd was `/workspaces/he-piantor-42`, branch
`eda-004g-native-main-routing-qualification`, HEAD
`4a96d6ff6ddca3fd19330e392ae8cf91c39f6b6c`, and worktree clean. GitHub's current
main also pointed to that HEAD. The retained [Issue snapshot](../hardware/kicad/qualification/eda-004g/evidence/issue85.json)
was updated **01:13:12 UTC**. Issue #85 is the execution/acceptance/stop authority;
earlier permissions were not inherited. All required workflow/history, D-014–18,
planning, EDA-004E/F, status and Dashboard instructions were read.

[PR #84](https://github.com/ihsinoky/he-piantor-42/pull/84) merged at
**00:39:55 UTC**, with the above merge commit. EDA-004F is an **accepted historical
report**, with its original small-fixture results unchanged. Its initial warning
failure and configured subsequent success remain distinct. That acceptance does
not qualify Main or adopt the method.

Earlier Circuit JSON converters stopped on duplicate-land connectivity/library
identity and meaningful schematic/ERC failures. EDA-004E passed small-board I/O
but failed initial DRC and had no schematic route. EDA-004F subsequently qualified
only six symbols/16 pins. The changed mechanism here was fixed kicad-sch-api
public schematic calls plus KiCad-owned public PCB serialization, with no earlier
converter. The first hypothesis was that bounded model/connection correspondence
and existing public facilities could represent the complete fixed Main. That
prerequisite was not established; the later Freerouting hypothesis was not tested.

## Fixed source and partial independent expectation

The immutable source authority is commit
`b84585ecc2cf32000285bbf389d9fea255436980` in the
[qualification plan](alternate-physical-backend-qualification-plan.md#exact-representative-main-baseline).
All five listed source/transitive/isolated-lock hashes match immutable commit,
current main and worktree individually; see
[input freeze](../hardware/kicad/qualification/eda-004g/evidence/input-freeze.json).
Production tscircuit **0.0.2646**, product source authority and source bytes were
not changed. The isolated frontend was not installed/executed. Historical routed
Circuit JSON was inspected read-only during source review; none was copied,
stripped or used to generate a new input or copper.

[Partial source intent](../hardware/kicad/qualification/eda-004g/source-intent.partial.json)
is a manual transcription independent of any schematic/PCB generator. It records
each of 49 identities, source values/packages, strategy-3 positions/rotations,
pin aliases/numbers, named-net membership and NC intent. Its hash was frozen
before the captured public model assessment and has not changed. It is expressly
**not a complete accepted geometry/role expectation or proof of source parity**.

Counting conventions are explicit: **193 logical pin numbers**, plus three extra
USB shield lands and one extra GH mechanical land, produce **197 physical endpoint
intents**: **167 required + 30 NC**. There are **29 logical NC pin numbers**; the
two GH `MP` lands explain the additional physical NC. These are different from
runtime `source_port` counts, which include generated internal duplicate ports.
The 37 named nets and six separate GH GND return contacts are recorded individually.
Counts alone are not acceptance.
A post-STOP [read-only comparison](../hardware/kicad/qualification/eda-004g/evidence/retained-intent-comparison.json) corroborates each identity/value, logical alias/net/NC, duplicate-port count and component anchor/rotation against retained source records. It reads no route copper for reuse and qualifies neither physical shapes nor Main generation/checks.

The table retains 48×44 mm, two layers, 1.2 mm, width/material spacing 0.20 mm,
via 0.60/0.30 mm and the source USB shield bond's complete anchor-frame path,
top layer, 0.20 mm width and 17 mm distinct length. Full per-pad shape/drill/layer,
stock-footprint expansion, outline reconciliation and the bond's frame transform/
physical attachment remain **unqualified**. Same pin numbers are not physical
connections. No material geometry was changed or accepted by inference.

## Public-model assessment and first stop

The [captured assessment](../hardware/kicad/qualification/eda-004g/evidence/processes/public-model-assessment-corrected/public-model-assessment.json)
used public `SymbolLibraryCache.discover_libraries/get_symbol` and
`components.add`. Available definitions exposed RP2040's individual supply,
GPIO, USB, QSPI, crystal and debug roles, AP2112K and USBLC6 pins, crystal,
passives and testpoint definitions. These are retained observations, not an
accepted complete Main role mapping. Manufacturer TI SLVSEN5B p.3 also confirms
TPS22919 IN/GND/ON/NC/QOD/OUT and that QOD may be left floating; verified
repository component-source/model records were read as references. No all-passive
Main mapping, guessed role or ungrounded power declaration was created.

| Selected snapshot observation | Required additional qualification |
| --- | --- |
| No `Power_Management:TPS22919`; public addition with valid `U1` reference raises `LibraryError` | A faithful six-pin TPS22919 definition with verified roles, loaded through supported facilities. |
| No exact `W25Q16JVUXIQ`; inspected `W25Q16JVSS` has eight pins | Exact UX identity, eight signals and separate unassigned EP, with manufacturer-backed disposition. No SOIC footprint substitution. |
| No exact `TYPE-C-31-M-12`; inspected official USB symbol has A/B/S numbers | Explicit mapping of combined source contacts, NC SBU contacts and four distinct shield lands. |
| No exact `BM14B-GHS-TBT`; generic inspected connector has fourteen pins | Fourteen contact meanings and two separate mechanical MP lands without dropping or electrically joining them. |

The pinned cache/collection public methods load definitions from existing library
files and instantiate components. No public symbol-definition author/register
method was found in those inspected classes. External custom symbol libraries
can be loaded; **their absence here does not prove a small custom library, another
verified library, or a different bounded model preparation could never work**.
Those alternatives were not implemented or exhaustively searched. No measured
large-implementation requirement or budget exhaustion is claimed.

At **01:31:39.130453 UTC**, Codex stopped on **incomplete faithful Main pin-model
coverage / ERC_UNQUALIFIED**, based on the bounded reuse assessment. This is the
executor's stop/disposition of an unestablished prerequisite, not a demonstrated
universal API limitation. The public `LibraryError` is the first terminal probe
result; incomplete checker/geometry coverage is a separate constraint.
No generic model substitution, private cache injection, validation-level change,
fork, GUI, generated-file format correction or expected-table revision followed.
[STOP ledger](../hardware/kicad/qualification/eda-004g/evidence/stop-decision.json).

Two preparation mistakes are preserved in
[corrections](../hardware/kicad/qualification/eda-004g/evidence/preparation-corrections.json):
the symbol download initially used the binary package directory and returned
HTTP 404; APT's public URI identified `kicad-library-symbols`, retaining the same
pinned package hash. The first component-add probe used source alias `U_LOAD`;
reference validation rejected that before lookup. The corrected feasibility
probe used `U1`, with identical symbol ID/value, then obtained the `LibraryError`.
The first failure is **not** evidence of a missing symbol. Both script versions,
both raw probe results and commands remain retained. A future Main source-ID to
valid KiCad-reference correspondence would itself need independent verification.

## Checker scope, negative tests and engineering stages

[Checker coverage](../hardware/kicad/qualification/eda-004g/evidence/checker-coverage.json)
records predecessor hashes and their actual limits. EDA-004F reads its unrotated
wire-stub/local-label small schematic/XML; it has no PCB copper reader.
EDA-004E checks two fixed footprints/seven pads/two tracks and configured rule
values, not general physical islands or effective spacing. The existing Main
Circuit JSON copper verifier has relevant algorithms, but no separately reviewed
KiCad adaptation. None is generalized or promoted to Main acceptance here.

The four required Main fault tests—actual wrong-net copper short, missing required
pad, duplicate-number land's missing physical connection, and missing effective
0.20 mm rule—are all **NOT ENTERED / UNQUALIFIED**. Historical small-fixture fault
detections are not substitutes. No fault-detection PASS is reported for Main;
insufficient validation independently prevents any MAIN_PASS.

| Issue #85 stage | Result |
| --- | --- |
| 1. Independent expectation/model/checker | **PARTIAL; prerequisite FAIL / STOP.** Input hashes and individual source-intent inventory recorded; complete roles/geometry/checker and required negative detections not established. |
| 2. Schematic and genuinely unrouted PCB | **NOT ENTERED.** No Main generation, ERC, schematic/PCB parity, geometry/layer/outline or copper inventory acceptance. |
| 3. Effective rules and DSN/SES | **NOT ENTERED.** Public bridge signatures observed during preparation only; neither transport fidelity nor effective 0.20 mm enforcement tested. Small transport attempts 0. |
| 4. Initial Main route | **NOT ENTERED, attempts 0.** No DSN/SES, routed PCB or post-route inspection. All four metrics null. |
| 5. Conditional confirmation | **NOT ENTERED, attempts 0.** First-run pass absent; no first/confirmation differences exist. |
| Complete environment reconstruction confirmation | **UNQUALIFIED.** Initial tool re-preparation is not a second full environment reconstruction or same-environment Main confirmation. |
| Product design, Wing, manufacturing, adoption/Human Gates | **NOT ENTERED / NOT APPROVED.** |

USB NPTH remains **OPEN — PRE-ORDER DFM REVIEW REQUIRED**. No KiCad Main DRC was
run, so no existing-versus-new USB violation conclusion is available. No exclusion
or manufacturing exception was added. Connection/shape/role uncertainty and
checker insufficiency were not waived to route.

## Environment, evidence and maintenance boundary

No earlier `/tmp/eda004e/f` environment remained. The unchanged EDA-004D installer
was reused under `/tmp/eda004g` and a new capture root. KiCad CLI identifies
**9.0.9**; binding **9.0.9-9.0.9~ubuntu24.04.1**. Binary package hash is
`b7e6d33867631dc44385067b703b4c39eadede2037a260790b19495fe17e43f0`;
official 9.0.9 symbol package hash is
`73bc5b5f7ada14abcbe324c5f289c6cf807db379a9ffaaaecc877df1b619bd0a`.
Dependency-package hashes, public bridge probe, environment overrides and all
process records are retained. DISPLAY/WAYLAND_DISPLAY were unset by capture.

kicad-sch-api source commit **505bca23e91cf3fa6e3b66976e529e775eada3ba** was
reinstalled from EDA-004F's immutable archive, hash
`fa7508829945457f9824ae3490bddfb81718f3cacedaeaa6ee6515c030ef398c`.
EDA-004F's unchanged hash-locked dependencies were reused. Installed Python source
matches the archive individually; build report/dependency freeze and selected
official symbol files, raw decompressed hashes and original license are retained.
Build-isolation tooling and mutable APT availability remain reproduction limits;
there is no full environment-reconstruction certification.

Host Python is 3.14.2 on Linux x86_64/glibc 2.39; Node/npm and host Microsoft
Java 25.0.4.1+1-LTS observations are in process records. Freerouting **v2.1.0**
was discovery only: its [release README](https://github.com/freerouting/freerouting/blob/v2.1.0/README.md)
selects Java 21 and its [build definition](https://github.com/freerouting/freerouting/blob/v2.1.0/build.gradle)
targets Java 21. A compatible Java distribution/build/hash, router artifact/hash,
help/settings, timeout/passes/threads/seed and input/config hashes were **not frozen
or executed before STOP**. Host Java is not declared qualified for routing.
This incomplete environment/run-contract preparation is disclosed, not a hidden
use of defaults. No route could be authorized without the prerequisites.

[Evidence/code root](../hardware/kicad/qualification/eda-004g/README.md) contains
the partial expectation, source/model freeze, versions/dependencies/library hashes,
preparation and feasibility code, commands/exit codes/raw stdout/stderr, individual
model observations, limits, attempt/effort/STOP records and submission verification.
No Main-generation code or generated Main schematic/unrouted PCB/DSN/SES/routed
PCB is present: those stages did not start. Lossless gzip/archive organization
does not change raw evidence. Saved-state verification does not launch experiments.

Maintenance remains unresolved: exact custom Main symbol definitions and their
electrical provenance, composite logical-to-physical mapping, full independent
pad/drill/copper extraction and negative checks, pinned rule/library registration,
DSN/SES fidelity, and deprecated SWIG bindings. The assessment did not measure
their implementation cost. PMO/PO must review this limited stop and the possible
boundedness of missing work; this report does not select or authorize a retry.

## Effort and submission

The six-hour issue frame ends **07:17:56 UTC**, with experiments cut off by
**06:47:56 UTC** to preserve the last 30 minutes. The recorded actual interval
from session start to experiment STOP is **13 min 43.130 s**; this is wall-clock,
not measured active engineer time. Preparation and process durations are retained
separately in the [effort ledger](../hardware/kicad/qualification/eda-004g/evidence/effort-ledger.json).
Unattended time and historical human/review/reporting time remain unknown.

Carry forward **3.286 h** known cumulative AI estimate. This evaluation uses a
conservative **0.750 h AI allowance**, including reporting/submission/CI reserve,
not measured engineer-hours: known cumulative estimate **4.036 h**. The original
16 h convention's nominal arithmetic remainder is **11.964 h**, not certification
of an exact remaining budget. Process times overlap session effort and are not
added twice. No budget reset, exhaustion or six-hour overrun is claimed.

Status/history/Dashboard synchronize the EDA-004G proposed STOP and PR #84's
accepted historical record. Prior reports/evidence, decisions, product sources,
production dependencies and CI experiment conditions remain unchanged. Submission
checks cover saved raw hashes, frozen partial inventory and probe, scope/old-file
preservation, JavaScript syntax and latest-record substitution, and whitespace.
**Required Main error detection remains unqualified**, regardless of those
submission checks. Actual latest PR-head CI observation is recorded in the PR
body after publication; successful management jobs or skipped experimental jobs
are not technical acceptance. Commit/push and Draft PR submit this report;
merge/auto-merge, adoption, Human Gate and product design are not performed.

Saved-state submission verification passed: **287 process records** (including
267 losslessly aggregated package-extraction records), all raw/artifact hashes,
input and frozen partial/probe hashes, distinct first/corrected failures, and
individual retained source-intent corroboration. Dashboard JavaScript syntax and
Node VM DOM latest-record substitution passed; no browser visual test is claimed.
Scope/previous-file preservation and `git diff --check` passed. These checks do
not supply the four missing Main fault detections or technical acceptance.
