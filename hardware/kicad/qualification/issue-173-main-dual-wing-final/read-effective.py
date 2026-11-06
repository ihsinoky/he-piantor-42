"""Read official resolver state, then abort BEFORE net selection/routing; no source edits."""
import sys,runpy,json,datetime,dataclasses,inspect
from pathlib import Path
out,input_pcb,*options=sys.argv[1:];stage=Path(input_pcb).parent.name;policy='off';E=Path(__file__).resolve().parent;R=Path.cwd();tool=R/'.issue155-runtime/KiCadRoutingTools';route=tool/'py_router/route.py'
sys.path[:0]=[str(tool/'py_router'),str(tool)]
def norm(x):
 if x is None or isinstance(x,(str,int,float,bool)):return x
 if isinstance(x,dict):return {str(k):norm(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [norm(v) for v in x]
 if isinstance(x,(set,frozenset)):return sorted([norm(v) for v in x],key=str)
 if dataclasses.is_dataclass(x):return norm(dataclasses.asdict(x))
 if hasattr(x,'__dict__'):return norm(vars(x))
 raise TypeError(type(x))
stopline=next(i for i,s in enumerate(route.read_text().splitlines(),1) if s=='    net_ids = resolve_net_ids(pcb_data, net_names)')
entry={};cli={}
class StopReadback(BaseException):pass
def trace(f,event,arg):
 if f.f_code.co_filename==str(route) and f.f_code.co_name=='batch_route':
  if event=='call':
   entry.update({k:norm(v) for k,v in f.f_locals.items()});cli.update(norm(vars(f.f_back.f_locals['args'])))
  if event=='line' and f.f_lineno==stopline:
   import fab_tiers,env_knobs,routing_defaults
   data=dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),stage=stage,policy=policy,stop_before_line=stopline,routing_started=False,cli_namespace=cli,batch_route_bound_parameters=entry,grid_route_config=norm(f.f_locals['config']),native_keepouts=norm(f.f_locals['pcb_data'].board_info.keepouts),fab_tier=norm(fab_tiers.get_default_fab_tier()),escalation_policy=norm(fab_tiers.get_escalation_policy()),routing_defaults={k:norm(v) for k,v in vars(routing_defaults).items() if k.isupper()},environment_knobs={k:norm(v) for k,v in vars(env_knobs).items() if k.isupper() and not k.startswith('_')})
   Path(out).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n');raise StopReadback()
 return trace
sys.argv=[str(route),input_pcb,str(E/'readback-never-written.kicad_pcb')]+options
sys.settrace(trace)
try:runpy.run_path(str(route),run_name='__main__')
except StopReadback:pass
finally:sys.settrace(None)
assert Path(out).exists();assert not (E/'readback-never-written.kicad_pcb').exists()
