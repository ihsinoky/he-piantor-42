# Interrupted tuning inventory (continuation)

Starting checkpoint: 47f7dd5. The first-candidate directory remains immutable.

Kept for verification: 17mm assembly-index/measurements/geometry-finish and hardware-inventory; M2x10 hardware and local north-head relief implementation; volume-preserving boundary regularizer and its intermediate two-solid diagnostic; bounded-face cap distance implementation. These are development checkpoints, not gate certification. Current exports/audits still describe the first candidate until regenerated.

Kept as experimental source only: routes_tuning.py and transport.py. Sampled tests in runtime show fan crossings, so these routes have not replaced fitted conductors. Runtime scratch is retained under .issue248-runtime/tuning, including a continuation-start geometry snapshot. __pycache__ is excluded from commits. No board or aluminium plate input is edited.

Continuation disposition: the interrupted metadata/geometry was retained as an early development commit, then superseded by fresh builds and full gate outputs for both pitches. Kept M2x10, bounded-face cap audit and volume-preserving 17mm shell repair. Rejected the interrupted transport/fan route as a fitted design (source kept for review); replaced fitted routes with a new corridor candidate, which clears fixed MUX bounds but still fails strand/fixed-part checks. Discarded generated __pycache__. The first-candidate evidence was not edited; obsolete current transition proofs were moved to per-pitch evidence/ because fresh builds cannot reuse their old geometry hashes. No board or aluminium source bytes changed.

The nominal-only M2x10 engagement claim was not sufficient: a later exact annulus probe found only 32.5% remaining material at the two north E seats. Their original source support material was restored (pilots retained), and verify_hardware.py now requires the complete thread-bearing annulus and root probe at all eight seats. Changed tray pairs and service motion were rerun; untouched exact-pair results are replayed only with identical serialized operand hashes and independently verified parent evidence. This supersedes the interrupted engagement metadata.
