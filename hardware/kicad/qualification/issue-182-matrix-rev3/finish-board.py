"""Remove the redundant B.Cu tail of the replaced WING_EN via; requalify.
All nonrouting nodes are exactly the Rev.2 source; no rules are changed.
"""
from common import *
import sexpdata as sx,shutil,sys
src=E/'runs/LOCAL-06/out.kicad_pcb';w=E/'runs/final';w.mkdir(exist_ok=False)
a=sx.loads(src.read_text());uid='efba21a4-bac2-4354-9d09-0f596ce8c965'
def field(n,k):return next(x[1:] for x in n if isinstance(x,list) and x and str(x[0])==k)
removed=[n for n in a[1:] if isinstance(n,list) and n and str(n[0])=='segment' and field(n,'uuid')==[uid]]
assert len(removed)==1
assert field(removed[0],'start')==[80.225,120.375] and field(removed[0],'end')==[79.075,120.375] and field(removed[0],'width')==[.1] and field(removed[0],'layer')==['B.Cu']
a=[a[0]]+[n for n in a[1:] if n not in removed]
(w/'out.kicad_pcb').write_text(sx.dumps(a)+'\n');shutil.copyfile(E/'runs/LOCAL-06/out.kicad_pro',w/'out.kicad_pro');shutil.copytree(E/'cell-inputs/GLOBAL-02',E/'cell-inputs/final')
save(E/'final-cleanup.json',dict(utc=now(),source_sha256=digest(src),output_sha256=digest(w/'out.kicad_pcb'),removed_segments=[sx.dumps(n) for n in removed],reason='After relocation, the via connects the onward B.Cu track at (80.225,120.375) directly. The old 1.15mm tail to the removed in-pad via is redundant; full independent requalification follows.',no_rule_changes=True,no_nonrouting_changes=True))
run('final-inspect',['/usr/bin/python3',E/'inspect-cell.py','final','m1-matrix18-16-17mm','KRT'],timeout=600)
run('final-via-audit',['/usr/bin/python3',E/'audit-via-pads.py',w/'out.kicad_pcb',E/'inspection/final'],timeout=120)
run('final-physical-audit',['/usr/bin/python3',E/'physical-audit.py','final'],timeout=120)
a=json.loads((E/'inspection/final/assessment.json').read_text());v=json.loads((E/'inspection/final/via-pad-audit.json').read_text())
assert a['pass_acceptance'] and v['pass_acceptance'],(a,v['minimum_gap_mm'])
print('Final board qualified, all four metrics zero; via pad minimum',v['minimum_gap_mm'])
