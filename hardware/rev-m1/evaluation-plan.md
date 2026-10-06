# Rev.M1 evaluation plan

Requirements only. The modular hardware and measurement firmware are not
claimed complete. [D-017](../../docs/decisions.md#d-017---revm1-mainwing-architecture-and-interface-freeze) / Issue #57 PO GO
accepted G0B and freezes the experiment structure and representative Main/Wing
interconnect. EDA-003B representative routing proof is next; if accepted, full
Rev.M1 implementation follows. G1 reviews the completed package before ordering.

The [accepted G0B record](g0b-freeze-proposal.md) is authoritative for the
three pitch-specific 3 x 3 Wings, 21-sensor full-load/electrical-load coverage,
three TMUX1208 / three ADC paths, test access and A/B/C measurement framework.

## Pitch / mechanical

Compare 17.0, 16.5 and 16.0 mm center spacing using documented switch/keycap
combinations, PCB thickness (1.2 mm baseline), alignment and travel setup.
Record typing feel, mechanical usability and switch/keycap interaction or
interference at each relevant pitch. Keep the historical D-002 clearance
rationale as evidence; none of the three pitches is the production decision.

## Magnetic

Measure travel curve and polarity, useful signal range and clipping margin,
repeatability/noise, adjacent-key magnetic crosstalk and pitch-dependent
interference. Include one-key sweeps, neighboring-key sweeps with the target
key stationary, and combined key positions/travel. Record sensor/switch sample
identity, spacing, alignment, travel reference, supply, temperature, sample
count and acquisition settings so comparisons are reproducible. Include
short-term thermal drift, Hall current and rail turn-on behavior retained from
D-011, plus the 42-key power-budget extrapolation. The accepted DRV5055 5 V
planning basis is 3 mA typical / 5 mA maximum, approximately 127 mA per
21-key Wing / 254 mA for two Wings; final USB/system power qualification
remains open.

## Analog interconnect

Measure the actual architecture:

```text
Hall -> TMUX -> Wing connector -> Main -> divider/filter -> ADC
```

Measure settling time, noise, repeatability, source/address-change behavior,
connector/interconnect impact and cross-channel coupling where relevant.
Include enable/bank transitions and worst relevant source changes, raw versus
filtered measurements, ADC clipping/headroom and settle-delay/sample-window
sweeps. Record observed error versus delay and resulting usable scan speed.

The setup must represent Rev.A closely enough that connector/MUX behavior is
useful for the two-bank/three-ADC architecture: document interconnect length,
return path, loads, populated/unused channels, three-output coverage and
production-equivalence limitations. A smaller first Wing must not silently
substitute a direct Hall-to-ADC path for the real connector/MUX path. The
[accepted coverage contract](g0b-freeze-proposal.md#6-production-equivalent-mux-and-bank-evidence)
defines bank/channel coverage; the JST GH 14-position connector and nominal
100 mm 1:1 harness are frozen in the [interface](main-wing-interface.md).

## Cost / geometry

For each magnetically and mechanically viable pitch, evaluate whether a
representative 21-key Wing fits inside 100 x 100 mm, including practical
connector, mounting and clearance needs. Record dimensional assumptions and
cost/assembly tradeoffs. 16.0 mm may help fit; fit is an optimization target,
not a pitch requirement. Magnetic performance and usability take priority.
Main + Evaluation Wing heterogeneous-panel feasibility is a separate cost
experiment under the [DFM policy](dfm-policy.md), not a required test geometry.

## Recorded evidence and later Human Gate

Produce raw CSV/time-series/travel data, setup photos/diagrams, firmware and
hardware revision identifiers, calibration method, sample identities, rail
voltage/current, temperature, timing settings, repeat statistics and plots.
Record each pitch's usability, interference, range, repeatability, settling,
noise/coupling, power and dimensional results, including failures and gaps.
G0B accepted the [measurement framework](g0b-freeze-proposal.md#8-measurement-acceptance-framework):
derivable numeric limits, comparative G2 decisions and characterization are
distinguished. Planning current estimates are not final production power
requirements. No measured passing result is claimed.

The post-EVT-002 G2 output is a measured-results report and explicit Human
Gate decision selecting production pitch among 17.0 / 16.5 / 16.0 mm and
magnetic/analog architecture, sensor choice, timing/filter baseline and Main
reuse suitability. Record required corrections, remaining risks or additional
experiments before the Rev.A circuit is fixed. PCB cost alone cannot select
pitch. G2 remains not-ready until physical evidence exists.
