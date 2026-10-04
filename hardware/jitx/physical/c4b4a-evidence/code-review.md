# JITX code review — C4B4A

Reviewer: jitx-code-review, same-model self-critique. Scope: coupon source,
measure_c4b4a.py, reproduce_c4b4a.py, qualify_c4b4a.py. Rule sources read:
JITX base Don'ts, physical-layout skill, architectural-patterns and code-review
checklist. Existing project observers are imported unchanged, never rebound.

CRITICAL: 0. The coupon directly composes the owning component/substrate
objects. No reflection-based child access, duplicated pads, private JITX call,
framework mutation, hand-edited CAD, relaxed rule or added route exists.

WARNING: 2 found during validation, resolved before acceptance:

- `usb_dfm_coupon.py:23`: feature `.at()` was invalid. Public shape `.at()`
  is now used inside Silkscreen. Both retained builds succeed with this fix.
- `qualify_c4b4a.py:136`: initial observer selected non-copper mask-only pads
  as copper. It now selects actual copper layer membership and asserts all
  20 CAD pad records, 16 copper pads, 16 top flashes and four bottom flashes.
  Both retained runs reconcile. Rule: "a claim made without backing evidence"
  (code-review compliance-theater checklist); no unsupported count is claimed.

NOTE: 2 retained:

- `qualify_c4b4a.py:40`: parser is intentionally bounded to this generated
  fixture, with a qualified fixed export-page coordinate offset. Absolute
  placement, outline, every pad and every drill independently validate that
  frame. Polarity/format/unsupported-command fault guards were tested. It is
  not a generic Gerber verifier; unexpected copper syntax fails.
- `measure_c4b4a.py:21`: analytic formula applies to accepted axis-aligned
  rectangular contact lands and circular locator holes only. Protected source
  hashes and accepted nominal guards prevent geometry substitutions. Shell
  curve comparison is within the accepted 0.001 mm observer tolerance.

All JSON dictionaries are read-only observations/manifests, not a parallel
model used to construct JITX design geometry. ZIP metadata is fixed; fabrication
member bytes remain untouched. Review asserts qualification fidelity only.
Final unresolved CRITICAL: 0; WARNING: 0; NOTE: 2.

## Task complete: C4B4A coupon and upload evidence

What was built: USBDFMCoupon + analytic measurement, supported generator,
read-only fidelity observer, qualification-only ZIP and human handoff.
Build: status ok twice via `jitx design build
he_piantor_42_jitx.usb_dfm_coupon.USBDFMCoupon --no-dependency-check`.
Primary/footprint source: accepted TYPE_C_31_M_12 / TYPEC31M12Landpattern,
unchanged project source. No new sourcing/data ingestion; accepted C4B3 is the
secondary measurement/disposition reference.
Checks: all four clearances, twelve lands, four shell pads/slots, two NPTH;
placement/layers/outline/silk, raw CAD/CAM input hashes, archive inventory/bytes;
20 C0/C1/C2 tests; lint/format/syntax/diff checks. Grep gates across package:
0 hard-fail hits, 0 review-required hits. Pyright unavailable in the existing
environment, no type-check pass claimed.
Interface notes: no functional power/signals/routing; one unpowered connector
geometry fixture. SI, decoupling, voltage domains, pin-mux and bus contention
N/A because no electronic system is being implemented. Component mappings stay
accepted; no connected nets needed for this geometry-only DFM experiment.
JITX code review (self): 0 unresolved critical/warnings, 2 bounded notes above.
Verdict (acceptance): accept for qualification handoff only. USB production
acceptance blocked pending separate external DFM/process evaluation.

## Phase exit gates

0 -> 1: PASS fixed user-authorized scope/data plan; baseline/source/environment
verified; PLAN and ARCHITECTURE exist under forward evidence.
1 -> 2: PASS reuse existing accepted component/substrate, no modeling changes;
public instantiation and independent measurement pass.
2 -> 3: PASS no new functional wiring/constraints required for geometry coupon.
3 -> 3b: PASS one component assembled/placed; no functional power-tree claim.
3b -> 4: PASS bounded geometry audit; no routes/vias/pours or changed pads.

## Phase 3b audit

Geometry: all source pad shapes and locator circles unchanged; rigid placement
preserves relative geometry. Export: supported one-way path and verified frame.
Manufacturing: four source gaps below unchanged 0.25 mm qualification rule;
smallest pair remains unresolved. Release limitations explicitly retained.
System-level EE/SI review N/A: unpowered, unrouted geometry-only coupon.

## Phase 4 verification

Two fresh supported JITX/KiCad CAM runs; source/PCB/Gerber/drill fidelity PASS.
Headless KiCad DRC executes with four expected hole errors and one library
warning; no DRC PASS claimed. Public source/CAM observation used; desktop JITX
UI review unavailable in this headless workflow, not a manufacturing certificate.
PCB DFM Check at JLCPCB is explicitly pending human action. No external DFM
result, supplier approval or adoption decision exists. PO MERGE/HOLD remains.
