# Rev.M1 / Rev.A DFM policy

Accepted DFM baseline under [D-017](../../docs/decisions.md#d-017---revm1-mainwing-architecture-and-interface-freeze); no panel, PCB or manufacturing
dataset is designed here. Rev.M1 Main layer/rule assumptions are revised by
[D-019](../../docs/decisions.md#d-019---revm1-main-four-layer-and-010-mm-design-rule-baseline). See [D-015](../../docs/decisions.md) and
[project gates](../../docs/project-status.md#human-gates).

For **Rev.M1 Main only**, [D-019](../../docs/decisions.md#d-019---revm1-main-four-layer-and-010-mm-design-rule-baseline)
sets four copper layers (F.Cu signal / In1.Cu GND plane / In2.Cu signal /
B.Cu signal), 1.2 mm thickness, 0.10 mm trace width / clearance, and
0.60/0.30 mm via diameter/drill. The two-layer baseline was the D-012-era
assumption. Wing layer construction and design rules remain unevaluated under
these conditions and are outside D-019; do not apply the Main change to Wings.

Prefer JLCPCB Economic PCBA where practical and retain the existing 1.2 mm
thickness baseline. Place SMD components on one side by default. Prefer Basic
parts, then Promotional Extended parts;
minimize unnecessary distinct Extended part types. Do not sacrifice electrical
or mechanical performance merely to reduce an Extended-part count. Actual
service eligibility, component classification, availability and quotation
must be verified later for the selected manufacturing package.

For Rev.M1, attempt if practical to place Main + Evaluation Wing within a
100 x 100 mm manufacturing area / heterogeneous panel concept. This is a
cost experiment/optimization; it must not distort electrical validation,
representative interconnect or pitch experiments. Main and Wing may be ordered
separately if required. C4A creates no panel layout and assumes no vendor panel
approval or price.

For Rev.A, Left and Right Wings may be separate PCB designs/manufacturing
datasets generated from the same project-owned definition. A single reversible
left/right PCBA is not required. 100 x 100 mm per Wing is desirable if the
chosen pitch allows it, but do not force 16.0 mm solely for cost. Magnetic
performance and usability take priority. Future geometry source must be
project-owned or explicitly approved at a later Human Gate; do not consume
`hardware/layout/**`.

**Representative Wing exception / superseded target (2026-11-05):**
[D-020](../../docs/decisions.md#d-020---representative-21-key-wing-100-x-100-mm-requirement-relaxation)
relaxes the historical 100 x 100 mm target for the Issue #127 representative
21-key Wing only, preserving Piantor geometry and accepting 110 x 100 mm
(16.0 mm pitch) / 116.5 x 104.75 mm (17.0 mm pitch). This does not change
3 x 3 pitch-evaluation Wing dimensions or approve a panel/manufacturing package.

G0B accepted these DFM constraints with architecture/interface and Main reuse.
The original D-017-era plan named EDA-003B representative stock-tscircuit
physical/routing proof next, with full Rev.M1 implementation conditional on
acceptance. EDA-003B and later method evaluations have since ended without
qualifying the current product path; that sequence is historical, not an
authorized next step. See the [current project status](../../docs/project-status.md).
G1
requires actual Main + Evaluation Wing manufacturing package, DRC/ERC, BOM,
Gerber, drill and placement outputs and pre-order review. G3 applies to the
later complete Rev.A package. No order or manufacturing release is authorized
by G0B. **USB NPTH — OPEN — PRE-ORDER DFM REVIEW REQUIRED** remains unchanged;
no manufacturing exception is granted. Final placement/routing and final
USB/system power qualification remain open.

Via-in-pad / paste-opening order specifications remain undecided: Issue #121's
25 observations are manufacturing notes, not DRC violations. USB J1 PTH
retention-leg assembly process also remains undecided, pending Issue #124.
See [D-019](../../docs/decisions.md#d-019---revm1-main-four-layer-and-010-mm-design-rule-baseline); no specification or
process is selected here.
