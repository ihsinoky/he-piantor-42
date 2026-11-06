"""Issue 147: read-only source access and isolated temporary state."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import time

R = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parent
T = R / '.issue147-runtime'
SOURCE = R / 'hardware/kicad/qualification/issue-141-wing-power-integrity'


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def environment():
    env = dict(os.environ)
    for name in ('DISPLAY', 'WAYLAND_DISPLAY'):
        env.pop(name, None)
    kicad = R / '.issue129-runtime/kicad'
    env.update(PYTHONDONTWRITEBYTECODE='1',
               PYTHONPATH=str(kicad / 'usr/lib/python3/dist-packages') + ':' +
               str(R / '.issue129-runtime/geometry/lib/python3.12/site-packages'),
               LD_LIBRARY_PATH=str(kicad / 'usr/lib/x86_64-linux-gnu') + ':' + str(kicad / 'usr/lib/kicad'),
               KICAD_STOCK_DATA_HOME=str(kicad / 'usr/share/kicad'),
               KICAD_CLI=str(kicad / 'usr/bin/kicad-cli'), TMPDIR=str(T / 'tmp'))
    for name in ('CONFIG', 'CACHE', 'DATA', 'STATE'):
        env['XDG_' + name + '_HOME'] = str(T / name.lower())
    for name in ('tmp', 'config', 'cache', 'data', 'state'):
        (T / name).mkdir(parents=True, exist_ok=True)
    return env


def run(name, argv, timeout=300):
    dest = E / 'processes' / name
    dest.mkdir(parents=True, exist_ok=False)
    start = now()
    tick = time.monotonic()
    with (dest / 'stdout').open('w') as out, (dest / 'stderr').open('w') as err:
        result = subprocess.run(list(map(str, argv)), cwd=R, env=environment(),
                                stdout=out, stderr=err, timeout=timeout, check=False)
    save(dest / 'record.json', dict(argv=list(map(str, argv)), cwd=str(R),
         start_utc=start, end_utc=now(), elapsed_seconds=time.monotonic() - tick,
         exit_code=result.returncode, timeout_seconds=timeout))
    if result.returncode:
        raise RuntimeError(f'{name}: exit {result.returncode}; see {dest}')

