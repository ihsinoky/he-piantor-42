"""Snapshot maker in the audit-main.py (Rev.7/Rev.8) schema.
Usage: snapshot.py <board.kicad_pcb> <outdir>"""
import json, sys
from pathlib import Path
import pcbnew as p

src, outdir = Path(sys.argv[1]), Path(sys.argv[2])
outdir.mkdir(parents=True, exist_ok=True)
b = p.LoadBoard(str(src))
b.BuildConnectivity()
p.ZONE_FILLER(b).Fill(b.Zones())
b.BuildConnectivity()
pads = []
for f in b.GetFootprints():
    for a in f.Pads():
        pads.append(dict(ref=f.GetReference(), number=a.GetNumber(),
                         position=[p.ToMM(a.GetPosition().x), p.ToMM(a.GetPosition().y)],
                         size=[p.ToMM(a.GetSize().x), p.ToMM(a.GetSize().y)],
                         angle=f.GetOrientationDegrees(), net=a.GetNetname(),
                         attribute='SMD' if a.GetAttribute() == p.PAD_ATTRIB_SMD else 'PTH',
                         shape='rect', drill=[p.ToMM(a.GetDrillSize().x), p.ToMM(a.GetDrillSize().y)],
                         layers=[l for l in list(b.GetEnabledLayers().CuStack()) if a.IsOnLayer(l)],
                         uuid=a.m_Uuid.AsString()))
tracks = []
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        tracks.append(dict(kind='via', position=[p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)],
                           size=p.ToMM(t.GetWidth()), drill=p.ToMM(t.GetDrill()), net=t.GetNetname(),
                           layers=[l for l in list(b.GetEnabledLayers().CuStack()) if t.IsOnLayer(l)],
                           uuid=t.m_Uuid.AsString()))
    else:
        tracks.append(dict(kind='track', start=[p.ToMM(t.GetStart().x), p.ToMM(t.GetStart().y)],
                           end=[p.ToMM(t.GetEnd().x), p.ToMM(t.GetEnd().y)], width=p.ToMM(t.GetWidth()),
                           net=t.GetNetname(), layer=t.GetLayer(), uuid=t.m_Uuid.AsString()))
snap = dict(components=[], pads=pads, tracks=tracks, zones=[],
            layers=list(b.GetEnabledLayers().CuStack()), thickness=1.2, rules={}, default={}, edges=[])
(outdir / 'snapshot.json').write_text(json.dumps(snap, indent=1) + '\n')
(outdir / 'assessment.json').write_text(json.dumps({"pass_acceptance": False, "note": "Stage B extraction input only"}) + '\n')
import shutil
shutil.copy(src, outdir / 'main.kicad_pcb')
print("snapshot written:", outdir, len(pads), "pads", len(tracks), "tracks")
