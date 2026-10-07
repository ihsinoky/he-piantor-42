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
m.terminal_contract(r,l)
mutations=[
 ('false PASS', lambda a,b:a.update(primary_classification='MAIN_PASS')),
 ('false zero', lambda a,b:a['main_metrics'].update(required_unrouted=0)),
 ('false ERC', lambda a,b:a.update(erc_status='PASS')),
 ('hidden attempt', lambda a,b:b['main_initial'].append({'partial':True})),
 ('hidden routing count', lambda a,b:b.update(smoke_routing_process_count=1)),
 ('false complete capture', lambda a,b:a.update(evidence_completeness='COMPLETE')),
]
for name,mutate in mutations:
 a,b=copy.deepcopy(r),copy.deepcopy(l);mutate(a,b)
 try:m.terminal_contract(a,b)
 except AssertionError:continue
 raise AssertionError('Accepted corrupt report: '+name)
print(json.dumps({'result':'PASS','adversarial_reporting_cases':len(mutations),'geometry_fault_cases':'NOT ENTERED'}))
