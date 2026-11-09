"""Preserve the Rev4 electrical contract; repair its review schematic's ERC metadata.
Only on-paper positions are snapped. PCB positions/rules remain byte-independent.
External VBUS/GND and the filtered buck rail V5V2 (fed through L1 from SW)
are explicitly flagged supply boundaries, never suppressed ERC rules.
"""
from common import *
import sexpdata as sx,copy,uuid
V=E.parent/'issue-196-main-rev4-phaseb';S=E/'schematic';S.mkdir(exist_ok=True)
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def child(n,t):return next(q for q in n if tag(q)==t)
a=sx.loads((V/'schematic/main.kicad_sch').read_text())
child(child(a,'title_block'),'title')[1]='Issue 221 Main Rev.5 / Fly / forced-PWM 5.2V'
libs=child(a,'lib_symbols'); shifts={};moved=[]
for lib in libs[1:]:
 if lib[1]=='Rev4:J4':
  lib[1]='Rev5:J4'
  next(q for q in lib if tag(q)=='property' and q[1]=='Value')[2]='781710004'

for inst in a[1:]:
 if tag(inst)!='symbol':continue
 ref=next(q[2] for q in inst if tag(q)=='property' and q[1]=='Reference')
 if ref=='J4':
  child(inst,'lib_id')[1]='Rev5:J4'
  for q in inst:
   if tag(q)=='property' and q[1]=='Value':q[2]='781710004'
   if tag(q)=='property' and q[1]=='Footprint':q[2]='Rev5:J4'
 at=child(inst,'at');x,y=at[1:3];dx=round(round(x/1.27)*1.27-x,6);dy=round(round(y/1.27)*1.27-y,6)
 lib=next(q for q in libs[1:] if q[1]==child(inst,'lib_id')[1])
 for sub in lib:
  if tag(sub)=='symbol':
   for pin in sub:
    if tag(pin)=='pin':
     px,py=child(pin,'at')[1:3];px=round(x+px,6);py=round(y-py,6)
     shifts[(px,py)]=(dx,dy);shifts[(round(px-7.62,6),py)]=(dx,dy)
 at[1]=round(x+dx,6);at[2]=round(y+dy,6)
 for q in inst:
  if tag(q)=='property':
   c=child(q,'at');c[1]=round(c[1]+dx,6);c[2]=round(c[2]+dy,6)
 moved.append(dict(ref=ref,paper_shift_mm=[dx,dy]))
for n in a[1:]:
 if tag(n)=='wire':
  pts=child(n,'pts');dx,dy=shifts[tuple(round(v,6) for v in pts[1][1:3])]
  for q in pts[1:]:q[1]=round(q[1]+dx,6);q[2]=round(q[2]+dy,6)
 if tag(n) in ['label','no_connect']:
  c=child(n,'at');dx,dy=shifts[tuple(round(v,6) for v in c[1:3])];c[1]=round(c[1]+dx,6);c[2]=round(c[2]+dy,6)
flag=sx.loads('(symbol "Rev5:PWR_FLAG" (power) (pin_names (offset 0)) (exclude_from_sim no) (in_bom no) (on_board no) (property "Reference" "#FLG" (at 0 2.54 0) (effects (font (size 1 1)))) (property "Value" "PWR_FLAG" (at 0 5.08 0) (effects (font (size 1 1)))) (symbol "PWR_FLAG_0_1" (polyline (pts (xy -1.27 0) (xy 0 1.27) (xy 1.27 0) (xy -1.27 0)) (stroke (width 0.254) (type default)) (fill (type none)))) (symbol "PWR_FLAG_1_1" (pin power_out line (at 0 0 90) (length 0) (name "pwr" (effects (font (size 1 1)))) (number "1" (effects (font (size 1 1)))))))')
libs.append(flag);root=child(a,'uuid')[1]
for i,net in enumerate(['VBUS','GND','V5V2']):
 x=25.4;y=25.4+i*12.7;ref='#FLG0'+str(i+1);uid=str(uuid.uuid4())
 n=sx.loads(f'(symbol (lib_id "Rev5:PWR_FLAG") (at {x} {y} 0) (unit 1) (exclude_from_sim no) (in_bom no) (on_board no) (dnp no) (uuid "{uid}") (property "Reference" "{ref}" (at {x} {y-2.54} 0) (effects (font (size 1 1)))) (property "Value" "PWR_FLAG" (at {x} {y-5.08} 0) (effects (font (size 1 1)))) (instances (project "main" (path "/{root}" (reference "{ref}") (unit 1)))))')
 a.append(n);a.append(sx.loads(f'(label "{net}" (at {x} {y} 0) (effects (font (size 1 1)) (justify left bottom)) (uuid "{uuid.uuid4()}"))'))
(S/'main.kicad_sch').write_text(sx.dumps(a)+'\n')
libcopy=copy.deepcopy(libs)
for n in libcopy[1:]:n[1]=n[1].split(':')[1]
(S/'review.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '+ ' '.join(sx.dumps(n) for n in libcopy[1:])+')\n')
(S/'sym-lib-table').write_text('(sym_lib_table (version 7) '+''.join(f'(lib (name "{name}")(type "KiCad")(uri "${{KIPRJMOD}}/review.kicad_sym")(options "")(descr "Frozen review symbols"))' for name in ['Rev4','Rev5'])+')\n')
(S/'fp-lib-table').write_text('(fp_lib_table (version 7)(lib (name "Rev4")(type "KiCad")(uri "${KIPRJMOD}/../../issue-196-main-rev4-phaseb/Rev4.pretty")(options "")(descr ""))(lib (name "Rev5")(type "KiCad")(uri "${KIPRJMOD}/../Rev5.pretty")(options "")(descr "")))\n')
# Same default ERC checks; no exclusions or severity downgrades.
(S/'main.kicad_pro').write_text('{}\n')
save(E/'schematic-repairs.json',dict(paper_shifts=moved,power_boundary_flags=['VBUS','GND','V5V2'],corrected_pin_type={},net_changes=0,board_changes=0,ERC_rules_disabled=[]))
