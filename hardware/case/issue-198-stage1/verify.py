"""Read exported STEP/STL independently, check watertightness and CSV hole transforms."""
from pathlib import Path
import collections, csv, hashlib, json, math, struct, sys
from build123d import import_step
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(out):
    d=json.loads((out/'dimensions.json').read_text())
    for p,h in d['inputs_sha256'].items():assert sha(ROOT/p)==h,p
    for p,h in json.loads((out/'exports-sha256.json').read_text()).items():assert sha(out/p)==h,p
    results={}
    for stem in ['tray','tray-left','tray-right']:
        shape=import_step(out/(stem+'.step'))
        assert shape.is_valid and len(shape.solids())==1,stem
        data=(out/(stem+'.stl')).read_bytes();n=struct.unpack_from('<I',data,80)[0]
        assert len(data)==84+50*n
        edges=collections.Counter();volume=0.
        for i in range(n):
            row=struct.unpack_from('<12fH',data,84+i*50)
            vs=[tuple(row[j:j+3]) for j in (3,6,9)]
            assert len(set(vs))==3
            for a,b in zip(vs,vs[1:]+vs[:1]):edges[tuple(sorted((a,b)))]+=1
            a,b,c=vs
            volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        bad=sum(v!=2 for v in edges.values());assert bad==0,(stem,bad)
        rel=abs(abs(volume)-shape.volume)/shape.volume
        assert rel<.001,(stem,rel)
        results[stem]=dict(valid=True,solids=1,triangles=n,nonmanifold_edges=bad,mesh_step_relative_volume_error=rel,volume_mm3=shape.volume)
    assert abs(results['tray-left']['volume_mm3']+results['tray-right']['volume_mm3']-results['tray']['volume_mm3'])<1e-3
    maxerror=0.
    for side in ('left','right'):
        t=d['wing_transforms'][side];m=t['matrix'];tx,ty=t['translation']
        # determinant -1: Y-up local converted to Y-south assembly.
        assert abs(m[0][0]*m[1][1]-m[0][1]*m[1][0]+1)<1e-12
        source=ROOT/f'hardware/case/issue-194-rev2/holes-{d["pitch_mm"]}mm-{side}.csv'
        with source.open() as f:
            for row in csv.DictReader(f):
                if row['kind']!='mounting':continue
                h=next(v for v in d['mounts'] if v['board']=='wing_'+side and v['ref']==row['reference'])
                dx,dy=h['xy'][0]-tx,h['xy'][1]-ty
                inverse=[m[0][0]*dx+m[1][0]*dy,m[0][1]*dx+m[1][1]*dy]
                err=math.dist(inverse,[float(row['x_mm']),float(row['y_mm'])]);maxerror=max(maxerror,err)
        assert maxerror<1e-10
    assembly=import_step(out/'assembly.step')
    solids=list(assembly.solids());assert len(solids)==5,len(solids)
    # Solid intersections catch Z stack mistakes invisible in plan view.
    overlaps=[]
    for i,a in enumerate(solids):
        for j,b in enumerate(solids[i+1:],i+1):
            intersection=a.intersect(b)
            volume=sum(s.volume for s in intersection) if intersection else 0.
            assert volume<1e-4,(i,j,volume)
            overlaps.append(dict(a=i,b=j,intersection_mm3=volume))
    result=dict(pass_check=True,pitch_mm=d['pitch_mm'],exports=results,mount_inverse_error_mm=maxerror,assembly_solid_count=len(solids),assembly_pairwise=overlaps)
    (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':verify(Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'17mm')
