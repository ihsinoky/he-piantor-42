"""Remove obsolete Rev.2 metadata without changing physical geometry or circuits."""
from pathlib import Path
import json
E=Path(__file__).resolve().parent;R=E.parents[3]
for g in json.loads((R/'hardware/case/issue-200-stage1/geometry.json').read_text())['variants']:
 w=E/('wing-rev3-'+g['variant']);p=w/'definition.json';s=json.loads(p.read_text())
 s.update(schema_version='wing-rev3-1',outline_policy='Stage 1b broad north shoulder with R5 join and stepped south trim',size_requirement='Issue200 Stage1b exact geometry; fixed Rev2 key frame',status='Issue200 Stage2 candidate; acceptance is bound to main PCB SHA256 in qualification.json')
 s.pop('connector_cable_access_mm',None)
 s['connector_access_assembly_mm']=g['connector']['finger_and_plug_access_assembly'];s['connector_access_z_mm']=g['connector']['access_z_mm']
 s['harness'].update(length_mm=200,length_decision='pending: 200mm adopted by D033; 124.097mm route candidate only',route_required_mm=g['harness']['required_mm'],candidate_lengths_mm=[g['harness']['required_mm'],200],bundle_envelope_max_mm=5,bend_radius_reservation_mm=5)
 s['service_notes']=['North service components; true native rotations, no mirrored pads','15 top testpoints support diameter1.2mm vertical probe access; see mechanical-verification.json','South 2mm band reserved for filled HALL_5V front / GND rear; no signal tracks or vias']
 p.write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n')
