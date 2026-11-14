"""All unordered physical constituent pairs; explicit own-mate classifications only."""
from common import *
import importlib.util
spec=importlib.util.spec_from_file_location('prior_verify',HERE.parent/'issue-232-final/verify.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
def common_record(a,b):
 from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
 from OCP.BRepGProp import BRepGProp
 from OCP.GProp import GProp_GProps
 op=BRepAlgoAPI_Common(a.wrapped,b.wrapped);op.SetRunParallel(True);op.SetUseOBB(True);op.Build()
 if not op.IsDone():raise RuntimeError('OCCT Common failed')
 if op.Shape().IsNull():return dict(volume_mm3=0.)
 props=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),props,True,False,False);v=abs(props.Mass())
 return dict(volume_mm3=v,common_bounds_mm=bounds(Shape.cast(op.Shape()))) if v>1e-6 else dict(volume_mm3=v)
def intended(a,b):
 for i,side in [(0,'left'),(1,'right')]:
  if {a,b}=={f'shell-insert-{i}','tray-'+side}:return 'own specified heat-insert press fit: OD3.2 in OD2.8 pilot'
  if {a,b}=={f'shell-insert-{i}',f'shell-screw-{i}'}:return 'own nominal M2 insert/thread mating'
 why=prior.intended(a,b)
 if why:return why
 if a==b and a.startswith(('shell-','strip-')):return 'same manufactured part constituent'
 for side in ('left','right'):
  w=lambda n:n.startswith('Wire-'+side+'-')
  if (w(a) and b in ('Main-GH-'+side+'-DRAWING-BOUND','underside-'+side+'-J_WING')) or (w(b) and a in ('Main-GH-'+side+'-DRAWING-BOUND','underside-'+side+'-J_WING')):return 'own GH termination, nominal bounded outlet'
 if 'Fly-170mm' in (a,b) and any(n.startswith(('EZmate-','Fly-official-67')) or n=='Main-study-J4' for n in (a,b)):return 'own EZmate termination'
 if {a,b}=={'EZmate-Main-plug','Main-study-J4'}:return 'own Main EZmate mate'
 return None
def audit(pitch):
 out=HERE/f'{pitch}mm';idx,allraw=cached(pitch)
 pairs=[(r,q) for r,q in zip(idx,allraw) if not r['name'].startswith('USB-reference-')]
 idx=[r for r,q in pairs];raw=[q for r,q in pairs]
 progress=RUN/f'audit{pitch}-progress.json';geometry_hash=sha(out/'assembly-index.json')
 done={}
 if progress.exists():
  p=read(progress)
  if p['geometry_hash']==geometry_hash:done=p['results']
 rejects=0;mates=[];candidates=[];hits=[];errors=[];references=[]
 for i,(a,k,s) in enumerate(raw):
  for j in range(i+1,len(raw)):
   b,l,t=raw[j];ab=idx[i]['bounds'];bb=idx[j]['bounds']
   if any(min(ab[1][d],bb[1][d])-max(ab[0][d],bb[0][d])<=1e-7 for d in range(3)):rejects+=1;continue
   why=intended(a,b)
   if why:mates.append(dict(i=i,j=j,a=a,b=b,reason=why));continue
   candidates.append((i,j))
 print(pitch,len(raw),'solids',len(candidates),'exact pairs',flush=True)
 for count,(i,j) in enumerate(candidates):
  key=f'{i}:{j}';a,k,s=raw[i];b,l,t=raw[j]
  needs_witness=key in done and done[key].get('volume_mm3',0)>1e-6 and 'common_bounds_mm' not in done[key]
  if key not in done or needs_witness:
   try:
    replay=common_record(s,t)
    if needs_witness:assert abs(replay['volume_mm3']-done[key]['volume_mm3'])<1e-6
    done[key]=replay
   except Exception as e:done[key]=dict(error=repr(e))
  r=dict(i=i,j=j,a=a,b=b,**done[key])
  if 'error' in r:errors.append(r)
  elif r['volume_mm3']>1e-6:
   if a.startswith('Main-study-') and b.startswith('Main-study-'):references.append(r)
   else:hits.append(r);print('HIT',a,b,r['volume_mm3'],flush=True)
  if count%20==0:
   save(progress,dict(geometry_hash=geometry_hash,results=done));print(pitch,count+1,'/',len(candidates),flush=True)
 save(progress,dict(geometry_hash=geometry_hash,results=done))
 total=len(raw)*(len(raw)-1)//2
 assert total==rejects+len(mates)+len(candidates)
 result=dict(status=P['status'],all_pairs_enumerated=True,all_exact_candidates_completed=True,assembly_solids=len(raw),total_pairs=total,aabb_rejected_pairs=rejects,intended_pairs=mates,exact_candidates=len(candidates),exact_results=[dict(i=i,j=j,**done[f'{i}:{j}']) for i,j in candidates],unexpected_interferences=hits,clearance_reservation_overlaps=references,boolean_errors=errors,invalid_solids=[r for r in idx if not r['valid']],passed=not hits and not errors and all(r['valid'] for r in idx),geometry_sha256=geometry_hash,threshold_mm3=1e-6)
 save(out/'audit.json',result)
 print('COMPLETE',pitch,'hits',len(hits),'errors',len(errors),flush=True)
if __name__=='__main__':audit(int(sys.argv[1]))
