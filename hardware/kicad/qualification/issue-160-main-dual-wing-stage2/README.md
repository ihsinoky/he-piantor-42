# Issue #160 Stage 2 — stopped at the mechanical gate

Outcome: **STOP_PROPOSE_C** under the explicit PO fallback policy. This is
an engineering judgment of multiple service disadvantages and unverified
3D operations, not proof that every plan A assembly method is impossible.
Plan C remains a proposal; it is not qualified or implemented.

See the [report](../../../../docs/issue-160-main-dual-wing-stage2.md) and
[D-024](../../../../docs/decisions.md#d-024---revm1-main-two-wing-interface-and-plan-a--plan-c-fallback).

| Evidence | Meaning |
| --- | --- |
| instructions.md, issue.json, pr159-input.json, start.json | Authority, merged input and four-hour limit |
| mechanical-gate.py / .json | Actual #155 source hashes and geometry, explicitly assumed grip/tool/tolerance/bend sweeps |
| native-readback.py / .json | Independent KiCad 9 original-board identity and R2 pad bounds, no save |
| mechanical-screen.svg | Cropped north-board projection; orange finger envelopes are assumptions, not 3D bodies |
| sources.json | Manufacturer source URLs, catalogue hash and access limitations; downloaded PDFs stay in runtime |
| protected-start.json.gz | Hashes of 10,725 pre-existing project files, including unrelated untracked evidence |
| verify.py / verification.json | Preservation and calculation checks; all new-revision qualification metrics are null / N/A |
| draft-pr-body.md, publication.json, processes/ | Review text and publication attempt results |
| manifest.json | Added-artifact hashes, excluding itself |

Reproduce from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 hardware/kicad/qualification/issue-160-main-dual-wing-stage2/verify.py
```

The mechanical calculation is Python stdlib only. Native readback uses the
existing KiCad bindings in `.issue129-runtime/kicad/`, without installation.
The verifier uses `.issue160-runtime/git` for the latest-main comparison;
in a fresh clone substitute the normal git metadata. Temporary output and
XDG directories stay in `.issue160-runtime/`. The SVG is a static review
drawing of JSON values; no PCB/CAM geometry is generated from it.

The initial mechanical script failed a list-versus-tuple assertion before
any result was produced. It was fixed to compare coordinates consistently.
Native readback confirms the coordinate result. Router attempts: **zero**.
No source schematic or PCB, manufacturing data, POFV classification or
quotation is revised. Historical #155/#157 outputs remain unchanged. No
ordering, billing or merge is authorized or performed.
