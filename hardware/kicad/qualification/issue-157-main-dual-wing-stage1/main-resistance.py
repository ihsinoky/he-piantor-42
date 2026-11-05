#!/usr/bin/env python3
"""Reuse #141 centerline model for two existing Main positive-rail paths.

Read-only; 1A test injection yields ohms. GND plane and other system loads are
excluded. This is a planning estimate, not sign-off or a proposed routing.
"""
from pathlib import Path
import importlib.util
import json
import hashlib
import sys
import pcbnew
sys.dont_write_bytecode=True
E=Path(__file__).resolve().parent;R=E.parents[3]
source=R/'hardware/kicad/qualification/issue-141-wing-power-integrity/dc-model.py'
snapshot=R/'hardware/kicad/qualification/issue-155-main-mounting-stage2/inspection/final/snapshot.json'
spec=importlib.util.spec_from_file_location('dc141',source)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
s=json.loads(snapshot.read_text())
board=pcbnew.LoadBoard(str(snapshot.with_name('main.kicad_pcb')))
layers=list(board.GetEnabledLayers().CuStack())
native_pads={p.m_Uuid.AsString():p for f in board.GetFootprints() for p in f.Pads()}
native_vias={v.m_Uuid.AsString():v for v in board.GetTracks() if isinstance(v,pcbnew.PCB_VIA)}
native_tracks={v.m_Uuid.AsString():v for v in board.GetTracks() if not isinstance(v,pcbnew.PCB_VIA)}
def xy(v):return [pcbnew.ToMM(v.x),pcbnew.ToMM(v.y)]
results=[]
for net,source_ref,source_pads,load_ref,load_pad in [('VBUS','J1',['2','11'],'U5','1'),('HALL_5V','U5',['6'],'J2','1')]:
    ps=[dict(p) for p in s['pads'] if p['net']==net]
    for p in ps:
        n=native_pads[p['uuid']]
        assert xy(n.GetPosition())==p['position'] and xy(n.GetSize())==p['size'] and n.GetNetname()==net
        p['layers']=[l for l in layers if n.IsOnLayer(l)]
        if p['ref']==source_ref and p['number'] in source_pads:p['ref']='J_WING'
        elif p['ref']==load_ref and p['number']==load_pad:p['ref']='U_H_LOAD'
    ts=[dict(t,width_mm=t['width']) for t in s['tracks'] if t['kind']=='track' and t['net']==net]
    assert all(t['width_mm']==.1 for t in ts)
    for t in ts:
        n=native_tracks[t['uuid']]
        assert xy(n.GetStart())==t['start'] and xy(n.GetEnd())==t['end']
        assert n.GetLayer()==t['layer'] and n.GetNetname()==net and pcbnew.ToMM(n.GetWidth())==t['width_mm']
    # Use snapshot's native via layer membership, not legacy two-layer labels.
    vs=[dict(t,diameter_mm=t['size'],drill_mm=t['drill'],layers=[l for l in layers if native_vias[t['uuid']].IsOnLayer(l)]) for t in s['tracks'] if t['kind']=='via' and t['net']==net]
    for p in ps:assert p['shape']=='rect'
    inv=dict(pads=ps,tracks=ts,vias=vs)
    for temp,factor in [(20,1),(20,.8),(125,1),(125,.8)]:
        result=m.model(inv,net,1.,0.,.1*factor,temp)
        resistance=result['pins']['U_H_LOAD.'+load_pad]
        results.append(dict(net=net,source=[source_ref,source_pads],load=[load_ref,load_pad],temperature_C=temp,width_factor=factor,
            resistance_ohm=resistance,track_count=len(ts),via_count=len(vs),kcl_residual_A=result['kcl_residual_A']))
spine=[]
for row in json.loads((E/'power-model.json').read_text())['summary']:
    same=lambda x:x['temperature_C']==row['temperature_C'] and x['width_factor']==row['width_factor']
    rv=next(x['resistance_ohm'] for x in results if same(x) and x['net']=='VBUS')
    rh=next(x['resistance_ohm'] for x in results if same(x) and x['net']=='HALL_5V')
    for topology,mult in [('star-at-U5-OUT',1),('splitter-at-J2',2)]:
        hall_drop=mult*row['branch_A']*rh
        vbus_drop=row['total_A']*rv
        spine.append(dict(load_case=row['load_case'],pitch_mm=row['pitch_mm'],temperature_C=row['temperature_C'],width_factor=row['width_factor'],topology=topology,
            existing_hall_drop_V=hall_drop,existing_vbus_drop_V=vbus_drop,
            old_J2_local_at_U5_VIN_4V75_V=row['local_at_source_4V75_V']-hall_drop,
            old_J2_local_at_USB_J1_4V75_V=row['local_at_source_4V75_V']-hall_drop-vbus_drop,
            old_J2_local_at_USB_J1_5V_V=row['local_at_source_5V_V']-hall_drop-vbus_drop))
print(json.dumps(dict(method='Verbatim #141 model() reused with Main #155 native snapshot; 1A test load',
    model_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),snapshot_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest(),
    limitations=['Positive rail only; GND plane not extracted','VBUS calculation excludes Main MCU/LDO load; USB upstream excluded',
        'Existing single-Wing route only; cannot predict new branch or shared-section split','35um foil,20um barrel,pad spreading and manufactured junction continuity inherited from #141'],results=results,spine_sensitivity=spine),indent=2))
