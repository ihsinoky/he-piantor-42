"""Official qmake6 + make build, source tree unchanged; runtime relocated by qt.conf."""
import pathlib,subprocess,os,json,time,datetime,hashlib
E=pathlib.Path(__file__).resolve().parent; ROOT=E.parents[4]; R=ROOT/'.issue101-runtime'; src=R/'freeRouting'
env=os.environ.copy();env['LD_LIBRARY_PATH']=str(R/'qt/usr/lib/x86_64-linux-gnu')
steps=[]
for name,argv in [('qmake-version',[str(R/'qt/usr/bin/qmake6'),'-v']),('qmake',[str(R/'qt/usr/bin/qmake6')]),('make',['make','-j2'])]:
 t=time.monotonic(); rec=dict(argv=argv,cwd=str(src),start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 with (E/(name+'.log')).open('wb') as f: result=subprocess.run(argv,cwd=src,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=5400)
 rec.update(exit_code=result.returncode,elapsed_seconds=time.monotonic()-t,end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());steps.append(rec)
 (E/'build-record.json').write_text(json.dumps(steps,indent=2)+'\n')
 if result.returncode: raise SystemExit(result.returncode)
print('Build complete',flush=True)
