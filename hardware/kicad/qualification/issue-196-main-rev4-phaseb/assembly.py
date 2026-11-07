"""BOM/CPL from qualified final geometry, original ledger and explicit MPN choices."""
from common import *
import pcbnew as p,csv,io,collections
w=E/'inspection/final';assert json.loads((w/'assessment.json').read_text())['pass_acceptance']
b=p.LoadBoard(str(w/'main.kicad_pcb'));fps={f.GetReference():f for f in b.GetFootprints()}
old=list(csv.DictReader((E.parent/'issue-185-main-rev3/main-bom.csv').open()));ledger={x['ref']:x for x in old}
ledger['J4']=dict(part_number='SM04B-SRSS-TB(LF)(SN)',lcsc='C160404')
rows=[]
for ref,f in sorted(fps.items()):
 if ref.startswith('H'):continue
 mpn,code=(ledger[ref]['part_number'],ledger[ref]['lcsc'])
 rows.append(dict(ref=ref,value=f.GetValue(),footprint='Rev4:'+ref,part_number=mpn,lcsc=code,assembled=not ref.startswith('TP'),source='LCSC C160404 exact JST MPN https://www.lcsc.com/product-detail/C160404.html; UDB C3 footprint' if ref=='J4' else 'Inherited amended Issue185 ledger (including C25 C1525); sourcing confirmation pending',procurement_confirmed=False))
assert len(rows)==59
assembled=[x for x in rows if x['assembled']];assert len(assembled)==55
out=E/'manufacturing';out.mkdir(exist_ok=True)
def csvwrite(path,fields,items):
 s=io.StringIO();w=csv.DictWriter(s,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(items);path.write_text(s.getvalue())
csvwrite(E/'main-bom.csv',list(rows[0]),rows)
csvwrite(out/'BOM.csv',['Comment','Designator','Footprint','LCSC Part #'],[dict(zip(['Comment','Designator','Footprint','LCSC Part #'],[x['part_number'],x['ref'],x['footprint'],x['lcsc']])) for x in assembled])
cpl=[]
for row in assembled:
 f=fps[row['ref']];pos=f.GetPosition();cpl.append({'Designator':row['ref'],'Mid X':f'{p.ToMM(pos.x)-62.107317799:.6f}mm','Mid Y':f'{137.9-p.ToMM(pos.y):.6f}mm','Layer':'top','Rotation':f'{f.GetOrientationDegrees():.6f}'})
csvwrite(out/'CPL.csv',list(cpl[0]),cpl)
save(E/'assembly-review.json',dict(utc=now(),source_sha256=digest(w/'main.kicad_pcb'),ledger_rows=59,assembled_parts=55,bare_testpads_excluded=4,mounting_holes_excluded=3,CPL_origin_absolute_xy_mm=[62.107317799,137.9],CPL_formula='X=KiCadX-62.107317799; Y=137.9-KiCadY; native angle, top side',J4_LCSC='C160404',J4_source='https://www.lcsc.com/product-detail/C160404.html',parts_pending=[x['ref'] for x in assembled if not x['lcsc']],manufacturer_acceptance=False))
print('BOM/CPL:',len(rows),'electrical;',len(assembled),'assembled')
