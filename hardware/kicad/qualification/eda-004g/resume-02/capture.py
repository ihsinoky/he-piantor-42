"""New PO-authorized epoch; prior STOP/attempt/freeze evidence is read-only."""
import os
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
os.environ['EDA004D_EVIDENCE_DIR'] = str(ROOT/'evidence')
sys.path.insert(0,str(ROOT.parents[3]/'tscircuit/qualification/eda-004d'))
from process import run, save, digest, utc  # noqa: E402,F401
