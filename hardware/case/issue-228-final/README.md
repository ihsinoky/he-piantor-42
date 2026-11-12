# Issue #228 — Phase C Fly candidate (BLOCKED)

Extends the PO-approved Phase A/B production tree. Both pitches have a local
north-wall Fly V4.2 seat; the receptacle face is 0.30 mm inside the outer wall.
PCB bottom remains Z10 mm. Two M2x6 screws / 0.5 mm insulating washers use
Ø4.5 mm bosses and Ø1.7 mm pilots, on 19 mm centers. There are **13 PCB fixing
points** (Main 3 + Wings 8 + Fly 2); four separate splice screws remain.

**This candidate does not pass the complete Phase C acceptance gate.** The
PO-supplied official STEP has an invalid USB shell (solid index 42 on direct
import). Its modeled internals also overlap the hollow reference USB plug at
nominal 6.2 mm engagement. The model is preserved without healing or remodeling.
`check_3d.py` writes its measurements and PNGs, then exits nonzero for these
blockers. A passed `verify.py` means the retained #198 checks with explicitly
reported connector mating reservations; see `phase_c_passed` as well.

The source STEP is copied byte-for-byte to
`inputs/TheFly_DaughterBoard_V4.2.stp`; assembly uses its complete 68 solids with
only a rigid Z180 rotation and translation. `fly.py` measures the PCB and holes,
creates the local recess/bosses, the USB reference plug, two EZmate reservations,
and a connected 170 mm R5 / Ø2 mm cable with stored service slack. Actual Rev.6 PCB data verifies Main J4's unchanged
position and 781710004 identity. Main's inherited board envelope is conservative
at the Rev.6 chamfered corners; its pocket and all other reference components
remain unchanged. J4 uses the official Fly's identical header solid aligned to
the Rev.6 pad row, top face up.

The front recess follows the real PCB scallops and lobes with 0.5 mm nominal
clearance. At 16 mm, the PCB-height scalloped relief extends into the old Wing
wall protection band, within the daughterboard bay, while remaining disjoint
from both Wing clearance pockets. Deep cavity and mounting features are retained. Wall material beside the port is retained. The opening is W16, starts at Z9.7, and opens through the Z15.2 case top. Its cut
ends at Z16.7 above the case. Reference plug: 8.25 × 2.40 mm hollow rounded shell,
0.20 mm wall, 6.65 mm exposed length; 12 × 6 mm overmold, 15 mm long; Ø4 mm cable
exit, 25 mm long. A larger 8.9 × 3.2 mm shell travel envelope checks the requested
case clearance. A continuous 30 mm insertion sweep checks every intermediate
position against case, PCB, hardware and other assembly parts. Intended connector
internals are reported separately and prevent a strict mating pass.

EZmate 781720004 reservations use 5.0 × 3.5 × 1.3 mm housing and a 1.9 mm mated
stack from Molex drawings 781720000-SD / 781710000-SD. Fly mates from below;
Main J4 mates from above. The nominal direct-route references are 73.871 / 72.499 mm
(17 / 16 pitch). The connected exported centerline is exactly **170 mm** in each
pitch: all 30 mm service allowance and 66.129 / 67.501 mm residual budget are
physically stored in an open central service detour. This replaces the nominal
central transit with an elevated R5 loop at centerline Z25 mm (tube top Z26 mm),
within X±8 mm. It rises north of the unchanged rack and descends east of it.
`route_length_mm` remains the nominal reference budget; `connected_length_mm`
and `waypoints_mm` describe the actual single connected exported cable. No
separate closed ring is counted toward length. Reloaded checks include Wing
routes, Wing storage reservations, all source instances and keycap volumes.

`usb-overlap-curve.json` contains the unmodified nominal hollow shell overlap
with original source solids 41 and 42 at 0..6 mm in 0.25 mm increments, plus
6.20 mm. The onset is numerically bracketed using a 1e-8 mm³ volume threshold.
These curves are decision material; strict connector qualification remains FAIL.

Checkpoint reconciliation found stale 16 mm PASS claims in the interrupted
report. The subsequent fix round relieves its Fly PCB/washer collisions at Z10.
Both retained verifiers now pass; strict checkers retain the source connector
blockers. The 17 mm case remains identical to checkpoint STEP DATA. No board,
fixing, rack, Wing reservation or connector is moved.

The approved outline, Wing/Main pockets, split at X3.5, splice plates, Wing
harness, storage rack and heights elsewhere are retained. `check_scope.py`
compares the trays against Phase B commit e54f583c: zero added/removed volume
outside the daughterboard bay. The only permitted removal in the old Wing
clearance-plus-2-mm wall band is the 16 mm scalloped PCB-height relief; the
actual Wing clearance pockets remain intact. The 16 mm checkpoint comparison
allows only that relief, with zero added material; the 17 mm trays must retain
identical normalized STEP DATA. It also compares the unchanged auxiliary STEP
DATA records, normalizing only assembly occurrence serial numbers.

Each pitch has STEP/STL for the five printable parts, `assembly.step`,
`harness.step`, `storage-200mm.step`, `fly-harness-and-usb.step`, dimension,
verification, outline, scope and 3D JSON, shelf CSV, review SVG, export manifest,
`assembled-top.png`, `north-wall-closeup.png` and `usb-overlap-curve.json`. The PNGs use actual exported
BRep triangles; the invalid official USB shell is shown using its actual BRep
edges because that source solid cannot tessellate. Only the five printable parts
are printable; the assembly is a blocked review candidate.

Reproduce from the checkout root; all writable runtime paths remain local:

```bash
mkdir -p .issue228-runtime/tmp .issue228-runtime/mplconfig
export TMPDIR="$PWD/.issue228-runtime/tmp"
export XDG_CACHE_HOME="$PWD/.issue228-runtime/cache"
export MPLCONFIGDIR="$PWD/.issue228-runtime/mplconfig"
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
CAD_PY="$PWD/.issue228-runtime/cad-venv/bin/python"
"$CAD_PY" hardware/case/issue-228-final/check_outline.py
for pitch in 17 16; do
  "$CAD_PY" hardware/case/issue-228-final/generate.py --pitch "$pitch"
done
GIT_DIR=./.issue228-runtime/git "$CAD_PY" hardware/case/issue-228-final/check_scope.py
for pitch in 17 16; do
  # Expected nonzero: writes audits/PNGs/curves, then reports preserved blockers.
  "$CAD_PY" hardware/case/issue-228-final/check_3d.py "$pitch"
  # Both pitches PASS the complete retained suite.
  "$CAD_PY" hardware/case/issue-228-final/verify.py "hardware/case/issue-228-final/${pitch}mm"
done
```

See [Phase C report](../../../.issue228-runtime/REPORT.md) for exact results and
remaining blockers. No push or PR changes; PR #229 remains held.
