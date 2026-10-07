"""Emit reviewed Stage 1 decision and cost evidence from classified geometry."""
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
E = HERE/'evidence'


def write(name, value):
    (E/name).write_text(json.dumps(value, indent=2)+'\n')


r = json.loads((E/'error-records-normalized.json').read_text())
c = json.loads((E/'physical-fault-clusters.json').read_text())
assert c['raw_error_record_count'] == 71 and c['independent_physical_fault_count'] == 54
families = [
    ('F1', 'pcb_placement_error', 'Same-net drill intrusion into SMD lands',
     'Same-net endpoint via placement does not preserve the stock no-via-in-pad condition.'),
    ('F2', 'pcb_pad_trace_clearance_error', 'MCU pad escape clearance',
     'Pad obstacle/rule treatment or subsequent escape geometry permits less than 0.20 mm clearance.'),
    ('F3', 'pcb_via_trace_clearance_error', 'Via annulus to unrelated-net routed copper',
     'Via clearance budgeting, interaction with other routed copper, or later geometry changes permit less than 0.20 mm clearance.'),
    ('F4', 'pcb_trace_error', 'Inter-route clearance, including attached-pad diagnostics',
     'Route-to-route spacing or later cleanup fails the 0.20 mm check. Some records share F2/F3 physical conflicts.'),
    ('F5', 'pcb_pad_pad_clearance_error', 'Via annulus beside an NC MCU land',
     'NC-pad obstacle clearance is insufficient; may share responsibility with F2/F3 rather than require a separate repair.'),
]
f = []
for fid, typ, name, hypothesis in families:
    ids = [e['record_id'] for e in r if e['type'] == typ]
    f.append(dict(family_id=fid, name=name, candidate_hypothesis=hypothesis, record_ids=ids,
                  raw_records=len(ids), cluster_ids=[x['cluster_id'] for x in c['clusters'] if set(ids)&set(x['record_ids'])],
                  responsibility_localized=False, confidence='LOW: geometry-informed candidate only; no internal-stage evidence'))
nominal = [e['record_id'] for e in r if e['type'] == 'pcb_via_trace_clearance_error' and abs(e['actual_minimum_spacing_mm']-.115)<.0003]
write('root-cause-families.json', dict(candidate_root_cause_family_count=5, proven_root_cause_family_count=0,
    interpretation='Five candidate responsibility hypotheses, not five proven independent causes. Diagnostic allocation is exclusive; physical clusters overlap families. May merge or split after localization.',
    families=f, recurring_signature=dict(record_ids=nominal, count=len(nominal), target_spacing_mm=.115, observation_band_mm=.0003,
        fraction_of_all_records_percent=100*len(nominal)/71,
        inference='Possible repeated clearance-budget signature. Numeric similarity alone does not prove the same fault or internal cause.'),
    combined_mcu_pad_and_trace_symptoms=dict(raw_records=36, percent=100*36/71,
        caution='50.7% is a combined symptom population, not a demonstrated single causal family. Includes separate inter-route conflict regions.')))
top = sorted(c['clusters'], key=lambda x: -x['raw_records_explained'])
write('cost-checkpoint.json', dict(raw_error_record_count=71, independent_physical_fault_count=54,
    count_caveat=c['count_interpretation'], independent_net_pair_lower_bound=37, candidate_root_cause_family_count=5,
    dominant_cluster=dict(cluster_id=top[0]['cluster_id'], raw_records=6, percent=100*6/71),
    top_three_clusters=dict(cluster_ids=[x['cluster_id'] for x in top[:3]], raw_records=14, percent=100*14/71),
    largest_candidate_symptom_family=dict(family_id='F3', raw_records=32, percent=100*32/71, causal_explanation_proven=False),
    stage_1='BROAD / DISTRIBUTED', representative_reproducer_status='NOT ENTERED: Stage 1 STOP',
    root_cause_localization_confidence='LOW: final material geometry is proved; earliest internal boundary unknown',
    likely_repositories='UNKNOWN; possible responsibility candidates are tscircuit/core, tscircuit/capacity-autorouter, tscircuit/checks; not a claim all need changes',
    likely_modules_files='UNKNOWN: no solver-stage or conversion boundary captured in accepted evidence',
    regression_test_feasibility='Full retained board/check replay feasible; isolated stock-routing regression unqualified',
    expected_upstream_suitability='UNKNOWN until a bounded cause and stable stock-routing reduction exist',
    repair_size_band='UNKNOWN', temporary_fork_patch_size='UNKNOWN: no patch exists',
    temporary_fork_maintenance='UNKNOWN; no narrow maintenance boundary established',
    hidden_additional_fault_risk='SUBSTANTIAL: 37 net/NC pairs and several diagnostics hide multiple local regions; this is not exhaustive new DRC',
    geometry_stability='Accepted EDA-003C two fresh processes have byte-identical Main geometry',
    value_of_another_cycle='Not justified within this Kill Gate. Repeated 0.115 mm via spacing is a useful lead if the PO explicitly authorizes a separate bounded cycle; it does not qualify an overall repair.',
    decision='STOP', final_classification='BACKEND_DECISION_REQUIRED'))
write('final-classification.json', dict(issue=65, classification='BACKEND_DECISION_REQUIRED',
    stage_1='BROAD / DISTRIBUTED', raw_error_record_count=71, independent_physical_fault_count=54,
    independent_net_pair_lower_bound=37, candidate_root_cause_family_count=5,
    reason='Many separate conflicts remain after geometric duplicate collapse. Five hypotheses do not establish a small localized responsibility set; repair surface remains UNKNOWN with substantial uncertainty.',
    qualification_complete=True, clearance_qualified=False, representative_selected=False,
    reduction_entered=False, root_cause_boundary_entered=False, upstream_search_entered=False, proof_of_fix_entered=False,
    accepted_wrong_net_count=0, accepted_required_unrouted_count=0, production_tscircuit='0.0.2646',
    next_human_gate_question='Should the PO authorize one separately budgeted investigation of the recurring via-clearance signature, or move to alternate backend/router evaluation or tscircuit NO-GO before any lower-priority Kill Gate?'))
# Standalone geometric evidence map, not a rendered board or manufacturing data.
parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 590" role="img" aria-label="54 Main clearance conflict components">',
         '<rect width="600" height="590" fill="white"/>',
         '<text x="35" y="25" font-family="sans-serif" font-size="17">Main: 54 local conflict components / 71 records</text>',
         '<rect x="35" y="50" width="528" height="484" fill="#f8fafc" stroke="#334155"/>']
colors = {1:'#b91c1c', 2:'#c2410c', 3:'#7c3aed', 5:'#0369a1'}
for cluster in c['clusters']:
    x, y = cluster['location']
    px, py = 35+(x+24)*11, 50+(22-y)*11
    title = html.escape(f"{cluster['cluster_id']}: {cluster['nets']}; {cluster['smallest_spacing_mm']:.6f} mm; {cluster['raw_records_explained']} records; {cluster['layer']}")
    parts.append(f'<circle cx="{px:.3f}" cy="{py:.3f}" r="4" fill="{colors[cluster["risk_priority"]]}" stroke="white"><title>{title}</title></circle>')
parts.extend(['<text x="35" y="558" font-family="sans-serif" font-size="12">48 × 44 mm board; coordinates +x right / +y up; top and bottom combined</text>',
              '<text x="35" y="578" font-family="sans-serif" font-size="12">Red: drill intrusion; orange: &lt;0.10 mm; purple: via clearance; blue: marginal</text>', '</svg>'])
(E/'main-fault-map.svg').write_text('\n'.join(parts)+'\n')
print('PASS: Stage 1 summary, risk map and cost STOP emitted')
