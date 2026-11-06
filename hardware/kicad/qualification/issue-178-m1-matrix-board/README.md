# Issue #178 — M1 dual-pitch 18-key matrix evidence

Report: [docs/issue-178-m1-matrix-board.md](../../../../docs/issue-178-m1-matrix-board.md).

- `board/`: delivered native PCB/project; library is `PCBA.pretty/`.
- `inspection/final/assessment.json`: independent all-net 0 / 0 / 0 / 0 pass.
- `manufacturing/`: Gerber/drills, PCBA paste, JLCPCB BOM/CPL, assembly drawing,
  review archive and fabrication requirements. Read `FABRICATION.md` first.
- `runs/KRT-M1-01/`: only automatic routing run, raw saved output and resolver.
- `inspection/KRT-M1-01/`: original result (one dangling GND stub, not hidden).
- `final-design-derivation.json`: exact stub removal and identical non-copper
  artwork/testpad paste edits on final input/output. `library-sync.json` records
  the follow-up library correction; no DRC category was suppressed.
- `cell-inputs/final/`: frozen unrouted input for the final strict transfer check.
- `inspection/final-before-library-sync/`: retained initial 18 library warnings.
- `native-design-readback.json`: every part/pad net, GH14 equivalence, 81
  interfield distances, holes/keepouts, column/row pitch.
- `manufacturing/manufacturing-check.json`: independent Gerbonara CAM readback.
- `via-pcba-review.json` / `all-vias.csv`: every via, native overlap classes.
- `processes/`: commands, actual outputs, timestamps and exit status, including
  harness errors fixed before qualification. No routing retry was needed.
- `start.json`: conservative UTC timebox; first bootstrap local/UTC mix corrected.
- `verification.json`, `manifest.json`, `publication.json`: final audits/handoff.

Reproduction uses the existing read-only `.issue129-runtime` KiCad 9.0.9,
geometry and JITX packages, `.issue147-runtime/viewer-venv` Gerbonara 1.5.0,
and an unmodified copy of KRT v0.23.8 in `.issue178-runtime/KiCadRoutingTools`.
All mutable state is under `.issue178-runtime/`; no `/tmp` runtime is used.
`common.py` defines the exact environment. Run authoring/route scripts only in
a fresh output directory; they refuse to overwrite evidence. Inspection is
against the input project's rules, with the frozen #87 copper oracle and #141
conservative broad-phase optimization. No predicate or tolerance was relaxed.
The native JITX dry build proves assembly conversion only; the delivered CAM
comes from the independently qualified native KiCad board.
