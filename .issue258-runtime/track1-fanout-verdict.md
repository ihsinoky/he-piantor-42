# Track 1 fanout verdict (N3, rotate-in-place t=0, KRT first pass + KiCad DRC)
Pose: J_WING rotated about Rev.4 anchor (case (+-27,-41)) by +90 (R) / -90 (L);
case pad row -> X=+-28.85, Y -32.87..-49.12; exit face X=+-20.95 toward bay.
Transform verified: pure rotation, all 14 pads err 0.0; U_MUX_C/B, U_HC1
centres map exactly onto phaseb case bounds (no reflection).
| variant | DRC | unconnected | blockers |
| 17R | 7 | 4 | pad14 x TP_W_H5V + TP_H_DIAG_RAW shorts (GND x HALL_5V, GND x H_C0_RAW); pad3 across Edge.Cuts (0.000 mm) |
| 17L | 5 | 2 | pad1 x TP_H_DIAG_RAW short (HALL_5V x H_C0_RAW); pad12 across Edge.Cuts |
| 16R | 7 | 8 | same classes as 17R |
| 16L | 8 | 3 | pad1 x TP_H_DIAG_RAW short; pad12 across Edge.Cuts (+2 GND track edge) |
Minor classes (solder_mask_bridge from the pad overlaps, silk) omitted above.
Verdict: fanout CANNOT CLOSE on any variant at this pose class - blockers are
placement-level (rotated pad row sweeps the B.Cu test-pad field at one end and
the slanted board edge at the other), not router residuals. Per brief, Track 1
stops here; harness gates NOT RUN. The #253 inner-corner-with-tab variant
(needs the outline extension) is outside this pose class and remains unrun.
