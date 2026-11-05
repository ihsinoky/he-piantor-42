"""Read-only source, inherited-file and export-log audit; no CAD generation."""
from pathlib import Path
from collections import Counter
import gzip
import json
import os
import sys
import pcbnew
from common import R, E, T, SOURCE, now, digest, save

start = json.loads((E/'resume-start.json').read_text())
inherited_changes = [name for name, h in start['inherited_file_hashes'].items()
                     if not (R/name).is_file() or digest(R/name) != h]
assert not inherited_changes, inherited_changes
baseline = json.loads(gzip.decompress((E/'protected-start-hashes.json.gz').read_bytes()))
# Audit files outside the mutable per-issue runtime against the original run's snapshot.
protected = {name: h for name, h in baseline.items() if not name.startswith('.issue147-runtime/')}
changed = []
for name, h in protected.items():
    p=R/name
    if isinstance(h, dict):
        matches = p.is_symlink() and os.readlink(p) == h['symlink']
    else:
        matches = p.is_file() and digest(p) == h
    if not matches:
        changed.append(name)
# The host may replace .git metadata between runs. Report it separately from worktree data.
git_metadata_changes = [name for name in changed if name.startswith('.git/')]
worktree_changes = [name for name in changed if not name.startswith('.git/')]
assert not worktree_changes, worktree_changes

xy=lambda p:[p.x/1e6,p.y/1e6]
results=[]
for pitch in (16,17):
    d=E/f'{pitch}mm'
    pre=json.loads((d/'preflight.json').read_text())
    prov=json.loads((d/'export-provenance.json').read_text())
    source=R/pre['source']
    runtime=T/f'{pitch}mm'/f'wing-{pitch}mm.kicad_pcb'
    assert digest(source)==pre['sha256']==prov['source_sha256']==digest(runtime)
    project=R/prov['project_source']
    assert digest(project)==prov['project_sha256']==digest(runtime.with_suffix('.kicad_pro'))
    assessment_path=SOURCE/'inspection'/pre['cell']/'assessment.json'
    assert digest(assessment_path)==pre['source_assessment_sha256']
    assessment=json.loads(assessment_path.read_text())
    assert assessment['pass_acceptance'] and not any(assessment['metrics'].values())
    b=pcbnew.LoadBoard(str(source))
    ds=b.GetDesignSettings()
    assert b.GetCopperLayerCount()==pre['copper_layers']==2
    assert ds.GetBoardThickness()/1e6==pre['thickness_mm']==1.2
    assert ds.m_MinClearance/1e6==pre['min_clearance_mm']==0.1
    source_tracks=[]
    source_vias=[]
    for t in b.GetTracks():
        if isinstance(t,pcbnew.PCB_VIA):
            source_vias.append((tuple(xy(t.GetPosition())),t.GetWidth(pcbnew.F_Cu)/1e6,t.GetDrillValue()/1e6,
                                t.IsTented(pcbnew.F_Mask),t.IsTented(pcbnew.B_Mask)))
        else:
            source_tracks.append((tuple(xy(t.GetStart())),tuple(xy(t.GetEnd())),t.GetWidth()/1e6,
                                  t.GetNetname(),b.GetLayerName(t.GetLayer())))
    assert Counter(source_tracks)==Counter((tuple(t['start']),tuple(t['end']),t['width_mm'],t['net'],t['layer']) for t in pre['tracks'])
    assert Counter(source_vias)==Counter((tuple(v['pos']),v['diameter_mm'],v['drill_mm'],v['tented_front'],v['tented_back']) for v in pre['vias'])
    source_pads=[]
    for f in b.GetFootprints():
        for p in f.Pads():
            source_pads.append((f.GetReference(),p.GetNumber(),tuple(xy(p.GetPosition())),tuple(xy(p.GetSize())),
                                tuple(xy(p.GetDrillSize())),p.GetOrientationDegrees(),int(p.GetAttribute()),int(p.GetShape()),
                                tuple(b.GetLayerName(i) for i in p.GetLayerSet().Seq())))
    assert Counter(source_pads)==Counter((p['ref'],p['number'],tuple(p['pos']),tuple(p['size']),tuple(p['drill']),
                                         p['angle_deg'],p['attribute'],p['shape'],tuple(p['layers'])) for p in pre['pads'])
    edges=[(tuple(xy(g.GetStart())),tuple(xy(g.GetEnd())),g.GetWidth()/1e6)
           for g in b.GetDrawings() if g.GetLayer()==pcbnew.Edge_Cuts]
    assert Counter(edges)==Counter((tuple(e['start']),tuple(e['end']),e['width_mm']) for e in pre['edges'])
    assert all(t[2]==(0.3 if t[3] in ('GND','HALL_5V') else 0.1) for t in source_tracks)
    assert all(v[1:3]==(0.6,0.3) for v in source_vias)
    assert not any(g.GetLayer()==pcbnew.Edge_Cuts for f in b.GetFootprints() for g in f.GraphicalItems())
    drc=json.loads((d/'drc.json').read_text())
    assert not drc['violations'] and not drc['unconnected_items']
    processes=[]
    for kind in ('drc','gerbers','drill','paste-reference'):
        p=E/'processes'/f'{pitch}mm-{kind}'
        rec=json.loads((p/'record.json').read_text())
        assert rec['exit_code']==0 and runtime.as_posix() in rec['argv']
        assert rec['start_utc']>=pre['inspected_utc']
        processes.append(str(p.relative_to(E)))
    results.append(dict(pitch_mm=pitch,source_sha256=digest(source),runtime_sha256=digest(runtime),
                        project_sha256=digest(project),preflight_native_readback_match=True,
                        issue141_acceptance_metrics=assessment['metrics'],inherited_drc_zero=True,
                        export_process_records=processes,tracks=len(source_tracks),vias=len(source_vias),
                        inherited_export_reused=True,cad_regenerated_in_resumed_run=False))
verification=dict(utc=now(),resume_start_utc=start['utc'],
     inherited_files_audited=len(start['inherited_file_hashes']),inherited_file_changes=inherited_changes,
     original_run_protected_files_audited=len(protected),original_worktree_changes=worktree_changes,
     original_git_metadata_changes=git_metadata_changes,source_checks=results,
     original_git_metadata_note='Original .git is read-only and has not been written by this resumed run. Host refresh differences, if any, are metadata only.')
if '--write' in sys.argv:
    assert not (E/'resumption-verification.json').exists()
    save(E/'resumption-verification.json',verification)
print(json.dumps(dict(protected=len(protected),git_metadata_changes=git_metadata_changes,sources=results),indent=2))
