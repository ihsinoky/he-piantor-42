# Architecture: HE Piantor 42 JITX Challenger Backend

## Module hierarchy

```text
hardware/jitx/
├── he_piantor_42_jitx/
│   └── main.py            # CLI-seeded bootstrap design only
├── parity/
│   └── m1-parity-contract.json
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
