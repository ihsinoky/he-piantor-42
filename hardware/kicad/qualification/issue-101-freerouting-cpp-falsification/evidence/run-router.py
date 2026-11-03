"""One smoke and at most one Main; exclusive directories prohibit repeats."""
import datetime, hashlib, json, os, pathlib, shutil, subprocess, sys, time
E=pathlib.Path(__file__).resolve().parent
ROOT=E.parents[4]
BIN=ROOT/'.issue101-runtime/freeRouting/bin/freeRouting'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
stage=sys.argv[1]; assert stage in ('smoke','main')
if stage=='main':
    smoke=json.loads((E/'processes/smoke/record.json').read_text())
    assert smoke['exit_code']==0 and (E/'processes/smoke/corrected.ses').is_file()
    assert json.loads((E/'smoke-gate.json').read_text())['main_allowed']
    independent=json.loads((E/'smoke-independent.json').read_text())
    assert all(independent[k]==0 for k in ['required_unconnected','wrong_net_actual_copper_contacts','targeted_material_violations','unexplained_transfer_changes'])
    assert json.loads((E/'smoke-ses-inspection.json').read_text())['paths_below_020mm']==0
source=ROOT/'hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes'/('smoke-restore' if stage=='smoke' else 'main-restore')/'corrected.dsn'
expected={'smoke':'7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9','main':'75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2'}[stage]
assert sha(source)==expected
work=E/'processes'/stage; work.mkdir(parents=True,exist_ok=False)
shutil.copyfile(source,work/'corrected.dsn')
argv=[str(BIN),'--autoroute','corrected.dsn']
env=os.environ.copy(); env.pop('DISPLAY',None); env.pop('WAYLAND_DISPLAY',None)
env.update(LANG='C.UTF-8',LC_ALL='C.UTF-8',TZ='UTC',QT_QPA_PLATFORM='offscreen',LD_LIBRARY_PATH=str(ROOT/'.issue101-runtime/qt/usr/lib/x86_64-linux-gnu'),QT_QPA_PLATFORM_PLUGIN_PATH=str(ROOT/'.issue101-runtime/qt/usr/lib/x86_64-linux-gnu/qt6/plugins/platforms'))
for key in ['CONFIG','CACHE','DATA','STATE','RUNTIME']:
    folder=ROOT/'.issue101-runtime'/('router-'+key.lower()); folder.mkdir(mode=0o700,exist_ok=True); env['XDG_'+key+'_HOME' if key!='RUNTIME' else 'XDG_RUNTIME_DIR']=str(folder)
record=dict(stage=stage,argv=argv,cwd=str(work),start_utc=utc(),input_sha256=expected,binary_sha256=sha(BIN),environment={k:env.get(k) for k in ['DISPLAY','WAYLAND_DISPLAY','LANG','LC_ALL','TZ','QT_QPA_PLATFORM','LD_LIBRARY_PATH','QT_QPA_PLATFORM_PLUGIN_PATH','XDG_CONFIG_HOME','XDG_CACHE_HOME','XDG_DATA_HOME','XDG_STATE_HOME','XDG_RUNTIME_DIR']},outer_timeout_seconds=max(1,int(datetime.datetime(2026,11,4,0,10,tzinfo=datetime.timezone.utc).timestamp()-time.time())))
(work/'record.json').write_text(json.dumps(record,indent=2)+'\n')
t=time.monotonic()
with (work/'stdout').open('wb') as out,(work/'stderr').open('wb') as err:
    try: record['exit_code']=subprocess.run(argv,cwd=work,env=env,stdout=out,stderr=err,timeout=record['outer_timeout_seconds']).returncode
    except subprocess.TimeoutExpired: record.update(exit_code=None,outer_timeout=True)
record.update(end_utc=utc(),elapsed_seconds=time.monotonic()-t,input_unchanged=sha(source)==expected and sha(work/'corrected.dsn')==expected)
record['artifacts']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in work.iterdir() if p.is_file() and p.name!='record.json'}
(work/'record.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
