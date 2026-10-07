# Bounded alternate physical backend qualification plan

## Authority and present result

Planning only under [Issue #71](https://github.com/ihsinoky/he-piantor-42/issues/71)
and the [explicit PO Human Gate comment](https://github.com/ihsinoky/he-piantor-42/issues/71#issuecomment-6046244229),
recorded in [D-018](decisions.md#d-018---bounded-alternate-physical-backend-qualification-planning).
Candidate **B** is first for qualification, not adopted. Additional product-track
exploration of the internal tscircuit router evaluated in EDA-003F has ended;
frontend retention remains under evaluation. This document reports no experiment
or tool installation. Execution requires a separate PO-created Issue and a
subsequent PO instruction after its number is confirmed.

[EDA-003F](tscircuit-clearance-intervention-ab.md) remains
**INTERVENTION_UNSAFE_REGRESSION / K1**. Control A has zero required unrouted,
zero wrong-net components and 71 material records / 54 physical conflicts;
intervention B has zero required unrouted but two wrong-net components.
Here “candidate B” denotes the alternate architecture, not that unsafe intervention.
[Project status](project-status.md#eda-003-history-and-current-planning-decision)
retains the completed EDA-003B/C/D/E/F classifications. Representative Main
routing remains unqualified. G0A/G0B stay done; later Human Gates remain not-ready.

Preserve D-014 historical electrical authority for the frozen four-key fixture,
D-015/D-017 Main/Wing architecture/interface and D-016 JITX physical backend
NO-GO. Production **tscircuit 0.0.2646**, two copper layers, **1.2 mm** thickness
and **0.20 mm material clearance** remain unchanged. USB NPTH is **OPEN —
PRE-ORDER DFM REVIEW REQUIRED**. No exception, backend adoption, full Rev.M1
implementation, ordering or release is approved. Production pitch, Hall selection,
Rev.A cable mechanics, final power qualification and other documented risks stay open.

## Candidate comparison

This is a project-fit assessment, not a tool PASS. Capability references are
primary sources accessed **2026-10-07**, listed below. README feature lists and
integration labels are claims to test, not acceptance evidence.

| Criterion | A: native TSX + alternate router + tscircuit manufacturing | B: native TSX + headless KiCad verification/manufacturing + local headless Freerouting | C: KiCad-native authoritative inputs |
| --- | --- | --- | --- |
| AI/Codex source-controlled use | Retains TSX and source graph; external route feedback into Circuit JSON needs supported integration. | Retains TSX; generated KiCad is secondary qualification output. Public converter entry points exist [S4]. | Reviewable native schematic/PCB/project/library inputs [S7]; entails new authority and frontend migration decision. |
| Non-interactive execution | Must prove local integration with the pinned TSX stack; an integration label [S5] is insufficient. | KiCad CLI checks/exports [S1]; DSN/SES bridge separately necessary [S2]. Freerouting documents GUI disable [S6]. Must prove the whole chain. | CLI checks/exports use the same KiCad tools; same DSN/SES/headless constraint if using Freerouting. Native source generation/updates still need proof. |
| Routing | Alternate router acceptance and lossless route return unqualified. Current props expose integration options [S8], not compatibility with the frozen stack. | DSN -> local Freerouting -> SES documented [S5/S6]; faithful transfer and safe Main routing unproved. | Changing source ownership alone does not improve fixed-placement routing with the same router. |
| ERC/DRC | Retained source metadata is insufficient for meaningful ERC; stock physical errors do not disappear by replacing routing alone. | KiCad CLI ERC/DRC [S1], contingent on proper schematic/pin semantics and independent graph/geometry parity. | Native symbols can encode pin types; meaningful ERC still needs verified mapping and configuration, not generic passive pins. |
| Gerber/Excellon | Retains historical exporter, including unresolved Main segment-survival assertion from EDA-003C. | KiCad CLI fabrication exports [S1], subject to later output reconciliation; no new exporter. | Same KiCad exports; native ownership removes a conversion boundary, not fabrication qualification. |
| Reproducibility | Lock stack, integration and local router; compare returned geometry and later CAM. | Pin converter, KiCad bridge, Java/router and frontend; fresh regeneration compares every boundary. | Pin native inputs/libraries/tools; deterministic regeneration and routing remain necessary. |
| Git reviewability | Compact TSX but router/generated diffs require semantic summaries. | TSX plus conversion maps, rule files and normalized geometry reports; raw KiCad/DSN/SES retained. | Text S-expressions are reviewable but UUID/order noise and large board diffs need semantic summaries [S7]. |
| CI | Potential local scripted chain; no extensive CI before Main gate. | Reuse local evidence scripts first; minimal relevant checks only. Product CI later after Main acceptance. | CLI validation can fit CI; frontend migration/CI effort is greater and deferred. |
| Two-layer Rev.M1 | Potentially suitable, unqualified; keep 48 × 44 mm Main placement/rules. | First candidate under PO decision; must preserve both copper layers, 1.2 mm and 0.20 mm. | Potentially suitable under identical constraints; no automatic fallback. |
| Future Rev.A | Can retain shared TSX Wing generator, but expansion unqualified. | Retains shared Wing source intent; later 21-key/keepout/interconnect and manufacturing proof needed. | Needs new approved shared Wing definition/authority; no use of hardware/layout as new input. |
| Maintenance cost | Possibly smaller only if an existing end-to-end local path is proved cheaper than B; exporter risks remain. | Two conversion boundaries plus deprecated binding risk; bounded glue and reconciliation may dominate cost. | Eliminates TSX conversion risk at cost of source migration, model/symbol maintenance and review retraining; router risk remains. |

B is prioritized by PO, not by assuming these claims already work. A may be
considered only after evidence of a lower-cost existing path and a new PO decision.
C is a possible separately approved minimal trial after B conversion failure.

## Primary capability evidence and selected KiCad boundary

- **S1:** [KiCad 9.0 CLI manual](https://docs.kicad.org/9.0/en/cli/cli.html)
  explicitly identifies **9.0.9**, revision `152cd19e`. Select 9.0.9 as the planning
  baseline, consistent with prior project CAM evidence. It documents `sch erc`,
  `pcb drc` (JSON reports, violation exit status, schematic parity),
  `pcb export gerbers`, `drill` (Excellon and PTH/NPTH separation), and position
  export. Its command inventory has no DSN export/SES import. Check exact binary
  version/help later; do not invent `kicad-cli pcb export dsn` or an SES CLI command.
- **S2:** [KiCad 9.0 pcbnew function reference](https://docs.kicad.org/doxygen-python-9.0/namespacepcbnew.html)
  exposes `ExportSpecctraDSN(BOARD, filename)` and
  `ImportSpecctraSES(BOARD, filename)` plus board load/save. This suggests a
  small standalone bridge; it does not prove packaging, fidelity or headless
  operation in the selected 9.0.9 installation.
- **S3:** [KiCad binding deprecation notice](https://dev-docs.kicad.org/en/apis-and-binding/pcbnew/index.html)
  documents standalone use but deprecates SWIG as of 9.0, with removal planned
  for 11.0 and no strict compatibility guarantees. A version-contained public
  binding wrapper is a qualification bridge, not a durable adopted architecture.
  [IPC add-on documentation](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/)
  says IPC in KiCad 9/10 requires a running GUI; headless support is described
  for 11. Do not silently substitute IPC, a newer major version or virtual-display
  GUI automation for a proven GUI-free 9.0.9 workflow.
- **S4:** [circuit-json-to-kicad README](https://github.com/tscircuit/circuit-json-to-kicad)
  claims schematic/PCB/project conversion; its [public source exports](https://github.com/tscircuit/circuit-json-to-kicad/blob/main/lib/index.ts)
  expose those converters. Inspect and pin a release in the execution Issue;
  support for this fixture's duplicated pads, NPTH, keepouts, rules and pin
  electrical attributes remains unqualified. EDA-003A rejected the reverse
  footprint importer; this forward converter requires its own independent proof.
- **S5:** [Freerouting upstream README](https://github.com/freerouting/freerouting)
  describes DSN input/SES output and lists KiCad/tscircuit integrations. None
  establishes a project PASS, a local-only integration or fixed-fixture fidelity.
- **S6:** [Freerouting CLI documentation](https://github.com/freerouting/freerouting/blob/master/docs/command_line_arguments.md)
  documents `-de`, `-do`, `--gui.enabled=false`, passes/threads and rules/settings.
  Adjacent rules files can affect input; isolate and hash them. Select an exact
  release and its matching Java requirement later, with no cloud routing or API
  service. CLI success/router-reported DRC does not substitute KiCad and independent checks.
- **S7:** [KiCad board file specification](https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/)
  describes native text structures including layers, setup, footprints and zones.
  Prefer existing parsers/converters and public APIs; documentation of a format
  does not authorize a large custom writer or full frontend migration.
- **S8:** [tscircuit group props source](https://github.com/tscircuit/props/blob/main/lib/components/group.ts)
  includes `routingDisabled` and alternate autorouter configuration. Moving
  upstream source is discovery evidence only. The accepted isolated installation
  also exposes `routingDisabled` in `@tscircuit/props 0.0.689`; inspect its locked
  core behavior rather than assuming every current feature exists in 0.0.2748.

No private API, permanent fork, router internals patch, large custom interchange
implementation or new manufacturing exporter is authorized. If an existing
converter and narrowly bounded public bridge cannot represent the required
information, stop rather than constructing a replacement EDA integration.

## Exact representative Main baseline

Use repository commit **`b84585ecc2cf32000285bbf389d9fea255436980`** and
`RepresentativeMain strategy={3}` from
[revm1-routing-proof.tsx](../hardware/tscircuit/src/qualification/revm1-routing-proof.tsx),
SHA-256 **`0caa8e53eed298c3cf65715a15a1d671d91de715d4eb8f790eeb13e17a777008`**.
Supporting inputs at that commit:

| File under hardware/tscircuit | SHA-256 |
| --- | --- |
| src/qualification/JstGh14.tsx | `ad23f75d53a917f8f43485b7fe887ff096ab0bdda244e3dc6e44fd73d93c787c` |
| src/qualification/native-support-footprints.tsx | `7b0efff9f5178b589c2ef7085625549bc4701ee24d2841ee7b46785921db55fe` |
| src/components/HallKey.tsx (transitive import; no Wing execution) | `0241daa3e2640bc870537ba3fa6571868858345f361456d80f73849dad32495c` |
| qualification/eda-003c/latest-stock/package-lock.json | `dec21cc020344ce8c8a769bd3ec92d99186546034974bcb702fc68f9dd7a455f` |

Frontend qualification copy uses accepted **tscircuit 0.0.2748**,
**@tscircuit/core 0.0.2097**, **@tscircuit/props 0.0.689**,
**circuit-json 0.0.516**, Bun **1.2.22**, and the unchanged EDA-003C isolated
lock; production 0.0.2646 is not changed. Record exact Node/npm, checks and all
transitive resolutions too. Do not run historical prepare/screen/intervention
scripts to generate an alternate input.

Preserve **49 components, 37 named nets, 167 required physical endpoints,
30 intentional NC ports**, fixed strategy-3 coordinates/rotations, **48 × 44 mm**
outline, two copper layers, 1.2 mm thickness, 0.20 mm widths/material-clearance
requirement, 0.60 mm via copper / 0.30 mm drill and all effective source rules.
Counts are sanity checks; identity-level graph/geometry parity is required.
The representative is a non-product fixture, not the full Rev.M1 design.

EDA-003C's raw Main hash
`97d51d510ecc7096261ad36297b48939609a14435a24926967b61197ed951131`
and F control are read-only comparison evidence for placement/graph/local bond,
not routing inputs. Never start from EDA-003B or F's shorted generated copper,
or strip historical generated files to manufacture a passing input.

## Genuinely unrouted isolated source

Copy source/dependencies under a new qualification root with its own dependency
resolution. Record original hashes, copy hashes and a small reviewable source diff.
Use the pinned public `routingDisabled` board property (or documented root
`pcbRoutingDisabled`) to disable existing routing; verify its actual behavior
before Main. Generate new Circuit JSON from that copy, keeping all ordinary
`Wiring` source `<trace>` connectivity declarations. Logical connections are
required graph edges, not pre-routed tracks.

`USB_SHELL_BOND` is different: an explicit source `pcbPath` joining duplicate
physical shield lands, 17.00 mm distinct local GND copper. Preserve its exact
source geometry, layer and width. Disabling routing may suppress this physical
bond too. Stage 1 must determine whether the public source path can retain only
this bond. If needed, a tiny reviewed public-API bridge may instantiate this
exact source-derived bond on the isolated KiCad board; reconcile its anchor-frame
transform and endpoint attachment independently. Do not copy arbitrary routed
copper, add hand-routed signal paths, or equate shared pad numbers with real
physical connection. If faithful bond transfer needs extensive custom work, STOP.

Before DSN export, prove that all copper consists solely of accepted footprint
lands and that explicitly identified local bond. No stock-generated global
tracks, vias, cached routing, pours or implicit breakout remain. Inventory every
physical segment, its source provenance and hash; nonlocal required nets must
be demonstrably unrouted. Logical and physical baseline counts are separate.
The independent final check must still require every duplicate land to connect.

## Transfer and ERC reconciliation

Build a canonical source intent/geometry manifest independent of the converter.
Reconcile at **unrouted Circuit JSON -> KiCad -> DSN**, and after **SES -> KiCad**:

- Component reference/value/part, logical pin alias/number, named net membership,
  explicit NC intent and source internal connections; detect missing, merged,
  renamed or additional objects, even where aggregate counts match.
- Every physical pad, including duplicate numbers/ports and six separate GH
  return contacts; preserve mechanical holes separately from electrical endpoints.
- Coordinates, rotation sign, origin, units/Y inversion and layer mapping; shapes,
  dimensions, corner radii if present, drill sizes/shapes, plating and annuli.
- Outline, copper-layer span, 1.2 mm stack metadata, all existing keepouts and
  prohibited copper/via/hole relationships; empty Main keepout inventories must
  reconcile explicitly rather than silently dropping data.
- Local bond topology and exact copper; effective global/netclass/custom rules,
  clearance and width settings, via rules, NC-pad obstacles, no via drill intrusion
  into SMD lands and board boundary. DSN defaults must not relax KiCad/source rules.

Predeclare numeric comparison tolerances and unit rounding as measurement
resolution, never a relaxation below 0.20 mm. Unsupported geometry, material
loss or an unexplained difference is a STOP. Retain full object maps and raw
warnings; no generic symbols, collapsed duplicate pads or ignored records can
stand in for parity.

The TSX baseline has **`schematicDisabled: true`** and underspecified pin/power
metadata. A generated schematic alone is not meaningful ERC. Stage 1 must
assess coverage of electrical pin types (input/output/bidirectional/power/passive,
NC and supply intent) using verified device definitions/datasheets and record
a semantic coverage table. A minimal qualification-only semantic mapping must
preserve the independently reconciled source graph, including power domains
and internal connections; schematic enablement may change the copy only, not
accepted source. All-passive/generic symbols or guessed attributes cannot PASS.
If adequate semantics cannot be provided through existing facilities within
the budget, record **ERC_UNQUALIFIED** and STOP; do not waive or invent ERC.

Run meaningful KiCad ERC and schematic/PCB parity when prerequisites exist,
plus independent canonical endpoint/net comparison. This prevents a converter
from producing both a wrong schematic and a matching wrong PCB that pass parity.

## Risk-first execution stages and acceptance

1. **Minimal environment/interchange feasibility:** pin environment; confirm
   exact CLI help, converter support, standalone board-load/DSN-export/SES-import/
   board-save bridge without display/GUI/manual edits. Use one tiny non-product
   roundtrip smoke fixture, with holes/duplicate pads/local bond and meaningful
   pin semantics, not a placement/router tuning benchmark. Exercise local
   Freerouting once only to prove transport. Record limitations and effort.
   STOP on missing headless path, unsupported semantics or excessive adapter work.
2. **Representative Main transfer and first safe complete route:** establish
   faithful unrouted input and ERC first. Lock the exact run contract before
   launching Main; route once, import through the approved public bridge and
   reconcile against source plus KiCad checks. No placement change or repair cycle.
3. **Confirmation only after initial PASS:** fresh process and clean recreated
   environment/work directories using identical pinned inputs/settings, not the
   first SES/cache. Regenerate every boundary and independently verify again.
   Preserve raw differences and normalized comparisons. Any unexplained material
   difference or failed check is non-reproducibility, not a reason for a third run.
4. **Later PO-authorized work only after Main PASS:** Wing Hall keepout behavior
   and Main/Wing Gerber/Excellon/BOM/PnP reconciliation, including independent
   1.2 mm handoff and known USB risk. CLI export success alone is insufficient.
5. **Later maintenance probe:** one qualification-only small source change
   (for example a passive value), regenerated/checked and semantically reviewed
   in Git; no production migration. Measure effort and diff noise.

The first execution Issue covers stages 1–3 only. Stage-1 smoke is not a Main
attempt or evidence of Main routing suitability. Stages 4–5 and extensive
frontend migration/product CI are forbidden before Main gate acceptance and
separate authorization; a Main PASS does not automatically launch them.

For both Main runs require:

| Acceptance metric | Required result |
| --- | --- |
| Required unrouted (all physical required lands) | **0** |
| Wrong-net copper components | **0** |
| Targeted material violations | **0** |
| Unexplained conversion loss | **0** |

Targeted material checks cover copper-pad/trace/via and NC-pad clearances,
hole/drill intrusion and clearance, invalid transitions, board boundaries and
all applicable source keepouts, with no weakening or new exclusions. Retain
known USB NPTH product risk as a named unresolved product review item; any
conversion/routing-added hole conflict fails. If KiCad reports an existing
geometry conflict, record it and STOP for PO disposition rather than creating
an executor-owned exclusion or manufacturing exception.

Use `kicad-cli pcb drc` with all errors recorded (including exclusions) and
meaningful `sch erc`, then independently reconstruct physical islands/shorts
from actual pad/track/via geometry and layer transitions, checking against the
source-intent manifest. Router annotations and net labels cannot join physical
islands. The existing Circuit JSON [verifier](../hardware/tscircuit/scripts/revm1-physical-connectivity.ts)
can inform logic and adversarial tests, but **cannot validate KiCad geometry
without a separately reviewed adaptation**. Review that bounded qualification
adaptation before relying on it: parser coverage, transforms, actual copper/
drill shapes, unsupported-geometry failure and fault injection for shorts,
missing pads/vias, duplicate lands, false labels and rule loss. If that work
exceeds the adapter/budget boundary, STOP; do not substitute router-reported DRC.

## Budget, run contract and STOP ledger

The first Main evaluation has an aggregate **two-workday engineering-effort cap**,
including preparation, installation/interchange, semantic/geometry reconciliation,
verification adaptation, both permitted runs, analysis and report. For auditing,
use at most **16 engineer-hours** (two eight-hour days); this is a conservative
planning accounting convention, not extra effort authorization. Log start/end,
active minutes, operator, task and cumulative effort; separately log unattended
wall-clock process time. Reserve report time instead of exhausting the cap in setup.

| Checkpoint | Planned cumulative effort ceiling | Proceed condition |
| --- | --- | --- |
| P0: versions, sources, commands, budget/run contract recorded | 1 h | Exact environment and constraints recorded; scope intact. |
| P1: minimal headless roundtrip, semantic coverage and adapter assessment | 4 h | Usable public bridge/converter path, no material loss. |
| P2: faithful Main transfer, independent verifier/meaningful ERC ready | 10 h | All pre-route reconciliation checks pass; no unresolved semantics. |
| P3: initial run, post-import checks | 13 h | All Main acceptance checks pass to permit confirmation. |
| P4: conditional fresh confirmation and terminal report | 16 h maximum | Same constraints pass reproducibly; otherwise STOP. |

Checkpoints are stop/review points, not invitations to spend the unused budget
on retries. Before execution predeclare routing wall-clock timeout, maximum
passes, threads/seed or determinism strategy, optimizer settings, layer directions,
width/via/clearance tables, file locations and environment configuration. Record
exact command/settings hash before the first smoke/Main route. Tool versions
and concrete limits are to be frozen in the separate execution Issue's run
contract, not discovered through repeated Main tuning. Unsupported declared
settings require STOP/new PO decision, not silent defaults. Permit **one initial
Main run**, then **one fresh confirmation only on initial PASS**. Timeout, crash,
partial output or wrong result consumes that attempt; no resume/retry/tuning.
Issue #71 itself permits zero routing runs.

Stop immediately on material transfer loss, headless failure, shorts, incomplete
routing, targeted violations, non-reproducibility, extensive adapter/router
internals work or exceeded effort. Record gate, phase, inputs/hashes, elapsed/
active effort, stdout/stderr, exit status, partial outputs and exact discrepancy.
Do not automatically try candidate A/C, move components, relax rules, suppress
errors or grant exceptions. New candidates, placement changes, retries/tuning
and exceptions require a **new PO decision**.

## Version and environment pinning before later execution

The execution Issue must select exact converter and Freerouting releases/commits
and record their package integrity or SHA-256, Java distribution/build, Python
and OS/architecture, KiCad 9.0.9 package/build and container digest if used,
Node/npm/Bun and full isolated frontend lock. Capture executable version/help,
install commands, registry/archive URLs, hashes and dependency resolutions.
Pin KiCad symbol/footprint library snapshots and embedded definitions, project/
netclass/custom rule files, DSN/rules, Java flags, locale/units, configuration
paths and any parser/bridge libraries. No global GUI state, adjacent unrecorded
rules or network/cloud router. Confirmation reconstructs from these recorded
inputs in a fresh isolated installation/environment. Tags and `latest` alone
are insufficient. Missing pins or packaging support is an environment STOP.
No KiCad/Freerouting installation or execution occurs in Issue #71.

## Final classification, fallback and reuse

Report independently: **ENVIRONMENT_BLOCKED**, **CONVERSION_BLOCKED**
(including missing graph/pin semantics), **ROUTING_BLOCKED** after faithful
transfer, **REPRODUCIBILITY_BLOCKED**, or **BUDGET_OR_ADAPTER_BLOCKED**.
Use **MAIN_PASS** only when every initial and fresh confirmation check passes;
ERC status and evidence completeness remain explicit fields. Preserve multiple
observed failures with the first terminal gate as primary. A fixed-placement
failure is project-specific evidence, not proof that an EDA/router is generally
incapable. No classification adopts a backend or releases hardware.

B conversion failure may support a new PO decision for a minimal C trial.
B routing failure after faithful transfer is not resolved simply by changing
frontend authority to C and retaining the same router. No automatic fallback
is allowed. PMO reviews evidence read-only and advises MERGE/HOLD; PO owns
new execution Issues/instructions, exceptions, candidate/adoption decisions,
Human Gates and merge. Codex supplies evidence and does not decide those gates.

Even a BLOCKED result can retain version manifests, repeatable setup scripts,
source-intent/geometry maps, pin-semantic coverage, independently reviewed
reconciliation code/fault fixtures, raw warnings and boundary-specific losses,
local bond/duplicate-pad knowledge and routing cost data. Reuse only demonstrated
substeps and compatible pinned versions, with their limits. Historical electrical
models, Main/Wing interface, DFM knowledge and frozen oracle remain useful;
failed routing/exports never become an accepted manufacturing package.

The [next execution Issue body draft](alternate-physical-backend-main-qualification-issue-draft.md)
is for PO manual creation. It has no speculative number and no Codex execution prompt.
