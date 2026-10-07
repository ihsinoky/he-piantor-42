"""Reuse accepted EDA-003D classifier for a supplied, unedited router output.
Only the input/output paths and stale accepted-population descriptive text adapt.
"""
import importlib.util
import inspect
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('accepted_classifier', here.parent/'eda-003d/classify.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
source = inspect.getsource(module.classify)
source = source.replace("accepted = HERE.parent/'eda-003c/evidence'\n    raw = gzip.decompress((accepted/'raw/latest-main.circuit.json.gz').read_bytes())", "raw = (HERE/'circuit.json').read_bytes()")
source = source.replace('The 37 distinct net/NC pairs are an independent lower bound regardless of such merges.', 'Distinct net/NC pairs provide a lower bound regardless of such merges.')
source = source.replace('the 71 accepted records', 'the replayed material records')
module.HERE = Path(sys.argv[1]).resolve()
(module.HERE/'evidence').mkdir(exist_ok=True)
exec(compile(source, __file__, 'exec'), module.__dict__)
module.classify()
