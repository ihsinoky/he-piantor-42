"""One disposable fixture: objects and KiCad saves only, no format writer."""
import json
import sys
from pathlib import Path
import pcbnew as p
ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/'fixture.json').read_text())

def v(xy): return p.VECTOR2I(*(p.FromMM(x) for x in xy))

def settings(board, project):
    manager=p.GetSettingsManager()
    # A nonexistent project returns False but establishes a new project object.
    print('LoadProject-existing', manager.LoadProject(str(project)))
    board.SetProject(manager.Prj())
    s=board.GetDesignSettings();r=C['rules']
    s.SetBoardThickness(p.FromMM(C['board']['thickness_mm']))
    board.SetCopperLayerCount(C['board']['copper_layers'])
    s.m_MinClearance=p.FromMM(r['min_clearance_mm'])
    s.m_TrackMinWidth=p.FromMM(r['min_track_width_mm'])
    s.m_CopperEdgeClearance=p.FromMM(r['copper_edge_clearance_mm'])
    n=s.m_NetSettings.GetDefaultNetclass()
    n.SetClearance(p.FromMM(r['default_clearance_mm']))
    n.SetTrackWidth(p.FromMM(r['default_track_width_mm']))
    n.SetViaDiameter(p.FromMM(r['via_diameter_mm']))
    n.SetViaDrill(p.FromMM(r['via_drill_mm']))
    return manager

def create(directory):
    directory.mkdir(exist_ok=False)
    b=p.BOARD();file=directory/'fixture.kicad_pcb'
    b.SetFileName(str(file));manager=settings(b,file.with_suffix('.kicad_pro'))
    nets={}
    for name in C['nets']:
        net=p.NETINFO_ITEM(b,name);b.Add(net);nets[name]=net
    spec=C['official']
    fp=p.FootprintLoad(str(ROOT/'library/Resistor_SMD.pretty'),spec['name'])
    assert fp is not None
    fp.SetFPID(p.LIB_ID(spec['library'],spec['name']))
    fp.SetReference(spec['reference']);fp.SetPosition(v(spec['position_mm']))
    fp.SetOrientationDegrees(spec['rotation_deg']);b.Add(fp)
    for pad in fp.Pads():
        pad.SetNet(nets[next(x['net'] for x in spec['pads'] if x['number']==pad.GetNumber())])
    spec=C['special'];fp=p.FOOTPRINT(b);fp.SetReference(spec['reference'])
    fp.SetAttributes(p.FP_SMD);b.Add(fp)
    pads=[]
    for x in spec['pads']:
        pad=p.PAD(fp);pad.SetNumber(x['number'])
        pad.SetShape(getattr(p,'PAD_SHAPE_'+x['shape']))
        pad.SetAttribute({'SMD':p.PAD_ATTRIB_SMD,'PTH':p.PAD_ATTRIB_PTH,'NPTH':p.PAD_ATTRIB_NPTH}[x['attribute']])
        pad.SetSize(v(x['size_mm']));pad.SetPosition(v(x['local_mm']))
        layers=p.LSET()
        for name in x['layers']:layers.AddLayer(b.GetLayerID(name))
        pad.SetLayerSet(layers)
        if x['shape']=='ROUNDRECT':pad.SetRoundRectRadiusRatio(x['roundrect_ratio'])
        if any(x['drill_mm']):
            pad.SetDrillSize(v(x['drill_mm']));pad.SetDrillShape(getattr(p,'PAD_DRILL_SHAPE_'+x['drill_shape']))
        if x['net']:pad.SetNet(nets[x['net']])
        fp.Add(pad);pads.append(pad)
    fp.SetPosition(v(spec['position_mm']));fp.SetOrientationDegrees(spec['rotation_deg'])
    for indices in [(0,1),(1,3)]:
        track=p.PCB_TRACK(b);track.SetStart(pads[indices[0]].GetPosition());track.SetEnd(pads[indices[1]].GetPosition())
        track.SetWidth(p.FromMM(.2));track.SetLayer(p.F_Cu);track.SetNet(nets['GND']);b.Add(track)
    corners=C['board']['outline_mm']
    for a,z in zip(corners,corners[1:]+corners[:1]):
        edge=p.PCB_SHAPE(b);edge.SetShape(p.SHAPE_T_SEGMENT);edge.SetStart(v(a));edge.SetEnd(v(z))
        edge.SetLayer(p.Edge_Cuts);edge.SetWidth(p.FromMM(C['board']['edge_width_mm']));b.Add(edge)
    assert p.SaveBoard(str(file),b)
    assert manager.SaveProject(str(file.with_suffix('.kicad_pro')))
    print('saved',file)

if __name__=='__main__': create(Path(sys.argv[1]).resolve())
