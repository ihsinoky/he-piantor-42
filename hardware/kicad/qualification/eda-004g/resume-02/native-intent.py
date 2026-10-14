"""Bounded Main-only reader/check: fresh source output vs frozen independent v1.

Not an interchangeable EDA converter. Unknown physical kinds/layers/rotations
fail; old routed data is never input. Returns exact source objects to public PCB
authoring only after individual source identity/net/shape checks pass.
"""
import json
import math
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def read(path):
    data=json.loads(Path(path).read_text());c=json.loads((ROOT/'main-contract-v2.json').read_text())
    def rows(t):return [x for x in data if x['type']==t]
    comps={x['source_component_id']:x for x in rows('source_component')}
    ports={x['source_port_id']:x for x in rows('source_port')}
    nets={x['source_net_id']:x['name'] for x in rows('source_net')}
    parent={p:p for p in ports}
    def find(p):
        while parent[p]!=p:p=parent[p]
        return p
    def join(a,b):parent[find(b)]=find(a)
    for x in rows('source_component_internal_connection')+rows('source_trace'):
        ids=x.get('source_port_ids',x.get('connected_source_port_ids',[]))
        for p in ids[1:]:join(ids[0],p)
    names={}
    for t in rows('source_trace'):
        for p in t['connected_source_port_ids']:names.setdefault(find(p),set()).update(nets[n] for n in t['connected_source_net_ids'])
    assert all(len(v)==1 for v in names.values()),'source named-net short'
    pc={x['pcb_component_id']:x for x in rows('pcb_component')}
    pp={x['pcb_port_id']:x for x in rows('pcb_port')}
    expected={x['reference']:x for x in c['components']}
    assert {x['name'] for x in comps.values()}==set(expected)
    assert set(nets.values())==set(c['named_nets'])
    def number(p):return str(p['pin_number']) if 'pin_number' in p else next(h[3:] for h in p['port_hints'] if re.fullmatch(r'pin\d+',h))
    logical={}
    for sid,p in ports.items():
        ref=comps[p['source_component_id']]['name'];n=number(p);group=names.get(find(sid),set());net=next(iter(group)) if group else None
        assert n in expected[ref]['pins'] and net==expected[ref]['pins'][n]['named_net'],(ref,n,net)
        if 'pin_number' in p:
            assert p['name']==expected[ref]['pins'][n]['alias'] and p.get('do_not_connect',False)==expected[ref]['pins'][n]['intentional_nc']
            logical[(ref,n)]=dict(net=net,alias=p['name'])
    assert len(logical)==193 and len(ports)==197
    for p in pc.values():
        ref=comps[p['source_component_id']]['name'];e=expected[ref]
        assert p['layer']=='top' and p['rotation']==e['source_ccw_rotation_deg']
        assert all(abs(p[k]-v)<1e-6 for k,v in zip(['display_offset_x','display_offset_y'],e['source_position_mm']))
    material=[]
    for kind in ('pcb_smtpad','pcb_plated_hole'):
        for p in rows(kind):
            port=ports[pp[p['pcb_port_id']]['source_port_id']];ref=comps[port['source_component_id']]['name'];n=number(port)
            assert p['shape'] in ('rect','circle','oval')
            size=[p['width'],p['height']] if kind=='pcb_smtpad' and p['shape']=='rect' else [2*p['radius']]*2 if kind=='pcb_smtpad' else [p['outer_width'],p['outer_height']]
            drill=[0,0] if kind=='pcb_smtpad' else [p['hole_width'],p['hole_height']]
            matches=[e for e in c['pads'] if e['source_id']==ref and e['number']==n and math.hypot(p['x']-e['source_position_mm'][0],p['y']-e['source_position_mm'][1])<1e-6]
            assert len(matches)==1,(ref,n,p)
            e=matches[0]
            assert all(abs(a-b)<1e-6 for a,b in zip(size,e['source_global_size_mm'])) and drill==e['drill_mm'] and p['shape']==e['shape'],(ref,n,size,e)
            assert p.get('corner_radius',0)==0,'Native extra corner radius outside frozen rect geometry'
            material.append(dict(**e,raw=p))
    assert len(material)==197 and len({e['id'] for e in material})==197
    for p,e in zip(sorted(rows('pcb_hole'),key=lambda x:x['x']),c['holes']):
        assert p['hole_shape']=='circle' and p['hole_diameter']==e['diameter_mm']
        assert math.hypot(p['x']-e['source_position_mm'][0],p['y']-e['source_position_mm'][1])<1e-6
    assert len(rows('pcb_hole'))==2
    assert not rows('pcb_via') and not rows('pcb_copper_pour') and not rows('pcb_keepout')
    traces=rows('pcb_trace');assert len(traces)==1
    source=next(t for t in rows('source_trace') if t['source_trace_id']==traces[0]['source_trace_id'])
    assert source['name']=='USB_SHELL_BOND'
    rawpoints=traces[0]['route'];assert all(p['route_type']=='wire' and p['layer']=='top' and p['width']==.2 for p in rawpoints)
    expected_points=[[-19.32,15.87]]+[[x-15,y+19] for x,y in c['local_bond']['source_anchor_frame_points_mm']]
    assert len(rawpoints)==len(expected_points) and all(math.hypot(p['x']-e[0],p['y']-e[1])<1e-6 for p,e in zip(rawpoints,expected_points))
    edges={}
    for a,b in zip(rawpoints,rawpoints[1:]):
        va=(round(a['x'],6),round(a['y'],6));vb=(round(b['x'],6),round(b['y'],6))
        if va!=vb:edges[tuple(sorted([va,vb]))]=dict(a=va,b=vb,width=.2,net='GND',layer='F.Cu')
    assert len(edges)==3 and abs(sum(math.dist(*k) for k in edges)-17)<1e-6
    b=rows('pcb_board')[0]
    assert b['width']==48 and b['height']==44 and b['thickness']==1.2 and b['num_layers']==2
    assert b['min_trace_width']==.2 and b['min_via_pad_diameter']==.6 and b['min_via_hole_diameter']==.3
    assert not [p for p in data if p['type'].endswith('_error')]
    return dict(data=data,contract=c,source_components=comps,pcb_components=pc,logical=logical,
                material=material,local_bond=list(edges.values()),holes=rows('pcb_hole'),
                warnings=[p for p in data if p['type'].endswith('_warning')],
                summary=dict(individual_components_pins_nets_geometry=True,physical_pads=197,required=167,nc=30,npth=2,
                             copper_global_tracks=0,vias=0,source_bond_path_length=34,distinct_bond_length=17,
                             no_historical_input=True,auxiliary_source_kinds=sorted({p['type'] for p in data if p['type'].startswith('pcb_')})))

if __name__=='__main__':
    import sys
    result=read(sys.argv[1]);Path(sys.argv[2]).write_text(json.dumps(dict(summary=result['summary'],warnings=result['warnings']),indent=2)+'\n')
    print(json.dumps(result['summary']))
