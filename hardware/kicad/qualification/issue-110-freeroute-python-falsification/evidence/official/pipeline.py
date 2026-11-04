"""End-to-end routing pipeline: DSN text in, SES text out.

Ties together the parser, board construction, the grid router, and the SES
writer — the Java-free replacement for the ``freerouting.jar`` step:

    dsn_text -> parse_dsn -> build_board -> route_board -> write_ses -> ses_text

Router output is in board units; wire paths and via locations are converted back
to DSN units (dividing by the resolution) for the SES ``(wire (path ...))`` and
``(via <padstack> x y)`` scopes.
"""

from __future__ import annotations

from freeroute.board import build_board
from freeroute.dsn import DsnBoard, parse_dsn
from freeroute.ses import RoutedVia, RoutedWire, RoutingResult, write_ses

from .exact_router import ExactRouteResult, route_board_exact
from .grid_router import RouteResult, route_board
from .room_router import route_board_rooms

__all__ = ["route", "route_dsn_board", "build_routing_result"]

#: fallback trace width / clearance in DSN units when the DSN has no rules
_DEFAULT_WIDTH_DSN = 2000
_DEFAULT_CLEARANCE_DSN = 2000
#: fallback via padstack name when the DSN declares none
_DEFAULT_VIA = "Via"


def _rule_width_dsn(dsn: DsnBoard) -> float:
    rules = dsn.structure_rules.width_rules
    return rules[0].value if rules else _DEFAULT_WIDTH_DSN


def _rule_clearance_dsn(dsn: DsnBoard) -> float:
    for rule in dsn.structure_rules.clearance_rules:
        if not rule.class_pairs:  # the layer-wide default clearance
            return rule.value
    return _DEFAULT_CLEARANCE_DSN


def _via_padstack(dsn: DsnBoard) -> str:
    return dsn.via_padstack_names[0] if dsn.via_padstack_names else _DEFAULT_VIA


def route_dsn_board(
    dsn: DsnBoard,
    *,
    layers: list[int] | None = None,
    rip_up: bool = True,
    max_passes: int = 10,
) -> tuple[RouteResult, int, list[str]]:
    """Route a parsed :class:`DsnBoard`; return the board-unit result, the scale,
    and the layer names. ``layers`` restricts routing to those signal-layer
    indices (default: all signal layers, i.e. multi-layer with vias); ``rip_up``
    toggles rip-up-and-retry (``False`` = greedy single pass)."""
    board = build_board(dsn)
    scale = max(dsn.resolution.value, 1)
    width_board = round(_rule_width_dsn(dsn) * scale)
    clearance_board = round(_rule_clearance_dsn(dsn) * scale)
    result = route_board(
        board,
        trace_width=width_board,
        clearance=clearance_board,
        layers=layers,
        rip_up=rip_up,
        max_passes=max_passes,
    )
    return result, scale, [layer.name for layer in dsn.layers]


def _to_routing_result(route, dsn: DsnBoard, scale: int, layer_names: list[str]) -> RoutingResult:
    """Convert a board-unit :class:`RouteResult` to a DSN-unit RoutingResult."""
    width_dsn = _rule_width_dsn(dsn)
    via_name = _via_padstack(dsn)
    # net_number is assigned in DSN order by build_board, so index i -> number i+1
    numbers_to_names = {i + 1: n.name for i, n in enumerate(dsn.nets)}

    result = RoutingResult()
    for net_no, segments in route.wires.items():
        name = numbers_to_names.get(net_no, str(net_no))
        for layer_index, path in segments:
            layer_name = layer_names[layer_index] if layer_index < len(layer_names) else "F.Cu"
            coords: list[float] = []
            for point in path:
                coords.append(point.x / scale)
                coords.append(point.y / scale)
            if len(coords) >= 4:
                result.add_wire(name, RoutedWire(layer=layer_name, width=width_dsn, coords=coords))
    for net_no, locations in route.vias.items():
        name = numbers_to_names.get(net_no, str(net_no))
        for loc in locations:
            result.add_via(name, RoutedVia(padstack=via_name, x=loc.x / scale, y=loc.y / scale))
    return result


def build_routing_result(
    dsn: DsnBoard,
    *,
    layers: list[int] | None = None,
    rip_up: bool = True,
    max_passes: int = 10,
) -> RoutingResult:
    """Route ``dsn`` (grid track) and convert to a DSN-unit RoutingResult."""
    route, scale, layer_names = route_dsn_board(
        dsn, layers=layers, rip_up=rip_up, max_passes=max_passes
    )
    return _to_routing_result(route, dsn, scale, layer_names)


def route_dsn_board_exact(
    dsn: DsnBoard,
    *,
    layers: list[int] | None = None,
    max_passes: int = 10,
    rip_up: bool = True,
    shove: bool = False,
    diagonal: bool = False,
) -> tuple[ExactRouteResult, int, list[str]]:
    """Route a parsed :class:`DsnBoard` with the exact-geometry (orthogonal,
    DRC-verified) track; return the exact result, the scale, and layer names.
    ``shove`` enables moving existing traces aside to recover dropped nets;
    ``rip_up`` toggles the underlying grid's rip-up-and-retry; ``diagonal`` enables
    the 45-degree recovery pass for still-dropped 2-pin nets."""
    board = build_board(dsn)
    scale = max(dsn.resolution.value, 1)
    width_board = round(_rule_width_dsn(dsn) * scale)
    clearance_board = round(_rule_clearance_dsn(dsn) * scale)
    exact = route_board_exact(
        board,
        trace_width=width_board,
        clearance=clearance_board,
        layers=layers,
        max_passes=max_passes,
        rip_up=rip_up,
        shove=shove,
        diagonal=diagonal,
    )
    return exact, scale, [layer.name for layer in dsn.layers]


def build_exact_routing_result(
    dsn: DsnBoard,
    *,
    layers: list[int] | None = None,
    shove: bool = False,
    diagonal: bool = False,
    rip_up: bool = True,
    max_passes: int = 10,
) -> RoutingResult:
    """Route ``dsn`` (exact track) and convert to a DSN-unit RoutingResult."""
    exact, scale, layer_names = route_dsn_board_exact(
        dsn,
        layers=layers,
        shove=shove,
        diagonal=diagonal,
        rip_up=rip_up,
        max_passes=max_passes,
    )
    return _to_routing_result(exact.result, dsn, scale, layer_names)


def route_dsn_board_rooms(
    dsn: DsnBoard, *, layers: list[int] | None = None, shove: bool = False, pack: bool = False
) -> tuple[ExactRouteResult, int, list[str]]:
    """Route a parsed :class:`DsnBoard` with the continuous expansion-room track;
    return the result, the scale, and layer names. ``shove`` enables occupancy-
    aware gate placement and shove-in-rooms recovery of otherwise-dropped nets.
    ``pack`` enables the coordinated multi-trace channel packer."""
    board = build_board(dsn)
    scale = max(dsn.resolution.value, 1)
    width_board = round(_rule_width_dsn(dsn) * scale)
    clearance_board = round(_rule_clearance_dsn(dsn) * scale)
    rooms = route_board_rooms(
        board,
        trace_width=width_board,
        clearance=clearance_board,
        layers=layers,
        shove=shove,
        pack=pack,
    )
    return rooms, scale, [layer.name for layer in dsn.layers]


def build_rooms_routing_result(
    dsn: DsnBoard, *, layers: list[int] | None = None, shove: bool = False, pack: bool = False
) -> RoutingResult:
    """Route ``dsn`` (room track) and convert to a DSN-unit RoutingResult."""
    rooms, scale, layer_names = route_dsn_board_rooms(dsn, layers=layers, shove=shove, pack=pack)
    return _to_routing_result(rooms.result, dsn, scale, layer_names)


def route(
    dsn_text: str,
    *,
    layers: list[int] | None = None,
    engine: str = "grid",
    shove: bool = False,
    pack: bool = False,
    diagonal: bool = False,
) -> str:
    """Route a Specctra DSN string and return the routed SES string.

    ``engine`` selects the routing track: ``"grid"`` (default; the multi-layer
    rip-up grid MVP — highest coverage, kept for backward compatibility),
    ``"exact"`` (orthogonal, exact-geometry, DRC-verified — cleaner output where
    it succeeds), or ``"room"`` (continuous expansion-room — exact free-space
    decomposition, routes off-grid channels the grid/exact tracks cannot).
    ``shove`` (exact and room engines) tries moving existing traces aside; on the
    room engine it also turns on occupancy-aware gate placement.
    """
    dsn = parse_dsn(dsn_text)
    if engine == "exact":
        result = build_exact_routing_result(dsn, layers=layers, shove=shove, diagonal=diagonal)
    elif engine == "room":
        result = build_rooms_routing_result(dsn, layers=layers, shove=shove, pack=pack)
    else:
        result = build_routing_result(dsn, layers=layers)
    return write_ses(dsn, result)
