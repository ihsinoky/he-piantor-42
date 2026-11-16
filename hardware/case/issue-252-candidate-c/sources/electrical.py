"""Issue #252 WP3 electrical extraction.
Per-element model (stated, conservative):
- GH mated pair contact: 30 mOhm (JST GH initial max, datasheet)
- crimp per termination: 5 mOhm (allowance, labelled)
- carrier trace: Cu 1 oz (35 um), rho 1.72e-8; width 0.5 (power/return
  nets) / 0.3 (signal) per the built carrier layout; lengths from the
  built board's pad-table trace_len; +1 via per net ~ 1 mOhm allowance
- wire AWG28: 213 mOhm/m; length = fitted finished segment length
Loop = HALL_5V line out + 6 GND returns in parallel (factor 7/6 on
per-line series elements shared by the return set).
Baseline = D-033 200 mm single harness, 2 mated pairs (Wing + Main).
Candidate C = SegW + SegM end-to-end, 4 mated pairs, + carrier traces.
Vfar: Rev.7 qualified 4.792958 V at 127 mA/Wing with the baseline
harness model; candidate Vfar = baseline Vfar - I*(loop_C - loop_base).
Main copper (board targets, kept separate per the #167 lesson):
common 49.491 / J2 20.961 / J3 43.051 mOhm (Rev.7 extraction, <=50)."""
import json, sys
sys.path.insert(0, '.')

CONTACT = 30.0      # mOhm per mated pair
CRIMP = 5.0         # mOhm per crimp termination (allowance)
WIRE = 213.0        # mOhm per metre, AWG28
RHO_CU = 1.72e-8
T_CU = 35e-6

def trace_r(length_mm, width_mm):
    return RHO_CU * (length_mm / 1000.0) / (width_mm / 1000.0 * T_CU) * 1000.0

POWER = {1, 2, 4, 8, 10, 12, 14}
tab = json.load(open('/home/hatch/workspace/projects/he-piantor-midconn/hardware/kicad/qualification/issue-252-carrier/inspection/pad-table.json'))
tl = tab['trace_len_mm']
FN = {1: 'HALL_5V', 2: 'GND', 3: 'MUX_A0', 4: 'GND', 5: 'MUX_A1',
      6: 'MUX_A2', 7: 'WING_EN', 8: 'GND', 9: 'MUX_OUT_A', 10: 'GND',
      11: 'MUX_OUT_B', 12: 'GND', 13: 'MUX_OUT_C', 14: 'GND'}
carrier = {}
for k in range(1, 15):
    nm = f'P{k:02d}_{FN[k]}'
    carrier[k] = round(trace_r(tl[nm], 0.5 if k in POWER else 0.3) + 1.0, 2)

lens = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'repair_score.json'))['lens']
def seg(side, seg, i):
    return lens[f'{seg}-{side}-{i:02d}']

rows = {}
for side in ('right', 'left'):
    for i in range(1, 15):
        rows[(side, i)] = (seg(side, 'SegW', i), seg(side, 'SegM', i))
worst = max(rows.items(), key=lambda kv: kv[1][0] + kv[1][1])
w_w, w_m = worst[1]
e2e = w_w + w_m

pair = CONTACT + 2 * CRIMP           # per mated pair, per line
def loop(pairs, wire_mm, trace_mohm):
    per_line = pairs * pair + wire_mm / 1000.0 * WIRE + trace_mohm
    return per_line * 7.0 / 6.0      # supply + 6 parallel returns

base = loop(2, 200.0, 0.0)
cand_trace = carrier[1]              # HALL_5V trace (returns similar class)
cand = loop(4, e2e, cand_trace)
I = 0.127
vfar_base = 4.792958
vfar_c = vfar_base - I * (cand - base) / 1000.0
out = {
    'carrier_trace_mohm_per_net': carrier,
    'worst_branch': {'side': worst[0][0], 'pin': worst[0][1],
                     'SegW_mm': w_w, 'SegM_mm': w_m, 'end_to_end_mm': round(e2e, 2)},
    'loop_baseline_mohm': round(base, 1),
    'loop_candidate_mohm': round(cand, 1),
    'loop_delta_mohm': round(cand - base, 1),
    'vfar_baseline_V': vfar_base,
    'vfar_candidate_V': round(vfar_c, 4),
    'vfar_target_V': 4.60,
    'margin_mV': round((vfar_c - 4.60) * 1000),
    'main_copper_mohm': {'common': 49.491, 'J2': 20.961, 'J3': 43.051,
                         'target': '<=50 (board targets, unchanged)'},
}
print(json.dumps(out, indent=1))
json.dump(out, open('electrical.json', 'w'), indent=1)
