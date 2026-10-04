# EDA-002C4B — JITX physical/manufacturing capability proof

**Verdict: BLOCKED.** Issue [#43](https://github.com/ihsinoky/he-piantor-42/issues/43).
This concludes the investigation, not a successful complete manufacturing gate.
C4C / G0A must decide whether to invest further, qualify downstream CAM, or use
another backend. This report makes no adoption decision.

## 1. Scope and authority

This is disposable EDA qualification infrastructure. It is **not physical
Rev.M1**, a reusable Main, Evaluation Wing, production PCB or panel. No Main/Wing
connector, pitch-test geometry, Left/Right Wings, G0B implementation or order
was created. D-014/D-015 and all frozen sources remain unchanged. No
`hardware/layout/**` input was read or used. C0 graph PASS, C1 manufacturer-model
PASS, C2 electrical PASS, C3 historical evidence and merged C4A PR #42 remain
accepted historical inputs; they are not reclassified by this result.

Initial branch was `eda-002c4b-jitx-physical-pipeline`, clean, with HEAD and merge
base both `8f6c401a902353547dcacbdfc76978ac807ce7f9`. The branch is retained.

## 2. Environment

Python 3.14.2; Python JITX 4.4.3; jitxlib-standard 4.4.0; existing Linux runtime
4.4.2. Package versions and `uv.lock` are unchanged. The sole pyproject change
registers the new public export plugin. Locked sync succeeds with
`UV_CACHE_DIR=/tmp/eda-c4b-uv-cache uv sync --locked --group dev`; the sandbox's
normal home cache is read-only. These are the previously validated versions,
not a new compatibility claim.

The expired existing license was refreshed with documented `jitx auth refresh`.
Network/local runtime commands required execution outside the filesystem/network
sandbox. No runtime replacement or dependency upgrade was used. Activating the
project venv exposes the normal `jitx design build/export` commands, including
both existing graph exporters. The C3 command-discovery issue is not present in
this correctly activated environment.

## 3. Supported workflow and reproduction

Discovery preceded physical code; the early capability matrix was committed
with the source checkpoint. Installed official `jitx`, physical-layout,
substrate-modeler and code-review skills were execution aids only. No skill
source or proprietary helper was copied into this repository.

Public workflow references:

- [CLI setup/build](https://docs.jitx.com/en/latest/getting-started/cli/index.html)
- [Board](https://docs.jitx.com/en/latest/api/jitx.board.html),
  [stackup](https://docs.jitx.com/en/latest/api/jitx.stackup.html),
  [substrate/fabrication constraints](https://docs.jitx.com/en/latest/api/jitx.substrate.html)
- [Code placement](https://docs.jitx.com/en/latest/essentials/physical_design/kinematic-tree.html)
- [Route API](https://docs.jitx.com/en/latest/api/jitx.circuit.html),
  [via API](https://docs.jitx.com/en/latest/api/jitx.via.html),
  [topological router](https://docs.jitx.com/en/latest/essentials/physical_design/autorouter.html)
- [Export plugin](https://docs.jitx.com/en/latest/api/jitx.plugin.html),
  [experimental RuntimeDesign](https://docs.jitx.com/en/latest/api/jitx.run.html),
  [Trace transforms](https://docs.jitx.com/en/latest/api/jitx.inspect.html)
- [JITX architecture / downstream outputs](https://docs.jitx.com/en/latest/jumpstart-kits/shared/JITX_Architecture_and_Systems_Requirements_v2_0.html)

From `hardware/jitx`:

```bash
UV_CACHE_DIR=/tmp/eda-c4b-uv-cache uv sync --locked --group dev
source .venv/bin/activate
jitx auth show
jitx runtime start --background
jitx design build he_piantor_42_jitx.m1.M1FourKeyElectrical --no-dependency-check
python -m physical.reproduce
python -m unittest discover -v
ruff format --check he_piantor_42_jitx physical parity tests
ruff check he_piantor_42_jitx physical parity tests
```

`physical.reproduce` restarts the installed runtime, removes **only** this
fixture's ignored generated design directory, then builds/captures/exports
sequentially, twice. It hashes all local electrical/component, physical and
parity Python modules, contract, normalization, pyproject and lockfile before
and after generation. It fails on changed source, missing placements, failed
source-route realization, pad overlap/outside-board findings, ODB/PnP mismatch,
electrical regression, or changed original component topology. It records
BLOCKED rather than treating those narrow checks as complete routing/DRC.
Repeated builds do not depend on hand-edited or GUI-created layout state.

Commands used each run:

```bash
jitx design build he_piantor_42_jitx.physical_qualification.M1FourKeyPhysicalQualification --no-dependency-check
jitx design export physical-qualification he_piantor_42_jitx.physical_qualification.M1FourKeyPhysicalQualification --output designs/c4b/run-1
jitx design export legacy-odb++ he_piantor_42_jitx.physical_qualification.M1FourKeyPhysicalQualification
```

Use `run-2` for the second capture. `--no-dependency-check` follows the locked
sync and avoids JITX's separate pip-based sync; it does not disable runtime
validation. `--dry`, private APIs, artifact patches, special export-bypass
flags and custom JITX forks are not used.

## 4. Capability matrix

A = supported/documented; B = supported but experimental/qualified;
C = unsupported/private/manual workaround required; N/A = not required for
this JLCPCB handoff. Availability classification is distinct from gate success.

| Capability | Class | Demonstration / qualification |
| --- | --- | --- |
| Board/substrate | A | Project-owned Board/Design/Substrate builds |
| Stack/layer thickness | A | Two conductors; five physical layers; nominal 1.2 mm sum |
| Explicit placement | A | 68 code placements survive capture and ODB export |
| Two-layer routing | A | Six source Route segments, two vias, actual copper on layers 0/1; full board incomplete |
| DRC-equivalent validation | B | Four engine-enforced copper constraints; narrow observer checks; no complete DRC/unrouted certificate |
| Direct Gerber | C | No supported direct command/workflow established in pinned JITX; downstream KiCad export available |
| Direct Excellon drill | C | No direct command established; ODB has plated and non-plated hole data |
| BOM | B | Public project exporter creates 68-row review CSV; orderable identities incomplete |
| PnP/centroid | B | Public capture creates review CSV; independently agrees with ODB positions/angles; JLC orientation unqualified |
| ODB++ | B | Installed public legacy export produces an archive; content ordering/IDs vary |
| Paste/assembly layers | B | Present in ODB++; features inspected; not standalone JLC Gerber layers |
| Fabrication drawing | N/A | Separate project fabrication notes possible; automated drawing not required by this proof |
| Non-interactive generation | B | Build/capture/ODB repeat from source; public runtime capture explicitly experimental |

Machine-readable matrix: `evidence/capability-matrix.json`.
A supported Route/Via API does not mean a complete automatic multilayer router
has been demonstrated. C labels describe the investigated pinned workflow, not
an assertion that JITX can never support these outputs.

## 5. Physical wrapper architecture

`M1FourKeyPhysicalQualification` binds a `QualificationBoard`,
`QualificationSubstrate`, and `M1PhysicalQualificationCircuit`.
The circuit subclasses `M1ElectricalCircuit`, calls its existing constructor,
and adds physical placement and routing objects. There is no duplicated
component population, replacement schematic, net rewiring or electrical fork.
The original `M1FourKeyElectrical` remains untouched.

Board: 80 × 60 mm rectangle centered at the origin; signal area 79 × 59 mm.
The nominal stack is mask 0.015 / copper 0.035 / FR4 1.10 / copper 0.035 /
mask 0.015 mm. Total is 1.20 mm including modeled mask, 1.17 mm without it.
This documents the thickness convention rather than claiming a JLC fabrication
quote. FR4 Dk 4.2 / loss tangent 0.02 are nominal qualification values, not
manufacturer-certified material properties or impedance targets. One through
via type: 0.65 mm pad, 0.30 mm mechanical drill, layers 0–1, tented, unfilled.
Nominal total-thickness/drill aspect ratio is 4:1; annular ring is 0.175 mm.

## 6. Placement result

All 68 components are explicitly placed in source, on top. The USB datum is
(-25, -24.5) mm, near the lower edge with its accepted lands inset. The MCU is
(-14, 0); flash/crystal/decoupling are grouped nearby. LDO/load-switch and their
support are grouped at the lower right of the MCU island. Hall devices are at
(28, -12/-4/4/12), with mux at (16, 0). Seventeen probe points have explicit
accessible locations. No production placement, SI, courtyard or mechanical
fit quality is claimed.

The observer compares pre-submission source poses with captured poses and
composes public parent and element transforms. It finds no cross-component
copper-pad overlap and no copper pads outside the board. An independent parser
checks all 68 ODB component positions and orientations against PnP review rows.
ODB angles are clockwise; JITX rows use CCW. This tests export consistency, not
supplier zero-angle conventions. Pad checks do not cover body/courtyard or
silkscreen collisions. Compact placement/route observations are committed as
validation evidence, not fabrication files.

## 7. Routing result

Six `Route` objects realize actual copper, confirmed by public `Route.traces`
geometry: Hall 0 OUT → top via → bottom via-to-via route → top probe;
Hall 1/2/3 OUT → their probes on top. Two vias are connected through public
`PortAttachment`; the original component-port graph is unchanged.

This is **partial routing**. All four mux endpoints on those Hall nets remain
unrouted, as do the other required circuit interconnections. The manifest
lists every resolved component endpoint group and its conservative routing
status, plus accepted unconnected component endpoints. USB SHIELD's single
semantic endpoint maps several physical stakes and still needs physical pad
connectivity review. Empty declarations/NCs retain C2 semantics.

The documented interactive router works one layer at a time with selected
pads/vias; source `Route`/sketch and via definitions provide deterministic
routing intent. No complete non-interactive multilayer auto-route-all command
was established from the public documentation/installed CLI. Source routing
is supported, but manually specifying and reviewing the entire 68-component
board was not forced merely to claim a green gate. The incomplete board is
not fit for fabrication and is a material C4C limitation for AI-driven work.

## 8. Design rules and validation result

All dimensions below are mm and are **qualification defaults**:

| Rule | Value | Enforcement/verification |
| --- | --- | --- |
| Copper width floor / default trace | 0.15 / 0.20 | Engine-generated copper / source design rule |
| Copper spacing floor / default | 0.15 / 0.20 | Engine / source design rule |
| Copper-to-hole / board edge | 0.25 / 0.50 | Engine-generated copper |
| Annular ring / drill minimum | 0.15 / 0.30 | Documentary; qualification via meets them |
| Leaded / BGA pitch minimum | 0.40 / 0.50 | Documentary; no new component qualification |
| Max board width/height | 80 / 60 | Documentary; explicit board dimensions |
| Silkscreen width/text height | 0.15 / 1.0 | Documentary |
| Silk-to-mask spacing | 0.15 | Documentary |
| Mask registration/opening/bridge | 0.05 / 0.15 / 0.10 | Documentary |
| TH outer pad expansion | 0.10 | Documentary |
| Hole-to-hole / PTH solder clearance | 0.25 / 0.20 | Documentary |
| Pad thermal relief gap/spoke/count | 0.25 / 0.25 / 4 | Source rule; no pours in this fixture |

The official FabricationConstraints reference explicitly limits automatic
engine enforcement to the four copper fields. Build status `ok` is not a
complete DRC or routing certificate. Source-route realization, pad overlap,
board containment, source-pose preservation and ODB/PnP comparisons pass.
Full connectivity, independent clearance/track/via/pad/mask/silk/fab DRC and
unrouted detection have **not** been demonstrated end-to-end. There are no SI
constraints or impedance claims. JITX's headless build output alone cannot
establish JLCPCB manufacturability. GUI Issues/DRC review was not performed;
public captured geometry and explicit endpoint accounting are the limited
fallback, rather than a claimed full DRC substitute.

## 9. Manufacturing outputs

Supported `legacy-odb++` creates:
`designs/<qualification-design>/outputs/odb.zip`, with profile, EDA and CAD
netlists, component records, two copper layers, top/bottom mask, paste,
overlay, plated drill tools/features and non-plated routing/hole features.
Actual layer names/inventory and SHA-256 hashes are in the manifest.
The project `physical-qualification` exporter produces
`physical-observation.json`, `electrical-graph.json`, `bom-review.csv` and
`pnp-review.csv` under `designs/c4b/run-{1,2}`. Generated packages are ignored;
only hashes, manifests and validation observations are committed.

The supported `legacy-kicad` command also creates a `.kicad_pcb` and companion
schematic/library data. It was tested without editing those outputs.
`kicad-cli` is not installed here. A downstream plotting-only CAM step could
retain JITX as the design source; it is distinct from moving design authority
into KiCad. That workflow, Gerber/Excellon integrity and DRC equivalence were
not demonstrated, and no external CAD round-trip was used to bypass this gate.
No direct JITX Gerber/Excellon package was generated. An ODB archive is not
silently substituted for the requested Gerber/drill acceptance criteria.
No fabrication drawing, STEP assembly or independent drill map was required
or demonstrated; PCB outline and paste are present in ODB.

## 10. Determinism

Final repeated generation uses unchanged hashed source, fresh fixture-generated
state and runtime restarts. The manifest records each file's SHA-256, all ODB
entry hashes, raw classifications and narrow semantic comparisons. In the final
pair, 38 of 39 ODB entries are byte-identical; the remaining top-copper feature
file differs in record order/IDs and passes the narrow multiset comparison.
BOM/PnP reviews, electrical graph and public physical observations are
byte-identical. ODB ZIP timestamps differ, and ODB feature/netlist ordering or
feature IDs can differ across fresh runs. These remain classified as raw
non-deterministic content, rather than being hidden as metadata.
The read-only multiset comparison removes only feature `;ID=` values and
compares records without changing any geometry/numeric/net attributes; it
provides narrower semantic evidence and makes no complete ODB cross-link
equivalence claim. Only verified creation/save timestamp-only differences
would receive the metadata-only classification. Gerber/Excellon determinism
is unsupported because those files were not generated.

## 11. JLCPCB handoff

**EDA output capability:** public placement/copper capture, ODB fabrication data,
and project BOM/PnP review CSVs work. A complete Gerber/Excellon handoff, fully
routed connectivity, complete DRC and qualified orientation mapping are missing.
The ordinary JLCPCB PCBA flow requests Gerber, BOM and CPL; this package cannot
be called ready for that flow. No upload, quote submission or order was made.
[JLCPCB component matching requirements](https://jlcpcb.com/help/article/component-matching-guidelines-for-pcba-orders),
[Gerber layer/drill guidance](https://jlcpcb.com/help/article/gerber-files-preparation).

**Product BOM completeness:** twelve manufacturer-specific instances have the
accepted MPN/JLC metadata (nine distinct models, four Hall instances).
Generic passives, LEDs, two-terminal button scaffolds and seventeen test-point
models lack orderable identities. The 68-row CSVs intentionally inventory the
fixture, including test points; they need assembly-population filtering,
BOM grouping/value formatting and supplier/orientation review before use.
Blank supplier identities are preserved; none were invented. Footprint-origin
positions are reviewable and match ODB, but supplier centroid/zero-angle
conventions and lower-left origin policy remain unqualified. These sourcing
and assembly choices are separate from the EDA capability gaps.

## 12. AI / source-control suitability

Concrete positives: direct placement diffs are readable; all 68 poses are
fixed in Python; six route intents/vias are editable through public APIs;
real builds and capture checks run automatically; the observer detects missing
poses, failed source routes, pad overlaps and ODB/PnP mismatches. Fresh-state
regeneration does not use GUI-authored placements/routes. Original topology
is compared independently and C2 remains enforced. No private APIs are called.

Concrete limits: complete multilayer routing and automatic full-board
unrouted/DRC failure detection are not established; substantial explicit route
intent or interactive work would still be required. Public runtime capture is
experimental. ODB feature order/IDs impede byte-level review, though captured
geometry and CSVs repeat. Supplier rotation validation and Gerber/drill CAM
remain open. The evidence supports automated **partial** physical work, not
an unattended Rev.M1 manufacturing pipeline.

## 13. Electrical regression and validation

The final real export of unchanged `M1FourKeyElectrical` passes the unchanged
C2 comparator: **68 components, 200 normalized endpoints, 43 named nets,
185 endpoint/net edges, four direct links, seven intentional NCs**, plus
23 accepted unused physical GPIOs. The wrapper's original component metadata
and component-port membership match that live electrical export; only two
physical via attachments are excluded from that separate comparison.

The validation record covers locked sync, 20 existing C0/C1/C2 tests including
bootstrap and independent real C2 exports, real electrical/physical builds,
five-layer/two-conductor/1.2 mm structural check, placement/route capture,
two manufacturing generations, ODB/PnP checks, ruff, Python compilation,
JavaScript syntax, diff whitespace and protected-file verification.
Pyright is unavailable in the activated environment and was not installed;
this is an explicit static-type validation gap, not a claimed pass.

## 14. Review and limitations

`jitx-code-review` same-model review: no remaining CRITICAL or WARNING code
findings. Parent/element transform composition was corrected before evidence.
Exporter identity dictionaries are serialization records, never a parallel
scene graph; type-name labeling is observation only. No reflection-based
component dispatch, private framework call, copied skill code or generated
artifact modification is used.

The skill-requested independent read-only review initially found CRITICAL 0,
WARNING 2, NOTE 3. Both warnings were fixed: all imported local design/parity
sources are hashed, and metadata classification verifies exact timestamp
fields. The landpattern-transform note was also fixed. Final independent
review: CRITICAL 0, unresolved WARNING 0, retained NOTE 2 (incomplete
routing/DRC; unqualified JLC orientation). These are gate limitations,
explicitly retained in the BLOCKED verdict, not silently accepted production
risks. No broad C3 research or component-model correction was necessary.

Task acceptance: board/stack/source placement and partial two-layer source
routing are demonstrated. The complete-board manufacturing acceptance is
**blocked**, with full routing/DRC and direct Gerber/drill handoff open.
Phase 0 scope/data are authorized by the task; existing C1/C2 are retained
inputs. Assembly and physical experiments build; the four-pass design audit
is restricted to checking unchanged application circuits/voltage domains,
original interface memberships and unchanged power tree. It makes no new
production/SI/thermal qualification. Phase 4 narrow checks pass; full board
acceptance does not. The independent review is a second perspective requested
by the installed skill, not a new electrical redesign.

## 15. C4C recommendation input

C4B **does not prove the required complete pipeline**. G0A can now review a
concrete BLOCKED result and decide whether supported multilayer routing,
complete validation, qualified CAM/Gerber/drill generation and orientation
mapping warrant further investment. The availability of supported ODB and
KiCad exports is useful positive evidence, not proof that the missing steps
are impossible or a waiver of the agreed criteria. Preserve C0–C3 and C2 PASS
regardless of that decision.

EDA-002C4C is next / Human Gate. G0A is ready-for-decision on this blocked
evidence, **not GO**. G0B remains not-ready; EVT-002 remains blocked/unstarted.
No D-016 is created. Do not merge this PR automatically.
