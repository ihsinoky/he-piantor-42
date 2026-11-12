"""Per-pitch Phase A gates, using independently reconstructed authoritative CSVs."""
import csv,json,math,re
from pathlib import Path
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union,nearest_points
from outline import proposed_outline,curve_design,usb_access
HERE=Path(__file__).resolve().parent

def check(pitch):
    source=HERE.parent/'issue-198-final'/f'{pitch}mm/dimensions.json'
    data=json.loads(source.read_text())
    boards={k:Polygon(v) for k,v in data['boards'].items()}
    for side in ('left','right'):
        t=data['wing_transforms'][side]
        with (HERE/f'inputs/rev3-final/outline-{pitch}mm-{side}.csv').open() as f:
            xy=[[float(r['x_mm']),float(r['y_mm'])] for r in csv.DictReader(f)]
        rebuilt=Polygon([[sum(t['matrix'][i][j]*p[j] for j in (0,1))+t['translation'][i] for i in (0,1)] for p in xy])
        assert rebuilt.equals_exact(boards['wing_'+side],1e-9)
    cavity=unary_union([g.buffer(.502,join_style=2) for g in boards.values()]+[box(-11,-24,11,12)]).simplify(.002,preserve_topology=True)
    outer=proposed_outline(cavity,boards)
    design=curve_design(boards)
    south=design['south_left'];path=LineString(south['path_xy_mm'])
    pcb=LineString(list(boards['wing_left'].exterior.coords)[:14])
    out=HERE/f'{pitch}mm';out.mkdir(exist_ok=True)
    profile=[]
    with (out/'shelf-profile.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['arclength_mm','shelf_mm','x_mm','y_mm','pcb_x_mm','pcb_y_mm'])
        for i in range(20001):
            s=path.length*i/20000;q=path.interpolate(s);a,b=nearest_points(q,pcb)
            row=[s,q.distance(pcb),q.x,q.y,b.x,b.y];profile.append(row);writer.writerow(row)
    turns=[]
    for a,b,c in zip(south['path_xy_mm'],south['path_xy_mm'][1:],south['path_xy_mm'][2:]):
        cross=(b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0])
        turns.append(1 if cross>0 else -1 if cross<0 else 0)
    pcb_source=HERE.parents[2]/'hardware/kicad/qualification/issue-196-main-rev4-phasea2/inputs/udb/c3.kicad_pcb'
    text=pcb_source.read_text()
    def position(ref):
        for block in text.split('(module ')[1:]:
            if re.search(r'\(fp_text reference '+ref+r'\s',block):
                m=re.search(r'\(at ([0-9.-]+) ([0-9.-]+)',block)
                return tuple(map(float,m.groups()))
        raise ValueError(ref)
    j1,j2=position('J1'),position('J2');usb_center=j1[0]-j2[0]
    result=dict(pitch_mm=pitch,pocket_outside_mm2=cavity.difference(outer).area,
                minimum_wall_mm=cavity.boundary.distance(outer.boundary),
                board_clearance_outside_mm2={k:g.buffer(.502,join_style=2).difference(outer).area for k,g in boards.items()},
                curvature_sign_changes=sum(a!=b for a,b in zip(turns,turns[1:])),
                turn_signs=sorted(set(turns)),shelf_max_mm=max(r[1] for r in profile),
                shelf_upper_bound_mm=max(r[1] for r in profile)+path.length/40000,
                shelf_max_witness=max(profile,key=lambda r:r[1]),
                design=design,outer_xy_mm=list(outer.exterior.coords),cavity_xy_mm=list(cavity.exterior.coords),
                usb_center_x_mm=usb_center,usb_slot_xy_mm=list(usb_access(outer,usb_center).exterior.coords),
                added_area_mm2=outer.difference(cavity.buffer(2,join_style=2)).area)
    if pitch==17:
        approved=json.loads((HERE.parent/'issue-228-outline/17mm-outline.json').read_text())
        # The active 17 mm construction is byte-identical in its fitting constants.
        import sys,importlib.util
        spec=importlib.util.spec_from_file_location('approved_outline',HERE.parent/'issue-228-outline/outline.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        result['approved_outline_deviation_mm']=outer.boundary.hausdorff_distance(module.proposed_outline(cavity,boards).boundary)
    assert result['pocket_outside_mm2']==0
    assert result['minimum_wall_mm']>=2-1e-8
    assert result['curvature_sign_changes']==0 and result['turn_signs']==[-1]
    assert max(result['board_clearance_outside_mm2'].values())==0
    (out/'outline-check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('design','outer_xy_mm','cavity_xy_mm','usb_slot_xy_mm')},indent=2),flush=True)

if __name__=='__main__':
    for pitch in (17,16):check(pitch)
