# JITX EDA evaluation

## EDA-002A capability checkpoint

EDA-002A started on 2026-10-02 with an environment capability probe against
repository commit `668e892b63de099a40cfcc5427775e761e800785` (the fetched `main`
head in this checkout). The probe reached the required **HUMAN / ENVIRONMENT
STOP** before project bootstrap.

The observed environment was:

| Capability | Observation | Result |
| --- | --- | --- |
| Python | `Python 3.14.4` | Passes the Python 3.12 minimum. |
| JITX CLI | `jitx` was not present on `PATH`; therefore no CLI version could be observed. | Blocked. |
| JITX runtime | `jitx runtime introspect` could not run because the CLI was absent; no runtime version was observed. | Blocked. |
| Authentication | `jitx auth show` could not run because the CLI was absent; authentication state is unknown, not authenticated-by-assumption. | Blocked. |
| Package/release alignment | No JITX package or runtime version was observable, so same-release-line compatibility could not be established. | Blocked. |
| Official skill | No JITx-Inc JITX skill was installed in the available Codex skill directories. | Unavailable. |
| Outbound access | Requests to GitHub, JITX documentation, and the Python package index were rejected by the environment proxy with HTTP 403. | Blocked. |
| Bootstrap build | Not attempted: the required CLI, runtime, version match, and authentication were not established. | **Not run; not PASS.** |

### Human/environment action required

Provide an environment with outbound access to the official JITX distribution
and service, install the JITX CLI and runtime, and complete `jitx auth show`
authentication through the required human workflow. Then rerun the probe,
record the actual CLI/package/runtime versions, confirm that package and runtime
use the same release line, and only then exact-pin the verified package version
and run a real non-interactive bootstrap build.

Because the bootstrap gate was not reached, this increment deliberately does
not create `hardware/jitx/pyproject.toml`, guess a JITX version, claim a build
result, or freeze `hardware/jitx/parity/m1-parity-contract.json`. The parity
contract and full M1 JITX electrical parity remain subsequent work after a
successful environment/bootstrap gate.

## EDA-002B GitHub Codespaces bootstrap

EDA-002B ran on 2026-10-03 with GitHub Copilot CLI in GitHub Codespaces, a
separate environment from the historical Cloud Codex probe above. It passed
the environment/bootstrap feasibility gate without changing the frozen
tscircuit reference.

| Capability | Observation | Result |
| --- | --- | --- |
| Outbound access | Project dependency resolution reached the JITX package index. | Pass |
| Python | `Python 3.14.2` | Pass |
| JITX CLI/package | `jitx 4.4.3`; project dependency is exactly `jitx==4.4.3`. | Pass |
| Linux runtime | Release runtime `4.4.2` on Linux; deliberately not updated. | Pass |
| Authentication | `Authorized: yes`; plan `free`. | Pass |
| Headless runtime | `jitx runtime start --background` started a project-local runtime. | Pass |
| Design discovery | `jitx design find` found `he_piantor_42_jitx.main.HePiantor42Bootstrap`. | Pass |
| Bootstrap build | `jitx build he_piantor_42_jitx.main.HePiantor42Bootstrap` returned `status: ok`. | Pass |

The canonical CLI-owned project is under `hardware/jitx/`. Its bootstrap design
is deliberately only the JITX seed design, not an M1 implementation. The
machine-readable `hardware/jitx/parity/m1-parity-contract.json` freezes the
future M1 graph and design-data comparison requirements from the project-owned
frozen sources. Full M1 JITX electrical parity is the next increment.

The external JITX skill, where used, was an execution-time agent aid only. No
skill source, script, or other proprietary JITX skill material is retained in
this repository.

## Authority and license boundary

The frozen M1 electrical golden reference remains
`hardware/tscircuit/src/evaluation/m1-four-key.tsx`, verified by
`hardware/tscircuit/scripts/verify-m1-electrical.tsx`. JITX is only a challenger
backend and is not authoritative. D-014 is unchanged, and EVT-002 has not
started.

No 42-key coordinate source was opened, imported, copied, or used during this
probe. In particular, the GPL/QMK-derived files under `hardware/layout/` were
not consumed. Future project-authored `hardware/jitx/**` design material remains
covered by the repository's CERN-OHL-P-2.0 hardware license map, and the M1
2-by-2 Hall grid must be reconstructed only from project-owned M1 requirements
and the frozen M1 golden reference.

## EDA-002C0 built-design graph introspection — PASS

EDA-002C0 ran on 2026-10-03 against the existing bootstrap design. It did not
implement an M1 component, consume `hardware/layout/**`, modify the frozen
tscircuit authority, or start EVT-002.

### Reproducible dependency strategy

The JITX project now uses the standard `uv` lock workflow documented for JITX
CLI projects:

```bash
cd hardware/jitx
uv sync --locked --group dev
uv run jitx build he_piantor_42_jitx.main.HePiantor42Bootstrap
```

`hardware/jitx/uv.lock` is committed and records every exact resolved package
and artifact hash. The resolution used for this probe includes:

| Package | Resolved version |
| --- | --- |
| `jitx` | `4.4.3` |
| `jitxlib-standard` | `4.4.0` |
| `jitxcore` | `4.4.0` |
| `ruff` | `0.16.10` |

The existing Linux JITX runtime is release `4.4.2`. It was left unchanged;
the dependency-lock work did not use a runtime update merely to satisfy the
lock tool.

### Documented plugin and introspection proof

JITX 4.4.3 exposes the standardized `jitx.plugin.export.Export` interface.
The project registers `parity.exporter` through the `jitx-plugin` entry-point
group, and JITX discovers it as the documented command:

```bash
uv run jitx design export bootstrap-graph \
  he_piantor_42_jitx.main.HePiantor42Bootstrap --output <path>
```

The exporter receives the actual built `RuntimeDesign` in
`Export.submitted()` and uses `RuntimeDesign.query(Component | Port)`,
`RuntimeDesign.nets().find(port)`, `jitx.inspect.visit()`, and `Trace.path`.
It exports component instances, deterministic structural identities, component
types, ports, resolved net membership, and captured component placement
transforms. It does not parse project Python source or any generated JITX
artifact; `cache/netlist.json`, `cache/design-explorer.json`,
`design-info/stable.design`, and `reference-designators.table` remain
diagnostic-only evidence.

The real bootstrap export contains two resistor instances at `circuit.r1` and
`circuit.r2`, each with `p1` and `p2`, and exactly two resolved groups:
`{circuit.r1.p1, circuit.r2.p1}` and
`{circuit.r1.p2, circuit.r2.p2}`. Reference designators are intentionally not
used as semantic identity. The minimal bootstrap exposes captured placement
transforms, but no richer public physical geometry.

`tests/test_bootstrap_graph.py` runs the non-dry export twice, compares the
normalized JSON objects, and asserts those component, port, and connectivity
facts. Both exports were semantically identical.

### Stability classification and decision

| API | Classification | Result |
| --- | --- | --- |
| `jitx.inspect.visit`, `jitx.inspect.extract`, `Trace.path` | A — documented public API | Used for structural traversal and identity. |
| `jitx.plugin.export.Export`, project `jitx-plugin` registration, and `jitx design export` | A — documented public API | Used as the exporter lifecycle boundary. |
| `RuntimeDesign` supplied to `Export.submitted()` / `Export.export()` | A at the documented plugin boundary | The standardized export hook supplies the built design object. |
| `RuntimeDesign.query()` and `RuntimeDesign.nets().find()` | B — documented, explicitly experimental (`jitx.run`) | Used for component/port query and resolved connectivity. |
| Generated graph files and private modules/attributes | C — undocumented/private | Not used by the project parity contract. |

**EDA-002C0: done / accepted / PASS.** A project-authored normalized
electrical graph exporter works through documented JITX APIs, and no
category-C implementation is required. PMO accepted the category-B
`RuntimeDesign` query/net methods for the JITX challenger/parity evaluation
workflow because the documented `Export` boundary and `Trace.path` identity
are used, no private API or generated artifact is consumed, the Python
environment is locked at `jitx==4.4.3`, and deterministic end-to-end bootstrap
tests protect the dependency. This acceptance does not make `RuntimeDesign` a
stable API.

**Compatibility rule:** Any future JITX Python package or JITX runtime version
change must rerun and pass the EDA-002C0 normalized graph exporter and
bootstrap graph self-test before graph-parity compatibility may be assumed.
EDA-002C1 component modeling is merged / accepted; at C0, M1 implementation,
placement, routing, DRC, EVT-002, and changes to frozen tscircuit remain out
of scope.

## EDA-002C1 manufacturer components — merged / accepted

All nine required manufacturer models now pass their component-modeling checks.
The five accepted models were preserved; RP2040, USBLC6-2SC6, TYPE-C-31-M-12
and W25Q16JVUXIQ were completed after manufacturer-primary re-investigation.
RP2040 retains all 57 physical pins/pads, including ADC0 at pin 38 and its
manufacturer-specific 3.20 mm exposed GND pad. ST's exact functional map is
verified. HRO's official PDF Download path yielded the exact M-12 sheet, used
to author contact lands, four plated shell slots and two locating NPTHs.
Winbond's official current datasheet defines UX, its eight signals and narrow
exposed metal; a parameterized SON generator provides the copper lands.

The locked package 4.4.3, standard library 4.4.0, runtime 4.4.2 and `uv.lock`
remain unchanged. Twelve structural/regression tests pass, as does the separate
EDA-002C0 graph-export regression. All four new real non-dry builds pass;
format/lint, type checks for the four new component modules, frozen M1 verifier
and `git diff --check` pass. Manufacturer PDFs stay in ignored `.sources/`;
ST's exact family PDF was accessible through the official web PDF reader while
local curl downloads timed out. No skill source or distributor footprint
geometry was copied.

**EDA-002C1: done / accepted; PR #36 merged at a27fc48.** Component-modeling
PASS does not establish geometric parity. Official HRO land/shell/locator
geometry and Winbond generator lands differ from frozen M1 requirements; the
complete discrepancy table remains in `hardware/jitx/component-sources.md`.

## EDA-002C2 M1 electrical graph parity — PASS candidate

Issue [#37](https://github.com/ihsinoky/he-piantor-42/issues/37) implements
`he_piantor_42_jitx.m1.M1FourKeyElectrical` with all nine accepted manufacturer
models, four Hall sensors, and generic passives/LEDs/buttons/test points.
`m1-electrical-graph` extends the existing exporter via the documented Export
boundary, consuming the actual RuntimeDesign. Explicit project-owned
normalization maps structural instance paths and physical manufacturer ports to
frozen semantic endpoints; no fuzzy matching or manufacturer-port renaming is
used. The circuit does not consume normalization or expected contract data.

The comparator reports **PASS** for 68 components, 200 normalized endpoints,
43 named nets, 185 endpoint/net edges, four direct links and seven intentional
NCs. It also checks 23 extra physical RP2040 GPIOs remain unconnected, passive
values, approved model types, MPN/JLC identities and RP2040 physical assignments
through public pad mappings. Exact connectivity groups catch unexpected shorts
and edges. Empty named CC1/CC2 nets and unnamed CC direct links are both retained
from the golden source. Runtime graph names are associated with public named
Net objects through the same `nets().find()` relation as component ports.

Two independent real exports produced byte-identical raw and normalized JSON.
Twenty Python tests pass, including unchanged bootstrap regression and eight C2
integration/fault-injection tests. Locked sync, real M1 build, ruff, pyright for
all new/changed Python modules, frozen tscircuit verifier and diff checks pass.
Execution used the unchanged JITX package 4.4.3, standard library 4.4.0 and Linux
runtime 4.4.2. Detailed reproduction, review and evidence are in
`hardware/jitx/parity/EDA-002C2.md` and `hardware/jitx/parity/evidence/`.

**EDA-002C2: done / accepted candidate; electrical parity PASS; PMO review waiting.**
**Geometry parity NOT established.** Geometry is excluded from the verdict;
generic physical choices and sample board/substrate are non-authoritative build
scaffolding. No manufacturer geometry, frozen tscircuit source/verifier,
parity contract or uv.lock changed. `hardware/layout/**` was not consumed or
modified. No placement, routing, DRC readiness or manufacturing artifacts are
claimed. D-014 and tscircuit authority remain unchanged.

**EDA-002C3: manufacturer-vs-frozen geometry reconciliation / PMO Human Gate —
next / unstarted**, especially HRO and Winbond. Their discrepancies remain
unresolved. **EVT-002 remains blocked/unstarted.** Electrical PASS does not
release either gate.
