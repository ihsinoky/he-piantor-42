from common import *
import shutil
pre=json.loads((E/'preflight-design-preflight4.json').read_text())
violations=[x for x in pre['violations'] if x['type'] not in {'text_height','silk_overlap','silk_over_copper','via_dangling'}]
# The three bounded manual layout revisions are exhausted. Do not hand-edit
# a fourth path. Let the ONE permitted global routing attempt replace the
# exact two still-conflicting seed segments, under unchanged clearance.
assert len(violations)==2 and all(x['type']=='clearance' for x in violations)
import sexpdata as sx
remove={i['uuid'] for x in violations for i in x['items'] if i['description'].startswith('Track [V5V2]')}
assert len(remove)==2
pcb=E/'inputs/global/main.kicad_pcb';original=pcb.read_bytes()
(E/'preflight-final-authoring.kicad_pcb').write_bytes(original)
a=sx.loads(original.decode());removed=[];out=[a[0]]
for x in a[1:]:
 uid=next((str(v[1]) for v in x if isinstance(v,list) and v and str(v[0])=='uuid'),None) if isinstance(x,list) else None
 if uid in remove:
  assert str(x[0])=='segment';removed.append(sx.dumps(x))
 else:out.append(x)
assert len(removed)==2
pcb.write_text(sx.dumps(out)+'\n')
save(E/'global-seed-ripup.json',dict(utc=now(),reason='Remaining 0.086mm V5V2-to-J1 clearance; bounded manual preparation ended. Exact two segments handed to the single global router attempt.',removed_segments=removed,no_manual_replacement=True,preparation_sha256=hashlib.sha256(original).hexdigest(),routing_input_sha256=digest(pcb)))
source=E/'inputs/global';w=E/'runs/global';w.mkdir(parents=True,exist_ok=False)
for ext in ['kicad_pcb','kicad_pro']:shutil.copyfile(source/('main.'+ext),w/('in.'+ext))
args=ARGS+['--keep-input-copper']
assert run('global-effective',[B/'venv/bin/python3',E/'read-effective.py',w/'effective.json',source/'main.kicad_pcb']+args)==0
read=json.loads((w/'effective.json').read_text());c=read['grid_route_config']
assert c['track_width']==.1 and c['clearance']==.1 and c['via_size']==.6 and c['via_drill']==.3 and c['layer_costs']==[1.,-1.,1.,1.]
assert read['escalation_policy'][0]=='off' and len(read['native_keepouts'])==4
save(E/'frozen-inputs.json',{str(x.relative_to(E)):digest(x) for x in source.iterdir() if x.is_file()})
rc=run('global-krt-route',[B/'venv/bin/python3','py_router/route.py',w/'in.kicad_pcb',w/'out.kicad_pcb']+args,cwd=K,timeout=1800)
save(w/'execution.json',dict(utc=now(),attempt=1,exit_code=rc,condition_args=args,input_unchanged=digest(w/'in.kicad_pcb')==digest(source/'main.kicad_pcb')))
raise SystemExit(rc)
