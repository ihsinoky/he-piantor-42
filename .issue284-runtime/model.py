#!/usr/bin/env python3
"""Issue #284 - MCU/radio term model. Sensor terms copied verbatim from
Issue #282 (per-bank EN). All MCU figures: datasheet-notes.md."""
import json

ETA = 0.85            # converter efficiency (#282 convention)
PACK_WH = 8.66        # 4x AA NiMH usable (#282)

# ---- fixed sensor terms (#282, never recomputed) ----
SENSOR_TYPING_W   = 0.190          # continuous Hall power, per-bank
SENSOR_PER_SWEEP_J = 67e-6         # per-bank sensor energy per sweep
SWEEP_S = 0.37e-3                  # per-bank sweep duration
H_TYP, H_DESK, H_AWAY = 2.0, 6.0, 16.0
T_DESK, T_AWAY = 10e-3, 100e-3

sensor = {
    "typing_mWh": SENSOR_TYPING_W * H_TYP * 1000,
    "desk_mWh":   SENSOR_PER_SWEEP_J / T_DESK * H_DESK * 1000,
    "away_mWh":   SENSOR_PER_SWEEP_J / T_AWAY * H_AWAY * 1000,
}
sensor["total_mWh"] = sum(sensor[k] for k in ("typing_mWh","desk_mWh","away_mWh"))

# ---- per-architecture MCU terms (datasheet-notes.md) ----
# powers in W, energies in J
ARCH = {
  "A": dict(  # RP2040 + nRF52840 co-processor
    floor_desk_W = 1.45e-3,   # SLEEP mode (fast wake at T=10 ms)
    floor_away_W = 0.66e-3,   # DORMANT + external RTC clock
    wake_desk_J  = 0.1e-6,
    wake_away_J  = 31.7e-6,   # XOSC 1 ms startup delay + PLL relock
    sweep_W      = 20e-3, sweep_s = 0.37e-3,   # PIO+ADC+DMA, CPU WFI
    proc_J       = 46e-3 * (8000/125e6),        # 8000 cyc @125 MHz, run 46 mW
    copro_floor_W = 9.5e-6,   # nRF52840 System ON+RAM+RTC, 24 h
    radio_mWh    = 0.55,
    spi_per_report_J = 0.5e-6,
  ),
  "B1": dict( # nRF52840 alone
    floor_desk_W = 9.5e-6, floor_away_W = 9.5e-6,
    wake_desk_J  = 0.05e-6, wake_away_J = 0.05e-6,
    sweep_W      = 6.6e-3, sweep_s = 0.40e-3,   # SAADC+TIMER+PPI, CPU WFI
    proc_J       = 9.9e-3 * (5000/64e6),        # 5000 cyc @64 MHz, run 9.9 mW
    copro_floor_W = 0.0, radio_mWh = 0.55, spi_per_report_J = 0.0,
  ),
  "B2": dict( # nRF54L15 alone
    floor_desk_W = 8.7e-6, floor_away_W = 8.7e-6,
    wake_desk_J  = 0.05e-6, wake_away_J = 0.05e-6,
    sweep_W      = 6.0e-3, sweep_s = 0.37e-3,
    proc_J       = 7.8e-3 * (5000/128e6),       # 5000 cyc @128 MHz, run 7.8 mW
    copro_floor_W = 0.0, radio_mWh = 0.50, spi_per_report_J = 0.0,
  ),
}
REPORTS_TYPING = 30 * 7200   # 30 frames/s over 2 h (traffic model)

def run(arch, A):
    proc_s = {"A": 8000/125e6, "B1": 5000/64e6, "B2": 5000/128e6}[arch]
    sweep_J = A["sweep_W"] * A["sweep_s"]
    per_sweep_desk_J = A["wake_desk_J"] + sweep_J + A["proc_J"]
    per_sweep_away_J = A["wake_away_J"] + sweep_J + A["proc_J"]
    def avg_W(T, floor_W, per_sweep_J, wake_s):
        active_s = wake_s + A["sweep_s"] + proc_s
        return (per_sweep_J + floor_W * max(T - active_s, 0)) / T
    desk_W = avg_W(T_DESK, A["floor_desk_W"], per_sweep_desk_J, 0.000002 if arch!="A" else 0.000002)
    away_W = avg_W(T_AWAY, A["floor_away_W"], per_sweep_away_J, 0.0012 if arch=="A" else 0.000002)
    typing_W = per_sweep_desk_J / SWEEP_S + A["spi_per_report_J"] * 30  # + SPI share (A only)
    out = {
        "typing_mcu_W": typing_W, "desk_mcu_W": desk_W, "away_mcu_W": away_W,
        "per_sweep_desk_uJ": per_sweep_desk_J*1e6, "per_sweep_away_uJ": per_sweep_away_J*1e6,
    }
    out["typing_mWh"] = typing_W * H_TYP * 1000
    out["desk_mWh"]   = desk_W * H_DESK * 1000
    out["away_mWh"]   = away_W * H_AWAY * 1000
    out["copro_floor_mWh"] = A["copro_floor_W"] * 24 * 1000
    out["radio_mWh"] = A["radio_mWh"]
    out["mcu_radio_total_mWh"] = (out["typing_mWh"] + out["desk_mWh"] + out["away_mWh"]
                                  + out["copro_floor_mWh"] + out["radio_mWh"])
    out["load_total_mWh"] = sensor["total_mWh"] + out["mcu_radio_total_mWh"]
    out["battery_mWh"] = out["load_total_mWh"] / ETA
    out["days"] = PACK_WH * 1000 / out["battery_mWh"]
    return out

results = {"sensor_fixed": sensor}
for name, A in ARCH.items():
    results[name] = run(name, A)

# delta decomposition A -> B1 / A -> B2 (load mWh)
for b in ("B1", "B2"):
    d = {
        "typing": results["A"]["typing_mWh"] - results[b]["typing_mWh"],
        "desk":   results["A"]["desk_mWh"]   - results[b]["desk_mWh"],
        "away":   results["A"]["away_mWh"]   - results[b]["away_mWh"],
        "floor+radio": (results["A"]["copro_floor_mWh"] + results["A"]["radio_mWh"])
                       - (results[b]["copro_floor_mWh"] + results[b]["radio_mWh"]),
    }
    d["total"] = sum(d.values())
    results[f"delta_A_to_{b}"] = d

results["sensor_ceiling_days"] = PACK_WH * 1000 / (sensor["total_mWh"] / ETA)

print(json.dumps(results, indent=1))
with open("mcu-power.json", "w") as f:
    json.dump(results, f, indent=1)
