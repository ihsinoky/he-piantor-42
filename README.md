# HE Piantor 42

42-key one-piece Hall-effect keyboard derived from the Beekeeb Piantor layout.

> [!WARNING]
> **Experimental hardware:** M1 and the planned Rev.A are engineering work in
> progress. No PCB has completed physical validation, and this repository does
> not describe a production-ready keyboard. Do not order or manufacture from
> the current files without completing the documented review gates.

## Target

- 42 keys
- Piantor-derived column-staggered layout
- One-piece reverse-V geometry
- 17.0 mm key pitch target
- Full-height Hall-effect magnetic switches
- USB-C wired only
- Vial-compatible keymap, 4 layers
- Dedicated power indicator LED
- Separate layer indicator LED
- JLCPCB PCBA target
- FDM-printable enclosure

## Development flow

1. Freeze switch / keycap / geometry requirements
2. Design and manufacture a small Hall-sensor evaluation PCB
3. Measure sensor range, noise and travel curve
4. Finalize the 42-key PCB
5. Implement Vial + Hall-effect firmware
6. Finalize enclosure
7. Generate JLCPCB and 3D-print manufacturing packages
8. Bring-up and validation

The authoritative status, including the frozen M1 electrical golden reference
and the placement/routing gate, is in [`docs/project-status.md`](docs/project-status.md).
`task/index.html` is a non-authoritative dashboard read model.

## Contribution status

The project is preparing for a public-release Human Gate. Hardware design
contributions are not currently being accepted while third-party provenance and
the JITX EDA evaluation gate are unresolved. After the repository is approved
for public release, prospective contributors should start with an Issue and
follow [`docs/development-workflow.md`](docs/development-workflow.md); a green
CI run does not replace Product Owner approval.

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
repository has not been declared public or production-ready by that report.
