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

## Backend role and product boundary

JITX remains a challenger pending C4B physical/manufacturing proof and C4C
adoption Human Gate (G0A). The frozen tscircuit four-key source and verifier
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

### EDA-002C4A — documentation / architecture rebaseline

Completion freezes the legacy four-key golden permanently as a qualification
fixture, retains C2 electrical PASS and C3 historical geometry evidence,
removes exact geometric convergence as an adoption criterion, defines physical
pipeline acceptance criteria, and separates physical Rev.M1 implementation
under [D-015](../../docs/decisions.md) from JITX qualification. No hardware,
footprint or PCB geometry changes, connector selection or adoption decision
occur here. D-014 remains unchanged. C3 discrepancies do not invalidate C2;
manufacturer evidence informs the new product, without correcting the legacy
tscircuit geometry or declaring all C3 questions resolved.

### EDA-002C4B — future physical/manufacturing pipeline proof

Use the existing four-key JITX electrical topology as a qualification fixture,
not the physical Rev.M1 product. Use stock/supported JITX workflow as far as
practical and record supported surfaces, limitations and reproduction steps.
Prove and review:

- board/substrate definition, component placement and two-layer routing;
- design-rule validation / DRC-equivalent capability with reviewable results;
- deterministic builds and reproduction from source-controlled inputs;
- Gerber, drill data, BOM, pick-and-place / centroid data, and other outputs
  required for the JLCPCB workflow;
- reviewability of generated outputs and suitability for AI-assisted,
  source-controlled development.

The gate needs a reproducible complete output package and documented checks
for each capability; unsupported steps or gaps must be explicit in the C4B
result for C4C review. No board is ordered. Geometry equality to frozen
legacy tscircuit is not required. Accepted C2 topology/parity stays protected;
manufacturer-correct C1/C3 JITX geometry may be used without rewriting the
legacy fixture. Physical proof does not itself adopt JITX.

### EDA-002C4C — future Human Gate / G0A

Inputs: C0-C3 accepted evidence and C4B physical/manufacturing pipeline result.
Explicit outcome:

- **GO:** JITX becomes the active EDA candidate for physical Rev.M1 / Rev.A.
- **NO-GO:** retain/fallback to another supported backend without invalidating
  C0-C3 evidence.

C4A makes neither decision. A future accepted D-016 may record JITX as the
active EDA for Rev.M1 and Rev.A; D-016 is not created or accepted now.
G0B separately freezes physical architecture/interface before implementation.
See [physical architecture](../rev-m1/architecture.md).
