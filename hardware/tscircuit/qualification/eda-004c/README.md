# EDA-004C evidence

**CONVERSION_BLOCKED / C1_DUPLICATE_GND_PAD_NET_LOSS**, Issue #75 / PR #76.
Synthetic source checks pass after disclosed preparation corrections, but the
second U_TX GND land loses its net in KiCad. DRC reports shorting_items;
synthetic schematic semantics/ERC also fail. Smoke initial/fresh routes 0/0;
Main 0. DSN/SES/post-route/reproducibility NOT ENTERED. No adoption or Human Gate.

See the [report](../../../../docs/alternate-physical-backend-smoke-requalification.md)
and evidence/final-classification.json. Historical EDA-004B files are untouched;
new raw is not a reconstruction of its missing output.

`process.py` preserves raw before checks and stops caller sequences on failure.
Acquisition/install scripts document executed preparation, not permission to
restart experiments. `check-input.py`, `check-boundary.py` and `test-checkers.py`
only examine saved data. `python3 -B validate.py` is read-only and launches no EDA
experiment. Full physical island/short/clearance verification is NOT ENTERED.
