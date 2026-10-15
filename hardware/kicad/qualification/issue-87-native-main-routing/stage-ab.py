from prepare import *
import gzip,shutil
ENV=json.loads((ROOT/'evidence/kicad-env.json').read_text())
CLI=str(BASE/'kicad/usr/bin/kicad-cli')
work=BASE/'main';work.mkdir()
origin=OLD/'evidence/processes/initial-author-pcb-explicit-public-library-io'
for name in ['main.kicad_pcb','main.kicad_pro']:shutil.copyfile(origin/name,work/name)
shutil.copyfile(OLD/'evidence/processes/initial-author-schematic/main.kicad_sch',work/'main.kicad_sch')
shutil.copyfile(OLD/'evidence/fp-lib-table',work/'fp-lib-table')
lib=BASE/'symbols';lib.mkdir()
for p in (OLD/'library').glob('*.kicad_sym*'):
    (lib/p.name.removesuffix('.gz')).write_bytes(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
# supported library registration only; embedded definitions/board/project bytes unchanged
(work/'sym-lib-table').write_text('(sym_lib_table (version 7)\n'+''.join(f'(lib (name "{p.stem}")(type "KiCad")(uri "{p}")(options "")(descr "Pinned reuse"))\n' for p in lib.glob('*.kicad_sym'))+')\n')
run('baseline-read',['/usr/bin/python3',str(OLD/'read-pcb.py'),str(work/'main.kicad_pcb'),str(work/'snapshot.json')],work,env=ENV,artifacts=[('snapshot.json',work/'snapshot.json')])
run('baseline-parity',[str(BASE/'geometry/bin/python'),str(OLD/'check-main.py'),str(OLD/'evidence/processes/initial-netlist/main.xml'),str(work/'snapshot.json'),str(ROOT/'evidence/baseline-parity.json')],work)
run('baseline-erc',[CLI,'sch','erc','--format','json','--severity-all','-o',str(work/'erc.json'),str(work/'main.kicad_sch')],work,env=ENV,artifacts=[('erc.json',work/'erc.json')])
assert not any(s['violations'] for s in json.loads((work/'erc.json').read_text())['sheets'])
run('baseline-drc',[CLI,'pcb','drc','--format','json','--severity-all','-o',str(work/'drc.json'),str(work/'main.kicad_pcb')],work,env=ENV,artifacts=[('drc.json',work/'drc.json')])
d=json.loads((work/'drc.json').read_text());assert len(d['violations'])==61
assert {x['type'] for x in d['violations']}=={'text_height','silk_overlap','silk_over_copper'}
for mode in ['spacing','via']:
    out=BASE/mode;run(mode+'-create',['/usr/bin/python3',str(ROOT/'pcb-probes.py'),mode,str(out)],BASE,env=ENV)
    if mode=='spacing':
        shutil.copyfile(work/'fp-lib-table',out/'fp-lib-table')
        run('spacing-drc',[CLI,'pcb','drc','--format','json','--severity-all','-o',str(out/'drc.json'),str(out/'main.kicad_pcb')],out,env=ENV,artifacts=[('drc.json',out/'drc.json'),('injection.json',out/'injection.json'),('main.kicad_pcb',out/'main.kicad_pcb')])
        uuids=set(json.loads((out/'injection.json').read_text())['uuids'])
        found=[x for x in json.loads((out/'drc.json').read_text())['violations'] if x['type']=='clearance' and {i['uuid'] for i in x['items']}==uuids]
        assert found, 'actual 0.10mm gap not detected'
        save(ROOT/'evidence/effective-spacing.json',dict(status='PASS_WITH_SCOPE',injected_gap_mm=.1,required_mm=.2,detection=found,unchanged_source_project_sha256=digest(work/'main.kicad_pro')))
    else:
        for kind in ['connected','missing-via','short']:
            f=out/kind/'probe.kicad_pcb';snap=out/kind/'snapshot.json'
            run('via-read-'+kind,['/usr/bin/python3',str(OLD/'read-pcb.py'),str(f),str(snap)],out/kind,env=ENV,artifacts=[('snapshot.json',snap),('probe.kicad_pcb',f)])
print('A + actual spacing enforcement + actual PCB via fixtures ready')
