from common import *
import re,copy,shutil
sys.path.insert(0,str(RT/'geometry/lib/python3.12/site-packages'))
import sexpdata as sx
def dsn_ast(s):return sx.loads(s.replace('(string_quote \")','(string_quote "quote")'))
expected={'main2':'46676e57e9618940a33c5e298244e97aaec61498a87aa7c58a264e444fc71e20','main4':'33f079d07bfb2dad9a76dce0667a1fd1371c94406df16f36ae17fe559d74af01'}
sources={'main4':E/'source-117/inputs/main','smoke4':E/'source-117/amendment-01/inputs/smoke-02','main2':R/'hardware/kicad/qualification/issue-115-kicad-routing-tools-escalation-off/evidence/inputs/main','smoke2':R/'hardware/kicad/qualification/issue-115-kicad-routing-tools-escalation-off/evidence/inputs/smoke'}
rows={}
for label,source in sources.items():
 w=E/'inputs'/label;w.mkdir(parents=True,exist_ok=True)
 pcb=(source/'main.kicad_pcb').read_text();dsn=(source/'corrected.dsn').read_text();pro=json.loads((source/'main.kicad_pro').read_text())
 if label in expected:assert sha(source/'main.kicad_pcb')==expected[label]
 if label=='main4':assert sha(source/'corrected.dsn')=='661d00c7d99adc270314a1a4940e64838999b948471f4d36a17aa9eac4d5e7f2'
 for ext in ['kicad_pcb','kicad_pro']:
  shutil.copyfile(source/f'main.{ext}',w/f'original.{ext}')
 shutil.copyfile(source/'corrected.dsn',w/'original.dsn')
 # Only zone copper rule values change in native PCB. Geometry/cache stays byte-identical.
 relaxed=re.sub(r'\((clearance|min_thickness|thermal_gap|thermal_bridge_width) 0\.2\)',r'(\1 0.127)',pcb)
 assert sx.loads(re.sub(r'\((clearance|min_thickness|thermal_gap|thermal_bridge_width) 0\.127\)',r'(\1 0.2)',relaxed))==sx.loads(pcb)
 (w/'main.kicad_pcb').write_text(relaxed)
 newpro=copy.deepcopy(pro);rules=newpro['board']['design_settings']['rules']
 rules['min_clearance']=rules['min_track_width']=.127
 for nc in newpro['net_settings']['classes']:
  for key in ['clearance','track_width','diff_pair_width','diff_pair_gap','diff_pair_via_gap']:nc[key]=.127
  nc['via_diameter']=.6;nc['via_drill']=.3
 pdiff=delta(pro,newpro)
 assert all(x['path'] in ['/board/design_settings/rules/min_clearance','/board/design_settings/rules/min_track_width','/net_settings/classes'] for x in pdiff)
 save(w/'main.kicad_pro',newpro)
 # Explicit DSN rule-only substitution, including all netclass rules. No wire/path widths changed.
 relaxed_dsn=re.sub(r'\((width|clearance) 200(?=[\s)])',r'(\1 127',dsn)
 assert re.sub(r'\((width|clearance) 127(?=[\s)])',r'(\1 200',relaxed_dsn)==dsn
 assert dsn_ast(re.sub(r'\((width|clearance) 127(?=[\s)])',r'(\1 200',relaxed_dsn))==dsn_ast(dsn)
 (w/'corrected.dsn').write_text(relaxed_dsn)
 def walk(n,path=()):
  if isinstance(n,list):
   if n and str(n[0])=='rule':
    for v in n[1:]:
     if isinstance(v,list) and str(v[0]) in ['width','clearance']:assert v[1]==127,(label,v)
   for i,v in enumerate(n):walk(v,path+(i,))
 walk(dsn_ast(relaxed_dsn))
 rows[label]=dict(source=str(source.relative_to(R)),original_pcb_sha256=sha(source/'main.kicad_pcb'),original_dsn_sha256=sha(source/'corrected.dsn'),relaxed_pcb_sha256=sha(w/'main.kicad_pcb'),relaxed_dsn_sha256=sha(w/'corrected.dsn'),relaxed_project_sha256=sha(w/'main.kicad_pro'),native_rule_reversal_full_AST_equal=True,DSN_rule_reversal_full_AST_equal=True,project_diff=pdiff,native_rule_changes=re.findall(r'\((?:clearance|min_thickness|thermal_gap|thermal_bridge_width) 0\.127\)',relaxed),dsn_rule_changes=re.findall(r'\((?:width|clearance) 127',relaxed_dsn),existing_copper_widths_unchanged=True,via_mm=[.6,.3])
save(E/'equivalence-gate.json',dict(utc=utc(),pass_equivalence=True,inputs=rows,scope='All native and DSN AST nodes restored by reverting only listed rule values; project full recursive diff; geometry, parts, net, original routes, via definitions, layer and plane roles unchanged. DSN explicit rule edit instead of re-export.'))
print('EQUIVALENCE PASS',utc())
