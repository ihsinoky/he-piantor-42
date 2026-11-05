# Main/Wing accepted interface contract

[D-017](../../docs/decisions.md#d-017---revm1-mainwing-architecture-and-interface-freeze) / Issue #57 PO GO accepts this boundary. No connector
footprint or physical board is implemented. This boundary
must support Rev.A's two banks of three TMUX1208, even if the first Evaluation
Wing populates fewer channels. See [D-015](../../docs/decisions.md) and
[acquisition baseline](../../docs/hall-acquisition.md).

## REQUIRED LOGICAL SIGNALS

| Signal/domain | Ownership and requirement |
| --- | --- |
| HALL_5V | Main generates switched USB-derived Hall power; Wing supplies Hall sensors and TMUX1208 from it. Measure load, startup and voltage at the Wing. |
| GND / analog reference | Shared Main/Wing return and ADC reference relationship; control return impedance and measure ground offset/noise. Six physical return contacts join common GND; see the accepted pin table below. |
| MUX_A0, MUX_A1, MUX_A2 | Main drives shared 3.3 V address control to Wing TMUX1208. Define sampling timing after source/address changes. |
| Wing/bank enable | Main controls each Wing/bank independently (Rev.A MUX_EN0/MUX_EN1); only one bank enabled at a time when analog outputs share ADC paths. Each `WING_EN` requires an explicit external Main-side hardware pull-down; exact resistor value remains implementation work. Switched HALL_5V stays default-off. Review transition timing. |
| Three analog MUX outputs | Production-compatible Wing exposes groups A/B/C for Main ADC0/1/2. Three TMUX1208 / three ADC paths and full-load electrical coverage are required; pitch Wings use the accepted coverage contract. |
| Additional control/reference | No reserved/additional signal is allocated. Any new requirement must reopen the accepted interface rather than repurpose GND. |

Analog boundary: Hall -> TMUX (Wing) -> connector/interconnect -> Main
6.8 kOhm / 10 kOhm divider + 1 nF provisional filter -> RP2040 ADC.
ADC dividers and filters remain on Main; raw HALL_5V-domain signals must not
bypass conditioning into the 3.3 V ADC domain. Main owns 3.3 V logic/core
power; a Wing 3.3 V supply is not assumed without interface review.

Decoupling ownership: Main owns source-rail bulk/local decoupling and MCU/ADC
reference conditioning. Wing owns local Hall and TMUX supply decoupling near
the loads. Exact values, return routing and interconnect transient response
remain implementation work; validate them as a complete path.

Testability requires accessible raw Hall outputs, MUX outputs on both sides
of the interconnect, filtered ADC nodes, HALL_5V and ground at Main and Wing,
address/enable visibility and Main SWD/reset/BOOTSEL access. Record disabled,
startup and bank/address-change behavior, clipping margin, settling, noise,
repeatability and coupling. Representative interconnect length/loading and
return path are frozen for evaluation in the accepted G0B record and must
not be bypassed for measurement convenience.

## Accepted connector / pin allocation

JST GH 14-position: `BM14B-GHS-TBT(LF)(SN)` header, `GHR-14V-S` housing,
`SSHL-002T-P0.2` contacts. The authoritative exact pin allocation and return
rationale are in [accepted G0B section 3](g0b-freeze-proposal.md#3-accepted-exact-14-pin-interface).
The evaluation harness is nominal 100 mm, 14 separate conductors, wired 1:1;
see [section 4](g0b-freeze-proposal.md#4-accepted-representative-evaluation-interconnect).
[Section 6](g0b-freeze-proposal.md#6-production-equivalent-mux-and-bank-evidence)
records the external pull-down and startup contract; section 7 records test access.

Final Rev.A cable mechanics/length, exact pull-down resistance, native footprint,
placement and routing remain implementation work. Full Rev.M1 implementation
is not active: G0B accepted -> EDA-003B representative routing proof -> if
accepted, full Rev.M1 implementation.
