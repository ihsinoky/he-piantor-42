"""Issue #127 native JITX placement/net assemblies. No routing/fab claim.

One parameterized definition drives components, physical-pin nets, and placement.
Main electrical/physical data and existing generic capacitor model are untouched.
"""

from jitx.board import Board
from jitx.circuit import Circuit
from jitx.design import Design
from jitx.net import Net
from jitx.shapes.composites import rectangle
from jitxlib.landpatterns.twopin.smt import SMT

from wing.definition import HALL_PINS, MUX_PINS, define_wing
from wing.matrix import define_m1_matrix

from .components.connectors.jst_bm14b_ghs_tbt import BM14B_GHS_TBT
from .components.generic_electrical import Capacitor, TestPoint
from .components.sensors.texas_instruments_drv5055a3qdbzr import DRV5055A3QDBZR
from .components.switches.texas_instruments_tmux1208pwr import TMUX1208PWR
from .physical_qualification import QualificationFabRules, QualificationSubstrate


class WingBypass(Capacitor):
    manufacturer = "Murata"
    mpn = "GRM188R71C104KA01D"
    landpattern = SMT("0603")


def make_wing_circuit(pitch: float, kind: str = "pitch9", spec=None) -> type[Circuit]:
    spec = define_wing(pitch, kind) if spec is None else spec
    declarations = {}
    for row in spec["components"]:
        declarations[row["reference"]] = {
            "hall": DRV5055A3QDBZR,
            "mux": TMUX1208PWR,
            "connector": BM14B_GHS_TBT,
            "capacitor": lambda: WingBypass(capacitance=1e-7),
            "testpoint": TestPoint,
        }[row["kind"]]()

    def initialize(self):
        endpoints = {}
        for row in spec["components"]:
            part = getattr(self, row["reference"])
            part.at(row["x_mm"], row["y_mm"], rotate=row["rotation_ccw_deg"])
            if row["kind"] == "hall":
                ports = {pin: getattr(part, port) for port, pin in HALL_PINS.items()}
            elif row["kind"] == "mux":
                ports = {pin: getattr(part, port) for port, pin in MUX_PINS.items()}
            elif row["kind"] == "connector":
                ports = {str(i): port for i, port in enumerate(part.p, 1)} | {"MP": part.MP}
            elif row["kind"] == "capacitor":
                ports = {"1": part.p1, "2": part.p2}
            else:
                ports = {"1": part.pin1}
            endpoints.update({f"{row['reference']}.{pin}": port for pin, port in ports.items()})
        for name, members in spec["nets"].items():
            setattr(self, name, Net([endpoints[m] for m in members], name=name))

    declarations["__init__"] = initialize
    return type(f"Wing_{kind}_{pitch:g}".replace(".", "_"), (Circuit,), declarations)


CIRCUITS = {
    (pitch, kind): make_wing_circuit(pitch, kind)
    for kind in ("pitch9", "representative21", "load21")
    for pitch in (16.0, 17.0)
}


def wing_circuit(pitch: float, kind: str = "pitch9") -> Circuit:
    """Instantiate a declared 16/17mm variant inside a JITX substrate context."""
    return CIRCUITS[pitch, kind]()


# CLI entry classes follow the existing class-body Circuit/Board/Substrate pattern.
# Create circuits only under the substrate context provided by JITX Design.
class WingFabRules(QualificationFabRules):
    max_board_width = 100.0
    max_board_height = 100.0


class WingSubstrate(QualificationSubstrate):
    constraints = WingFabRules()


def make_wing_design(name, pitch, kind):
    spec = define_wing(pitch, kind)
    circuit_type = CIRCUITS.get((pitch, kind)) or make_wing_circuit(pitch, kind)
    board_type = type(
        f"{name}Board",
        (Board,),
        {
            "shape": rectangle(spec["width_mm"], spec["height_mm"]),
            "signal_area": rectangle(spec["width_mm"] - 1, spec["height_mm"] - 1),
        },
    )
    return type(
        name,
        (Design,),
        {
            "board": board_type(),
            "substrate": WingSubstrate(),
            "circuit": circuit_type(),
        },
    )


Pitch16 = make_wing_design("Pitch16", 16.0, "pitch9")
Pitch17 = make_wing_design("Pitch17", 17.0, "pitch9")
Representative16 = make_wing_design("Representative16", 16.0, "representative21")
Representative17 = make_wing_design("Representative17", 17.0, "representative21")
Load16 = make_wing_design("Load16", 16.0, "load21")
Load17 = make_wing_design("Load17", 17.0, "load21")


# M1 evaluation board has two independent 3x3 pitch fields on one substrate.


class M1MatrixFabRules(WingFabRules):
    max_board_width = 128.0
    max_board_height = 80.0
    min_copper_width = 0.10
    min_copper_copper_space = 0.10
    min_copper_hole_space = 0.20
    min_copper_edge_space = 0.20


class M1MatrixSubstrate(QualificationSubstrate):
    constraints = M1MatrixFabRules()

    class ThroughVia(QualificationSubstrate.ThroughVia):
        diameter = 0.60
        hole_diameter = 0.30


class M1MatrixBoard(Board):
    shape = rectangle(128.0, 80.0)
    signal_area = rectangle(127.0, 79.0)


M1MatrixCircuit = make_wing_circuit(16, "matrix18", define_m1_matrix())


class M1Matrix18(Design):
    board = M1MatrixBoard()
    substrate = M1MatrixSubstrate()
    circuit = M1MatrixCircuit()
