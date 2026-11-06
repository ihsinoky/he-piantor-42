"""BOM/CPL from qualified final geometry, original ledger and explicit MPN choices."""
from common import *
import pcbnew as p,csv,io,collections
w=E/'inspection/final';assert json.loads((w/'assessment.json').read_text())['pass_acceptance']
b=p.LoadBoard(str(w/'main.kicad_pcb'));fps={f.GetReference():f for f in b.GetFootprints()}
old=list(csv.DictReader((R/'hardware/kicad/qualification/issue-124-main-bom-pcba/main-bom.csv').open()));ledger={x['ref']:x for x in old}
mpns={'C23':('GRM21BC81C226ME44L','C258782'),'C24':('GRM21BC81C226ME44L','C258782'),'C25':('GRM155R71E104KE14D','C77014'),'C26':('C3225X7R1C226K250AC',''),'C27':('C3225X7R1C226K250AC',''),'C28':('C3225X7R1C226K250AC',''),'R17':('TNPW060354K9BEEA',''),'R18':('TNPW060310K0BEEA','C844890'),'U6':('TPS63070RNMR','C109322'),'L1':('XFL4020-152MEC','C3033018')}
for ref,orig in [('R16','R6'),('R19','R6'),('J3','J2')]:mpns[ref]=(ledger[orig]['part_number'],ledger[orig]['lcsc'])
rows=[]
for ref,f in sorted(fps.items()):
 if ref.startswith('H'):continue
 mpn,code=(ledger[ref]['part_number'],ledger[ref]['lcsc']) if ref in ledger else mpns[ref]
 rows.append(dict(ref=ref,value=f.GetValue(),footprint='Stage175:'+ref,part_number=mpn,lcsc=code,assembled=not ref.startswith('TP'),source='Inherited #124 ledger' if ref in ledger else 'Issue175 retained exact MPN; Issue185 geometry; sourcing and manufacturer acceptance pending',procurement_confirmed=False))
assert len(rows)==62
assembled=[x for x in rows if x['assembled']];assert len(assembled)==58
out=E/'manufacturing';out.mkdir(exist_ok=True)
def csvwrite(path,fields,items):
 s=io.StringIO();w=csv.DictWriter(s,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(items);path.write_text(s.getvalue())
csvwrite(E/'main-bom.csv',list(rows[0]),rows)
csvwrite(out/'BOM.csv',['Comment','Designator','Footprint','LCSC Part #'],[dict(zip(['Comment','Designator','Footprint','LCSC Part #'],[x['part_number'],x['ref'],x['footprint'],x['lcsc']])) for x in assembled])
cpl=[]
for row in assembled:
 f=fps[row['ref']];pos=f.GetPosition();cpl.append({'Designator':row['ref'],'Mid X':f'{p.ToMM(pos.x)-76:.6f}mm','Mid Y':f'{122-p.ToMM(pos.y):.6f}mm','Layer':'top','Rotation':f'{f.GetOrientationDegrees():.6f}'})
csvwrite(out/'CPL.csv',list(cpl[0]),cpl)
j1=list(fps['J1'].Pads());assert collections.Counter(a.GetAttribute() for a in j1)=={p.PAD_ATTRIB_SMD:12,p.PAD_ATTRIB_PTH:4,p.PAD_ATTRIB_NPTH:2}
save(E/'assembly-review.json',dict(utc=now(),source_sha256=digest(w/'main.kicad_pcb'),ledger_rows=62,assembled_parts=58,bare_testpads_excluded=4,mounting_holes_excluded=4,added_refs=sorted(set(fps)-{x['ref'] for x in old}-{f'H{i}' for i in range(1,5)}),CPL_origin_absolute_xy_mm=[76,122],CPL_formula='X=KiCadX-76; Y=122-KiCadY; KiCad angle, top side',j1_process='12 SMD contacts + 4 PTH shell legs in same Economic PCBA; 2 NPTH mechanical; no separate manual assembly assumed',manufacturer_acceptance=False,parts_not_in_current_catalog=[x['ref'] for x in assembled if not x['lcsc']],pricing='Final account quote, stock, minimum/attrition, POFV surcharge, shell workflow, freight/tax not confirmed; no order or charge'))
print('BOM/CPL:',len(rows),'electrical references;',len(assembled),'assembled')
