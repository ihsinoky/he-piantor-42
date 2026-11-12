"""Issue 228 Phase A: round 2 tangent Bezier silhouette; unchanged pocket.

Pure 2D Shapely construction shared by the generator and approval drawing.
Coordinates are assembly XY in mm (positive Y south). Curves sampled in 512 uniform parameter intervals per span.
"""
import math
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


def curve_design(boards, wall=2., clearance=.502):
    envelope, line = wing_envelope(boards['wing_left'], clearance, wall)
    n = min(envelope.exterior.coords, key=lambda p:p[1])
    pinky, thumb = sorted(line['endpoints'])
    pts = list(boards['wing_left'].exterior.coords)[:-1]
    sn = min(pts,key=lambda p:p[1])
    sp = max(pts,key=lambda p:abs(p[0]))
    st = max(pts,key=lambda p:p[1])
    si = min(pts,key=lambda p:abs(p[0]))
    def unit(a,b):
        d = tuple(b[i]-a[i] for i in (0,1)); l=math.hypot(*d)
        return tuple(x/l for x in d)
    dp, dt = unit(sn,sp), unit(st,si)
    # Preserve the original center-south bridge and both side directions.
    bridge_y = boards['main'].bounds[3]+clearance+wall
    a_y, z_y = sp[1]+1.7576445984952933, bridge_y+9.598
    a = (pinky[0]+(a_y-pinky[1])*dp[0]/dp[1],a_y)
    z = (thumb[0]+(z_y-thumb[1])*dt[0]/dt[1],z_y)
    bridge = (thumb[0]+(bridge_y-thumb[1])*dt[0]/dt[1],bridge_y)
    handle=40.
    south=[a,tuple(a[i]+handle*dp[i] for i in (0,1)),
           tuple(z[i]-handle*dt[i] for i in (0,1)),z]
    neck=min((p for p in pts if abs(p[1]+45.)<1e-7),key=lambda p:abs(p[0]))
    slope=(neck[1]-sn[1])/(neck[0]-sn[0])
    north=[(-n[0],n[1]),(0.,n[1]-n[0]*slope),n]
    return dict(south_left_controls_xy_mm=south,
                south_right_controls_xy_mm=[(-x,y) for x,y in south],
                north_controls_xy_mm=north,left_north_xy_mm=n,
                left_bridge_xy_mm=bridge,handle_length_mm=handle,
                steps_per_span=CURVE_STEPS)


def usb_access(outer, center_x=0.):
    """12mm open-top slot, extended through the new north wall.

    Default Z=11.2..15.2mm (4mm high, open above). Final alignment belongs
    to the pending Fly seat rework; daughterboard seat is unchanged.
    """
    from shapely.geometry import box
    return box(center_x-6.,outer.bounds[1]-1.,center_x+6.,-34.)


def proposed_outline(cavity, boards, wall=2., clearance=.502):
    d=curve_design(boards,wall,clearance)
    left=[d['left_north_xy_mm'],*bezier(d['south_left_controls_xy_mm']),
          d['left_bridge_xy_mm']]
    result=Polygon([*left,*[(-x,y) for x,y in reversed(left)],
                    *bezier(d['north_controls_xy_mm'])[1:-1]])
    assert result.is_valid and result.geom_type=='Polygon'
    assert result.buffer(1e-8).covers(cavity)
    assert result.boundary.distance(cavity.boundary)>=wall-1e-8
    return result
