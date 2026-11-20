#!/usr/bin/env python3
"""Issue #299 Stage 1 - wireless Wing HALL_3V3 far-sensor rail budget.
All resistances/currents from tree sources (cited in wwing-design.md S4).
Chain: SYS_3V3 -> TPS22919 -> Main copper -> FH12(Main) -> FFC loop ->
FH12(Wing) -> Wing zone distribution -> far sensor VCC pin.
Return: 6 GND FFC lanes in parallel + B.Cu GND zone (in Wing bound).
"""
# Currents (mA): 21 TMAG/Wing; typ 2.6 / max 5.0 mA @3.3V (#282 SBASAI5E);
# MUX 3x 0.1 mA conservative (#288 droop load basis; datasheet IDD ~10 nA typ)
I_typ = 21 * 2.6 + 3 * 0.1
I_max = 21 * 5.0 + 3 * 0.1

def budget(lane_ohm, ron_ohm, label):
    ffc_loop = lane_ohm * (1 + 1/6)      # 1 supply lane + 6 return lanes parallel
    elems = {
        "TPS22919 RON (TI SLVSEN5B)": ron_ohm,
        "Main copper, extracted as-built (#292 REPORT)": 0.090,
        "FFC loop (lane %.2f ohm)" % lane_ohm: ffc_loop,
        "FH12 mated pairs x2 (60 mOhm class ea, #292 S5.2)": 0.120,
        "Wing zone distribution bound (Stage 1)": 0.025,
    }
    R = sum(elems.values())
    print(f"--- {label}: R_total = {R:.3f} ohm")
    for k, v in elems.items():
        print(f"    {k:55s} {v:7.3f} ohm  drop@typ {v*I_typ:6.2f} mV  drop@max {v*I_max:6.2f} mV")
    for I, nm in ((I_typ, "typ"), (I_max, "max")):
        d = R * I
        print(f"    TOTAL drop @{nm} ({I:.1f} mA): {d:.1f} mV | far VCC = {3.3 - d/1000:.3f} V | ratiometric scale err = {d/33:.2f} %")
    return R

print(f"Burst currents: typ {I_typ:.1f} mA, max {I_max:.1f} mA (21 sensors/Wing, per-Wing EN bank)")
budget(0.10, 0.090, "EXPECTED lanes (0.10 ohm, D-042 amendment record), RON typ 90 mOhm")
budget(0.10, 0.135, "EXPECTED lanes, RON max-class 135 mOhm")
budget(0.30, 0.090, "PROPOSED wireless lane acceptance 0.30 ohm, RON typ")
budget(1.30, 0.090, "LEGACY wired lane acceptance limit 1.30 ohm, RON typ")
