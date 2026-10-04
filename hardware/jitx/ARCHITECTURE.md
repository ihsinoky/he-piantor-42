# Architecture: HE Piantor 42 JITX Challenger Backend

## Module hierarchy

```text
hardware/jitx/
├── he_piantor_42_jitx/
│   ├── main.py            # CLI-seeded bootstrap design
│   ├── m1.py              # M1 electrical challenger assembly
│   ├── physical_qualification.py # Disposable C4B wrapper; not physical Rev.M1
│   └── components/        # Accepted manufacturer and generic models
├── parity/
│   ├── exporter.py         # Registered normalized built-design graph exporter
│   ├── m1-parity-contract.json # Frozen input
│   ├── m1-normalization.json   # Explicit identity mapping
│   ├── m1.py                   # Strict electrical comparator
│   └── evidence/               # Actual runtime / normalized graphs and result
├── physical/              # C4B observer, reproduction runner and evidence
├── tests/
│   ├── test_bootstrap_graph.py
│   └── test_m1_electrical_parity.py
├── uv.lock                 # Committed exact Python dependency resolution
├── PLAN.md
└── ARCHITECTURE.md
```

## Backend role and product boundary

JITX remains a challenger: C4B investigation is BLOCKED; C4C / G0A is next
for a Human Gate decision on the concrete evidence and remaining investment. The frozen tscircuit four-key source and verifier
remain the historical electrical authority under unchanged D-014 and a
permanent qualification oracle. They do not define the physical Rev.M1 product.
The bootstrap seed is not the four-key parity implementation.

Physical Rev.M1 uses the new [Main + Evaluation Wing architecture](../rev-m1/architecture.md)
under D-015. Main owns MCU/USB/power and three ADC divider/filter paths; Wing
owns Hall/TMUX and test geometry. Rev.A intends accepted Main reuse with
Left/Right 21-key Wings, three TMUX1208 each, from one project-owned definition.
Separate manufacturing datasets are permitted; reversible PCBA is not required.
No schematic, footprint or physical implementation is added in C4A.
`../layout/**` must not be consumed. Future Wing generation geometry source
requires project ownership or explicit Human Gate approval.

## Current implementation

The five previously accepted models are preserved. RP2040, USBLC6-2SC6,
W25Q16JVUXIQ and HRO TYPE-C-31-M-12 now also have manufacturer-derived models,
full physical inventories, explicit pad maps, structural tests and real builds.
RP2040 uses exact recommended copper with its 3.20 mm reduced GND pad; ST uses
SOT23_6; Winbond uses SON from exact UX dimensions; HRO uses project-owned
Landpattern/Pad APIs from its exact M-12 sheet. SHIELD groups four physical
stakes; the flash EP remains a separate unassigned physical port.

All nine pass component-modeling checks. EDA-002C1 is done / accepted: PR #36
was squash-merged into main at a27fc48. EDA-002C2 is done / accepted / merged
PR #38 at `67b6c302`: complete M1 electrical graph parity PASS. Geometry parity
is explicitly NOT established. Manufacturer HRO and Winbond geometry differs
from frozen M1 geometry; `component-sources.md` records the discrepancies for
EDA-002C3 (issue #39 / merged PR #40): the unchanged report and reconciliation
record retain valid historical manufacturer/frozen discrepancy evidence.
D-015 removes exact geometry convergence as an adoption criterion; this does
not resolve every footprint-policy question or invalidate C2 electrical PASS.
Manufacturer evidence should inform the new Rev.M1 design; no legacy geometry
is corrected. No product placement, routing, DRC or EVT-002 has started.

## EDA-002C0 graph-introspection gate

The reproducible project environment uses the standard `uv` lock workflow:
`uv lock` generates the committed `uv.lock`, and
`uv sync --locked --group dev` restores it. The lock resolves
`jitx==4.4.3`, `jitxlib-standard==4.4.0`, `jitxcore==4.4.0`, and
`ruff==0.16.10`, along with every transitive package and artifact hash. The
Linux JITX runtime remains the separately validated release `4.4.2`; this
increment does not update it.

`parity.exporter` is registered in `pyproject.toml` through the standard
`jitx-plugin` entry-point group. The documented `jitx design export
bootstrap-graph` command invokes the standardized
`jitx.plugin.export.Export` lifecycle:

1. `Export.submitted(design)` receives the submitted `RuntimeDesign` and
   records component instances, `Trace.path` structural identities, component
   types, ports, resolved nets, and port-to-net membership.
2. `Export.export(design)` records public captured placement transforms and
   writes deterministic normalized JSON.

The exporter only calls public/documented JITX objects:
`Export`, `RuntimeDesign.query`, `RuntimeDesign.nets().find`,
`jitx.inspect.visit`, and `Trace.path`. It neither parses Python source nor
any generated JITX artifact, and it never surfaces backend IDs or generated
reference designators as semantic identity.

`jitx.inspect` and `jitx.plugin.export.Export` are category-A documented
public APIs. `RuntimeDesign` is supplied through that documented plugin
boundary, but its defining `jitx.run` module is category-B: documented and
explicitly experimental. This is not a category-C/private dependency. Two
real non-dry bootstrap exports produced identical normalized graphs, and
`tests/test_bootstrap_graph.py` asserts the two resistor identities, their
ports, and the two resolved connectivity groups. The bootstrap's captured
public geometry is a placement transform; no richer physical geometry is
exposed by this minimal design.

EDA-002C0 is done and accepted as PASS. PMO accepted the category-B
`RuntimeDesign` graph methods for the JITX challenger/parity evaluation
workflow, but this does not make `RuntimeDesign` a stable API. Any future JITX
Python package or JITX runtime version change must rerun and pass the EDA-002C0
normalized graph exporter and bootstrap graph self-test before graph-parity
compatibility may be assumed. EDA-002C1 is merged / accepted. EDA-002C2 is done / accepted / merged PR #38 with electrical parity PASS.
The source manifest preserves the explicit geometry-parity differences.

## EDA-002C2 electrical assembly boundary

`he_piantor_42_jitx.m1.M1FourKeyElectrical` owns `M1ElectricalCircuit`: 68
components, 200 frozen semantic endpoints, 43 named nets, 185 endpoint/net
edges, four direct links, seven intentional NCs. All nine accepted manufacturer
classes are used, including four Hall sensors. Twenty-three additional physical
RP2040 GPIO ports are explicitly inventoried and checked unconnected.

The circuit constructs JITX components and connections directly; it does not
read the contract or normalization file. `parity/m1-normalization.json` owns
explicit component paths, physical-to-semantic aliases, approved model types,
extra unconnected endpoints and passive group references. `parity/m1.py`
compares actual runtime graph facts against the unchanged frozen contract and
fails with actionable differences. Unknown/missing/duplicate identities fail
closed. RP2040 pin numbers come from actual public `PadMapping.items()` and the
manufacturer model's physical pad inventory, without inspecting pad geometry.

`m1-electrical-graph` extends the C0 exporter through the same documented
Export lifecycle. At `submitted()`, this runtime's resolved name is unset;
public named Net objects and Port objects are bound through `nets().find()` to
the same runtime connectivity object. Empty CC1/CC2 declarations are retained,
while the CC direct links retain unnamed connectivity as in the golden source.
No name is guessed from membership. Runtime object IDs are only local grouping
keys and are never emitted. The C0 exporter and regression remain intact.

The normalized graph excludes transforms, coordinates, footprints and all
other geometry. Generic capacitor/LED/button SMT choices and test-point lands,
plus the sample board/substrate, are non-authoritative build scaffolding.
No final placement, routing, manufacturing output or readiness is implied.
See `parity/EDA-002C2.md` and `parity/evidence/` for review and validation.

## EDA-002C4 sequence — evaluation rebaseline (issue #41)

### EDA-002C4A — accepted / merged PR #42

Merged baseline: `8f6c401a902353547dcacbdfc76978ac807ce7f9`.

Completion freezes the legacy four-key golden permanently as a qualification
fixture, retains C2 electrical PASS and C3 historical geometry evidence,
removes exact geometric convergence as an adoption criterion, defines physical
pipeline acceptance criteria, and separates physical Rev.M1 implementation
under [D-015](../../docs/decisions.md) from JITX qualification. No hardware,
footprint or PCB geometry changes, connector selection or adoption decision
occur here. D-014 remains unchanged. C3 discrepancies do not invalidate C2;
manufacturer evidence informs the new product, without correcting the legacy
tscircuit geometry or declaring all C3 questions resolved.

### EDA-002C4B — completed investigation / BLOCKED (issue #43)

The disposable four-key physical wrapper builds with a project-owned 80 × 60 mm,
nominal 1.2 mm two-layer stack and explicit placement of all 68 existing
components. Six source route segments realize copper on both layers through
two vias. Public capture, BOM/PnP review CSVs and supported ODB++ exports repeat;
68 ODB placements/angles agree with the review CSVs. C2 electrical parity
remains PASS with the accepted counts and unchanged contract.

**BLOCKED:** full board routing/DRC and a supported, qualified Gerber/Excellon
handoff are not demonstrated. ODB content order/IDs vary despite matching narrow
geometric records. Supported KiCad export was investigated; downstream CAM and
JLCPCB rotation conventions remain unqualified. Generic BOM completeness is a
separate product sourcing limitation. No private API, artifact patch, external
CAD round-trip, component redesign, product Main/Wing implementation or order
was used. See the [C4B report](physical/EDA-002C4B.md) and machine-readable evidence.

C4C is next / Human Gate; G0A is ready-for-decision on this blocked evidence,
not GO. G0B remains not-ready and EVT-002 remains blocked/unstarted. No D-016
or adoption decision is made here.

### EDA-002C4C — next / Human Gate / G0A

Inputs: C0-C3 accepted evidence and C4B physical/manufacturing pipeline result.
Explicit outcome:

- **GO:** JITX becomes the active EDA candidate for physical Rev.M1 / Rev.A.
- **NO-GO:** retain/fallback to another supported backend without invalidating
  C0-C3 evidence.

C4A makes neither decision. A future accepted D-016 may record JITX as the
active EDA for Rev.M1 and Rev.A; D-016 is not created or accepted now.
G0B separately freezes physical architecture/interface before implementation.
See [physical architecture](../rev-m1/architecture.md).
