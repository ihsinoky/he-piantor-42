# Issue #147 manufacturing evidence

Authoritative handoff: [`docs/issue-147-wing-order-prep.md`](../../../../docs/issue-147-wing-order-prep.md).

- `wing-16mm-jlcpcb-review.zip`, `wing-17mm-jlcpcb-review.zip`: nine flat manufacturing files each (seven Gerbers, separate PTH/NPTH Excellon). Review candidates, subject to the report's PO gates.
- `<pitch>/gerber/`: unchanged exports inherited from the interrupted run. `.gbrjob` is retained as evidence only; it is excluded from the ZIP.
- `<pitch>/preflight.json`, `export-provenance.json`, `drc.json`, `drill-report.txt`, `processes/`: inherited input inspection and KiCad export records. `16mm/drc-before-library-config.json` is a retained failed runtime-library lookup report, superseded by `16mm/drc.json`; no design was changed.
- `<pitch>/manufacturing-check.json`, `manufacturing-checks.json`: parsed source-to-export geometry and archive comparison.
- `<pitch>/preview-review/`: reviewed high-contrast PNG/SVG plates, drawn from actual exports with Gerbonara. Both copper composites use front-view coordinates, including the bottom copper. The mask plates show openings, not green coating. White silk plates are intentional: no printed legend exists in the source.
- `<pitch>/paste-reference-not-for-order/`: top paste 190 apertures, bottom empty, retained separately. No stencil, PCBA, BOM or CPL order is intended.
- `visual-review.json`: image review observations and dispositions.
- `resume-start.json`, `resumption-verification.json`: inherited file hashes, original 45,864-path baseline audit, native source readback and successful process provenance.
- `resume-processes/`: resumed parser/render logs and the inherited viewer failure. Excellon coordinates have 0.001 mm resolution; the inherited inspector incorrectly demanded 0.000001 mm equality. The resumed inspector matches every hole uniquely within the output resolution and reports actual maximum displacement (0.000075 mm).
- `checklist.json`: explicit continuation of every previously open #138 checklist item.
- `manifest.json`, `final-verification.json`: final file hashes and final checks. The manifest excludes itself; publication records, when added afterward, identify that timing.

The interrupted run's `common.py`, `prepare-export.py`, and `inspect-gerbers.py` remain byte-identical. **Do not rerun them in place**: the exporter would overwrite inherited evidence and the old inspector contains the drill-resolution assertion.

Read-only audit with the already available local CAD runtime:

```bash
source .issue147-runtime/env.sh
python3 hardware/kicad/qualification/issue-147-wing-order-prep/verify-resumption.py
```

`inspect-gerbers-resumed.py` performs parsed copper/pad/via/outline/mask/drill checks and ZIP packaging. `render-review.py` creates filter-free visual plates. They deliberately refuse to overwrite existing ZIPs / review directories. For reproduction, copy this evidence tree to an isolated checkout, remove only generated outputs in that copy (`manufacturing-check*.json`, per-pitch `manufacturing-check.json`, review ZIPs and `preview-review/`), and run:

```bash
PYTHONDONTWRITEBYTECODE=1 .issue147-runtime/viewer-venv/bin/python \
  hardware/kicad/qualification/issue-147-wing-order-prep/inspect-gerbers-resumed.py
PYTHONDONTWRITEBYTECODE=1 .issue147-runtime/viewer-venv/bin/python \
  hardware/kicad/qualification/issue-147-wing-order-prep/render-review.py
```

Runtime dependency versions are in `resume-processes/versions.json`. A different machine needs equivalent KiCad 9.0.9/pcbnew and Python dependencies; absolute paths in inherited records describe the original execution environment. Offline parsing does not certify the manufacturer's CAM interpretation or final price. No manufacturer upload, enquiry, order or payment was made.
