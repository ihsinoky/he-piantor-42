# Rev.M1 / Rev.A DFM policy

Accepted DFM baseline under [D-017](../../docs/decisions.md#d-017---revm1-mainwing-architecture-and-interface-freeze); no panel, PCB or manufacturing
dataset is designed here. See [D-015](../../docs/decisions.md) and
[project gates](../../docs/project-status.md#human-gates).

Prefer JLCPCB Economic PCBA where practical, two copper layers unless separately
reconsidered, and the existing 1.2 mm thickness baseline. Place SMD components
on one side by default. Prefer Basic parts, then Promotional Extended parts;
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

G0B accepted these DFM constraints with architecture/interface and Main reuse.
EDA-003B representative stock-tscircuit physical/routing proof is next; if
accepted, full Rev.M1 implementation follows. G1
requires actual Main + Evaluation Wing manufacturing package, DRC/ERC, BOM,
Gerber, drill and placement outputs and pre-order review. G3 applies to the
later complete Rev.A package. No order or manufacturing release is authorized
by G0B. **USB NPTH — OPEN — PRE-ORDER DFM REVIEW REQUIRED** remains unchanged;
no manufacturing exception is granted. Final placement/routing and final
USB/system power qualification remain open.
