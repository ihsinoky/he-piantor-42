# Architecture: HE Piantor 42 JITX Challenger Backend

## Module hierarchy

```text
hardware/jitx/
├── he_piantor_42_jitx/
│   ├── main.py            # CLI-seeded bootstrap design
│   ├── m1.py              # M1 electrical challenger assembly
│   └── components/        # Accepted manufacturer and generic models
├── parity/
│   ├── exporter.py         # Registered normalized built-design graph exporter
│   ├── m1-parity-contract.json # Frozen input
│   ├── m1-normalization.json   # Explicit identity mapping
│   ├── m1.py                   # Strict electrical comparator
│   └── evidence/               # Actual runtime / normalized graphs and result
├── tests/
│   ├── test_bootstrap_graph.py
│   └── test_m1_electrical_parity.py
├── uv.lock                 # Committed exact Python dependency resolution
├── PLAN.md
└── ARCHITECTURE.md
```

## Backend role

JITX is a challenger backend. The M1 electrical source of truth is the frozen
tscircuit design at `../tscircuit/src/evaluation/m1-four-key.tsx`; its verifier
is `../tscircuit/scripts/verify-m1-electrical.tsx`. The bootstrap design is
not an M1 implementation and must not be used for parity claims.

## Future M1 boundary

The future M1 challenger must reproduce the parity contract's electrical graph
and generated design data: a two-copper-layer, 1.2 mm board; the project-owned
four-sensor 2x2 grid at 17.0 mm pitch; and all documented connectivity and
critical footprint requirements. It must not consume `../layout/**`.

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
EDA-002C3 (issue #39): evidence package prepared in `geometry/EDA-002C3.md` and
`geometry/geometry-reconciliation.json`; PMO Human Gate decisions PENDING.
HRO: ADOPT_MANUFACTURER; Winbond: NEED_MORE_EVIDENCE. The limited audit records
RP2040 and five additional derived-land differences. No geometry changes; C3
is not done/accepted. No placement, routing, DRC or EVT-002 has started.

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
