# Main Rev.6 review package — not released for manufacture

Use this directory's `main-rev6-fabrication-review.zip`, `BOM.csv` and
`CPL-jlcpcb-gerber-frame.csv` together. The CPL uses the actual Gerber origin;
`CPL.csv` retains the Rev.5 legacy datum and must not be substituted without the
verified translation. All 55 placements and 1,485 relative vectors were checked.
Gerber centerlines, copper, masks, paste and separated plated/non-plated drills
were independently read back against the final board. Four-layer/1.2 mm board
and electrical design/material assumptions are unchanged from Rev.5.

Outline: six straight edges, with all three former 60° tips cut back 4 mm along
each adjoining side. Minimum copper distance to a new face is 0.549999609 mm.
BOM and component poses are identical to Rev.5, including J4 Molex 781710004 /
C588524, J2 and J3. No Matrix, Wing or case revision is included.

All Rev.5 gates remain: supplier DFM, stencil/paste acceptance, stock confirmation,
CPL rotation/pin1 acceptance, assembled cable/mating/strain-relief fit and physical
power/noise checks. Before first Main power, test the Fly while disconnected from
Main: with Fly on USB, measure cable pin1 relative to pin4 and record +5 V/GND
polarity; disconnect power before attaching Main. Refer to D-035 and the Rev.5
handoff for inherited assembly details. This work authorizes no quote submission,
order, PO adoption or manufacturing release.
