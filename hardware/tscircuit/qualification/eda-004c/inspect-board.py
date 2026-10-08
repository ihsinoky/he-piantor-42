"""Read-only standalone KiCad object extraction, no router connectivity claims."""
import pcbnew as p
import json,sys

def xy(v):return [p.ToMM(v.x),p.ToMM(v.y)]
b=p.LoadBoard(sys.argv[1])
result={'version':p.GetBuildVersion(),'thickness_mm':p.ToMM(b.GetDesignSettings().GetBoardThickness()),'copper_layers':b.GetCopperLayerCount(),'components':[],'pads':[],'tracks':[],'outline':[]}
for f in b.GetFootprints():
 result['components'].append({'ref':f.GetReference(),'value':f.GetValue(),'position':xy(f.GetPosition()),'rotation':f.GetOrientationDegrees(),'layer':b.GetLayerName(f.GetLayer())})
 for a in f.Pads():
  result['pads'].append({'ref':f.GetReference(),'number':a.GetNumber(),'net':a.GetNetname(),'position':xy(a.GetPosition()),'rotation':a.GetOrientationDegrees(),'size':xy(a.GetSize()),'drill':xy(a.GetDrillSize()),'drill_shape':int(a.GetDrillShape()),'shape':int(a.GetShape()),'attribute':int(a.GetAttribute()),'layers':[b.GetLayerName(i) for i in a.GetLayerSet().Seq()]})
for a in b.GetTracks():
 result['tracks'].append({'kind':a.GetClass(),'net':a.GetNetname(),'start':xy(a.GetStart()),'end':xy(a.GetEnd()),'width':p.ToMM(a.GetWidth()),'layer':b.GetLayerName(a.GetLayer())})
for a in b.GetDrawings():
 if a.GetLayer()==p.Edge_Cuts:
  result['outline'].append({'shape':int(a.GetShape()),'start':xy(a.GetStart()),'end':xy(a.GetEnd())})
result['zones']=b.GetAreaCount()
result['constants']={k:int(getattr(p,k)) for k in ['PAD_SHAPE_RECT','PAD_SHAPE_OVAL','PAD_SHAPE_CIRCLE','PAD_ATTRIB_PTH','PAD_ATTRIB_SMD','PAD_ATTRIB_NPTH','PAD_DRILL_SHAPE_CIRCLE','PAD_DRILL_SHAPE_OBLONG','SHAPE_T_SEGMENT']}
with open(sys.argv[2],'w') as f:json.dump(result,f,indent=2);f.write('\n')
print('read-only board inventory captured')
