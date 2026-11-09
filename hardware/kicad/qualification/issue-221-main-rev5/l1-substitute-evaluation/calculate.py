"""Reproduce Issue #223 design extraction and incremental DCR sensitivity.

Offline; reads existing Rev.5 files and writes only this evaluation directory.
This is a steady-state screening calculation, not converter qualification.
"""
import hashlib
import json
import math
import pathlib
import re
import xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).resolve().parent
REV5 = HERE.parent
ROOT = REV5.parents[3]
budget = json.loads((REV5 / "power-budget.json").read_text())
net = ET.parse(REV5 / "schematic/main.net.xml")
components = {c.attrib["ref"]: c for c in net.findall("./components/comp")}
assert components["L1"].findtext("value") == "1.5uH XFL4020-152MEC"
assert "TPS63070" in components["U6"].findtext("value")
nodes = {(n.attrib["ref"], n.attrib["pin"]): item.attrib["name"].lstrip("/")
         for item in net.findall("./nets/net") for n in item.findall("node")}
assert nodes["L1", "1"] == "SW1" and nodes["L1", "2"] == "SW2"
assert nodes["U6", "1"] == "GND"  # PS/SYNC: forced PWM
board = (REV5 / "inspection/final/main.kicad_pcb").read_text()
index = board.index('(property "Reference" "L1"')
start = board.rfind('\n\t(footprint', 0, index)
end = board.find('\n\t(footprint', index)
footprint = board[start:end]
pads = re.findall(r'\(pad "([12])" smd rect\s+\(at ([^)]*)\)\s+\(size ([^)]*)\)', footprint)
assert pads == [("1", "-1.55 0", "1.3 3.6"), ("2", "1.55 0", "1.3 3.6")]

# Existing Rev.5 upstream sweep is a reservation, not a guaranteed VIN limit.
corner = min(budget["upstream_sensitivity"], key=lambda r: r["converter_V"])
vout = 5.354  # #165/#167 DC high corner + transient allocation; conservative
iout = 2 * budget["design_Wing_A"]
eta = corner["efficiency_assumption"]
# Re-solve KVL at 5.354V, rather than reuse the sweep's 5.304V input point.
upstream_r = corner["Fly_PTC_EZmate_contacts_reservation_ohm"] + corner["main_input_loop_ohm"]
other_main = .110
term = corner["USB_V"] - upstream_r * other_main
vin = (term + math.sqrt(term**2 - 4*upstream_r*iout*vout/eta))/2
assert abs(corner["USB_V"] - upstream_r*(iout*vout/(eta*vin)+other_main) - vin) < 1e-12
frequency = 2.1e6  # TI 7.5 minimum, not only 2.4MHz typical
alpha = .00393  # copper approximation, referenced at 25C for catalogue DCR
parts = {
    "C3033018": dict(L_uH=1.5, DCR_typ_mohm=14.4, DCR_max_mohm=15.8,
                     Isat_10pct_A=4.1, Isat_20pct_A=4.4, Isat_30pct_A=4.6,
                     Irms_20C_A=6.7, Irms_40C_A=9.1),
    "C7417180": dict(L_uH=1.5, DCR_typ_mohm=13., DCR_max_mohm=14.3,
                     Isat_10pct_A=3.2, Isat_20pct_A=5.3, Isat_30pct_A=7.5,
                     Irms_20C_A=8., Irms_40C_A=11.1),
    "C3221841": dict(L_uH=1.5, DCR_typ_mohm=14.4, DCR_max_mohm=15.8,
                     Isat_10pct_A=4.1, Isat_20pct_A=4.5, Isat_30pct_A=7.5,
                     Irms_20C_A=6.7, Irms_40C_A=9.1),
    "C5355380": dict(L_uH=1., DCR_typ_mohm=10.8, DCR_max_mohm=11.9,
                     Isat_10pct_A=4.5, Isat_20pct_A=5.1, Isat_30pct_A=5.4,
                     Irms_20C_A=8., Irms_40C_A=11.),
}


def waveform(inductance, efficiency=eta, output=vout):
    duty = (output - vin) / output
    average = iout / (efficiency * (1-duty))
    ripple = vin * duty / (frequency * inductance)
    rms2 = average**2 + ripple**2 / 12
    return dict(duty=duty, average_A=average, ripple_pp_A=ripple,
                peak_A=average+ripple/2, rms_A=math.sqrt(rms2))


results = {}
for code, p in parts.items():
    # Include tolerance and a 10% DC-bias allowance. Compare to 10%-drop Isat.
    effective = p["L_uH"] * 1e-6 * .8 * .9
    wave = waveform(effective)
    margin = 1.2 * wave["peak_A"]  # TI 9.2.2.2 recommended margin
    assert p["Isat_10pct_A"] >= margin
    dcr_rows = []
    for temperature in (25, 125):
        multiplier = 1 + alpha * (temperature-25)
        resistance = p["DCR_max_mohm"] / 1000 * multiplier
        reference = parts["C3033018"]["DCR_max_mohm"] / 1000 * multiplier
        # Same 1.5uH waveform isolates DCR delta (different-L part gets its own
        # copper-loss result; its DCR-only delta is explicitly hypothetical).
        ref_wave = waveform(1.5e-6 * .8 * .9)
        delta_p = ref_wave["rms_A"]**2 * (resistance-reference)
        power = iout * vout
        baseline_eta = .90
        incremental_eta = power / (power / baseline_eta + delta_p)
        dcr_rows.append(dict(temperature_C=temperature, DCR_ohm=resistance,
                             copper_loss_W=wave["rms_A"]**2 * resistance,
                             DCR_only_delta_loss_W=delta_p,
                             DCR_only_output_equivalent_delta_ohm=delta_p / iout**2,
                             illustrative_eta_baseline=baseline_eta,
                             illustrative_eta_after_increment=incremental_eta,
                             delta_efficiency_percentage_points=100*(incremental_eta-baseline_eta)))
    results[code] = dict(specification=p, effective_L_uH=effective*1e6,
                         waveform=wave, required_Isat_with_20pct_margin_A=margin,
                         Isat_10pct_to_peak_ratio=p["Isat_10pct_A"]/wave["peak_A"],
                         Irms_20C_to_model_rms_ratio=p["Irms_20C_A"]/wave["rms_A"],
                         dcr_sensitivity=dcr_rows)

sources = [REV5 / "schematic/main.kicad_sch", REV5 / "schematic/main.net.xml",
           REV5 / "inspection/final/main.kicad_pcb", REV5 / "power-budget.json",
           REV5 / "power-budget.py", ROOT / "docs/decisions.md",
           ROOT / "docs/issue-165-dual-wing-power-study.md",
           ROOT / "docs/issue-167-main-dual-wing-stage2.md"]
result = dict(
    source_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
    extracted=dict(L1_value=components["L1"].findtext("value"),
                   footprint=components["L1"].findtext("footprint"),
                   U6_value=components["U6"].findtext("value"),
                   pad_centers_x_mm=[-1.55, 1.55], pad_size_mm=[1.3, 3.6],
                   pad_inner_gap_mm=1.8, pad_outer_span_mm=4.4,
                   upstream_min_corner=corner),
    assumptions=dict(vin_V=vin, vout_V=vout, iout_A=iout, efficiency=eta,
                     frequency_Hz=frequency, L_tolerance_fraction=.2,
                     L_bias_loss_fraction=.1, copper_alpha_per_K=alpha,
                     warning="Sensitivity corner, not guaranteed VIN/efficiency/temperature or startup/fault current"),
    parts=results,
    RHPZ_at_Lmax_1p8uH_Hz=(vin/vout)**2*vout/(2*math.pi*iout*1.8e-6),
    geometry=dict(nominal_terminal_x_mm=[.785, 1.605], existing_pad_x_mm=[.9, 2.2],
                  nominal_overlap_x_mm=.705, min_overlap_x_with_gap_and_width_tolerance_mm=.53,
                  terminal_y_span_typ_mm=3.25, pad_y_span_mm=3.6,
                  note="XFL/XGL share terminal drawing and recommended land. PCB land differs from manufacturer recommendation; no new land/mask/paste introduced."))
(HERE / "calculation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"screening_corner": result["assumptions"],
                  "recommended_part": results["C7417180"]}, indent=2))
