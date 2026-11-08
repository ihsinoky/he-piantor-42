# HE Piantor 42

42-key Hall-effect keyboard targeting a unified reverse-V assembly. D-015
defines reusable Main + Left/Right Wings; future Wing geometry must be
project-owned or explicitly approved.

> [!WARNING]
> **Experimental hardware:** Main Rev.4, Matrix Rev.3, Wing Rev.3 and the final
> case data are design baselines. No PCB has completed physical validation,
> and this repository does
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

The design baseline is Main Rev.4 / Matrix Rev.3 / Wing Rev.3 / final case data.
Start with the [current artifacts index](docs/artifacts-index.md) for CAD,
manufacturing packages, case exports and recorded verification.
[Project status](docs/project-status.md) is authoritative for outstanding gates:
Order 1 awaits PO GO, production pitch awaits Matrix measurements, and physical
validation is pending. The [dashboard](task/index.html) shows the milestone plan
and current position as a non-authoritative read model.

## Contribution status

Public release is completed, as recorded in
[`docs/public-release-readiness.md`](docs/public-release-readiness.md).
JITX physical-backend evaluation concluded NO-GO (D-016); it is historical,
not an unresolved current design gate. Prospective contributors should start
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

設計の世代・過去の試行・証跡は [履歴索引](docs/history-index.md) を参照。
