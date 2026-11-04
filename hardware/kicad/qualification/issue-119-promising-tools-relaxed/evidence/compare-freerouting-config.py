from common import *
old=json.loads((R/'hardware/kicad/qualification/issue-95-freerouting-v250-run2/evidence/processes/run-2/record.json').read_text())['command']
new=json.loads((E/'processes/main4-free-route/record.json').read_text())['argv']
def norm(args):
 out=[]
 for i,arg in enumerate(args):
  if i==0:arg='<JAVA>'
  elif arg.startswith('-Djava.io.tmpdir='):arg='-Djava.io.tmpdir=<TMP>'
  elif arg.startswith('--user_data_path='):arg='--user_data_path=<USER>'
  elif args[i-1] in ['-jar','-de','-do']:arg={'-jar':'<JAR>','-de':'<INPUT>','-do':'<OUTPUT>'}[args[i-1]]
  out.append(arg)
 return out
assert norm(old)==norm(new),(norm(old),norm(new))
save(E/'configuration/freerouting-vs-95.json',dict(utc=utc(),all_algorithm_flags_identical=True,normalized_command=norm(new),old_raw_command=old,new_raw_command=new,only_path_differences=True,source95_record_sha256=sha(R/'hardware/kicad/qualification/issue-95-freerouting-v250-run2/evidence/processes/run-2/record.json'),timing='Post-run verification of the predeclared #95 argv; no settings changed or rerun.'))
