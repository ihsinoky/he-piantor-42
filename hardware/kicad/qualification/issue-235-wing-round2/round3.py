"""Issue235 round3: deterministic 16L-only repair and unchanged round2 gates.

python3 hardware/kicad/qualification/issue-235-wing-round2/round3.py reproduce
python3 hardware/kicad/qualification/issue-235-wing-round2/round3.py verify
Scratch and subprocess logs live exclusively in .issue235r3-runtime.
"""
from pathlib import Path
import gzip, hashlib, json, os, shlex, subprocess, sys

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
R = E.parents[3]
T = R / '.issue235r3-runtime'
W = E / 'wing-rev4-16mm-left'
D = W / 'round3'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n')

def evidence_files():
    return sorted([f for f in W.rglob('*') if f.is_file() and f!=D/'evidence.json' and f.suffix!='.kicad_prl'] +
        [E/f for f in ('REPORT3.md','round3.py','round3-diagram.py','round3-post-screen.py')])

def seal():
    save(D/'evidence.json',dict(board_sha256=sha(W/'main.kicad_pcb'),
        files={str(f.relative_to(R)):sha(f) for f in evidence_files()}))

def verify_seal():
    manifest=json.loads((D/'evidence.json').read_text())
    actual={str(f.relative_to(R)):sha(f) for f in evidence_files()}
    assert actual==manifest['files'],'round3 evidence manifest mismatch'
    assert manifest['board_sha256']==sha(W/'main.kicad_pcb')
    print('Round3 evidence manifest verified',flush=True)

def setup():
    c = json.loads((E / 'toolchain.json').read_text())
    for n in ('tmp', 'config', 'cache', 'data', 'state'):
        (T / n).mkdir(parents=True, exist_ok=True)
    env = dict(PYTHONDONTWRITEBYTECODE='1',
        PYTHONPATH=c['KICAD_ROOT']+'/usr/lib/python3/dist-packages:'+c['GEOMETRY_SITE'],
        LD_LIBRARY_PATH=c['KICAD_ROOT']+'/usr/lib/x86_64-linux-gnu:'+c['KICAD_ROOT']+'/usr/lib/kicad',
        KICAD_STOCK_DATA_HOME=c['KICAD_ROOT']+'/usr/share/kicad', TMPDIR=str(T/'tmp'))
    env.update({'XDG_'+n.upper()+'_HOME':str(T/n) for n in ('config','cache','data','state')})
    s = '#!/bin/bash\nset -eu\n' + ''.join('export '+k+'='+shlex.quote(v)+'\n' for k,v in env.items())
    s += 'export PATH='+shlex.quote(c['KICAD_ROOT']+'/usr/bin')+':"$PATH"\nunset DISPLAY WAYLAND_DISPLAY\nexec "$@"\n'
    (T/'run').write_text(s)
    (T/'run').chmod(0o755)
    return c

def scoped(script):
    """Reuse original validators verbatim except scope and output destination.
    Assert substitutions so upstream changes cannot silently widen scope.
    """
    s = (E/(script+'.py')).read_text()
    loop = "for w in sorted(E.glob('wing-rev4-*')):"
    if script!='verify-fem':
        assert s.count(loop) == 1
        s = s.replace(loop, "for w in [E/'wing-rev4-16mm-left']:")
    for filename in {
        'electrical-check':['electrical-contract.json'],
        'power-summary':['power-summary.json','power-sensitivity.csv'],
        'congestion':['congestion-summary.json'],
        'verify-fem':['fem-selfcheck.json'],
        'body-clearance':['body-clearance.json'],
    }[script]:
        target = "E/'"+filename+"'"
        assert target in s
        s = s.replace(target, "D/'"+filename+"'")
    # __file__ deliberately points at the original implementation.
    sys.argv=[str(E/(script+'.py'))]
    exec(compile(s,str(E/(script+'.py')),'exec'),dict(__file__=str(E/(script+'.py')),D=D))

def board_repair():
    import pcbnew as p
    from verify import xy
    delta = json.loads((D/'repair.json').read_text())
    source = D/'round2-main.kicad_pcb'
    assert sha(source) == delta['source_sha256']
    b = p.LoadBoard(str(source))
    manager = p.GetSettingsManager()
    manager.LoadProject(str(W/'input.kicad_pro'))
    b.SetProject(manager.Prj())
    tracks = {t.m_Uuid.AsString(): t for t in b.GetTracks()}
    V = lambda q:p.VECTOR2I(round(q[0]*1e6),round(q[1]*1e6))
    def signature(t):
        via = isinstance(t,p.PCB_VIA)
        d = dict(uuid=t.m_Uuid.AsString(),net=t.GetNetname(),
            width_mm=p.ToMM(t.GetWidth(p.F_Cu) if via else t.GetWidth()),kind='via' if via else 'track')
        if via:d.update(position_mm=xy(t.GetPosition()),drill_mm=p.ToMM(t.GetDrillValue()))
        else:d.update(start_mm=xy(t.GetStart()),end_mm=xy(t.GetEnd()),layer=b.GetLayerName(t.GetLayer()))
        return d
    def configure(t, d):
        t.SetWidth(p.FromMM(d['width_mm']))
        t.SetNetCode(b.FindNet(d['net']).GetNetCode())
        if d['kind']=='via':
            t.SetPosition(V(d['position_mm']))
            t.SetDrill(p.FromMM(d['drill_mm']))
            t.SetViaType(p.VIATYPE_THROUGH)
            t.SetLayerPair(p.F_Cu,p.B_Cu)
        else:
            t.SetStart(V(d['start_mm']));t.SetEnd(V(d['end_mm']))
            t.SetLayer(p.F_Cu if d['layer']=='F.Cu' else p.B_Cu)
    for d in delta['removed']:
        t=tracks[d['uuid']];assert signature(t)==d;b.Delete(t)
    for d in delta['changed']:
        t=tracks[d['before']['uuid']];assert signature(t)==d['before'];configure(t,d['after'])
    uuid_map = {}
    for d in delta['added']:
        assert d['uuid'] not in tracks
        t=p.PCB_VIA(b) if d['kind']=='via' else p.PCB_TRACK(b)
        configure(t,d);uuid_map[t.m_Uuid.AsString()]=d['uuid'];b.Add(t)
    b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity()
    assert p.SaveBoard(str(W/'main.kicad_pcb'),b)
    # pcbnew exposes UUID as read-only. Restore recorded IDs in the serialized
    # board; the subsequent native reload/refill/audit validates this file.
    text=(W/'main.kicad_pcb').read_text()
    for generated,recorded in uuid_map.items():
        assert text.count(generated)==1
        text=text.replace(generated,recorded)
    (W/'main.kicad_pcb').write_text(text)

def verify():
    import pcbnew as p
    from verify import shape_signature, xy, polys
    protected=json.loads(gzip.decompress((D/'protected-files.json.gz').read_bytes()))
    changed=[f for f,h in protected.items() if not (R/f).is_file() or sha(R/f)!=h]
    assert not changed,changed
    a=p.LoadBoard(str(D/'round2-main.kicad_pcb'));b=p.LoadBoard(str(W/'main.kicad_pcb'))
    assert shape_signature(a)==shape_signature(b),'placement, pad, role or pose changed'
    def edges(board):
        return sorted((xy(d.GetStart()),xy(d.GetEnd()),d.GetWidth()) for d in board.GetDrawings() if d.GetLayer()==p.Edge_Cuts)
    assert edges(a)==edges(b)
    def zones(board):
        return sorted((z.GetNetname(),list(z.GetLayerSet().Seq()),z.GetIsRuleArea(),polys(z.Outline()).wkt) for z in board.Zones())
    assert zones(a)==zones(b),'pour outlines or reservations changed'
    assert (W/'input.kicad_pro').read_bytes()==(W/'main.kicad_pro').read_bytes()
    q=json.loads((W/'qualification.json').read_text())
    assert q['sha256']==sha(W/'main.kicad_pcb') and q['pass']
    assert all(v==0 for v in q['metrics'].values()) and q['min_via_pad_gap_mm']>=.125
    drc=json.loads((W/'drc.json').read_text());assert not drc['violations'] and not drc['unconnected_items']
    extraction=json.loads((W/'resistance-extraction.json').read_text())
    assert extraction['board_sha256']==q['sha256'] and len(extraction['rows'])==8
    power=json.loads((D/'power-summary.json').read_text());assert len(power['boards'])==1
    assert power['boards'][0]['source_sha256']==q['sha256'] and not power['adopted_200mm_below_4p60']
    contract=json.loads((D/'electrical-contract.json').read_text());assert len(contract)==1 and contract[0]['logical_errors']==0
    assert json.loads((D/'fem-selfcheck.json').read_text())['pass_all']
    posts=json.loads((D/'post-rescreen.json').read_text())
    assert posts['pass_all'] and posts['board_sha256']==q['sha256'] and len(posts['posts'])==6
    bodies=json.loads((D/'body-clearance.json').read_text())
    assert len(bodies)==1 and bodies[0]['pass_body_overlap_screen']
    result=dict(pass_all_round3_gates=True,board_sha256=q['sha256'],
        protected_tracked_files=len(protected),protected_file_changes=changed,
        other_three_variants_byte_identical=True,all_footprints_pads_holes_outline_reservations_unchanged=True,
        case_post_body_rescreen='round3/body-clearance.json and round3/post-rescreen.json; component/pad poses fixed, moved and added via obstacles rescreened.',
        metrics=q['metrics'],minimum_via_pad_gap_mm=q['min_via_pad_gap_mm'],
        inherited_case_harness_and_adoption_limitations_remain=True)
    save(D/'verification.json',result)
    print(json.dumps(result,indent=2))

def main():
    command=sys.argv[1] if len(sys.argv)>1 else 'verify'
    c=setup()
    if command in ('reproduce','verify'):
        def run(args,label):
            with (T/(label+'.log')).open('w') as log:
                subprocess.run([str(T/'run'),c['ROUTER_PYTHON'],*args],cwd=R,stdout=log,stderr=subprocess.STDOUT,check=True)
            for cache in W.glob('*.kicad_prl'):
                (T/'ui-cache').mkdir(exist_ok=True)
                cache.replace(T/'ui-cache'/cache.name)
            print(label+' passed',flush=True)
        if command=='reproduce':
            run([str(__file__),'repair'],'repair')
            run([str(E/'audit.py'),W.name],'audit')
            run([str(__file__),'electrical-check'],'electrical-contract')
            run([str(E/'extract-resistance.py'),W.name],'extraction')
            run([str(__file__),'power-summary'],'power-summary')
            run([str(__file__),'congestion'],'congestion')
            run([str(__file__),'verify-fem'],'fem-selfcheck')
            run([str(E/'round3-diagram.py')],'diagram')
            run([str(__file__),'body-clearance'],'body-clearance')
            run([str(E/'round3-post-screen.py')],'post-rescreen')
        run([str(__file__),'check'],'verification')
        if command=='reproduce':seal()
        verify_seal()
    elif command=='repair':board_repair()
    elif command=='check':verify()
    elif command in ('electrical-check','power-summary','congestion','verify-fem','body-clearance'):scoped(command)
    else:raise SystemExit('Unknown command '+command)

if __name__=='__main__':main()
