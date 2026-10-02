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
