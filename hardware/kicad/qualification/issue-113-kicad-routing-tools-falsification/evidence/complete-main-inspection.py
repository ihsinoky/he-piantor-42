"""Resolve historical library path and repeat DRC only; preserve the first DRC."""
import runpy,collections
from pathlib import Path
E=Path(__file__).resolve().parent;globals().update(runpy.run_path(str(E/'prepare-inputs.py')))
w=E/'inspection/main';lib=OLD/'library/Qualification.pretty'
(w/'fp-lib-table').write_text(f'(fp_lib_table (version 7) (lib (name "Qualification")(type "KiCad")(uri "{lib}")(options "")(descr "Original fixed qualification footprints")))\n')
save(E/'main-library-resolution.json',dict(reason='First independent DRC reported 49 lib_footprint_issues because the historical /workspaces path was unavailable. Register the unchanged historical Qualification.pretty at its actual path; no PCB/project/rule or routing changes.',original_table=str((OLD/'evidence/fp-lib-table').relative_to(R)),registered_path=str(lib),library_hashes={str(p.relative_to(R)):digest(p) for p in lib.rglob('*') if p.is_file()},original_drc='inspection/main/drc.json',final_drc='inspection/main/drc-with-library.json'))
assert run('main-independent-drc-with-library',[RT/'kicad/usr/bin/kicad-cli','pcb','drc','--format','json','--severity-all','-o',w/'drc-with-library.json',w/'main.kicad_pcb'])==0
drc=json.loads((w/'drc-with-library.json').read_text());assert not any(v['type']=='lib_footprint_issues' for v in drc['violations'])
p=E/'main-independent.json';a=json.loads(p.read_text());save(E/'main-independent-before-library.json',a)
a['measured_kicad_unconnected_items']=len(drc['unconnected_items']);a['independent_material_drc_count']=sum(v['type'] not in {'text_height','silk_overlap','silk_over_copper'} for v in drc['violations']);a['drc_type_counts']=dict(collections.Counter(v['type'] for v in drc['violations']));a['final_drc']='inspection/main/drc-with-library.json';a['library_configuration_repaired_without_board_change']=True
assert a['measured_kicad_unconnected_items']==5 and all(v is None for v in a['metrics'].values())
save(p,a)
print(json.dumps({k:v for k,v in a.items() if k!='board_diff'},indent=2))
