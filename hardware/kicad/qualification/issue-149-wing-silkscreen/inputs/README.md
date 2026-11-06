# Frozen comparison inputs — not manufacturing candidates

`issue147/{16,17}mm/preflight.json` and `gerber/` are byte-identical copies of
prior #147 evidence. `provenance.json` records their original paths and hashes.
They preserve the prior no-silk comparison baseline even though PR #148 is unmerged.
The prior source PCB hash equals the tracked #141 accepted board in each pitch.
Only the new root-level `wing-*-silk149-review.zip` files supersede #147 candidates.
