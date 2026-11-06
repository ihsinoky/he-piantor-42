# Issue 150 Stage 1 evidence

The proposal is [docs/issue-150-case-stage1.md](../../../docs/issue-150-case-stage1.md).
This directory contains dimension evidence, not production CAD or manufacturing instructions.
All values are millimetres unless stated otherwise. Proposed clearances/tolerances are
engineering allocations, not measured results or supplier guarantees.

## Reproduction

From the repository root, Python 3 standard library only:

```bash
mkdir -p .issue150-runtime/tmp
python3 hardware/case/issue-150-stage1/measure.py > .issue150-runtime/tmp/measurements.json
cmp hardware/case/issue-150-stage1/measurements.json .issue150-runtime/tmp/measurements.json
python3 hardware/case/issue-150-stage1/verify.py
```

`measure.py` reads the committed #141 acceptance PCBs, both JITX definitions,
and #121's accepted Main PCB. It checks thickness, four Wing NPTH, sensor centers
and front mounting, then evaluates all 210 key pairs per pitch with axis-aligned
square envelopes. `source_pairs` retains every pair. Rounded corners, rotational
play, keycap underside ribs, elastic motion and full 3D solids are not simulated.

The #149 files were untracked at task start. `inputs/issue149-interface.json`
freezes their parsed mechanical inventory and exact source SHA256, with the two
original mounting-hole CSVs. This permits reproduction without requiring an
unmerged #149 tree. The run checked the actual local #149 PCB hashes and compared
geometry against #141; it did not publish or edit that prior work. The full #149
silkscreen, electrical or fabrication qualification is outside this evidence.

`keys-*.csv` uses absolute KiCad top-view coordinates, X right/Y down, no reflection.
These are sensor/key design centers, not validated magnet offsets or plate toolpaths.
`measurements.json` includes the exact source hashes, source component inventory,
Main bounds and its two USB locator holes, which must not be reused for case screws.
The JITX historical 80x60 qualification board is not the current 48x44 Main.

## Public dimensions

`sources/records.json` records manufacturer URLs, page references, access limitations,
and source PDF hashes where available. PNGs are actual PDF page renders, inspected
for dimension and datum interpretation; no generated illustration is used as evidence.

- Gateron: SPEC-KS-20T-041 v1, dated 2024-08-19, PDF page 7 drawing.
  The original PDF is ~6 MB and stays in `.issue150-runtime/evidence/`.
- Signature Plastics: DSA Family, manufacturer's current guide links to its Shopify
  PDF. Standard 1x1 skirt 0.725 inch, height 0.291 inch. The older
  solutionsinplastic.com URL failed direct retrieval; the official linked CDN
  file succeeded. This is an incompatible reference cap, not the selected narrow cap.
- TI: DRV5055 Rev.C, verified on the official website. The already committed #138
  PDF is reused read-only; page 14 contains the Hall element location.
- JST GH: official PDF was readable through Web PDF extraction, but direct curl
  returned 403. No successful local download or PDF hash is claimed. The 14-position
  width and mating dimensions are also consistent with the accepted G0B record.
  Proposed R5 and service clearances are not JST specifications.

## Verification and publication

`verification.json` records local checks. `manifest.json` hashes the report and all
files here except itself and the later `publication.json`. `verify.py` checks the
manifest, JSON syntax, key CSVs, local links, dimensions and deterministic recomputation.
The private task runtime holds a hash baseline of 10,230 tracked/prior #147/#149 files.
Its optional check is used in this workspace; the baseline is not required for a new clone.

Only this directory and the new report are staged. The normal `.git` directory is
read-only in this environment. The branch and commits are in `.issue150-runtime/git`
with the repository root as work tree. For recovery after an unavailable push:

```bash
git fetch ./.issue150-runtime/git issue-150-case-stage1
git push origin FETCH_HEAD:issue-150-case-stage1
gh pr create --draft --base main --head issue-150-case-stage1 \
  --title 'docs: 筐体設計 Stage 1 の機械要件と寸法根拠 (#150)' \
  --body-file hardware/case/issue-150-stage1/pr-draft.md
```

Publication status is separate from local verification. No order, paid service,
manufacturer upload, merge, board modification or Stage 2 CAD is performed.
