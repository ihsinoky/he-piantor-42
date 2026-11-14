"""Align root-sheet net naming and document existing mechanical holes.
No electrical pin-to-pin connections or physical PCB objects are changed.
"""
from pathlib import Path
import re,uuid,gzip,json,hashlib
E=Path(__file__).resolve().parent;w=E/'main';archive=E/'continuation-start/main.kicad_sch.gz'
if not archive.exists():archive.write_bytes(gzip.compress((w/'main.kicad_sch').read_bytes(),mtime=0))
s=gzip.decompress(archive.read_bytes()).decode()
# Root-sheet locals export with a leading slash. Board uses global flat names.
s,count=re.subn(r'\(label "([^"]+)" \(at ([^)]*)\) \(effects',r'(global_label "\1" (shape input) (at \2) (effects',s)
def end(s,start):
 d=0;quoted=False;escape=False
 for i in range(start,len(s)):
  c=s[i]
  if quoted:
   if escape:escape=False
   elif c=='\\':escape=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c=='(':d+=1
  elif c==')':
   d-=1
   if not d:return i+1
 raise ValueError('unbalanced')
root_uuid=re.search(r'\(uuid "([^"]+)"',s)[1]
def uid(name):return str(uuid.uuid5(uuid.NAMESPACE_URL,'issue250:'+name))
lib=(w/'review.kicad_sym').read_text();symbols=[]
for i,ref in enumerate(['H1','H2','H3']):
 block=f'''(symbol "{ref}" (pin_names (offset 1.016)) (in_bom no) (on_board yes)
 (property "Reference" "H" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
 (property "Value" "NPTH_2.2mm" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
 (symbol "{ref}_0_1" (circle (center 0 0) (radius 1.1) (stroke (width .254) (type default)) (fill (type none)))))'''
 if '(symbol "'+ref+'"' not in lib:lib=lib.rstrip()[:-1]+'\n'+block+'\n)'
 symbols.append(block.replace('(symbol "'+ref+'"','(symbol "Rev4:'+ref+'"',1))
 x=100+i*30;y=800
 inst=f'''(symbol (lib_id "Rev4:{ref}") (at {x} {y} 0) (unit 1) (exclude_from_sim yes) (in_bom no) (on_board yes) (dnp no) (uuid "{uid(ref)}")
 (property "Reference" "{ref}" (at {x} {y-4} 0) (effects (font (size 1.27 1.27))))
 (property "Value" "NPTH_2.2mm" (at {x} {y+4} 0) (effects (font (size 1.27 1.27))))
 (property "Footprint" "Rev4:{ref}" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))
 (instances (project "main" (path "/{root_uuid}" (reference "{ref}") (unit 1)))))'''
 s=s.rstrip()[:-1]+'\n'+inst+'\n)'
i=s.index('(lib_symbols');j=end(s,i);s=s[:j-1]+'\n'+'\n'.join(symbols)+s[j-1:]
(w/'main.kicad_sch').write_text(s);(w/'review.kicad_sym').write_text(lib)
(w/'schematic-repair.json').write_text(json.dumps(dict(globalized_labels=count,added_mechanical_symbols=['H1','H2','H3'],electrical_pins_added=0,pcb_objects_changed=0,reason='Root sheet net-name prefixes and existing mechanical holes accounted for; pin connectivity must be verified with exported netlist'),indent=2)+'\n')
