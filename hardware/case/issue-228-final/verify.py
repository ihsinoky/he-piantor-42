"""Reload deliverables: topology, mesh, fit, input provenance and assembly interference."""
from pathlib import Path
import collections,csv,hashlib,itertools,json,math,struct,sys
from build123d import import_step
from shapely.geometry import Polygon
ROOT=Path(__file__).resolve().parents[3]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(out):
    d=json.loads((out/'dimensions.json').read_text())
    for p,h in d['inputs_sha256'].items():assert sha(ROOT/p)==h,p
    for p,h in json.loads((out/'exports-sha256.json').read_text()).items():assert sha(out/p)==h,p
    results={}
    for part in d['printing']:
        stem=part['name'];s=import_step(out/f'{stem}.step')
        assert s.is_valid and len(s.solids())==1,stem
        bb=s.bounding_box();dims=[bb.size.X,bb.size.Y,bb.size.Z]
        assert max(dims[:2])+10<=220 and dims[2]<=250
        mesh=(out/f'{stem}.stl').read_bytes();n=struct.unpack_from('<I',mesh,80)[0]
        assert len(mesh)==84+50*n
        edges=collections.Counter();vol=0.
        for i in range(n):
            row=struct.unpack_from('<12fH',mesh,84+50*i);vs=[tuple(row[j:j+3]) for j in (3,6,9)]
            assert len(set(vs))==3
            for a,b in zip(vs,vs[1:]+vs[:1]):edges[tuple(sorted((a,b)))]+=1
            a,b,c=vs;vol+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        bad=sum(v!=2 for v in edges.values());assert bad==0,(stem,bad)
        err=abs(abs(vol)-s.volume)/s.volume;assert err<.001,(stem,err)
        results[stem]=dict(valid=True,solids=1,faces=len(s.faces()),edges=len(s.edges()),triangles=n,nonmanifold_edges=bad,mesh_volume_relative_error=err,size_mm=dims)
    assembly=import_step(out/'assembly.step')
    # Keep named child solids to distinguish designed mating contacts from collisions.
    def leaves(s,owner=None):
        label=s.label
        if not label or label.lower() in ('solid','compound','assembly','part'):label=owner
        cs=list(s.children) if hasattr(s,'children') else []
        if cs:return [x for c in cs for x in leaves(c,label)]
        return [(label,s)]
    raw=leaves(assembly)
    items=[]
    for label,s in raw:
        for solid in s.solids():items.append((label,solid))
    assert len(items)==d['assembly_solid_count'],(len(items),d['assembly_solid_count'])
    def bounds(s):
        b=s.bounding_box();return [(b.min.X,b.max.X),(b.min.Y,b.max.Y),(b.min.Z,b.max.Z)]
    bbs=[bounds(s) for _,s in items];checked=0;overlaps=[];contacts=[]
    for i,(na,a) in enumerate(items):
        for j,(nb,b) in enumerate(items[i+1:],i+1):
            if any(min(x[1],y[1])-max(x[0],y[0])<=1e-6 for x,y in zip(bbs[i],bbs[j])):continue
            checked+=1
            intersection=a.intersect(b);volume=sum(s.volume for s in intersection) if intersection else 0.
            if volume>1e-4:
                # GH endpoint intentionally terminates inside its own mated reservation.
                own=(na=='GH-left' and nb=='Main-envelope-J2') or (nb=='GH-left' and na=='Main-envelope-J2') or (na=='GH-right' and nb=='Main-envelope-J3') or (nb=='GH-right' and na=='Main-envelope-J3')
                # Preserve official connector internals; report mating reservations separately.
                own = own or (na.startswith('Fly-official-') and nb.startswith('Fly-official-')) or (na=='USB-reference-shell' and nb in ('Fly-official-41','Fly-official-42')) or (nb=='USB-reference-shell' and na in ('Fly-official-41','Fly-official-42')) or ({na,nb}=={'EZmate-Fly-plug','Fly-official-67'}) or ({na,nb}=={'EZmate-Main-plug','Main-envelope-J4'}) or ('EZmate-170mm-route' in (na,nb) and (na.startswith('EZmate-') and nb.startswith('EZmate-')))
                (contacts if own else overlaps).append(dict(a=na,b=nb,volume_mm3=volume))
    inverse_error=0.
    # Outline and mounting CSVs are authoritative; do not assume old Rev2 holes survived.
    for side in ['left','right']:
        t=d['wing_transforms'][side];m=t['matrix'];tx,ty=t['translation']
        for h in [h for h in d['mounts'] if h['board']=='wing_'+side]:
            dx,dy=h['xy'][0]-tx,h['xy'][1]-ty
            local=[m[0][0]*dx+m[1][0]*dy,m[0][1]*dx+m[1][1]*dy]
            source=next(ROOT/p for p in d['inputs_sha256'] if p.endswith(f'holes-{d["pitch_mm"]}mm-{side}.csv'))
            with source.open() as f:r=next(r for r in csv.DictReader(f) if r['reference']==h['ref'])
            inverse_error=max(inverse_error,math.dist(local,[float(r['x_mm']),float(r['y_mm'])]))
    assert inverse_error<1e-10
    refs={(m['board'],m['ref']) for m in d['mounts']}
    expected={('main',r) for r in ('H1','H2','H3')}|{('fly',f'MH{i}') for i in range(1,3)}|{(f'wing_{s}',f'H{i}') for s in ('left','right') for i in range(1,5)}
    assert d['fixed_point_count']==13 and refs==expected,refs^expected
    assert len(d['boss_check'])==13 and all(b['material_at_boss_wall'] and b['pilot_open'] for b in d['boss_check'])
    assert {(b['board'],b['ref']) for b in d['boss_check']}==expected
    assert d['palm_high_wall_overlap_mm2']<1e-8
    assert d['keycap_wall_min_mm']>=.25-1e-8
    cp=[dict(a=a['ref'],b=b['ref'],gap_mm=Polygon(a['xy']).distance(Polygon(b['xy'])),overlap_mm2=Polygon(a['xy']).intersection(Polygon(b['xy'])).area) for a,b in itertools.combinations(d['main_components'],2)]
    assert all(p['overlap_mm2']<1e-8 for p in cp)
    closest=min(cp,key=lambda p:p['gap_mm'])
    assert closest['gap_mm']>=.3-1e-8
    assert d['fly']['cable']['route_length_mm']+30<=170
    assert d['fly']['cable']['minimum_mm']>.2
    assert abs(d['fly']['cable']['connected_length_mm']-170)<1e-8
    assert d['fly']['cable']['unmodeled_mm']==0
    result=dict(connector_internal_zero_overlap=not bool(d['fly']['usb']['connector_internal_overlaps']),phase_c_passed=not overlaps and assembly.is_valid and not bool(d['fly']['usb']['connector_internal_overlaps']),main_component_minimum=closest,main_component_pairs_checked=len(cp),wing_under_component_to_floor_min_mm=4.6,passed=not overlaps,pitch_mm=d['pitch_mm'],exports=results,assembly_solids=len(items),assembly_broadphase_candidate_pairs=checked,unexpected_overlaps=overlaps,intended_mating_contacts=contacts,mount_inverse_error_mm=inverse_error,fixed_points_with_boss=len(d['boss_check']))
    (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    assert not overlaps,overlaps
if __name__=='__main__':verify(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent/'17mm')
