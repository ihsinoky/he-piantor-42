"""Read-only inspection of saved routing results using existing project oracles."""
import datetime,hashlib,json,os,pathlib,subprocess,sys,time
E=pathlib.Path(__file__).resolve().parent; ROOT=E.parents[4]; TMP=ROOT/'.issue107-runtime'; K=ROOT/'.issue105-runtime/kicad'
env=os.environ.copy(); env.pop('DISPLAY',None); env.pop('WAYLAND_DISPLAY',None)
env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(K/'usr/lib/python3/dist-packages'),LD_LIBRARY_PATH=str(K/'usr/lib/x86_64-linux-gnu')+':'+str(K/'usr/lib/kicad'),KICAD_STOCK_DATA_HOME=str(K/'usr/share/kicad'))
for k in ['CONFIG','CACHE','DATA','STATE']:
    path=TMP/k.lower(); path.mkdir(exist_ok=True); env['XDG_'+k+'_HOME']=str(path)
(E/'kicad-env.json').write_text(json.dumps({k:v for k,v in env.items() if k.startswith(('XDG_','KICAD','PYTHON','LD_LIBRARY'))},indent=2)+'\n')
def run(name,argv):
    work=E/'processes'/name; work.mkdir(exist_ok=False); t=time.monotonic()
    rec=dict(argv=list(map(str,argv)),cwd=str(ROOT),start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    with (work/'stdout').open('wb') as out,(work/'stderr').open('wb') as err:
        r=subprocess.run(rec['argv'],cwd=ROOT,env=env,stdout=out,stderr=err,timeout=180)
    rec.update(exit_code=r.returncode,elapsed_seconds=time.monotonic()-t,end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    (work/'record.json').write_text(json.dumps(rec,indent=2)+'\n'); print(name,r.returncode,flush=True)
    assert r.returncode==0,(name,(work/'stderr').read_text())
stage=sys.argv[1]
run(stage+'-ses-import',['/usr/bin/python3','-B',E/'import-session.py',stage])
work=E/'processes'/(stage+'-import'); old=ROOT/'hardware/kicad/qualification/issue-87-native-main-routing/evidence/processes'/('smoke-read-before' if stage=='smoke' else 'baseline-read')
run(stage+'-read-return',['/usr/bin/python3','-B',ROOT/'hardware/kicad/qualification/eda-004g/resume-02/read-pcb.py',work/'main.kicad_pcb',work/'snapshot.json'])
if stage=='smoke': run('smoke-prepare-library',['/usr/bin/python3','-B',E/'prepare-smoke-library.py'])
run(stage+'-drc',[K/'usr/bin/kicad-cli','pcb','drc','--format','json','--severity-all','-o',work/'drc.json',work/'main.kicad_pcb'])
check=ROOT/'hardware/kicad/qualification/issue-87-native-main-routing/resume-01'/('check-import.py' if stage=='smoke' else 'assess-main.py')
args=([stage] if stage=='smoke' else [])+[old/'main.kicad_pcb',work/'main.kicad_pcb',old/'snapshot.json',work/'snapshot.json',work/'drc.json',E/(stage+'-independent.json')]
run(stage+'-independent',[ROOT/'.issue105-runtime/geometry/bin/python','-B',check,*args])
if stage=='smoke':
    independent=json.loads((E/'smoke-independent.json').read_text())
    for key in ['required_unconnected','wrong_net_actual_copper_contacts','targeted_material_violations','unexplained_transfer_changes']: assert independent[key]==0
    width=json.loads((E/'smoke-ses-inspection.json').read_text()); assert width['paths_below_020mm']==0
    (E/'smoke-gate.json').write_text(json.dumps(dict(main_allowed=True,headless_exit_zero=True,ses_generated=True,kicad_import_success=True,independent_checks_passed=True,validated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
