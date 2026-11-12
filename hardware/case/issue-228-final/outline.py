"""Issue 228 Phase A: round 4 convex south sweep silhouette; unchanged pocket.

Pure 2D Shapely construction shared by the generator and approval drawing.
Coordinates are assembly XY in mm (positive Y south). Quadratic spans use 512 chords; R5 endpoint arcs use 128 chords.
"""
import math
from functools import lru_cache
from shapely.geometry import Polygon
from shapely.ops import unary_union


def _intersection(a, direction, normal, support):
    scale = (support - sum(normal[i] * a[i] for i in range(2))) / sum(
        normal[i] * direction[i] for i in range(2))
    return tuple(a[i] + scale * direction[i] for i in range(2))


def wing_envelope(board, clearance=.502, wall=2.):
    """Replace the complete thumb/pinky hull chain with one supporting line.

    Its direction joins the outermost pinky PCB point to the southernmost
    thumb PCB point. Translate it south until it supports ALL PCB vertices,
    then intersect the existing pinky and inner-thumb side lines. A miter
    offset supplies the unchanged clearance plus wall; no PCB is trimmed.
    """
    points = list(board.exterior.coords)[:-1]
    pinky = max(points, key=lambda p: abs(p[0]))
    thumb = max(points, key=lambda p: p[1])
    north = min(points, key=lambda p: p[1])
    inner = min(points, key=lambda p: abs(p[0]))
    # The Wing north/central boundary has an existing corner at local datum
    # transition (assembly y=-45); retain it rather than fill the central bay.
    neck = min((p for p in points if abs(p[1] + 45.) < 1e-7),
               key=lambda p: abs(p[0]))
    direction = (thumb[0] - pinky[0], thumb[1] - pinky[1])
    length = math.hypot(*direction)
    normal = (-direction[1] / length, direction[0] / length)
    if normal[1] < 0:
        normal = tuple(-v for v in normal)
    # Include the old miter tips, which can project beyond a simple PCB hull
    # offset at the thumb staircase. 0.002 mm covers pocket simplification.
    existing = board.buffer(clearance, join_style=2).buffer(wall, join_style=2)
    support = max(sum(normal[i] * p[i] for i in range(2))
                  for p in existing.exterior.coords) - clearance - wall + .002
    end_pinky = _intersection(pinky, tuple(pinky[i]-north[i] for i in range(2)), normal, support)
    end_thumb = _intersection(thumb, tuple(thumb[i]-inner[i] for i in range(2)), normal, support)
    envelope = Polygon([north, end_pinky, end_thumb, inner, neck])
    assert envelope.buffer(1e-8).covers(board)
    result = envelope.buffer(clearance + wall, join_style=2)
    # Recover the offset south segment for the gate's exact dimensions.
    south_support = support + clearance + wall
    vertices = list(result.exterior.coords)[:-1]
    south = [p for p in vertices if abs(sum(normal[i]*p[i] for i in range(2))-south_support) < 1e-7]
    assert len(south) == 2
    return result, dict(endpoints=south, length_mm=math.dist(*south),
                        normal=list(normal), support_mm=south_support,
                        pcb_chord_shift_mm=support-sum(normal[i]*pinky[i] for i in range(2)))


def round1_outline(cavity, boards, wall=2., clearance=.502):
    legacy = cavity.buffer(wall, join_style=2)
    wings = [wing_envelope(boards['wing_'+side], clearance, wall)[0]
             for side in ('left', 'right')]
    result = unary_union([legacy, *wings])
    assert result.geom_type == 'Polygon' and result.is_valid
    assert result.buffer(1e-8).covers(legacy)
    return result

CURVE_STEPS = 512


def bezier(controls, steps=CURVE_STEPS):
    """Polynomial Bezier including both ends; shared with Phase B."""
    degree = len(controls)-1
    return [tuple(sum(math.comb(degree,j)*(1-i/steps)**(degree-j)
                      *(i/steps)**j*p[k] for j,p in enumerate(controls))
                  for k in (0,1)) for i in range(steps+1)]


def _datums(boards, wall=2., clearance=.502):
    envelope, line = wing_envelope(boards['wing_left'], clearance, wall)
    n = min(envelope.exterior.coords, key=lambda p:p[1])
    _, thumb = sorted(line['endpoints'])
    pts = list(boards['wing_left'].exterior.coords)[:-1]
    sn = min(pts,key=lambda p:p[1])
    st = max(pts,key=lambda p:p[1])
    si = min(pts,key=lambda p:abs(p[0]))
    # Preserve the round-2 center-south bridge and north-side datums.
    dt=_unit(tuple(si[i]-st[i] for i in (0,1)))
    bridge_y = boards['main'].bounds[3]+clearance+wall
    bridge = (thumb[0]+(bridge_y-thumb[1])*dt[0]/dt[1],bridge_y)
    neck=min((p for p in pts if abs(p[1]+45.)<1e-7),key=lambda p:abs(p[0]))
    slope=(neck[1]-sn[1])/(neck[0]-sn[0])
    north=[(-n[0],n[1]),(0.,n[1]-n[0]*slope),n]
    return dict(north_controls_xy_mm=north,left_north_xy_mm=n,
                left_bridge_xy_mm=bridge,
                steps_per_span=CURVE_STEPS)


def usb_access(outer, center_x=0.):
    """12mm open-top slot, extended through the new north wall.

    Default Z=11.2..15.2mm (4mm high, open above). Final alignment belongs
    to the pending Fly seat rework; daughterboard seat is unchanged.
    """
    from shapely.geometry import box
    return box(center_x-6.,outer.bounds[1]-1.,center_x+6.,-34.)


def _unit(v):
    length=math.hypot(*v)
    return tuple(x/length for x in v)


def _fillet(a, corner, b, radius=5.):
    """Exact circular fillet of incoming/outgoing support lines."""
    u=_unit(tuple(a[k]-corner[k] for k in (0,1)))
    v=_unit(tuple(b[k]-corner[k] for k in (0,1)))
    angle=math.acos(sum(u[k]*v[k] for k in (0,1)))
    trim=radius/math.tan(angle/2)
    start=tuple(corner[k]+trim*u[k] for k in (0,1))
    end=tuple(corner[k]+trim*v[k] for k in (0,1))
    bisector=_unit(tuple(u[k]+v[k] for k in (0,1)))
    center=tuple(corner[k]+radius/math.sin(angle/2)*bisector[k] for k in (0,1))
    t0=math.atan2(start[1]-center[1],start[0]-center[0])
    t1=math.atan2(end[1]-center[1],end[0]-center[0])
    sweep=(t1-t0+math.pi)%(2*math.pi)-math.pi
    points=[(center[0]+radius*math.cos(t0+sweep*i/128),
             center[1]+radius*math.sin(t0+sweep*i/128)) for i in range(129)]
    return dict(radius_mm=radius,unfilleted_interior_angle_degrees=math.degrees(angle),
                corner_xy_mm=corner,center_xy_mm=center,start_xy_mm=start,end_xy_mm=end,
                sweep_radians=sweep,points_xy_mm=points)


def south_design(boards,wall=2.,clearance=.502):
    old=boards['wing_left'].buffer(clearance,join_style=2).buffer(wall,join_style=2)
    # Projecting column and thumb tips, in their boundary order. Landmarks
    # derive from the unchanged Wing polygon rather than a second PCB model.
    pcb=list(boards['wing_left'].exterior.coords)
    tips=[pcb[i] for i in (13,10,5,1,0)]
    outer=list(old.exterior.coords)
    stepped=[min(outer,key=lambda q:math.dist(p,q)) for p in tips]
    _,line=wing_envelope(boards['wing_left'],clearance,wall)
    a,z=sorted(line['endpoints'])
    n=_datums(boards,wall,clearance)['left_north_xy_mm']
    bridge=_datums(boards,wall,clearance)['left_bridge_xy_mm']
    # One quadratic Bezier, chosen by minimum-area fitting in this family
    # against the unchanged pocket's 2 mm wall. No valley/tip interpolation.
    # Store offsets in the envelope frame so the construction follows inputs;
    # the 17 mm values below preserve the PO-approved Phase A solution.
    axis=_unit(tuple(z[k]-a[k] for k in (0,1)))
    normal=line['normal']
    control=tuple((a[k]+z[k])/2-.4973600073038203*axis[k]
                  +.8591183323990996*normal[k] for k in (0,1))
    # Move along the existing side supports; north and bridge stay identical.
    a=(a[0]+1.3271297251184493/math.sqrt(3),a[1]-1.3271297251184493)
    z=(z[0]+.8153908363390627/math.sqrt(3),z[1]-.8153908363390627)
    # Keep the PO-approved 17 mm solution exactly; independently solve other inputs.
    # PCB data identity selects the approved fit; 16 mm uses its own optimization.
    from pathlib import Path
    import json
    approved = json.loads((Path(__file__).resolve().parent.parent/'issue-198-final/17mm/dimensions.json').read_text())
    if not boards['wing_left'].equals_exact(Polygon(approved['boards']['wing_left']), 1e-9):
        a,z,control = _fit_pitch(tuple((k,v.wkt) for k,v in boards.items()),wall,clearance)
    first=_fillet(n,a,control);last=_fillet(control,z,bridge)
    span=[first['end_xy_mm'],control,last['start_xy_mm']]
    path=first['points_xy_mm']+bezier(span)[1:]+last['points_xy_mm'][1:]
    return dict(spans_controls_xy_mm=[span],fillets=[first,last],path_xy_mm=path,
                pcb_tip_xy_mm=tips,stepped_tip_xy_mm=stepped,
                family='single quadratic Bezier; strictly convex control triangle',
                continuity='tangent quadratic sweep and R5 circular endpoint fillets')


def proposed_outline(cavity, boards, wall=2., clearance=.502):
    d=_datums(boards,wall,clearance)
    south=south_design(boards,wall,clearance)
    left=[d['left_north_xy_mm'],*south['path_xy_mm'],d['left_bridge_xy_mm']]
    result=Polygon([*left,*[(-x,y) for x,y in reversed(left)],
                    *bezier(d['north_controls_xy_mm'])[1:-1]])
    assert result.is_valid and result.geom_type=='Polygon'
    assert result.buffer(1e-8).covers(cavity)
    assert result.boundary.distance(cavity.boundary)>=wall-1e-8
    return result


def curve_design(boards, wall=2., clearance=.502):
    d=_datums(boards,wall,clearance)
    d['south_left']=south_design(boards,wall,clearance)
    return d


@lru_cache(maxsize=4)
def _fit_pitch(board_wkts, wall, clearance):
    """Phase A SLSQP minimum-area quadratic + R5 family, fitted to this PCB.

    Side-support motion, area objective, minimum wall and convexity constraints
    match fit4.py. All coordinates and bounds derive from this pitch's inputs.
    """
    from scipy.optimize import minimize
    from shapely import wkt
    from shapely.geometry import box
    boards={k:wkt.loads(v) for k,v in board_wkts}
    cavity=unary_union([g.buffer(clearance,join_style=2) for g in boards.values()]+[box(-11,-24,11,12)]).simplify(.002,preserve_topology=True)
    datums=_datums(boards,wall,clearance)
    north=datums['north_controls_xy_mm'];n=datums['left_north_xy_mm'];bridge=datums['left_bridge_xy_mm']
    _,line=wing_envelope(boards['wing_left'],clearance,wall)
    initial_a,initial_z=sorted(line['endpoints'])
    axis=_unit(tuple(initial_z[k]-initial_a[k] for k in (0,1)))
    # Warm-start coefficients in this pitch's own envelope frame, never XY coordinates.
    initial_c=tuple((initial_a[k]+initial_z[k])/2-.4973600073038203*axis[k]+.8591183323990996*line['normal'][k] for k in (0,1))
    initial_a=(initial_a[0]+1.3271297251184493/math.sqrt(3),initial_a[1]-1.3271297251184493)
    initial_z=(initial_z[0]+.8153908363390627/math.sqrt(3),initial_z[1]-.8153908363390627)
    def build(x):
        a=(initial_a[0]-(x[0]-initial_a[1])/math.sqrt(3),x[0])
        z=(initial_z[0]-(x[1]-initial_z[1])/math.sqrt(3),x[1])
        c=tuple(x[2:])
        f=_fillet(n,a,c);g=_fillet(c,z,bridge)
        span=[f['end_xy_mm'],c,g['start_xy_mm']]
        path=f['points_xy_mm']+bezier(span,128)[1:]+g['points_xy_mm'][1:]
        left=[n,*path,bridge]
        poly=Polygon([*left,*[(-x,y) for x,y in reversed(left)],*bezier(north)[1:-1]])
        return poly,span,f,g,a,z,c
    def constraints(x):
        p,span,f,g,*_=build(x)
        u=[span[1][i]-span[0][i] for i in (0,1)]
        v=[span[2][i]-span[1][i] for i in (0,1)]
        return [p.boundary.distance(cavity.boundary)-wall,
                -(u[0]*v[1]-u[1]*v[0]),-f['sweep_radians'],-g['sweep_radians']]
    initial=[initial_a[1],initial_z[1],*initial_c]
    result=minimize(lambda x:build(x)[0].area/1000, initial,method='SLSQP',
                    constraints=[dict(type='ineq',fun=constraints)],
                    bounds=[(v-10,v+10) for v in initial],
                    options=dict(maxiter=250,ftol=1e-11,eps=1e-4))
    p,span,f,g,a,z,c=build(result.x)
    assert min(constraints(result.x))>=-1e-8, (result.message,constraints(result.x))
    assert p.covers(cavity), 'fitted wing containment'
    assert p.boundary.distance(cavity.boundary)>=wall-1e-8
    print('Independent pitch fit:',result.message,'iterations',result.nit,'area',p.area,flush=True)
    return a,z,c
