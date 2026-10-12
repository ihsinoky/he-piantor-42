"""Thin adapter; original recorder remains unchanged at the baseline commit."""
import os
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
os.environ['EDA004D_EVIDENCE_DIR'] = str(ROOT / 'evidence')
sys.path.insert(0, str(ROOT.parents[2] / 'tscircuit/qualification/eda-004d'))
from process import run, save, digest, utc  # noqa: E402,F401
