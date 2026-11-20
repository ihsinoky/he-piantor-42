#!/usr/bin/env python3
"""Post-pass: assign JSWD (TC2050) pad nets BY PAD POSITION on the
saved work board. (Number-keyed assignment on the plugin-loaded
footprint landed on the wrong pads in this KiCad build - measured:
NPTH holes took SYS_3V3, NC pads 6/7/8 took GND. Positions are
unambiguous; numbers are only used as a cross-check printout.)
"""
import pcbnew as p

WORK = '.issue292-runtime/wmain-work.kicad_pcb'
mm = p.ToMM
B = p.LoadBoard(WORK)

def net(name):
    return B.FindNet(name).GetNetCode()

EXPECT = {  # (x, y) -> net name or None
    (107.96, 136.625): 'SYS_3V3', (109.23, 136.625): 'SWDIO',
    (110.50, 136.625): 'GND',     (111.77, 136.625): 'SWDCLK',
    (113.04, 136.625): 'GND',     (113.04, 135.355): None,
    (111.77, 135.355): None,      (110.50, 135.355): None,
    (109.23, 135.355): 'GND',     (107.96, 135.355): 'RESET_N',
    (106.69, 135.99): None,       (114.31, 134.974): None,
    (114.31, 137.006): None,
}
fp = None
for f in list(B.GetFootprints()):
    if f.GetFPID().GetUniStringLibId() == 'TC2050-IDC-NL':
        fp = f
assert fp is not None
done = 0
for pad in fp.Pads():
    pos = (round(mm(pad.GetPosition().x), 3), round(mm(pad.GetPosition().y), 3))
    # nearest expected position (the field is rotated -1.35 deg, so
    # actual pad positions sit up to ~0.1 mm off the axis-aligned
    # table; pads are 1.27 mm apart, so nearest-match is unique)
    best, hit = 1e9, None
    for (ex, ey), n in EXPECT.items():
        d = ((pos[0] - ex) ** 2 + (pos[1] - ey) ** 2) ** 0.5
        if d < best:
            best, hit = d, n
    assert best <= 0.15, ('unmatched pad', pos, pad.GetNumber(), best)
    pad.SetNetCode(net(hit) if hit else 0)
    print('pad num=%r at %s -> %s' % (pad.GetNumber(), pos, hit))
    done += 1
assert done == 13, done
B.Save(WORK)
print('pad nets fixed by position, saved')
