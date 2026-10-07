#!/usr/bin/env python3
"""Adversarial reporting checks only. No KiCad/geometry coverage claim."""
import copy
import importlib.util
import json
import sys
from pathlib import Path
sys.dont_write_bytecode = True
p=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('validation',p/'validate.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=json.loads((p/'evidence/final-classification.json').read_text())
l=json.loads((p/'evidence/attempt-ledger.json').read_text())
secondary=json.loads((p/'evidence/converter-package-failure.json').read_text())
m.terminal_contract(r,l,secondary)
mutations=[
 ('false PASS', lambda a,b,c:a.update(primary_classification='MAIN_PASS')),
 ('false zero', lambda a,b,c:a['main_metrics'].update(required_unrouted=0)),
 ('false ERC', lambda a,b,c:a.update(erc_status='PASS')),
 ('hidden attempt', lambda a,b,c:b['main_initial'].append({'partial':True})),
 ('hidden routing count', lambda a,b,c:b.update(smoke_routing_process_count=1)),
 ('false complete capture', lambda a,b,c:a.update(evidence_completeness='COMPLETE')),
 ('secondary restored as first result gate', lambda a,b,c:a.update(first_terminal_gate=m.SECONDARY_GATE)),
 ('secondary restored as first ledger gate', lambda a,b,c:b.update(first_terminal_gate=m.SECONDARY_GATE)),
 ('secondary metadata falsely first', lambda a,b,c:c.update(first_terminal_gate=m.SECONDARY_GATE)),
 ('all records agree on wrong first gate', lambda a,b,c:[record.update(first_terminal_gate=m.SECONDARY_GATE) for record in (a,b,c)]),
 ('reversed observation order', lambda a,b,c:a['ordered_failure_observations'].reverse()),
 ('false immediate stop', lambda a,b,c:b.update(immediate_stop_compliance=True)),
 ('technical completion false claim', lambda a,b,c:a.update(technical_qualification_complete=True)),
 ('ambiguous completion field restored', lambda a,b,c:a.update(qualification_execution_complete=True)),
 ('hidden post-failure operation', lambda a,b,c:b.update(operations_after_first_failure=[])),
 ('guessed numeric exit code', lambda a,b,c:a['ordered_failure_observations'][0].update(exit_code=1)),
]
for name,mutate in mutations:
 a,b,c=copy.deepcopy(r),copy.deepcopy(l),copy.deepcopy(secondary);mutate(a,b,c)
 try:m.terminal_contract(a,b,c)
 except AssertionError:continue
 raise AssertionError('Accepted corrupt report: '+name)
print(json.dumps({'result':'PASS','adversarial_reporting_cases':len(mutations),'geometry_fault_cases':'NOT ENTERED','meaning':'Reporting tests only; not geometry/backend qualification PASS'}))
