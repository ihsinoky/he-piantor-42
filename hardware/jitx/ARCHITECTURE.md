# Architecture: HE Piantor 42 JITX Challenger Backend

## Module hierarchy

```text
hardware/jitx/
├── he_piantor_42_jitx/
│   └── main.py            # CLI-seeded bootstrap design only
├── parity/
│   └── m1-parity-contract.json
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

A real non-dry build of
`he_piantor_42_jitx.main.HePiantor42Bootstrap` succeeded. It generated a
minimal `cache/netlist.json` with resolved endpoint groups plus richer
`cache/design-explorer.json`, `design-info/stable.design`, and
`design-info/reference-designators.table` files. The latter artifacts appear
to expose component instances, hierarchy, types, pins, nets, endpoint
membership, generated reference designators, and physical package data.

This is not an approved exporter architecture. JITX public documentation does
not identify those files as supported stable graph-export APIs, and identical
builds changed raw `stable.design` and `netlist.json` hashes. Depending on
their undocumented identifiers or schema would violate this project's
stability requirement. Consequently, no semantic-identity mapping, normalized
graph exporter, or bootstrap graph self-test is implemented. Stable M1
machine-parity comparison is **not technically feasible on the current public
JITX contract**. PMO review must obtain a supported API/output commitment from
JITX before resuming this work.
