"""Read-only introspection of the installed public 9.0.9 binding."""
import json
import pcbnew as p
print(p.GetBuildVersion())
for obj in [p,p.BOARD(),p.BOARD().GetDesignSettings(),p.PAD,p.FOOTPRINT]:
 print(type(obj).__name__, [n for n in dir(obj) if any(t.lower() in n.lower() for t in ['project','netclass','clearance','settings','drill','load','save','thickness','layer','rules'])])
for name in ['BOARD','FootprintLoad','SaveBoard','LoadBoard','SETTINGS_MANAGER','GetSettingsManager','PROJECT','NETCLASS','NET_SETTINGS']:
 cls=getattr(p,name,None);print(name, getattr(cls,'__doc__',None))
 if cls:print([n for n in dir(cls) if not n.startswith('_')])
