from session import *
import shutil
assert json.loads((ROOT/'evidence/effective-rule-acceptance.json').read_text())['status']=='PASS_WITH_SCOPE'
for name in ['smoke','main']:assert json.loads((ROOT/'evidence'/(name+'-dsn-parity.json')).read_text())['status']=='PASS_WITH_SCOPE'
fixed=json.loads((ROOT/'evidence/fixed-settings.json').read_text());work=BASE/'smoke-route';work.mkdir(exist_ok=False)
user=work/'user-data';user.mkdir();temp=work/'temp';temp.mkdir()
shutil.copyfile(ROOT/'evidence/settings-parsed.json',user/'freerouting.json')
shutil.copyfile(BASE/'smoke/corrected.dsn',work/'input.dsn')
ses=work/'output.ses'
command=[str(JAVA)]+fixed['java_flags']+['-Djava.io.tmpdir='+str(temp),'-jar',str(JAR),'--user_data_path='+str(user)]+fixed['cli_arguments']+['-de',str(work/'input.dsn'),'-do',str(ses)]
save(ROOT/'evidence/small-run-contract.json',dict(status='FROZEN',utc=utc(),command=command,input_sha256=digest(work/'input.dsn'),jar_sha256=digest(JAR),settings_sha256=digest(user/'freerouting.json'),fixed_settings_sha256=digest(ROOT/'evidence/fixed-settings.json'),timeout_seconds=180,passes=100,routing_threads=1,optimizer_threads=0,seed=None,reproduction=fixed['reproduction'],small_trial_before=0,main_initial_before=0,confirmation_before=0))
ledger=ROOT/'evidence/attempt-ledger.json';assert not ledger.exists()
save(ledger,dict(small=[dict(registered_utc=utc(),process='small-route',input_sha256=digest(work/'input.dsn'))],attempts=[],initial_all_conditions_pass=False))
run('small-route',command,work,180,env={'LANG':'C.UTF-8','LC_ALL':'C.UTF-8'},artifacts=[('output.ses',ses),('effective-start-settings.json',user/'freerouting.json')])
assert ses.is_file() and ses.stat().st_size>0
print('one small routing process complete; acceptance still pending SES import and checks')
