"""Native quadratic Beziers and exact R5 arcs for the approved sampled outline.

Only outer-curve vertices created by 2D clipping are projected onto the
analytic source (maximum Phase A chord error 0.000112 mm). Interior edges
remain straight. Every height layer uses the same underlying curves.
"""
from shapely.geometry import LineString,Point
from build123d import Edge,Wire,Vector,Location
from OCP.BRep import BRep_Tool
from OCP.GeomAPI import GeomAPI_ProjectPointOnCurve
PATHS=[]
CURVES=[]

def configure(boards):
    from outline import curve_design,bezier
    d=curve_design(boards);s=d['south_left']
    paths=[s['fillets'][0]['points_xy_mm'],bezier(s['spans_controls_xy_mm'][0]),s['fillets'][1]['points_xy_mm']]
    def v(p):return (*p,0.)
    curves=[Edge.make_three_point_arc(v(paths[0][0]),v(paths[0][64]),v(paths[0][-1])),
            Edge.make_bezier(*[v(p) for p in s['spans_controls_xy_mm'][0]]),
            Edge.make_three_point_arc(v(paths[2][0]),v(paths[2][64]),v(paths[2][-1]))]
    mirrored=[[( -x,y) for x,y in p] for p in paths]
    mirror_curves=[Edge.make_three_point_arc(v(mirrored[0][0]),v(mirrored[0][64]),v(mirrored[0][-1])),
                   Edge.make_bezier(*[(-p[0],p[1],0.) for p in s['spans_controls_xy_mm'][0]]),
                   Edge.make_three_point_arc(v(mirrored[2][0]),v(mirrored[2][64]),v(mirrored[2][-1]))]
    PATHS[:]=[LineString(p) for p in paths+mirrored]+[LineString(bezier(d['north_controls_xy_mm']))]
    CURVES[:]=curves+mirror_curves+[Edge.make_bezier(*[v(p) for p in d['north_controls_xy_mm']])]

def wire(points,z):
    points=list(points)
    if points[0]==points[-1]:points.pop()
    labels=[]
    for a,b in zip(points,points[1:]+points[:1]):
        labels.append(next((i for i,path in enumerate(PATHS) if path.distance(Point(a))<1e-7 and path.distance(Point(b))<1e-7),None))
    if all(i is None for i in labels):
        return Wire.make_polygon([Vector(x,y,z) for x,y in points],close=True)
    start=next(i for i in range(len(points)) if labels[i]!=labels[i-1])
    points=points[start:]+points[:start];labels=labels[start:]+labels[:start]
    groups=[];i=0
    while i<len(labels):
        j=i+1
        if labels[i] is not None:
            while j<len(labels) and labels[j]==labels[i]:j+=1
        groups.append((i,j,labels[i]));i=j
    # Project only run endpoints; straight support/cut edges share these vertices.
    projected={}
    for i,j,label in groups:
        if label is None:continue
        curve=BRep_Tool.Curve_s(CURVES[label].wrapped,float(),float())
        for k in (i,j%len(points)):
            p=GeomAPI_ProjectPointOnCurve(Vector(*points[k],0).to_pnt(),curve).NearestPoint()
            projected[k]=Vector(p.X(),p.Y(),z)
    def at(k):return projected.get(k%len(points),Vector(*points[k%len(points)],z))
    edges=[]
    for i,j,label in groups:
        if label is None:edges.append(Edge.make_line(at(i),at(j)))
        else:
            edge=CURVES[label].moved(Location((0,0,z)))
            u=edge.param_at_point(at(i));v=edge.param_at_point(at(j))
            part=edge.trim(min(u,v),max(u,v))
            edges.append(part if u<v else part.reversed())
    return Wire(edges)
