import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, route

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
nc = b.FindNet('GND').GetNetCode()
tests = [
    ('VSS->trackpt 0.30w', (78.25, 118.4, 0), (79.067925, 121.025, 0), 0.30),
    ('VSS->trackpt 0.10w', (78.25, 118.4, 0), (79.067925, 121.025, 0), 0.10),
    ('VSS->TP_GND_B pad', (85.0, 127.0, 0), (79.067925, 121.025, 0), 0.30),
    ('EN_A pads 0.10w', (50.25, 90.7, 0), (50.25, 74.7, 0), 0.10),
    ('REF A->B 0.10w', (84.932075, 124.275, 0), (102.932075, 124.275, 0), 0.10),
]
for name, pa, pb, w in tests:
    n = {'GND': nc}.get(name.split()[0], None)
    res = route(obs, pa, pb, nc if 'VSS' in name or 'TP' in name else b.FindNet(name.split()[0]).GetNetCode(), w)
    print(name, '->', 'OK' if res else 'FAIL')
