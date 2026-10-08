"""Build only the isolated patched source, preserving upstream originals."""
from process import *
import shutil
BASE = Path(os.environ.get('EDA004D_WORK_DIR', '/tmp/eda004d'))
source = BASE / 'patched-converter'
(source / 'node_modules').symlink_to(BASE / 'runtime/node_modules')
# Exact existing kicadts build lock supplies tsup 8.5.1. Runtime lock is unchanged.
# Runtime artifact only: no declaration generation needed for this qualification.
run('patched-converter-build', [str(BASE / 'kicadts/node_modules/.bin/tsup-node'),
    'lib/index.ts', '--format', 'esm'], source, 180,
    artifacts=[('index.js', source / 'dist/index.js')])
shutil.copyfile(ROOT / 'convert.mjs', BASE / 'runtime/convert.mjs')
shutil.copyfile(source / 'dist/index.js', BASE / 'runtime/node_modules/circuit-json-to-kicad/dist/index.js')
save(EVIDENCE / 'patched-build.json', {'tsup_lock_reference':
    '../eda-004c/kicadts-build-package-lock.json', 'runtime_lock_reference':
    '../eda-004c/converter-package-lock.json', 'artifact_sha256': digest(source / 'dist/index.js'),
    'isolated_install_only': True, 'declaration_generation': 'omitted; not a runtime input'})
