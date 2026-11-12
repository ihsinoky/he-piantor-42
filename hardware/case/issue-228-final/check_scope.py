"""Phase C scope gate against the committed Phase B STEP data; scratch stays local."""
from base import *
import os,re,subprocess
CHECKPOINT='84e2ec10'
BASE='e54f583c2fcb0cbdfde5363f3d43b281927fa2e3'
SCRATCH=ROOT/'.issue228-runtime/phase-c-baseline'

def baseline(pitch,name):
    SCRATCH.mkdir(parents=True,exist_ok=True)
    env={**os.environ,'GIT_DIR':os.environ.get('GIT_DIR',str(ROOT/'.issue228-runtime/git'))}
    raw=subprocess.check_output(['git','show',f'{BASE}:hardware/case/issue-228-final/{pitch}mm/{name}'],cwd=ROOT,env=env)
    path=SCRATCH/f'{pitch}-{name}';path.write_bytes(raw)
    return path

def payload(raw):
    # Occurrence serials depend on prior exports; every geometric DATA record stays exact.
    return re.sub(r"NEXT_ASSEMBLY_USAGE_OCCURRENCE\('[0-9]+'", "NEXT_ASSEMBLY_USAGE_OCCURRENCE('ID'",raw.decode().split('DATA;',1)[1])

def check(pitch):
    out=HERE/f'{pitch}mm';d=json.loads((out/'dimensions.json').read_text());cy=d['fly']['transform']['translation_mm'][1]
    local=prism(box(-12.301,d['fly']['wall_outer_y_at_x0_mm']-1.001,12.301,-17.999),1.999,22)
    mouth=prism(box(-8.001,cy-60,8.001,cy+3.001),d['fly']['board_bottom_z_mm']-.301,7.002)
    protected=prism(unary_union([Polygon(d['boards']['wing_'+side]).buffer(2.502,join_style=2) for side in ['left','right']]),2.00001,40)
    # Fix-round authorization: only the 16 mm PCB-height scalloped relief may
    # enter the old wall band. The actual Wing clearance pockets stay intact.
    relief_xy=Polygon(d['boards']['fly']).buffer(.5,resolution=48).simplify(.005,preserve_topology=True)
    wing_pockets=unary_union([Polygon(d['boards']['wing_'+side]).buffer(.502,join_style=2) for side in ['left','right']])
    assert relief_xy.disjoint(wing_pockets)
    relief=prism(relief_xy,9.8,6.2)
    allowed=local.fuse(mouth);result=dict(baseline_commit=BASE,pitch_mm=pitch)
    for side in ['left','right']:
        name=f'tray-{side}.step';old=import_step(baseline(pitch,name));new=import_step(out/name)
        outside=[]
        for shape in [new.cut(old),old.cut(new)]:outside.append(sum(q.volume for q in shape.cut(allowed).solids()))
        assert max(outside)<1e-5,(pitch,side,outside)
        wing_delta=old.cut(new).intersect(protected)
        wing_removed=sum(s.volume for s in wing_delta) if wing_delta else 0.
        wing_added_shape=new.cut(old).intersect(protected)
        wing_added=sum(s.volume for s in wing_added_shape) if wing_added_shape else 0.
        unapproved=Compound(children=list(wing_delta)).cut(relief) if pitch==16 and wing_delta else wing_delta
        unapproved_volume=sum(s.volume for s in unapproved.solids()) if unapproved else 0.
        assert max(unapproved_volume,wing_added)<1e-5,('Wing wall modified outside relief',pitch,side,wing_removed,wing_added)
        result[side]=dict(added_outside_mm3=outside[0],removed_outside_mm3=outside[1],removed_wing_wall_mm3=wing_removed,added_wing_wall_mm3=wing_added,removed_wing_wall_outside_fix_relief_mm3=unapproved_volume)
    result['continuation_case_checkpoint']=CHECKPOINT
    result['continuation_case_volume_change_mm3']={}
    for side in ['left','right']:
        name=f'tray-{side}.step'
        raw=subprocess.check_output(['git','show',f'{CHECKPOINT}:hardware/case/issue-228-final/{pitch}mm/{name}'],cwd=ROOT,env={**os.environ,'GIT_DIR':os.environ.get('GIT_DIR',str(ROOT/'.issue228-runtime/git'))})
        current=(out/name).read_bytes()
        if pitch==17:
            # Complete records, not just equal volumes: 17 mm stays frozen.
            assert payload(raw)==payload(current),('Fix round changed 17 mm case DATA',pitch,side)
            result['continuation_case_volume_change_mm3'][side]=dict(added=0.,removed=0.,proof='Identical complete normalized STEP DATA records')
        else:
            path=SCRATCH/f'checkpoint-{pitch}-{name}';path.write_bytes(raw)
            checkpoint=import_step(path);new=import_step(out/name)
            added=new.cut(checkpoint);removed=checkpoint.cut(new)
            added_volume=sum(s.volume for s in added.solids())
            outside_relief=sum(s.volume for s in removed.cut(relief).solids())
            assert max(added_volume,outside_relief)<1e-5,(side,added_volume,outside_relief)
            result['continuation_case_volume_change_mm3'][side]=dict(added=added_volume,removed=sum(s.volume for s in removed.solids()),removed_outside_fix_relief_mm3=outside_relief)
    result['wing_pocket_to_fix_relief_mm']=relief_xy.distance(wing_pockets)
    trays=Compound(children=[import_step(out/f'tray-{side}.step') for side in ['left','right']])
    result['fly_boss_geometry']=[]
    for h in [h for h in d['mounts'] if h['board']=='fly']:
        x,y=h['xy'];pilot=cylinder(x,y,.85,2,8)
        boss=cylinder(x,y,2.25,2,8).cut(pilot)
        missing=sum(s.volume for s in boss.cut(trays).solids())
        obstruction=pilot.intersect(trays)
        obstruction_volume=sum(s.volume for s in obstruction) if obstruction else 0.
        assert max(missing,obstruction_volume)<1e-5,(pitch,h['ref'],missing,obstruction_volume)
        result['fly_boss_geometry'].append(dict(ref=h['ref'],missing_boss_mm3=missing,pilot_obstruction_mm3=obstruction_volume))
    result['unchanged_data_sha256']={}
    for name in ['splice-1.step','splice-2.step','cable-rack.step','harness.step','storage-200mm.step']:
        old=baseline(pitch,name).read_bytes();new=(out/name).read_bytes()
        assert payload(old)==payload(new),(pitch,name)
        result['unchanged_data_sha256'][name]=hashlib.sha256(payload(new).encode()).hexdigest()
    # Retain the original Wing/Main XY pockets as an additional independent input check.
    original=json.loads(subprocess.check_output(['git','show',f'{BASE}:hardware/case/issue-228-final/{pitch}mm/dimensions.json'],cwd=ROOT,env={**os.environ,'GIT_DIR':os.environ.get('GIT_DIR',str(ROOT/'.issue228-runtime/git'))}))
    for name in ['main','wing_left','wing_right']:assert d['boards'][name]==original['boards'][name]
    assert d['wing_transforms']==original['wing_transforms']
    for a,b in zip(d['routes'],original['routes']):
        for k in ['side','source_planar_mm','source_required_mm','actual_3d_mm','with_30mm_allowance_mm','nominal_200_slack_mm','endpoint_z_mm','cruise_z_mm','radius_mm']:assert a[k]==b[k],k
        assert abs(a['case_min_mm']-b['case_min_mm'])<1e-8
    old_components={c['ref']:c for c in original['main_components']}
    assert all(c==old_components[c['ref']] for c in d['main_components'] if c['ref']!='J4')
    result['passed']=True
    save(out/'scope-check.json',result);print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':
    for pitch in [17,16]:check(pitch)
