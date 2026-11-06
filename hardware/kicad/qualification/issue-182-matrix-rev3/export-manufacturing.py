"""Faithful final-board CAM, and JLCPCB-format BOM/CPL with explicit body centroids."""
from common import *
import pcbnew as p,csv,io,collections,shutil
assert json.loads((E/'inspection/final/assessment.json').read_text())['pass_acceptance']
assert json.loads((E/'inspection/final/via-pad-audit.json').read_text())['pass_acceptance']
source=E/'runs/final/out.kicad_pcb';out=E/'manufacturing';out.mkdir(exist_ok=False)
board=E/'board';board.mkdir(exist_ok=False);active=board/'m1-matrix18.kicad_pcb';shutil.copyfile(source,active)
# Use the frozen design project for the deliverable, not router measurement metadata.
shutil.copyfile(E/'cell-inputs/final/main.kicad_pro',active.with_suffix('.kicad_pro'))
(board/'fp-lib-table').write_text('(fp_lib_table (version 7)(lib (name "Wing129")(type "KiCad")(uri "${KIPRJMOD}/../PCBA.pretty")(options "")(descr "M1 matrix PCB local library")))\n')
b=p.LoadBoard(str(active));fps={f.GetReference():f for f in b.GetFootprints()};spec=json.loads((SOURCE/'definition.json').read_text())
cli=environment()['KICAD_CLI'];fab=out/'gerber';paste=out/'paste';fab.mkdir();paste.mkdir()
run('manufacturing-final-drc',[cli,'pcb','drc','--format','json','--severity-all','--all-track-errors','--exit-code-violations','-o',out/'drc.json',active],timeout=600)
run('export-gerbers',[cli,'pcb','export','gerbers','--layers','F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts','--precision','6','--subtract-soldermask','-o',str(fab)+'/',active])
run('export-drills',[cli,'pcb','export','drill','--format','excellon','--drill-origin','absolute','--excellon-units','mm','--excellon-zeros-format','decimal','--excellon-oval-format','alternate','--excellon-separate-th','--generate-report','--report-path',out/'drill-report.txt','-o',str(fab)+'/',active])
run('export-paste',[cli,'pcb','export','gerbers','--layers','F.Paste,B.Paste','--precision','6','-o',str(paste)+'/',active])
codes={'hall':'C266128','mux':'C494728','capacitor':'C45000','connector':'C265384'}
packages={'hall':'SOT-23-3','mux':'TSSOP-16','capacitor':'0603','connector':'GH14_1.25mm_SMD_TopEntry'}
centroids={'hall':[0,0],'mux':[0,0],'capacitor':[0,0],'connector':[0,-2.325]}
def csvwrite(path,fields,rows):
 s=io.StringIO();w=csv.DictWriter(s,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows);path.write_text(s.getvalue())
groups=collections.defaultdict(list);cpl=[];ledger=[]
for c in sorted(spec['components'],key=lambda x:x['reference']):
 if c['kind']=='testpoint':continue
 ref=c['reference'];kind=c['kind'];f=fps[ref];assert f.GetOrientationDegrees()==0 and c['side']=='top'
 dx,dy=centroids[kind];x=p.ToMM(f.GetPosition().x)+dx;y=p.ToMM(f.GetPosition().y)-dy
 # Body centroid in lower-left board-origin coordinates, +Y up; all top CCW.
 row={'Designator':ref,'Mid X':f'{x-36:.6f}mm','Mid Y':f'{140-y:.6f}mm','Layer':'top','Rotation':'0.000000'}
 cpl.append(row);groups[(c['mpn'],packages[kind],codes[kind])].append(ref)
 q1=next(q for q in f.Pads() if q.GetNumber()=='1')
 ledger.append(dict(reference=ref,mpn=c['mpn'],lcsc=codes[kind],package=packages[kind],footprint_origin_kicad_mm=[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)],body_centroid_kicad_mm=[x,y],centroid_offset_definition_y_up_mm=[dx,dy],pin1_kicad_mm=[p.ToMM(q1.GetPosition().x),p.ToMM(q1.GetPosition().y)],rotation_ccw_deg=0,cpl=row))
bom=[dict(zip(['Comment','Designator','Footprint','LCSC Part #'],[mpn,','.join(refs),package,code])) for (mpn,package,code),refs in sorted(groups.items())]
csvwrite(out/'BOM.csv',['Comment','Designator','Footprint','LCSC Part #'],bom);csvwrite(out/'CPL.csv',['Designator','Mid X','Mid Y','Layer','Rotation'],cpl)
assert len(cpl)==43 and set(r['Designator'] for r in cpl)=={r for v in groups.values() for r in v}
assert len(bom)==4
save(E/'assembly-review.json',dict(utc=now(),source_sha256=digest(active),assembled_components=43,grouped_bom_rows=4,quantities_by_kind={'hall':18,'mux':3,'capacitor':21,'connector':1},testpads_excluded=18,NPTH_excluded=4,centroid_origin_kicad_mm=[36,140],formula='CPL X=KiCad body centroid X-36; CPL Y=140-KiCad body centroid Y; millimetres; top; CCW degrees',GH14_body_offset_y_up_mm=[0,-2.325],GH14_body_offset_source='hardware/tscircuit/src/qualification/JstGh14.tsx; approved KRD-32980-5 R0 drawing, body rectangle centre (0,-2.325), signal row origin (0,0)',rotation_basis='All footprints 0 degrees; native top-view pad maps and pin1 dots in assembly drawing. Manufacturer library rotations and centroid alignment must be reviewed against the drawing before eventual release.',manufacturer_preview_approved=False,procurement_confirmed=False,parts=ledger))
# Native inventory used for independent CAM readback.
xy=lambda v:[p.ToMM(v.x),p.ToMM(v.y)]
tracks=[];vias=[];pads=[];edges=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):vias.append(dict(pos=xy(t.GetPosition()),diameter_mm=p.ToMM(t.GetWidth(p.F_Cu)),drill_mm=p.ToMM(t.GetDrillValue()),tented_front=t.IsTented(p.F_Mask),tented_back=t.IsTented(p.B_Mask)))
 else:tracks.append(dict(start=xy(t.GetStart()),end=xy(t.GetEnd()),width_mm=p.ToMM(t.GetWidth()),net=t.GetNetname(),layer=b.GetLayerName(t.GetLayer())))
for f in b.GetFootprints():
 for q in f.Pads():pads.append(dict(ref=f.GetReference(),number=q.GetNumber(),pos=xy(q.GetPosition()),size=xy(q.GetSize()),drill=xy(q.GetDrillSize()),angle_deg=q.GetOrientationDegrees(),attribute=int(q.GetAttribute()),shape=int(q.GetShape()),layers=[b.GetLayerName(i) for i in q.GetLayerSet().Seq()]))
for g in b.GetDrawings():
 if g.GetLayer()==p.Edge_Cuts:edges.append(dict(start=xy(g.GetStart()),end=xy(g.GetEnd()),width_mm=p.ToMM(g.GetWidth())))
save(out/'native-inventory.json',dict(source_sha256=digest(active),tracks=tracks,vias=vias,pads=pads,edges=edges,npth=[q for q in pads if q['attribute']==int(p.PAD_ATTRIB_NPTH)],smd_pad_count=sum(q['attribute']==int(p.PAD_ATTRIB_SMD) for q in pads),outline_bounds_mm=[36,60,164,140]))
assert digest(active)==digest(source)
save(E/'export-provenance.json',dict(utc=now(),qualified_source_sha256=digest(source),delivered_board_sha256=digest(active),source_design_project_sha256=digest(active.with_suffix('.kicad_pro')),no_copper_changes=True,gerber_origin='KiCad absolute; mm; 4.6 precision',drill_origin='KiCad absolute; mm; decimal 0.001mm quantization',CPL_origin='Lower left of board (KiCad36,140); +Y up; explicit connector body centroid offset',paste_policy='43 mounted parts only; 18 bare TPs no paste; bottom paste empty',order_or_charge=False))
print('Manufacturing export + JLC BOM/CPL:',len(cpl),'parts')
