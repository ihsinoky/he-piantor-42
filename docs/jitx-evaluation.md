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

## EDA-002C0 built-design graph introspection — PMO STOP

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

### Real build and generated data

`uv run jitx build he_piantor_42_jitx.main.HePiantor42Bootstrap` completed with
`status: ok`. The non-dry build produced:

- `cache/netlist.json`: resolved net names and endpoint groups
- `cache/design-explorer.json`: a richer internal graph with component,
  hierarchy, pin, net, package, and geometry entries
- `design-info/stable.design`: a richer JSON design snapshot
- `design-info/reference-designators.table`: built component-ID to generated
  reference-designator mapping

The bootstrap proof shows that the built design, rather than project Python
source, contains the requested graph facts. However, this does **not** clear
the graph-export gate. JITX public documentation does not document any of the
four file names or schemas as a public, stable graph-export API. A second
identical non-dry build changed the raw SHA-256 hashes of `stable.design` and
`netlist.json`; the reference-designator table was byte-identical. The richer
files also use generated identifiers that cannot be accepted as a stable
semantic identity contract without vendor documentation.

### Decision and limitation

The only currently visible route to a normalized graph with component identity,
type, pins, nets, endpoints, generated reference designators, and geometry
would be parsing undocumented JITX-generated internal payloads. EDA-002C0
does not do that. It adds no exporter and no bootstrap graph self-test, because
doing so would silently depend on an unsupported schema and weaken the parity
requirement.

The intended semantic identities (`U_MCU`, `U_FLASH`, `U_MUX`, `J_USB`) cannot
yet be mapped through a JITX-supported, repeatable object identity mechanism.
Future work must use a vendor-supported public graph API or documented stable
output that provides deterministic hierarchical paths or explicit project
metadata. Until then, full M1 machine graph parity is **not technically
feasible**. This is an acceptable STOP result for PMO review, not a completion
claim for M1 electrical parity.
