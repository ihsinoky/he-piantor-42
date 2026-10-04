"""Read-only C3 observations; stdout only, no build or baseline mutation.

Run from hardware/jitx with the existing .venv/bin/python. The manufacturer
transcription and classifications belong to EDA-002C3.md, not this observer.
"""

import hashlib
import importlib.metadata
import json
import re
from pathlib import Path

from jitx.sample import SampleSubstrate
from jitx.substrate import SubstrateContext
from jitx.test import TestCase
from jitxlib.landpatterns.pads import NPTHPad

from he_piantor_42_jitx.components.connectors.hro_type_c_31_m_12 import TYPE_C_31_M_12
from he_piantor_42_jitx.components.crystals.abracon_abm8_272_t3 import ABM8_272_T3
from he_piantor_42_jitx.components.mcu.raspberry_pi_rp2040 import RP2040
from he_piantor_42_jitx.components.memory.winbond_w25q16jvuxiq import W25Q16JVUXIQ
from he_piantor_42_jitx.components.power.diodes_ap2112k_3_3trg1 import AP2112K_3_3TRG1
from he_piantor_42_jitx.components.power.texas_instruments_tps22919dckr import TPS22919DCKR
from he_piantor_42_jitx.components.protection.st_usblc6_2sc6 import USBLC6_2SC6
from he_piantor_42_jitx.components.sensors.texas_instruments_drv5055a3qdbzr import DRV5055A3QDBZR
from he_piantor_42_jitx.components.switches.texas_instruments_tmux1208pwr import TMUX1208PWR

ROOT = Path(__file__).resolve().parents[3]
JITX = ROOT / "hardware/jitx"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pad_observation(pad):
    if isinstance(pad, NPTHPad):
        x0, y0, x1, y1 = pad.cutout.shape.to_shapely().bounds
        return {
            "center_mm": list(pad.transform.translation),
            "drill_size_mm": [x1 - x0, y1 - y0],
        }
    x0, y0, x1, y1 = pad.shape.to_shapely().bounds
    result = {
        "center_mm": list(pad.transform.translation),
        "copper_size_mm": [x1 - x0, y1 - y0],
    }
    if hasattr(pad, "cutout"):
        x0, y0, x1, y1 = pad.cutout.shape.to_shapely().bounds
        result["drill_size_mm"] = [x1 - x0, y1 - y0]
    return result


def main():
    frozen_path = ROOT / "hardware/tscircuit/src/evaluation/m1-four-key.tsx"
    frozen = frozen_path.read_text()
    contact_y, contact_length = re.search(
        r"pcbY=\{([-\d.]+)\} width=\{width\} height=\{([-\d.]+)\}", frozen
    ).groups()
    contacts = [
        {
            "contact": name,
            "center_mm": [float(x), float(contact_y)],
            "copper_size_mm": [float(width or 0.3), float(contact_length)],
        }
        for name, x, width in re.findall(
            r'usbContact\("([^"\n]+)", ([-\d.]+)(?:, ([-\d.]+))?\)', frozen
        )
    ]
    shell = []
    for tag in re.findall(r"<platedhole [^>]+/>", frozen):
        fields = {key: float(value) for key, value in re.findall(r"(\w+)=\{([-\d.]+)\}", tag)}
        shell.append(fields)
    locators = [
        [float(v) for v in values]
        for values in re.findall(
            r"<hole pcbX=\{([-\d.]+)\} pcbY=\{([-\d.]+)\} diameter=\{([-\d.]+)\}",
            frozen,
        )
    ]
    assert len(contacts) == 12 and len(shell) == 4 and len(locators) == 2
    flash_source = frozen.split("const flashFootprint = <footprint>", 1)[1].split(
        "</footprint>", 1
    )[0]
    flash_positions = re.findall(r"\[(\d+),([-\d.]+),([-\d.]+)\]", flash_source)
    flash_width, flash_height = re.search(
        r"width=\{([-\d.]+)\} height=\{([-\d.]+)\}", flash_source
    ).groups()
    ep_x, ep_y, ep_width, ep_height = re.search(
        r"pcbX=\{([-\d.]+)\} pcbY=\{([-\d.]+)\} "
        r"width=\{([-\d.]+)\} height=\{([-\d.]+)\}",
        flash_source,
    ).groups()
    assert len(flash_positions) == 8
    paths = [
        frozen_path,
        JITX / "he_piantor_42_jitx/components/connectors/hro_type_c_31_m_12.py",
        JITX / "he_piantor_42_jitx/components/memory/winbond_w25q16jvuxiq.py",
        JITX / "uv.lock",
    ]
    result = {
        "scope": "Geometry observations only; no parity or approval verdict",
        "versions": {p: importlib.metadata.version(p) for p in ("jitx", "jitxlib-standard")},
        "project_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in paths},
        "frozen_hro": {"contacts": contacts, "shell": shell, "locators_x_y_diameter_mm": locators},
        "frozen_winbond": {
            "signals": {
                n: {
                    "center_mm": [float(x), float(y)],
                    "copper_size_mm": [float(flash_width), float(flash_height)],
                }
                for n, x, y in flash_positions
            },
            "exposed_land": {
                "center_mm": [float(ep_x), float(ep_y)],
                "copper_size_mm": [float(ep_width), float(ep_height)],
            },
        },
    }
    with SubstrateContext(SampleSubstrate()):
        hro = TYPE_C_31_M_12()
        flash = W25Q16JVUXIQ()
        result["jitx_hro"] = {
            "contacts": [pad_observation(p) for p in hro.landpattern.contacts],
            "shell": [pad_observation(p) for p in hro.landpattern.shell],
            "locators": [pad_observation(p) for p in hro.landpattern.locating],
        }
        result["jitx_winbond"] = {
            "signals": {str(n): pad_observation(flash.landpattern.p[n]) for n in range(1, 9)},
            "exposed_land": pad_observation(flash.landpattern.thermal_pads[0]),
        }
        rp = RP2040()
        crystal = ABM8_272_T3()
        other = {
            "RP2040": rp.landpattern.physical_pads(),
            "ABM8-272-T3": [getattr(crystal.landpattern, f"p{n}") for n in range(1, 5)],
        }
        for component_type, count in (
            (USBLC6_2SC6, 6),
            (AP2112K_3_3TRG1, 5),
            (TPS22919DCKR, 6),
            (TMUX1208PWR, 16),
            (DRV5055A3QDBZR, 3),
        ):
            component = component_type()
            other[component.mpn] = [component.landpattern.p[n] for n in range(1, count + 1)]
        result["jitx_other_seven_limited_audit"] = {
            name: {
                "pad_count": len(pads),
                "distinct_copper_sizes_mm": sorted(
                    {tuple(round(v, 9) for v in pad_observation(p)["copper_size_mm"]) for p in pads}
                ),
            }
            for name, pads in other.items()
        }
    from jitxlib.landpatterns import ipc, leads
    from jitxlib.landpatterns.leads import protrusions

    result["generator_sha256"] = {
        name: sha256(Path(module.__file__))
        for name, module in (
            ("ipc.py", ipc),
            ("leads/__init__.py", leads),
            ("leads/protrusions.py", protrusions),
        )
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    # Public inspection harness provides JITX's structural context without
    # a runtime build or access to private framework APIs.
    class ObservationContext(TestCase):
        pass

    ObservationContext.setUpClass()
    try:
        main()
    finally:
        ObservationContext.doClassCleanups()
