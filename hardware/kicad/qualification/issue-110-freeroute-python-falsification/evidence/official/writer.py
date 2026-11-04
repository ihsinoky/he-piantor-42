"""Specctra SES session-file writer.

Ports the write path of FreeRouting's ``io/specctra/SesWriter.java`` to operate
on this project's parsed :class:`~freeroute.dsn.model.DsnBoard` plus an
in-memory :class:`~freeroute.ses.model.RoutingResult`. The emitted structure is::

    (session <name>
      (base_design <name>)
      (placement
        (resolution <unit> <n>)
        (component <image> (place <ref> x y front|back rot) ...))
      (was_is)
      (routes
        (resolution <unit> <n>)
        (parser ...)
        (library_out (padstack <name> (shape (...)) (attach off)))
        (network_out
          (net <name>
            (wire (path <layer> <width> x1 y1 ...))
            (via <padstack> x y)))))

FreeRouting's ``SesReader`` (and, in practice, ``kicad-cli pcb import
specctra-ses``) only *require* the ``routes > network_out > net > wire/via``
subtree plus the ``routes`` ``resolution`` for coordinate scaling; the other
scopes are echoed for a well-formed file and skipped on read. Each ``_write_*``
here corresponds to a ``write*`` method in ``SesWriter``.
"""

from __future__ import annotations

import math

from freeroute.dsn.model import DsnBoard
from freeroute.dsn.shapes import Circle, Path, Polygon, Rectangle, Shape

from .indent import Identifier, IndentWriter
from .model import RoutedNet, RoutedVia, RoutedWire, RoutingResult

__all__ = ["write_ses", "write_ses_file"]


def _iround(value: float) -> int:
    """Round half up, matching Java's ``(int) Math.round(x)``."""
    return math.floor(value + 0.5)


def write_ses(
    board: DsnBoard,
    result: RoutingResult | None = None,
    design_name: str | None = None,
) -> str:
    """Serialize ``board`` + ``result`` to a Specctra SES string.

    ``result`` may be ``None`` (or empty) for a valid no-op session that carries
    no wires or vias — enough to prove the DSN-in / SES-out round trip.
    ``design_name`` defaults to the board's pcb name; the session name is the
    design name with a ``.dsn`` suffix rewritten to ``.ses``.
    """
    if result is None:
        result = RoutingResult()

    design = design_name if design_name is not None else board.name
    session_name = design.replace(".dsn", ".ses")
    ident = Identifier(string_quote=board.parser.string_quote)

    out = IndentWriter()
    _write_session_scope(out, ident, board, result, session_name, design)
    text = out.getvalue()
    if not text.endswith("\n"):
        text += "\n"
    return text


def write_ses_file(
    board: DsnBoard,
    path: str,
    result: RoutingResult | None = None,
    design_name: str | None = None,
) -> None:
    """Write the SES output to ``path`` (UTF-8)."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(write_ses(board, result, design_name))


# --- scope writers (mirror SesWriter.write*) ---------------------------------


def _write_session_scope(
    out: IndentWriter,
    ident: Identifier,
    board: DsnBoard,
    result: RoutingResult,
    session_name: str,
    design_name: str,
) -> None:
    out.start_scope(new_line=False)
    out.write("session ")
    ident.write(session_name, out)
    out.new_line()
    out.write("(base_design ")
    ident.write(design_name, out)
    out.write(")")
    _write_placement(out, ident, board)
    _write_was_is(out)
    _write_routes(out, ident, board, result)
    out.end_scope()


def _write_resolution(out: IndentWriter, board: DsnBoard) -> None:
    out.new_line()
    out.write(f"(resolution {board.resolution.unit} {board.resolution.value})")


def _write_placement(out: IndentWriter, ident: Identifier, board: DsnBoard) -> None:
    out.start_scope()
    out.write("placement")
    _write_resolution(out, board)
    for placement in board.placements:
        placed = [p for p in placement.places if p.x is not None and p.y is not None]
        if not placed:
            continue
        out.start_scope()
        out.write("component ")
        ident.write(placement.lib_name, out)
        for place in placed:
            out.new_line()
            out.write("(place ")
            ident.write(place.name, out)
            out.write(f" {_iround(place.x)} {_iround(place.y)}")
            out.write(" front " if place.is_front else " back ")
            out.write(str(_iround(place.rotation)))
            if place.position_fixed:
                out.new_line()
                out.write(" (lock_type position)")
            out.write(")")
        out.end_scope()
    out.end_scope()


def _write_was_is(out: IndentWriter) -> None:
    # No pin/gate swaps are modelled yet, so this scope is intentionally empty.
    out.start_scope()
    out.write("was_is")
    out.end_scope()


def _write_routes(
    out: IndentWriter, ident: Identifier, board: DsnBoard, result: RoutingResult
) -> None:
    out.start_scope()
    out.write("routes ")
    _write_resolution(out, board)
    _write_parser(out, ident, board)
    _write_library_out(out, ident, board)
    _write_network_out(out, ident, result)
    out.end_scope()


def _write_parser(out: IndentWriter, ident: Identifier, board: DsnBoard) -> None:
    # Reduced parser scope (SesWriter passes p_reduced=true): omit string_quote /
    # space_in_quoted_tokens / generated_by_freerouting; echo host_cad/version.
    out.start_scope()
    out.write("parser")
    if board.parser.host_cad is not None:
        out.new_line()
        out.write("(host_cad ")
        ident.write(board.parser.host_cad, out)
        out.write(")")
    if board.parser.host_version is not None:
        out.new_line()
        out.write("(host_version ")
        ident.write(board.parser.host_version, out)
        out.write(")")
    out.end_scope()


def _write_library_out(out: IndentWriter, ident: Identifier, board: DsnBoard) -> None:
    out.start_scope()
    out.write("library_out ")
    for name in board.via_padstack_names:
        padstack = board.padstack(name)
        if padstack is not None:
            _write_padstack(out, ident, padstack)
    out.end_scope()


def _write_padstack(out: IndentWriter, ident: Identifier, padstack) -> None:
    out.start_scope()
    out.write("padstack ")
    ident.write(padstack.name, out)
    for shape in padstack.shapes:
        out.start_scope()
        out.write("shape")
        _write_shape_int(out, ident, shape)
        out.end_scope()
    if not padstack.attach_allowed:
        out.new_line()
        out.write("(attach off)")
    out.end_scope()


def _write_shape_int(out: IndentWriter, ident: Identifier, shape: Shape) -> None:
    """Write a padstack shape with integer coordinates (mirrors write_scope_int)."""
    out.start_scope()
    if isinstance(shape, Rectangle):
        out.write("rect ")
        ident.write(shape.layer, out)
        for c in shape.coords[:4]:
            out.write(f" {_iround(c)}")
    elif isinstance(shape, Circle):
        out.write("circle ")
        ident.write(shape.layer, out)
        out.write(f" {_iround(shape.diameter)}")
        if shape.center_x or shape.center_y:
            out.write(f" {_iround(shape.center_x)} {_iround(shape.center_y)}")
    elif isinstance(shape, Polygon):
        out.write("polygon ")
        ident.write(shape.layer, out)
        out.write(f" {_iround(shape.aperture_width)}")
        for c in shape.coords:
            out.write(f" {_iround(c)}")
    elif isinstance(shape, Path):
        out.write("path ")
        ident.write(shape.layer, out)
        out.write(f" {_iround(shape.width)}")
        for c in shape.coords:
            out.write(f" {_iround(c)}")
    else:  # pragma: no cover - defensive: unknown shape type
        out.write("rect ")
        ident.write(shape.layer, out)
    out.end_scope()


def _write_network_out(out: IndentWriter, ident: Identifier, result: RoutingResult) -> None:
    out.start_scope()
    out.write("network_out ")
    for net in result.routed_nets():
        _write_net(out, ident, net)
    out.end_scope()


def _write_net(out: IndentWriter, ident: Identifier, net: RoutedNet) -> None:
    out.start_scope()
    out.write("net ")
    ident.write(net.name, out)
    for wire in net.wires:
        _write_wire(out, ident, wire)
    for via in net.vias:
        _write_via(out, ident, via)
    out.end_scope()


def _write_wire(out: IndentWriter, ident: Identifier, wire: RoutedWire) -> None:
    out.start_scope()
    out.write("wire")
    _write_path(out, ident, wire.layer, wire.width, wire.coords)
    if wire.fixed:
        out.new_line()
        out.write("(type fix)")
    out.end_scope()


def _write_path(
    out: IndentWriter,
    ident: Identifier,
    layer: str,
    width: float,
    coords: list[float],
) -> None:
    out.start_scope()
    out.write("path ")
    ident.write(layer, out)
    out.write(" ")
    out.write(str(_iround(width)))
    corner_count = len(coords) // 2
    for i in range(corner_count):
        out.new_line()
        out.write(str(_iround(coords[2 * i])))
        out.write(" ")
        out.write(str(_iround(coords[2 * i + 1])))
    out.end_scope()


def _write_via(out: IndentWriter, ident: Identifier, via: RoutedVia) -> None:
    out.start_scope()
    out.write("via ")
    ident.write(via.padstack, out)
    out.write(f" {_iround(via.x)} {_iround(via.y)}")
    if via.fixed:
        out.new_line()
        out.write("(type fix)")
    out.end_scope()
