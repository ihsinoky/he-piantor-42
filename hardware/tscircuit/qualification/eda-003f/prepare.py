"""Prepare independent A/B environments from the accepted exact stock lock.

Usage: python3 prepare.py /tmp/ABSENT_ENV
Then cd ENV && npm ci --ignore-scripts (B patches are applied separately).
"""
from pathlib import Path
import hashlib
import json
import shutil
import sys

here = Path(__file__).resolve().parent
stock = here.parent/'eda-003c/latest-stock'
out = Path(sys.argv[1]).resolve()
assert not out.exists(), 'Use an absent environment directory'
out.mkdir(parents=True)
for name in ['package.json','package-lock.json','src','scripts']:
    source, target = stock/name, out/name
    if source.is_dir(): shutil.copytree(source,target)
    else: shutil.copy2(source,target)
assert json.loads((out/'package.json').read_text())['dependencies']['tscircuit']=='0.0.2748'
assert hashlib.sha256((out/'package-lock.json').read_bytes()).digest()==hashlib.sha256((stock/'package-lock.json').read_bytes()).digest()
print(out)
