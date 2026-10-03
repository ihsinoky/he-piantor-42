# Architecture: HE Piantor 42 JITX Challenger Backend

## Module hierarchy

```text
hardware/jitx/
├── he_piantor_42_jitx/
│   └── main.py            # CLI-seeded bootstrap design only
├── parity/
│   ├── exporter.py         # Registered normalized built-design graph exporter
│   └── m1-parity-contract.json
├── tests/
│   └── test_bootstrap_graph.py
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

No M1 components, circuits, substrate, constraints, or physical layout are
implemented in this increment. This deliberately leaves the package as the
canonical JITX CLI bootstrap until a separately approved electrical-parity
increment supplies component sources and a full architecture.

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
compatibility may be assumed. EDA-002C1 component modeling is next and
unblocked.
