"""Reuse recorded EDA-004C locks and same-source kicadts build procedure."""
from process import *
import shutil, tarfile
BASE = Path(os.environ.get('EDA004D_WORK_DIR', '/tmp/eda004d'))
PRIOR = ROOT.parent / 'eda-004c'
archive = PRIOR / 'evidence/raw/kicadts-source.tar.gz'
with tarfile.open(archive) as t:
    t.extractall(BASE / 'kicadts', filter='data')
source_files = json.loads((PRIOR / 'evidence/source-build-provenance.json').read_text())['source_files']
for name, expected in source_files.items():
    assert digest(BASE / 'kicadts' / name) == expected, name
save(EVIDENCE / 'kicadts-source-parity.json', {'status': 'PASS', 'commit':
    'f3ea106bdc65ca901e9b23255ad3be0bd2a624ab', 'files': source_files})
run('kicadts-install', ['npm', 'ci', '--ignore-scripts'], BASE / 'kicadts', 240)
run('kicadts-build', ['npm', 'run', 'build'], BASE / 'kicadts', 180,
    artifacts=[('index.js', BASE / 'kicadts/dist/index.js'),
               ('index.d.ts', BASE / 'kicadts/dist/index.d.ts')])
run('converter-runtime-install', ['npm', 'ci', '--ignore-scripts'], BASE / 'runtime', 240)
shutil.copytree(BASE / 'kicadts/dist', BASE / 'runtime/node_modules/kicadts/dist')
save(EVIDENCE / 'runtime-provenance.json', {
    'converter_lock': digest(BASE / 'runtime/package-lock.json'),
    'kicadts_build_lock': digest(BASE / 'kicadts/package-lock.json'),
    'kicadts_dist': digest(BASE / 'kicadts/dist/index.js'),
    'original_converter_dist': digest(BASE / 'runtime/node_modules/circuit-json-to-kicad/dist/index.js'),
    'method': 'EDA-004C exact locks; lifecycle disabled; upstream npm run build; same-source dist attached to exact locked Git dependency'})
