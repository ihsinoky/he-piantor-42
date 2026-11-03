"""Resume official make after completing relocated GL dependencies; no source changes."""
import pathlib,subprocess,os,json,time,datetime
E=pathlib.Path(__file__).resolve().parent;ROOT=E.parents[4];R=ROOT/'.issue101-runtime'
env=os.environ.copy();env['LD_LIBRARY_PATH']=str(R/'qt/usr/lib/x86_64-linux-gnu');env['LIBRARY_PATH']=env['LD_LIBRARY_PATH']
steps=json.loads((E/'build-record.json').read_text());t=time.monotonic()
rec=dict(argv=['make','-j2'],cwd=str(R/'freeRouting'),environment={k:env[k] for k in ['LD_LIBRARY_PATH','LIBRARY_PATH']},start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reason='Complete missing relocated GL runtime dependency and linker search path; source unchanged')
with (E/'make-resume.log').open('wb') as out:r=subprocess.run(rec['argv'],cwd=R/'freeRouting',env=env,stdout=out,stderr=subprocess.STDOUT,timeout=600)
rec.update(exit_code=r.returncode,elapsed_seconds=time.monotonic()-t,end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());steps.append(rec)
(E/'build-record.json').write_text(json.dumps(steps,indent=2)+'\n');print(rec);raise SystemExit(r.returncode)
