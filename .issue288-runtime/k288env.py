"""Issue #288 Stage 2 environment: KiCad 9.0.9 runtime from the main clone."""
import os
from pathlib import Path

KICAD = Path('/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad')
WT = Path('/home/hatch/workspace/projects/he-piantor-wmatrix')
RT = WT / '.issue288-runtime'
DONOR = WT / 'hardware/kicad/qualification/issue-182-matrix-rev3/board/m1-matrix18.kicad_pcb'
TREE = WT / 'hardware/kicad/qualification/issue-288-wmatrix'


def apply_env():
    for name in ('DISPLAY', 'WAYLAND_DISPLAY'):
        os.environ.pop(name, None)
    os.environ.update(
        PYTHONDONTWRITEBYTECODE='1',
        PYTHONPATH=str(KICAD / 'usr/lib/python3/dist-packages'),
        LD_LIBRARY_PATH=str(KICAD / 'usr/lib/x86_64-linux-gnu') + ':' + str(KICAD / 'usr/lib/kicad'),
        KICAD_STOCK_DATA_HOME=str(KICAD / 'usr/share/kicad'),
        KICAD_CLI=str(KICAD / 'usr/bin/kicad-cli'),
    )
    for name in ('CONFIG', 'CACHE', 'DATA', 'STATE'):
        d = RT / ('xdg-' + name.lower())
        d.mkdir(parents=True, exist_ok=True)
        os.environ['XDG_' + name + '_HOME'] = str(d)
    tmp = RT / 'tmp'
    tmp.mkdir(parents=True, exist_ok=True)
    os.environ['TMPDIR'] = str(tmp)
    os.environ['PATH'] = str(KICAD / 'usr/bin') + ':' + os.environ['PATH']
