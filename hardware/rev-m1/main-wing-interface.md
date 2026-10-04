# Main/Wing logical interface contract

Requirements only; no connector footprint or MPN is selected. This boundary
must support Rev.A's two banks of three TMUX1208, even if the first Evaluation
Wing populates fewer channels. See [D-015](../../docs/decisions.md) and
[acquisition baseline](../../docs/hall-acquisition.md).

## REQUIRED LOGICAL SIGNALS

| Signal/domain | Ownership and requirement |
| --- | --- |
| HALL_5V | Main generates switched USB-derived Hall power; Wing supplies Hall sensors and TMUX1208 from it. Measure load, startup and voltage at the Wing. |
| GND / analog reference | Shared Main/Wing return and ADC reference relationship; control return impedance and measure ground offset/noise. Physical return allocation remains TBD. |
| MUX_A0, MUX_A1, MUX_A2 | Main drives shared 3.3 V address control to Wing TMUX1208. Define sampling timing after source/address changes. |
| Wing/bank enable | Main controls each Wing/bank independently (Rev.A MUX_EN0/MUX_EN1); only one bank enabled at a time when analog outputs share ADC paths. Require safe startup/disabled behavior and review transition timing. |
| Three analog MUX outputs | Production-compatible Wing exposes groups A/B/C for Main ADC0/1/2. First Wing may use fewer; test coverage must still represent future loading and cross-channel behavior. |
| Additional control/reference | Identify any required signals during interface design and review at G0B; no final pin count is asserted here. |

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
return path must be reviewed at G0B, not bypassed for measurement convenience.

## TBD PHYSICAL CONNECTOR IMPLEMENTATION

Exact connector type/MPN, pin count/order, ground/reference and shielding
allocation, cable or board-to-board mechanics, retention, orientation/keying,
interconnect length and routing, power capacity, and test access are TBD.
G0B must review connector selection and pinout together with production-bank
compatibility and the experiments before Rev.M1 schematic/PCB work proceeds.
No connector selection or layout occurs in C4A.
