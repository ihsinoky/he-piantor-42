"""Issue #268 stage 0: baseline inspection of Matrix Rev.3 board (read-only)."""
import json, sys
import pcbnew

path = sys.argv[1]
b = pcbnew.LoadBoard(path)
out = {}
bb = b.GetBoardEdgesBoundingBox()
out['outline_bbox_mm'] = [bb.GetLeft()/1e6, bb.GetTop()/1e6, bb.GetRight()/1e6, bb.GetBottom()/1e6]
out['layers'] = b.GetCopperLayerCount()
out['footprints'] = len(list(b.GetFootprints()))
for fp in b.GetFootprints():
    if fp.GetReference() == 'J_WING':
        pos = fp.GetPosition()
        out['J_WING'] = dict(
            lib=str(fp.GetFPID().GetLibItemName()), layer=int(fp.GetLayer()),
            x=pos.x/1e6, y=pos.y/1e6, rot=fp.GetOrientationDegrees(),
            pads=[dict(n=p.GetNumber(), net=p.GetNetname(),
                       x=p.GetPosition().x/1e6, y=p.GetPosition().y/1e6,
                       sx=p.GetSize().x/1e6, sy=p.GetSize().y/1e6,
                       layer=int(p.GetLayer())) for p in fp.Pads()])
ds = b.GetDesignSettings()
out['min_track'] = ds.m_TrackMinWidth/1e6
out['min_clearance'] = ds.m_MinClearance/1e6
out['min_via_dia'] = ds.m_ViasMinSize/1e6
print(json.dumps(out, indent=1))
