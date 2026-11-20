"""Invariant (2): after the swap, U1 pad-number -> net assignment on the
new board must equal the pre-swap board's exactly (nets follow numbers),
and sampled assignments must match DS1807 S3 functions."""
import pcbnew as p, sys
from pathlib import Path
E = Path('.').resolve()
old = p.LoadBoard(str(E.parent/'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb'))
new = p.LoadBoard(sys.argv[1])
def m(b):
    u = [f for f in b.GetFootprints() if str(f.GetReference()) == 'U1'][0]
    return {pad.GetNumber(): pad.GetNetname() for pad in u.Pads()}
mo, mn = m(old), m(new)
diff = {k: (mo.get(k), mn.get(k)) for k in set(mo) | set(mn) if mo.get(k) != mn.get(k)}
print('old pads:', len(mo), 'new pads:', len(mn), 'assignment diffs:', diff)
# Spot checks vs DS1807 R19 pin table (pp.9-10) + maker Eagle pinmap:
# 1 VSS, 2 P0.09 (unused here), 12 VBUS, 24 VSS, 26 VCC_nRF, 28 SWDIO, 30 SWDCLK
spot = {'1': 'GND', '2': '', '7': 'GND', '12': 'VBUS', '20': 'ANT_LINK', '22': 'ANT_LINK',
        '24': 'GND', '26': 'SYS_3V3', '28': 'SWDIO', '30': 'SWDCLK', '13': 'RESET_N'}
for k, v in spot.items():
    print('pin', k, 'expected', v, 'actual', mn.get(k), 'OK' if mn.get(k) == v else 'MISMATCH')
nc = [k for k in map(str, range(65, 79)) if mn.get(k)]
print('NC pads 65-78 carrying a net (must be []):', nc)
