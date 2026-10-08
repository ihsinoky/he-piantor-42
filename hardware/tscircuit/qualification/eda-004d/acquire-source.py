"""Capture exact converter upstream, without relying on an existing /tmp tree."""
from process import *
BASE = Path('/tmp/eda004d')
BASE.mkdir(exist_ok=False)
run('converter-source-download', ['curl', '-fL',
    'https://codeload.github.com/tscircuit/circuit-json-to-kicad/tar.gz/8dee5b926f5db28800292b46b66a712c71aba055',
    '-o', str(BASE / 'converter-source.tar.gz')], BASE, 120,
    artifacts=[('converter-source.tar.gz', BASE / 'converter-source.tar.gz')])
run('converter-source-extract', ['tar', '-xzf', str(BASE / 'converter-source.tar.gz'),
    '-C', str(BASE)], BASE)
