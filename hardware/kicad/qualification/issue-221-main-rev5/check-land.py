"""Molex 781710000-SD A, sheets1/2, component side dimensions and numbering."""
from common import *
import pcbnew as p
b=p.LoadBoard(str(E/'inspection/final/main.kicad_pcb'));f=next(f for f in b.GetFootprints() if f.GetReference()=='J4')
xy=lambda v:[round(p.ToMM(v.x),6),round(p.ToMM(v.y),6)]
pads={a.GetNumber():a for a in f.Pads() if a.GetNumber()};rows=[]
for i,x in enumerate([101.8,100.6,99.4,98.2],1):
 a=pads[str(i)];assert xy(a.GetPosition())==[x,91.875] and xy(a.GetSize())==[.6,.85]
 assert a.GetNetname()==['VBUS','USB_DM_ESD','USB_DP_ESD','GND'][i-1]
 assert a.GetShape()==p.PAD_SHAPE_RECT and a.IsOnLayer(p.F_Paste) and a.IsOnLayer(p.F_Mask)
 rows.append(dict(pin=i,position_mm=xy(a.GetPosition()),land_size_mm=xy(a.GetSize()),net=a.GetNetname()))
mounts=[a for a in f.Pads() if not a.GetNumber()];assert len(mounts)==2
assert sorted(xy(a.GetPosition()) for a in mounts)==[[97.05,88.1],[102.95,88.1]]
assert all(xy(a.GetSize())==[.7,.8] and not a.GetNetname() for a in mounts)
# SD sheet2: signal-pad inner edge to nail far edge = 3.75; .8 gap
# from pin1 center to nearest nail edge. Centred official footprint coordinates.
assert abs((1.9+.8/2)-(-1.875+.85/2)-3.75)<1e-9
assert abs((-1.8)-(-2.95+.7/2)-.8)<1e-9
# Conservative whole-body envelope covers the drawing's hatched F.Cu area.
# Only the specified six pads may occupy it; inner GND plane is unaffected.
from shapely.geometry import box,LineString,Point
from shapely.ops import unary_union
import importlib.util
spec=importlib.util.spec_from_file_location('audit221',E/'audit-vias.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
body=box(96.7,87.48,103.3,92.04)
allowed=unary_union([audit.pad_polygon(a,p.F_Cu) for a in f.Pads()])
forbidden=body.difference(allowed.buffer(.000002));intrusions=[]
for t in b.GetTracks():
 if not t.IsOnLayer(p.F_Cu):continue
 g=Point(xy(t.GetPosition())).buffer(p.ToMM(t.GetWidth(p.F_Cu))/2) if isinstance(t,p.PCB_VIA) else LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2,quad_segs=64)
 area=g.intersection(forbidden).area
 if area>1e-10:intrusions.append(dict(uuid=t.m_Uuid.AsString(),area_mm2=area))
for fp in b.GetFootprints():
 if fp.GetReference()=='J4':continue
 for a in fp.Pads():
  if a.IsOnLayer(p.F_Cu) and a.GetAttribute()!=p.PAD_ATTRIB_NPTH:
   area=audit.pad_polygon(a,p.F_Cu).intersection(body).area
   if area>1e-10:intrusions.append(dict(ref=fp.GetReference(),pad=a.GetNumber(),area_mm2=area))
assert not intrusions,intrusions
save(E/'land-check.json',dict(pass_check=True,board_sha256=digest(E/'inspection/final/main.kicad_pcb'),drawing='sources/781710000-SD-revA.pdf',drawing_sha256=digest(E/'sources/781710000-SD-revA.pdf'),drawing_id='781710000-SD PSD000 A, 2022-06-07, sheets 1 and 2; 4-circuit table A6.6/B3.6/C5.0/D3.9',official_footprint_sha256=digest(E/'sources/molex-kicad-official.kicad_mod'),reference='https://github.com/KiCad/kicad-footprints/blob/master/Connector_Molex.pretty/Molex_Pico-EZmate_78171-0004_1x04-1MP_P1.20mm_Vertical.kicad_mod',pitch_mm=1.2,electrical_lands=rows,mechanical_lands=[dict(position_mm=xy(a.GetPosition()),size_mm=xy(a.GetSize()),net=a.GetNetname()) for a in mounts],signal_inner_to_nail_far_edge_mm=3.75,signal_to_nail_x_edge_mm=.8,component_side_numbering='In unrotated top view pin1 is leftmost upper contact next to circuit1 triangle; board rotation180 places pin1 at lower right',reference_pcb_thickness_mm=1.0,reference_stencil_thickness_mm=.1,reference_aperture_ratio_percent=100,actual_pcb_thickness_mm=1.2,modifications_to_kicad_reference=['rectangular lands retain the specified full .60x.85 and .70x.80 extents','mechanical nails unnumbered/unconnected','hidden reference/value; Rev5:J4 identifier'],F_Cu_body_envelope_mm=[96.7,87.48,103.3,92.04],routing_in_nonrecommended_body_area=intrusions,power_escape_width_mm=.6,power_widening_at_y_mm=92.65,power_outside_width_mm=1.1,assembly_review_required=True))
print('Land dimension/numbering audit PASS')
