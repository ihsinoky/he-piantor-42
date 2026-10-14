"""Independent KiCad public object snapshot; not used by authoring."""
import json
import sys
from pathlib import Path
import pcbnew as p
def xy(v):return [p.ToMM(v.x),p.ToMM(v.y)]
b=p.LoadBoard(sys.argv[1]);assert b is not None
manager=p.GetSettingsManager();manager.LoadProject(str(Path(sys.argv[1]).with_suffix('.kicad_pro')));b.SetProject(manager.Prj())
pads=[];components=[];tracks=[]
for f in b.GetFootprints():
    components.append(dict(ref=f.GetReference(),source_id=f.GetLibDescription(),value=f.GetValue(),position=xy(f.GetPosition()),angle=f.GetOrientationDegrees(),footprint=f.GetFPIDAsString()))
    for a in f.Pads():
        pads.append(dict(ref=f.GetReference(),number=a.GetNumber(),position=xy(a.GetPosition()),size=xy(a.GetSize()),angle=a.GetOrientationDegrees(),net=a.GetNetname(),attribute=a.GetAttribute(),shape=a.GetShape(),drill=xy(a.GetDrillSize()),layers=[l for l in [p.F_Cu,p.B_Cu] if a.IsOnLayer(l)],uuid=a.m_Uuid.AsString()))
for t in b.GetTracks():
    if isinstance(t,p.PCB_VIA):
        tracks.append(dict(kind='via',position=xy(t.GetPosition()),size=p.ToMM(t.GetWidth()),drill=p.ToMM(t.GetDrillValue()),net=t.GetNetname(),layers=[l for l in [p.F_Cu,p.B_Cu] if t.IsOnLayer(l)],uuid=t.m_Uuid.AsString()))
    else:
        assert isinstance(t,p.PCB_TRACK)
        tracks.append(dict(kind='track',start=xy(t.GetStart()),end=xy(t.GetEnd()),width=p.ToMM(t.GetWidth()),net=t.GetNetname(),layer=t.GetLayer(),uuid=t.m_Uuid.AsString()))
s=b.GetDesignSettings();nc=s.m_NetSettings.GetDefaultNetclass()
d=dict(components=components,pads=pads,tracks=tracks,zones=b.GetAreaCount(),layers=b.GetCopperLayerCount(),thickness=p.ToMM(s.GetBoardThickness()),rules={name:p.ToMM(getattr(s,name)) for name in ['m_MinClearance','m_HoleClearance','m_HoleToHoleMin','m_CopperEdgeClearance','m_TrackMinWidth']},default=dict(clearance=p.ToMM(nc.GetClearance()),width=p.ToMM(nc.GetTrackWidth()),via=p.ToMM(nc.GetViaDiameter()),drill=p.ToMM(nc.GetViaDrill())),edges=[dict(start=xy(x.GetStart()),end=xy(x.GetEnd()),width=p.ToMM(x.GetWidth())) for x in b.GetDrawings() if x.GetLayer()==p.Edge_Cuts])
Path(sys.argv[2]).write_text(json.dumps(d,indent=2)+'\n');print('public actual PCB snapshot saved')
