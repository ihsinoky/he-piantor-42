"""Issue 228 Phase A: five-line Wing envelopes; unchanged central geometry.

Pure 2D Shapely construction shared by the generator and approval drawing.
Coordinates are assembly XY in mm (positive Y south). No sampled curves.
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


def proposed_outline(cavity, boards, wall=2., clearance=.502):
    legacy = cavity.buffer(wall, join_style=2)
    wings = [wing_envelope(boards['wing_'+side], clearance, wall)[0]
             for side in ('left', 'right')]
    result = unary_union([legacy, *wings])
    assert result.geom_type == 'Polygon' and result.is_valid
    assert result.buffer(1e-8).covers(legacy)
    return result
