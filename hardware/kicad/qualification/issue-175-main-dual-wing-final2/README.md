# Issue175 evidence

PCB qualification passes with two placement candidates and exactly one whole-board route. All 44 nets and four independent metrics pass; final PCBA quotation and vendor acceptance remain unavailable. No manufacturing GO, order, charge or merge.

- [Report](../../../../docs/issue-175-main-dual-wing-final2.md)
- [Status](status.json), [candidate selection](candidate-selection.json), [independent placement](placement-check.json)
- [Final board](inspection/final/main.kicad_pcb), [assessment](inspection/final/assessment.json), [circuit check](circuit-check-final.json)
- [Resistance](resistance-summary.json), [FEM verification](ground-model-verification.json)
- [Manufacturing package](manufacturing/), [CAM validation](cam-check.json), [POFV](pofv-reclassification-final.json)
- [Quote handoff](manufacturing/quote-handoff.md), [quote status](pcba-update-status.json)
- [Fallback preservation](fallback-preservation.json), [execution records](processes/)

Use `.issue175-runtime/git` for the committed branch `issue-175-main-dual-wing-final2`. Seed-a remains in the unchanged Issue173 fallback package; do not mix its 0805 BOM/CAM with this 1210 package.
