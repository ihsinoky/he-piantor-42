# HE Piantor 42

42-key Hall-effect keyboard targeting a unified reverse-V assembly. D-015
defines reusable Main + Left/Right Wings; future Wing geometry must be
project-owned or explicitly approved.

> [!WARNING]
> **Experimental hardware:** M1 and the planned Rev.A are engineering work in
> progress. No PCB has completed physical validation, and this repository does
> not describe a production-ready keyboard. Do not order or manufacture from
> the current files without completing the documented review gates.

## Target

- 42 keys
- Piantor-derived column-staggered layout
- Unified reverse-V keyboard assembly; modular Main + Wings
- Evaluate 17.0 / 16.5 / 16.0 mm pitch; production pitch remains open
- Full-height Hall-effect magnetic switches
- USB-C wired only
- Vial-compatible keymap, 4 layers
- Dedicated power indicator LED
- Separate layer indicator LED
- JLCPCB PCBA target
- FDM-printable enclosure

## Development flow

1. Freeze switch / keycap / geometry requirements
2. Complete G0A EDA adoption and G0B Main/Wing architecture/interface freeze
3. Design reusable Main + Evaluation Wing(s); complete G1 before ordering
4. Measure magnetic, pitch and actual interconnect behavior; decide G2
5. Reuse accepted Main with Left/Right 21-key Wings for Rev.A
6. Implement Vial + Hall-effect firmware
7. Finalize enclosure
8. Generate JLCPCB and 3D-print manufacturing packages
9. Bring-up and validation

The authoritative status, including the permanent frozen four-key qualification
fixture, separate physical Rev.M1 Main/Wing architecture and implementation gates, is in [`docs/project-status.md`](docs/project-status.md).
`task/index.html` is a non-authoritative dashboard read model.

## Contribution status

Public release is completed, as recorded in
[`docs/public-release-readiness.md`](docs/public-release-readiness.md).
Hardware design contributions are not currently being accepted while the JITX
EDA evaluation gate remains unresolved. Prospective contributors should start
with an Issue and follow
[`docs/development-workflow.md`](docs/development-workflow.md); a green CI run
does not replace Product Owner approval.

## Licensing

This is a mixed-license repository:

- project-authored hardware, mechanical, and manufacturing designs use
  CERN-OHL-P-2.0;
- project-authored firmware, software, scripts, dashboard, and documentation
  use the MIT License; and
- third-party files retain their original licenses and notices.

See the authoritative [`LICENSE.md`](LICENSE.md) path map, the full texts under
[`LICENSES/`](LICENSES/), and the canonical
[third-party inventory](hardware/lib/THIRD_PARTY.md). Items marked **REVIEW
REQUIRED** are public-release blockers, not an assertion of ownership.

Public-release audit evidence and the current Human Gate result are documented
in [`docs/public-release-readiness.md`](docs/public-release-readiness.md). This
repository has completed public release; the hardware remains experimental and
is not production-ready.
