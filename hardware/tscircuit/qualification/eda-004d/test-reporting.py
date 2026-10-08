"""In-memory outcome fault tests and launch-free terminal STOP guard check."""
from process import *
import copy
from validate import check_outcome
outcome=json.loads((EVIDENCE/'final-classification.json').read_text())
pre=json.loads((EVIDENCE/'pre-route-acceptance.json').read_text())
ledger=json.loads((EVIDENCE/'attempt-ledger.json').read_text())
check_outcome(outcome,pre,ledger)
results=[]
def fault(name,change):
 a=copy.deepcopy(outcome);b=copy.deepcopy(pre);c=copy.deepcopy(ledger);change(a,b,c)
 try:check_outcome(a,b,c)
 except AssertionError:results.append({'name':name,'detected':True});return
 raise AssertionError(name)
fault('false classification PASS',lambda a,b,c:a.update(classification='SMOKE_PASS'))
fault('false pre-route PASS',lambda a,b,c:b.update(all_conditions_pass=True))
fault('unentered unrouted reported zero',lambda a,b,c:a['initial'].update(required_unrouted=0))
fault('unentered fresh DRC reported zero',lambda a,b,c:a['fresh'].update(project_required_material_drc=0))
fault('unentered wrong-net copper reported zero',lambda a,b,c:a['initial'].update(wrong_net_physical_copper=0))
fault('real ERC detection invented',lambda a,b,c:a.update(real_output_output_erc_detection=True))
fault('full geometry checker invented',lambda a,b,c:a.update(independent_full_physical_checker='PASS'))
fault('fresh qualification invented',lambda a,b,c:a.update(fresh_status='PASS'))
fault('route attempt erased',lambda a,b,c:c['attempts'].append({'kind':'initial'}))
fault('ERC warning waived',lambda a,b,c:b.update(erc_warnings=0))
try:run('experiment-forbidden-after-stop',['command-that-must-not-launch'],ROOT)
except RuntimeError as e:assert 'Terminal STOP' in str(e)
else:raise AssertionError('STOP guard allowed launch')
assert not (EVIDENCE/'processes/experiment-forbidden-after-stop').exists()
results.append({'name':'post-STOP experiment rejected before launch/registration','detected':True})
save(EVIDENCE/'reporting-fault-tests.json',{'status':'PASS','count':len(results),'tests':results,'scope':'Deliverable reporting and control guard only; not EDA qualification'})
print(f'{len(results)} reporting/control faults detected')
