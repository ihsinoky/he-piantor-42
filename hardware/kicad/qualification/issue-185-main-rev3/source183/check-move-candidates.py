"""Check saved hypothetical candidate copper with native KiCad collision shapes.

This verifies candidates only, without editing/saving boards or redoing the audit.
It is not a full routing/connectivity/zone-refill qualification.
"""
from audit import *

def check(source,runtime):
    b,pads,tracks,vias,keepouts,npth=load_geometry(source,runtime)
    w=E/source['board'];probes=json.loads((w/'move-probes.json').read_text())
    rows={r['uuid']:r for r in json.loads((w/'all-vias.json').read_text())}
    checks=[]
    for q in probes:
        r=rows[q['via_uuid']];radius=r['diameter_mm']/2;tested=[]
        for key in ['fixed_copper_nearest_mm','straight_stub_candidate_mm']:
            pos=q[key]
            if pos is None:continue
            center=point(pos);disk=p.SHAPE_CIRCLE(center,round(radius*MM))
            pad_gap=min(shape.Distance(center)/MM-radius for a in pads for shape in a['shapes'].values())
            assert pad_gap>=0.1-1e-12,(source['board'],q['via_uuid'],pad_gap)
            other_via_gap=min(math.dist(pos,xy(o.GetPosition()))-radius-o.GetWidth(p.F_Cu)/2/MM for o in vias if o.m_Uuid.AsString()!=q['via_uuid'])
            assert other_via_gap>=0.1-1e-12,(source['board'],q['via_uuid'],other_via_gap)
            assert not any(t.GetEffectiveShape(t.GetLayer()).Collide(disk,p.FromMM(0.1)) for t in tracks if not isinstance(t,p.PCB_VIA) and t.GetNetname()!=r['net'])
            failures=[]
            if key=='straight_stub_candidate_mm':
                assert q['anchors']
                for a in q['anchors']:
                    l=b.GetLayerID(a['layer']);segment=p.SHAPE_SEGMENT(point(a['position_mm']),center,p.FromMM(a['width_mm']))
                    for pad in pads:
                        if pad['net']!=r['net'] and l in pad['shapes'] and pad['shapes'][l].Collide(segment,p.FromMM(0.1)):
                            failures.append(dict(anchor=a['uuid'],obstacle=pad['uuid'],kind='pad'))
                    for t in tracks:
                        if t.GetNetname()==r['net'] or not t.IsOnLayer(l):continue
                        if t.GetEffectiveShape(l).Collide(segment,p.FromMM(0.1)):
                            failures.append(dict(anchor=a['uuid'],obstacle=t.m_Uuid.AsString(),kind=t.GetClass()))
            tested.append(dict(candidate=key,position_mm=pos,min_pad_gap_mm=round(pad_gap,9),min_other_via_gap_mm=round(other_via_gap,9),native_stub_clearance_failures=failures))
        checks.append(dict(via_uuid=q['via_uuid'],candidates=tested))
    out=dict(board=source['board'],source_sha256=source['sha256'],kicad_version=p.Version(),checked_vias=len(probes),checks=checks,stub_failures=sum(len(c['native_stub_clearance_failures']) for q in checks for c in q['candidates']),design_saved=False,full_drc_or_connectivity_check=False)
    dump(w/'move-native-check.json',out);print(source['board'],'native stub failures',out['stub_failures'])
    assert out['stub_failures']==0

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--runtime',type=Path,default=Path('.issue183-runtime'));parser.add_argument('--board',action='append');args=parser.parse_args()
    for source in json.loads((E/'sources.json').read_text()):
        if not args.board or source['board'] in args.board:check(source,args.runtime)
