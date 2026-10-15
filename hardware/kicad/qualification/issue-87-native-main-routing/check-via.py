"""Check actual saved/reloaded copper with the same graph used by Main checker."""
import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('checker',ROOT/'check-main.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
results={}
for kind in ['connected','missing-via','short']:
    s=json.loads((ROOT/'evidence/processes'/('via-read-'+kind)/'snapshot.json').read_text());r=m.snapshot_graph(s);results[kind]=r
assert not results['connected']['shorts'] and not results['connected']['disconnected']
assert results['missing-via']['disconnected']=={'N':2} and not results['missing-via']['shorts']
assert results['short']['shorts'] and not results['short']['disconnected']
# Main baseline produces exactly the old result after graph factoring.
s=json.loads((ROOT/'evidence/processes/baseline-read/snapshot.json').read_text())
new=m.pcb(s);old=json.loads((ROOT/'evidence/baseline-parity.json').read_text())['pcb'];assert new==old
(ROOT/'evidence/via-checker-acceptance.json').write_text(json.dumps(dict(status='PASS_WITH_SCOPE',scope='three actual saved/reloaded tiny two-layer PCBs; via barrel joins both copper annuli; no via leaves overlapping F/B tracks electrically separate; wrong-net physical track contact detected',cases=results,main_baseline_regression_equal=True),indent=2)+'\n')
print('actual via positive, missing-via and short detection PASS; Main baseline unchanged')
