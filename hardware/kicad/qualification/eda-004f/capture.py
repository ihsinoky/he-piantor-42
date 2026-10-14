"""Reuse the unchanged EDA-004D recorder, isolating all new evidence."""
import os
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
os.environ['EDA004D_EVIDENCE_DIR'] = str(ROOT / 'evidence')
sys.path.insert(0, str(ROOT.parents[2] / 'tscircuit/qualification/eda-004d'))
from process import run as _run, save, digest, utc  # noqa: E402,F401


def run(name, *args, **kwargs):
    if (ROOT / 'evidence/terminal-result.json').exists() and not name.startswith(
        ('verify-', 'record-', 'git-', 'ci-')
    ):
        raise RuntimeError('Completed bounded evaluation: further experiments forbidden')
    return _run(name, *args, **kwargs)
