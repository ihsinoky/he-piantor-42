import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, route

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
nc = b.FindNet('HALL_3V3').GetNetCode()
src = (97.067925, 120.375, 0)  # U_MUXB pin2, in the stranded fragment
tests = {
    'C_MUX_A pad1 (87,120.16)': (87.0, 120.156067, 0),
    'MUXA pin2 (79.07,120.38)': (79.067925, 120.375, 0),
    'R_SHUNT pad S (121,130.95)': (121.0, 130.95, 0),
    'C_MUX_B pad2 GND-side n/a': (105.0, 121.843933, 0),
}
for name, dst in tests.items():
    if 'n/a' in name:
        continue
    res = route(obs, src, dst, nc, 0.10)
    print(name, '->', 'OK' if res else 'FAIL')
