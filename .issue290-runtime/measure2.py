import sys, traceback
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
import fitlibF as FF
from build123d import Box, Pos
bodies = dict(FF.bodies_at(17, -2.65))
shell = bodies['shell-central']
def probe_z(solid, x, y):
    p = Pos(x, y, 11) * Box(1.0, 1.0, 30)
    c = solid & p
    if c is None or c.volume < 1e-6:
        return None
    bb = c.bounding_box()
    return (round(bb.min.Z, 2), round(bb.max.Z, 2))
print('shell-central bottom/top Z; X = -40..40 step 8')
for y in (60, 45, 32, 20, 8, -4, -16, -28, -40, -50):
    cells = []
    for x in range(-40, 41, 8):
        r = probe_z(shell, x, y)
        cells.append('   .   ' if r is None else f'{r[0]:.0f}/{r[1]:.0f}')
    print(f'Y={y:4d}: ' + ' '.join(cells))
