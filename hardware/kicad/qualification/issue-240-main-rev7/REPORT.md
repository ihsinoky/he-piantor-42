# Issue 240 — Main Rev.7 side-entry study candidate

Study only, 2026-11-13. **Electrical qualification passes. The requested strictly local
routing scope does not pass.** No adoption, baseline/decision update, order or
manufacturing release is made. The separate [bay report](../../../case/issue-240-bay-cover/REPORT.md)
controls the combined mechanical verdict.

| Gate | Fresh result |
|---|---:|
| Native KiCad DRC / unconnected / schematic parity | 0 / 0 / 0 |
| Native ERC | 0 |
| Independent physical connectivity: opens / wrong contacts | 0 / 0, 40 nets |
| Via-to-pad physical gap, minimum / required | **0.145 / 0.100 mm** |
| Input loop, 125°C / −20% track width | **49.086 mΩ** |
| Common rail loop, same corner | **49.491 mΩ** |
| J2 / J3 branch loops | **20.961 / 43.051 mΩ** |
| Worst six-return Vfar, Rev.6 model and 200 mm wire bound | **4.792958 V** |
| Required input / Vfar | ≤50 mΩ / ≥4.60 V |
| Rev.6 reference input / Vfar | 48.683 mΩ / 4.798 V |

The input changes by +0.403 mΩ; Vfar changes by about −5.0 mV. The common-loop
margin to 50 mΩ is only **0.509 mΩ**. These are model results, not measured
operating guarantees. Material assumptions, 125°C copper extrapolation, 35 µm
sheet/20 µm barrel, etch treatment, contact allowances, switching loss, load and
Wing model are inherited from the Rev.6 yardstick. The 125°C solver corner is
not a claim that JST permits a 125°C operating assembly. The conservative 200 mm
conductor calculation also bounds a correctly made 160 mm AWG28-equivalent
harness; it does not qualify mechanical storage or cable procurement.

## Connector and invariants

J2/J3 are **SM14B-GHS-TB(LF)(SN), C265343**, with standard GHR-14V-S plugs and
SSHL-002T-P0.2 contacts. Logical cavities 1–14 retain the D-024 nets, including
six independent returns. The stock library's mechanical lands are renamed 15
and stay NC. The native board uses matching local `Rev7.pretty` footprints;
rectangular solder lands contain the catalog round-rectangle lands. Connector
silk segments that failed clipping checks are moved to fabrication drawings.

Mating points outward from Main: J2 −120°, J3 +120°. Case-frame origins are
(−17.102146,42.075) and (+17.102146,42.075); exit directions are
(−0.866025,−0.5)/(+0.866025,−0.5). The 1.85 mm origin shift aligns the pad-row
geometry, but **reverses the physical numbered row**. Actual numbered nets are
rerouted; this is not a pin-compatible footprint-only substitution. Cable
wiring remains cavity-to-same-cavity, not a crossed harness.

The tested inward orientation preserved signal landings but its mated housing
reservations overlapped numerous installed Main parts. It was rejected; the
trial R18/Y1/C22 moves are **absent from the final candidate**.

[Native invariants](invariants.json) verify unchanged outline, three mounts,
J4 placement/pin nets, every other component placement and every numbered
pad-to-net assignment. The schematic changes connector identity only; its
fresh ERC and physical native connectivity pass independently.

## Named routing exception — requires review

**This candidate exceeds the requested J2/J3-only copper scope.** It must not be
represented as a completed local-change solution. Copper differences span
KiCad X76.300…120.950 / Y91.150…127.381, **44.650 ×36.231 mm**, across 16 nets
and 58 net/layer pairs. [Scope summary](scope-summary.json) and
[geometric copper differences](routing-geometry-diff.json) give every net,
area, bounds, total track length and via-count change. The envelope includes
the USB_DM_ESD repair near J4, although J4 itself does not move.

The initial unrestricted cleanup/layer-swapping route degraded resistance.
The retained-input route fixes those transformations, but collateral signal
repairs and the power recovery still extend outside the connector windows.
The accepted electrical result requires positive-copper widening (up to
2.00 mm where foreign-copper clearance permits) and a replacement V5V2
converter-to-switch route. [Width recovery](power-width-recovery.json) lists
all edited widths. Power connectivity/topology remains the same; power copper
geometry does not. Calling this exception unavoidable would require a further
layout search, which this study does not establish.

Incremental hardware/BOM cost of those routing changes is **zero added parts,
zero added layers and zero outline area**. Board assembly substitutes two
headers; the saved stock observation is availability evidence, not a current
purchase quote. No supplier price or unchanged fabrication quote is asserted.
Layout review, USB signal integrity and the reduced resistance margin remain
review items. This is **not a fully compliant Rev.7 adoption package**.

## Evidence and reproduction

The frozen candidate is [main.kicad_pcb](inspection/final/main.kicad_pcb).
[Top view PNG](drawings/top-view.png) / [SVG](drawings/top-view.svg), native layer
SVGs, source/current JST catalog and footprint provenance accompany it.
JST's [current GH catalog](https://www.jst.com/wp-content/uploads/2025/06/eGH.pdf),
p2, explicitly gives the side-entry **4.35 mm reference mated height** and
7.15 mm axial length. The 4.35 figure is not inferred from bare-header height.

Run `python3 hardware/kicad/qualification/issue-240-main-rev7/verify.py` for the
saved electrical gates and hashes. Run `bash .../reproduce.sh` to repeat native
checks, the all-via audit, extraction, solver checks and drawings. Existing
process records are archived only under `.issue240-runtime/reproduction/`.
`env.sh` names the read-only KiCad/geometry dependencies. Every recorded process
has its command, environment context, elapsed time, stdout/stderr and exit code.

`build.py`, `prepare-route.py`, `trim-debris.py`, `widen-power.py`, `refill.py`,
`finalize.py` and the saved routing invocation log explain construction.
Run `bash .../rebuild-route.sh` to reconstruct the studied routing from Rev.6; it
then runs full qualification. Routing UUIDs may differ; saved evidence is
hash-linked to the frozen candidate. All intermediate/rejected boards live
only in `.issue240-runtime/`.
No Gerber, drill, CPL, fabrication ZIP or Rev.7 manufacturing package is supplied.
