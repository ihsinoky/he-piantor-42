"""Reduce isolated observation snapshots to selected lineage candidates and hypotheses."""
import gzip
import hashlib
import json
import math
import sys
from pathlib import Path
from analyze import distance_point_segment
HERE=Path(__file__).resolve().parent
CAP=Path(sys.argv[1])
SOURCE=Path(sys.argv[2])
def read(p):return json.loads(p.read_text())
def write(name,data):(HERE/'evidence'/name).write_text(json.dumps(data,indent=2)+'\n')
sig=read(HERE/'evidence/signature-population.json')['records']
selected=[r for r in sig if r['record_id'] in ['R039','R044','R055']]
phases=['highDensityRouteSolver','highDensityForceImproveSolver','highDensityRepairSolver','highDensityStitchSolver','traceSimplificationSolver','traceWidthSolver','globalDrcForceImproveSolver','pipeline9JointDrcRepairSolver','effortCleanupSolver','lengthMatchingPostProcessingSolver']
observations=[]
for phase in phases:
    d=read(CAP/(phase+'.json'))
    routes=next((d[k] for k in ['output','simplifiedHdRoutes','mergedHdRoutes','routes','hdRoutes'] if isinstance(d.get(k),list)),None)
    if isinstance(d.get('output'),dict):routes=d['output'].get('hdRoutes')
    assert routes is not None,phase
    for rec in selected:
        owners=[r for r in routes if r.get('connectionName')==rec['via_owner_pcb_trace_id'].removesuffix('_0')]
        traces=[r for r in routes if r.get('connectionName')==rec['pcb_trace_id'].removesuffix('_0')]
        candidates=[(r,v) for r in owners for v in r.get('vias',[])]
        assert candidates and traces,(phase,rec['record_id'])
        owner,via=min(candidates,key=lambda rv:math.dist([rv[1]['x'],rv[1]['y']],rec['via_center_mm']))
        center=[via['x'],via['y']]; z=0 if rec['layer']=='top' else 1
        segs=[(t,a,b) for t in traces for a,b in zip(t['route'],t['route'][1:]) if a['z']==b['z']==z]
        def gap(seg):
            t,a,b=seg
            return distance_point_segment(center,[a['x'],a['y']],[b['x'],b['y']])-owner['viaDiameter']/2-(a.get('traceThickness',t['traceThickness'])/2)
        trace,a,b=min(segs,key=gap)
        g=gap((trace,a,b))
        observations.append(dict(phase=phase,record_id=rec['record_id'],via_center_mm=center,via_diameter_mm=owner['viaDiameter'],via_radius_mm=owner['viaDiameter']/2,
            trace_a_mm=[a['x'],a['y']],trace_b_mm=[b['x'],b['y']],trace_width_mm=a.get('traceThickness',trace['traceThickness']),layer=rec['layer'],
            gap_mm=g,violates_020=g<.2,near_signature=abs(g-.115)<=.0003,
            effective_target_radius_mm=None,position_delta_from_final_mm=math.dist(center,rec['via_center_mm'])))
new=read(CAP/'circuit.json')
old=json.loads(gzip.decompress((HERE.parent/'eda-003c/evidence/raw/latest-main.circuit.json.gz').read_bytes()))
ids={x.get('pcb_via_id',x.get('pcb_trace_id')):x for x in new if x['type'] in ['pcb_via','pcb_trace']}
selected_comparison=[]
for rec in sig:
    v=ids[rec['via_id']];t=ids[rec['pcb_trace_id']];center=[v['x'],v['y']]
    segs=[(a,b) for a,b in zip(t['route'],t['route'][1:]) if a['route_type']==b['route_type']=='wire' and a['layer']==b['layer']==rec['layer']]
    gap=min(distance_point_segment(center,[a['x'],a['y']],[b['x'],b['y']])-v['outer_diameter']/2-a['width']/2 for a,b in segs)
    delta=gap-rec['material_spacing_mm'];assert abs(delta)<1e-10
    selected_comparison.append(dict(record_id=rec['record_id'],captured_gap_mm=gap,accepted_gap_delta_mm=delta,via_position_delta_mm=math.dist(center,rec['via_center_mm'])))
input_srj=read(CAP/'input.json')
board=next(x for x in old if x['type']=='pcb_board')
source_files={
 'local_projection':'deps/node_modules/high-density-repair01/lib/HighDensityForceImproveSolver.ts',
 'global_projection':'deps/node_modules/high-density-repair03/lib/solvers/GlobalDrcForceImproveSolver/solverHelpers.ts',
 'global_config':'deps/node_modules/high-density-repair03/lib/solvers/GlobalDrcForceImproveSolver/solverConfig.ts',
 'global_preset':'deps/node_modules/high-density-repair03/lib/solvers/GlobalDrcForceImproveSolver/drcPresets.ts',
 'joint_projection':'deps/node_modules/@tscircuit/repair04/node_modules/high-density-repair03/lib/solvers/GlobalDrcForceImproveSolver/solverHelpers.ts',
 'pipeline':'lib/autorouter-pipelines/AutoroutingPipeline9_PreloadedTraceGraph/AutoroutingPipelineSolver9_PreloadedTraceGraph.ts'}
# Recover only the six directly inspected source-map modules, without network access.
assert str(SOURCE.resolve()).startswith('/tmp/'), 'Source extraction must be disposable'
stock_map=read(HERE.parent/'eda-003c/latest-stock/node_modules/@tscircuit/capacity-autorouter/dist/index.js.map')
content_by_path=dict(zip(stock_map['sources'],stock_map['sourcesContent']))
for value in source_files.values():
    map_path='../'+value.removeprefix('deps/')
    text=content_by_path[map_path]
    destination=SOURCE/value
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():assert destination.read_text()==text
    else:destination.write_text(text)
sources={key:{'source_map_path':value,'sha256':hashlib.sha256((SOURCE/value).read_bytes()).hexdigest()} for key,value in source_files.items()}
for key,v in sources.items():
    lines=(SOURCE/v['source_map_path']).read_text().splitlines()
    ranges={'local_projection':[(190,200),(1019,1047)],'global_projection':[(2580,2604)],'joint_projection':[(2548,2573)],'global_config':[(13,29)],'global_preset':[(1,9)],'pipeline':[(625,640),(645,680),(810,837),(840,869)]}[key]
    v['excerpts']=[{'start_line':a,'text':'\n'.join(lines[a-1:b])} for a,b in ranges]
write('pipeline-boundary.json',dict(method='One stock process; public Pipeline9 _step wrapper records outputs without changing arguments/results. Unchanged TSX transpiled with installed TypeScript to Node in /tmp; no dependency files edited.',
 capture_command='node capture-pipeline.mjs /tmp/eda003e-capture; node /tmp/eda003e-capture/run.mjs; python3 collect-boundary.py /tmp/eda003e-capture /tmp/eda003e-source',
 lineage_caveat='Before stitching, select closest via to accepted final position within exact owner connectionName, and closest same-layer segment within exact conflicting connectionName. This is a lineage candidate, not a proved one-to-one via ancestry across topology changes.',
 source_board_rule=board,solver_input_rules={k:v for k,v in input_srj.items() if not isinstance(v,(dict,list))},
 obstacle_creation={'input_obstacle_count':len(input_srj['obstacles']),'signature_vias_and_traces_present':False,'reason':'Selected vias/traces are generated; they are absent as finished copper in initial input.', 'via_location':None,'trace_geometry':None},
 obstacle_inflation={'stock_pipeline_margin_mm':.15,'evidence':'Pipeline9 highDensityRouteSolver receives cms.srj.defaultObstacleMargin ?? 0.15; captured original input omits defaultObstacleMargin. Effective per-case inflated geometry was not captured.','effective_radius_mm':None,'violation_present':None},
 observations=observations,selected_final_comparison=selected_comparison,
 conversion={'signature_spacing_preserved':True,'selected_via_copper_diameter_mm':.6,'selected_trace_width_mm':.2,'earliest_proven_final_signature_boundary':'pipeline9JointDrcRepairSolver output for three selected cases; R055 also has near-signature at earlier local force output', 'source':'Captured HD output and material Circuit JSON comparisons'},
 checker={'package':'@tscircuit/checks 0.0.241','function':'checkViaTraceClearance','rule':'min_trace_to_pad_edge_clearance','rule_mm':.2,'uses_copper_outer_radius':True},
 earliest_observed_invalid_boundary='highDensityRouteSolver output for three owner/trace lineage candidates; common causal boundary UNKNOWN',
 comparability={'entire_generated_json_byte_identical':False,'all_15_selected_final_minima_match_tolerance_mm':1e-10,'all_selected_via_centers_match_tolerance_mm':1e-10,'note':'Node observation run is not the accepted Bun qualification. It has changes outside the selected population; no board-wide determinism or new qualification claim.'},
 snapshot_hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(CAP.glob('*.json'))},sources=sources))
hypotheses=[
 ('repair_target','r_via + half_width + relaxed_trace_clearance + slack - r_via - half_width',{'r_via':.3,'half_width':.1,'relaxed_trace_clearance':.1,'slack':.015},.115,'STRONG_CORRELATION','high-density-repair01 projection and both high-density-repair03 pushViaSegmentPair versions explicitly use this target. Exact arithmetic; per-record callback attribution unproved.'),
 ('requested_rule','requested_clearance',{'requested_clearance':.2},.2,'REJECTED','Captured source and SRJ preserve .20; not the observed target.'),
 ('drill_instead_of_copper','requested_clearance + drill_radius - copper_radius',{'requested_clearance':.2,'drill_radius':.15,'copper_radius':.3},.05,'REJECTED','Does not match; stock checker uses outer copper radius.'),
 ('missing_half_width','requested_clearance - half_width',{'requested_clearance':.2,'half_width':.1},.1,'REJECTED','Missing half width alone does not explain .115.'),
 ('margin_as_center_budget','router_margin - half_width',{'router_margin':.15,'half_width':.1},.05,'REJECTED','Pipeline default obstacle margin is .15; no observed derivation of .115 from this alone.'),
 ('radius_only','copper_radius - drill_radius',{'copper_radius':.3,'drill_radius':.15},.15,'REJECTED','Actual annulus radial thickness is .15, not .115.'),
 ('rounding','rounding_only',{'local_rounding_step_mm':.001,'observed_rule_deficit_mm':.085},None,'REJECTED','Sub-mm rounding can perturb projection targets; .001 mm quantization cannot account for .085 mm deficit alone. Final coordinates are not on that grid.'),
 ('grid','grid_or_cell_size',{},None,'UNKNOWN','No common generating cell size measured. Broad repair spatial cell is a search accelerator, not proven spacing target.'),
 ('postprocess','unknown_postprocessing_offset',{},None,'UNKNOWN','Later stages mutate spacing; no common explicit .085 offset identified.')]
table=[]
for ident,formula,inputs,expected,classification,evidence in hypotheses:
    table.append(dict(id=ident,formula=formula,inputs=inputs,expected_result_mm=expected,classification=classification,source_code_evidence=evidence,
      per_record=[dict(record_id=r['record_id'],observed_mm=r['material_spacing_mm'],observed_delta_mm=None if expected is None else r['material_spacing_mm']-expected) for r in sig]))
write('numeric-derivation.json',dict(result='Exact stock target arithmetic .10 + .015 = .115; STRONG_CORRELATION to accepted population, not exact common-cause proof.',target_centerline_mm=.3+.1+.1+.015,valid_centerline_mm=.3+.1+.2,hypotheses=table,sources=sources))
print('Collected',len(observations),'boundary observations and',len(table),'hypotheses')
