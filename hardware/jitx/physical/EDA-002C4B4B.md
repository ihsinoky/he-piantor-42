# EDA-002C4B4B — external DFM evidence and disposition

Issue [#51](https://github.com/ihsinoky/he-piantor-42/issues/51).
**Downstream manufacturing path: PASS_WITH_LIMITATIONS.**
**USB product release: OPEN — PRE-ORDER DFM REVIEW REQUIRED.**
C4B5 complete-routing feasibility is next; C4C / G0A Human Gate follows C4B5.
This increment does not qualify a production PCB or make an adoption decision.

## Baseline and evidence provenance

Before editing, clean HEAD, local main, freshly fetched origin/main and
merge-base all equaled `b0caab98a196ad68cd01d92ecf41734bfa9429ca`.
Branch: `eda-002c4b4b-external-dfm-disposition`. Issue #51 was read completely;
there were no comments. C4B4A is completed / merged PR #50.
C4B through C4B4A reports and evidence remain unchanged historical records.
This forward disposition uses their retained measurements and fabrication
fidelity evidence, plus the PO-supplied external evidence:

- [Human JLCDFM observation](c4b4b-evidence/jlcdfm-observation.md): exact C4B4A
  ZIP, rigid 2-layer FR-4 / 1 oz outer copper / 1.2 mm finished thickness;
  **INCONCLUSIVE** for the exact NPTH-to-pad-copper measurement.
- [JLCPCB Japan support/sales response](c4b4b-evidence/jlcpcb-support-response.md),
  received 2026-10-05: sanitized technical paraphrase; 0.20 mm minimum
  capability and qualitative recommendation for additional clearance.

No raw web report or original correspondence is attached; provenance is the
human evidence supplied in the issue and instructions. No supplier quotation,
independent external verification or production acceptance is inferred.

## Capability and unchanged project policy

Accepted analytic source gaps from [C4B3 independent measurement](c4b3-evidence/independent-source-measurements.json)
match [C4B4A source and Gerber/Excellon reconciliation](c4b4a-evidence/reconciliation.json):

| USB contact | Nominal gap (mm) | Meets 0.20 mm floor numerically |
| --- | ---: | --- |
| A1_B12 | 0.2000999900 | Yes |
| A12_B1 | 0.2000999900 | Yes |
| A4_B9 | 0.2348831648 | Yes |
| A9_B4 | 0.2348831648 | Yes |

JLCPCB confirms approximately 0.2001 / 0.2349 mm numerically satisfy its
**0.20 mm minimum manufacturing capability**. This is not production approval;
actual acceptance remains subject to order-time CAM/process review.

Project policy remains **0.20 mm manufacturer capability floor / 0.25 mm
project preferred target / 0.001 mm project numerical review guard**.
The target and guard are project-owned, not JLCPCB requirements or
recommendations. The existing guard means a gap below 0.201 mm must not
supply an automatic release pass. Meeting the guard is necessary, not
sufficient, for the existing exception review. The smallest pair has about
0.0001 mm nominal headroom and falls below the guard; all four are below the
preferred target. No policy, qualification rule or production exception changes.

## Downstream path disposition

**JITX -> legacy-kicad -> KiCad -> Gerber/Excellon: PASS_WITH_LIMITATIONS.**
The retained C4B3/C4B4A evidence establishes preservation of accepted source
geometry through fabrication outputs. These USB gaps belong to the accepted
connector geometry; they are not distortions introduced by JITX/KiCad export.
The supplier confirms they meet the published capability floor numerically.
The clearance concern therefore moves from a JITX-backend qualification
blocker to a product manufacturing-release risk.

The documented thickness handoff limitation remains: generated CAD overall
thickness and Gerber-job metadata report misleading **1.6 mm**, while the
intended finished thickness is **1.2 mm**. Production handoff must exclude the
misleading CAD/job metadata, use the preserved individual Gerbers and separate
PTH/NPTH Excellon, and independently select/confirm **1.2 mm finished thickness**.
See [C4B3 handoff evidence](c4b3-evidence/handoff.json) and the
[C4B4A ZIP manifest](c4b4a-evidence/upload-manifest.json).
This is a limited qualification of the demonstrated downstream path, not a
full DRC pass, complete-routing result or production PCB qualification.

## Product release and progression

**USB footprint: OPEN — PRE-ORDER DFM REVIEW REQUIRED.**
Before an actual Rev.M1 / Rev.A fabrication order, the project must either:

- Increase NPTH-to-copper margin where feasible; or
- Explicitly accept/document the manufacturer-minimum geometry and pass the
  actual order-time CAM/process review.

No production exception is granted here. The web observation supplies no
explicit measurement; absence of a warning supplies no production approval.
The support reply supplies capability guidance, not final manufacturing release.

**EDA-002C4B5 — complete-routing feasibility** is the next technical increment,
unimplemented here. **C4C / G0A Human Gate remains after C4B5**; no GO/NO-GO
adoption decision is made. Physical Main/Wing remains unimplemented.

## Verification and review

Documentation/status only: no design geometry, pads, NPTHs, stackup, routing,
rules, dependencies or CI/workflows changed. No runtime start, artifact
regeneration, expensive C0/C1/C2 requalification, login/contact or order.

Lightweight verification **PASS**:

- `node --check task/data/project-status.js` and `git diff --check`.
- Dashboard evaluation: unique six-field task rows, stream dimensions,
  C4B4A done, C4B5 todo, G0A not-ready, and C4C after C4B5.
- Relative Markdown evidence links resolve.
- All 125 existing tracked JITX files byte-identical to the verified baseline,
  covering historical reports/evidence, design source and configuration.
- Retained local ZIP SHA-256 matches the C4B4A manifest and supplied upload;
  both retained reconciliation runs confirm all four nominal gaps meet 0.20 mm
  and source/output deltas remain below 0.000001 mm.

Applicable engineering-ci results are reported on the Draft PR; no
layout/product-KiCad/firmware/tscircuit trigger paths change.

Self-review checks the five requested risks: 0.25 mm is explicitly project-owned;
no production approval is claimed; JLCDFM coverage is bounded to observed UI;
historical reports/evidence are untouched; C4B5 precedes C4C everywhere in the
updated status. PMO reviews evidence fidelity, path/product separation and
retained pre-order risk. PO decides MERGE / HOLD; no automatic merge.
