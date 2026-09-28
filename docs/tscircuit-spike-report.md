# tscircuit Hall-key technical spike (Issue #13)

Status: **STOPPED at STOP 4 — non-reproducible result; Human Gate required**

This report records a strictly scoped investigation. It does not make the
Product Owner's GO / NO-GO decision. No tscircuit design source or generated
manufacturing data was committed because the required locked toolchain could
not be obtained in the Codex Cloud execution environment.

## Execution context and source protection

- Execution date: 2026-09-28 (UTC).
- Starting commit: `0168de45e5b8fcafa724c3603642f675f626efeb`
  (`Establish Issue #7 development governance (#8)`). This was the newest
  locally available commit. The checkout has no configured Git remote, so the
  requested refresh from `main` could not be performed or independently
  verified.
- Issue branch: `issue-13-tscircuit-spike`.
- The complete Issue #13 work contract supplied to Codex was used as the spike
  specification. GitHub CLI could not retrieve the hosted copy because it had
  no authentication or repository remote.
- The protected schematic
  `hardware/sensor-test/kicad/integrated-sensor-test.kicad_sch` was not
  modified. The named protected PCB
  `hardware/sensor-test/kicad/integrated-sensor-test.kicad_pcb` is absent from
  the starting commit and working tree; it was not created or modified. No
  KiCad library or footprint was modified, deleted, or rewritten.
- The authoritative footprint input remains
  `hardware/lib/third_party/marbastlib-he.pretty/SW_MX_HE_0deg_1u.kicad_mod`.

## Dependency installation and exact versions

Intended installation method: non-interactive `npm ci` from a committed
`package-lock.json` after selecting and pinning the tscircuit packages.

The registry could not be queried from this environment. Both package metadata
requests returned HTTP 403 from the configured network proxy:

```text
$ npm view @tscircuit/core version --json
npm error code E403
npm error 403 403 Forbidden - GET https://registry.npmjs.org/@tscircuit%2fcore

$ npm view circuit-json-to-kicad version --json
npm error code E403
npm error 403 403 Forbidden - GET https://registry.npmjs.org/circuit-json-to-kicad
```

`git ls-remote https://github.com/tscircuit/core.git HEAD` also failed with
`CONNECT tunnel failed, response 403`. The npm cache contained no tscircuit or
Circuit JSON package that could be used offline.

Consequently:

- exact tscircuit version: **NOT DETERMINED / NOT INSTALLED**;
- exact related dependency versions: **NOT DETERMINED / NOT INSTALLED**;
- lockfile: **NOT CREATED** (inventing versions or a lockfile would not be
  reproducible evidence);
- authentication required by tscircuit itself: **UNKNOWN**;
- paid/free requirements: **UNKNOWN**;
- observed external-network dependency: access to the public npm registry (or
  an equivalent approved package mirror) is required to select and install the
  toolchain; access was denied by the Codex Cloud proxy.

This is an execution-environment limitation, not evidence that the public
packages themselves require authentication or payment.

## Commands used and Codex Cloud result

The relevant investigation commands were:

```sh
git status --short --branch
git remote -v
gh issue view 13 --json number,title,body,state,url
git switch -c issue-13-tscircuit-spike
npm view @tscircuit/core version --json
npm view circuit-json-to-kicad version --json
npm search tscircuit kicad --json
npm cache ls
git ls-remote https://github.com/tscircuit/core.git HEAD
```

Codex Cloud result: branch creation and local repository inspection succeeded.
GitHub access and npm/GitHub dependency discovery were blocked (GitHub CLI had
no login; outbound registry and GitHub connections returned HTTP 403).

## Capability evidence

| Investigation item | Result | Evidence / reason |
| --- | --- | --- |
| Minimal DRV5055A3 circuit | NOT DEMONSTRATED | No verified, locked tscircuit toolchain was available. |
| Hall sensor count and nets | NOT DEMONSTRATED | No Circuit JSON/design output was generated; therefore no API output existed to check. |
| Required Hall footprint assigned | NOT DEMONSTRATED | The supported local KiCad-footprint import API could not be established from installed tooling or documentation. |
| Footprint import | NOT DEMONSTRATED | Import was not attempted without a verified API. No substitute footprint was fabricated. |
| Pad count and positions | NOT DEMONSTRATED IN TSCIRCUIT | The authoritative file was inspected only; no imported representation existed for comparison. |
| Drill/mechanical holes | NOT DEMONSTRATED IN TSCIRCUIT | Same limitation. |
| Hall sensor pad location | NOT DEMONSTRATED IN TSCIRCUIT | Same limitation. |
| Keepout behavior | NOT DEMONSTRATED | No importer/output was available to show whether source keepouts survive conversion. |
| Four copper layers | NOT DEMONSTRATED | No verified tscircuit board representation was generated. |
| Native DRC | NOT RUN | No installed tscircuit toolchain. |
| Repository-specific checks | NOT IMPLEMENTED OR RUN | Implementing checks against invented output/API structures would create false evidence. |
| GitHub Actions | NOT RUN / NOT ADDED | A workflow without a real lockfile and verified commands could not meet the clean-checkout CI requirement. Existing KiCad CI was left unchanged. |

The absence of these demonstrations must not be interpreted as proof that
tscircuit lacks the capabilities. It means this execution did not produce
evidence for them.

## Manufacturing-output investigation

No fake or placeholder manufacturing files were created.

| Output | Required classification | Evidence / specific reason |
| --- | --- | --- |
| Gerber | **UNKNOWN — toolchain and non-interactive export API could not be installed or inspected** | npm and GitHub access were blocked. |
| Drill | **UNKNOWN — toolchain and non-interactive export API could not be installed or inspected** | npm and GitHub access were blocked. |
| BOM | **UNKNOWN — toolchain and non-interactive export API could not be installed or inspected** | npm and GitHub access were blocked. |
| Pick-and-place / CPL | **UNKNOWN — toolchain and non-interactive export API could not be installed or inspected** | npm and GitHub access were blocked. |

No conclusion can be drawn about authentication or paid-plan requirements for
these exports from the evidence available in this run.

## STOP condition and limitations

**STOP 4 — non-reproducible result was reached.** A clean checkout with locked
dependencies could not be demonstrated because package metadata and packages
were inaccessible and no cached toolchain existed. Creating guessed dependency
versions, handwritten generated Circuit JSON, or imitation outputs would
contradict the Issue's reproducibility and generated-file rules.

STOP 1 was not positively reached: footprint integrity was not tested at all.
It remains a mandatory unresolved gate for a resumed spike. STOP 2, STOP 3, and
STOP 5 were not demonstrated.

The spike therefore stopped before implementation, CI workflow creation, DRC,
or artifact generation. This preserves the baseline and avoids converting an
environment failure into unsupported claims.

## Acceptance Criteria status

- Isolated, pinned tscircuit project: **not demonstrated**.
- Minimal Hall-key circuit: **not demonstrated**.
- Authoritative footprint imported and verified: **not demonstrated**.
- Four-copper-layer representation: **not demonstrated**.
- Automated electrical/project checks: **not demonstrated**.
- Non-interactive CI and artifact upload: **not demonstrated**.
- Manufacturing-output capability classifications: **recorded as UNKNOWN with
  the specific investigation blocker**.
- Existing KiCad baseline protected: **demonstrated by the branch diff**.
- Factual spike report: **demonstrated by this document**.

## Evidence for the Human Gate

The current evidence is insufficient for either a tscircuit GO or a technical
NO-GO. It does establish that this Codex Cloud environment cannot presently
bootstrap the required JavaScript toolchain from the public package/source
hosts. The PO/PMO should distinguish that infrastructure limitation from
tscircuit product capability.

If the spike is resumed after the Human Gate, the minimum next step is to
provide non-interactive access to an approved npm mirror or a repository-owned,
integrity-checked dependency source. The resumed work must still independently
verify the local KiCad footprint import (especially mechanical holes, Hall pad,
and keepouts), four-layer output, native DRC, and every manufacturing export;
none should be presumed from this report.

No final GO / NO-GO recommendation is made here.
