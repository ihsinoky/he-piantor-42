import copy,importlib.util,json
from pathlib import Path
from process import EVIDENCE,ROOT,save
spec=importlib.util.spec_from_file_location('v',ROOT/'validate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
r=json.loads((EVIDENCE/'final-classification.json').read_text());l=json.loads((EVIDENCE/'attempt-ledger.json').read_text());s=json.loads((EVIDENCE/'stop-decision.json').read_text())
v.terminal(r,l,s)
cases=[('false SMOKE_PASS',lambda a,b,c:a.update(classification='SMOKE_PASS')),('false zero',lambda a,b,c:a['required_acceptance_metrics']['required_unconnected'].update(initial=0)),('hidden attempt',lambda a,b,c:b['attempts'].append({'kind':'initial'})),('false technical complete',lambda a,b,c:a.update(technical_qualification_complete=True)),('false adoption',lambda a,b,c:a.update(backend_adopted=True)),('changed first gate',lambda a,b,c:c.update(first_terminal_gate='ENVIRONMENT_BLOCKED')),('hidden post-stop process',lambda a,b,c:a.update(after_stop_experiment_count=1)),('false reproducibility',lambda a,b,c:a['stages'].update(normalized_connection_shape_reproducibility='PASS'))]
for name,mutate in cases:
 a,b,c=map(copy.deepcopy,[r,l,s]);mutate(a,b,c)
 try:v.terminal(a,b,c)
 except AssertionError:continue
 raise AssertionError('reporting mutation escaped: '+name)
save(EVIDENCE/'reporting-fault-tests.json',{'status':'PASS','count':len(cases),'tests':[x[0] for x in cases]})
print(f'{len(cases)} reporting faults detected')
