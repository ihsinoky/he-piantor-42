import sys
from pathlib import Path
import pcbnew
sys.path.insert(0, str(Path(__file__).parent))
from s24_router import Obstacles, route

TREE = Path('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix')
b = pcbnew.LoadBoard(str(TREE / 'wmatrix.kicad_pcb'))
obs = Obstacles(b)
nc = b.FindNet('HALL_3V3').GetNetCode()
src = (115.067925, 120.375, 0)
tests = {
    'C_MUX_B pad1 (105,120.16)': (105.0, 120.156067, 0),
    'C_MUX_C pad1 (123,120.16)': (123.0, 120.156067, 0),
    'MUXC pin13 (120.93,121.03)': (120.932075, 121.025, 0),
    'R_SHUNT pad S (121,130.95)': (121.0, 130.95, 0),
    'MUXB pin2 via neck comp (97.07,120.38)': (97.067925, 120.375, 0),
}
for name, dst in tests.items():
    res = route(obs, src, dst, nc, 0.10)
    print(name, '->', 'OK' if res else 'FAIL')
