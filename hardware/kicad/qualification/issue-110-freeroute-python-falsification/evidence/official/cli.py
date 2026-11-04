"""freeroute command-line interface: Specctra DSN in, routed SES out.

Flag-compatible with the FreeRouting JAR (``-de`` / ``-do`` / ``-mp``) so it can
be dropped in wherever ``java -jar freerouting.jar`` was invoked, plus the
freeroute-specific engine selection (``--engine``) and its opt-in passes.

Not every engine supports every pass. The matrix below is the single source of
truth; an unsupported combination is an error, never a silent no-op::

    engine   --pack  --shove  --diagonal  --no-rip-up  -mp/--max-passes
    grid       no      no        no          yes            yes
    exact      no      yes       yes         yes            yes
    room       yes     yes       no          no             no
"""

from __future__ import annotations

import argparse
import sys

from freeroute.dsn.reader import parse_dsn
from freeroute.route.pipeline import (
    build_exact_routing_result,
    build_rooms_routing_result,
    build_routing_result,
)
from freeroute.ses import write_ses

#: which optional flags each engine actually implements. Anything not listed for
#: an engine is rejected by :func:`_validate` rather than quietly ignored.
ENGINE_OPTIONS: dict[str, frozenset[str]] = {
    "grid": frozenset({"rip_up", "max_passes"}),
    "exact": frozenset({"shove", "diagonal", "rip_up", "max_passes"}),
    "room": frozenset({"shove", "pack"}),
}

#: option key -> the CLI spelling to name in an error message
_FLAG_NAMES = {
    "pack": "--pack",
    "shove": "--shove",
    "diagonal": "--diagonal",
    "rip_up": "--no-rip-up",
    "max_passes": "-mp/--max-passes",
}


def _supported_by(option: str) -> str:
    engines = [e for e, opts in ENGINE_OPTIONS.items() if option in opts]
    return " or ".join(f"--engine {e}" for e in engines)


def _validate(parser: argparse.ArgumentParser, engine: str, requested: list[str]) -> None:
    """Reject any requested option the selected engine does not implement."""
    supported = ENGINE_OPTIONS[engine]
    for option in requested:
        if option not in supported:
            parser.error(
                f"{_FLAG_NAMES[option]} is not supported by --engine {engine} "
                f"(supported by: {_supported_by(option)})"
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="freeroute",
        description="Native PCB autorouter — route a Specctra DSN and write an SES session file.",
    )
    parser.add_argument("dsn", nargs="?", help="input Specctra .dsn file")
    parser.add_argument(
        "-de", "--design", dest="design", help="input .dsn (FreeRouting-compatible alias)"
    )
    parser.add_argument(
        "-do", "-o", "--output", dest="output", help="output .ses file (default: stdout)"
    )
    parser.add_argument(
        "-mp",
        "--max-passes",
        type=int,
        default=None,
        help="rip-up-and-retry pass bound (grid and exact engines; default 10)",
    )
    parser.add_argument(
        "--engine",
        choices=sorted(ENGINE_OPTIONS),
        default="grid",
        help=(
            "routing track: grid (default; multi-layer rip-up maze, highest coverage), "
            "exact (orthogonal, exact-geometry DRC-verified output), "
            "room (continuous expansion rooms, routes off-grid channels)"
        ),
    )
    parser.add_argument(
        "--pack",
        action="store_true",
        help="coordinated multi-trace channel packing (room engine only)",
    )
    parser.add_argument(
        "--shove",
        action="store_true",
        help="shove committed traces aside to recover dropped nets (exact and room engines)",
    )
    parser.add_argument(
        "--diagonal",
        action="store_true",
        help="45-degree recovery pass for dropped 2-pin nets (exact engine only)",
    )
    parser.add_argument(
        "--no-rip-up",
        action="store_true",
        help="disable rip-up-and-retry (grid and exact engines)",
    )
    parser.add_argument("--layers", help="comma-separated signal layer indices to route on")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    dsn_path = args.design or args.dsn
    if not dsn_path:
        parser.error("no input DSN (pass a path, or -de <file>)")

    requested = [
        option
        for option, asked in (
            ("pack", args.pack),
            ("shove", args.shove),
            ("diagonal", args.diagonal),
            ("rip_up", args.no_rip_up),
            ("max_passes", args.max_passes is not None),
        )
        if asked
    ]
    _validate(parser, args.engine, requested)

    try:
        layers = [int(x) for x in args.layers.split(",")] if args.layers else None
    except ValueError:
        parser.error(f"--layers must be comma-separated integers (got: {args.layers!r})")

    try:
        with open(dsn_path, encoding="utf-8") as f:
            dsn_text = f.read()
    except OSError as e:
        print(f"freeroute: cannot read {dsn_path}: {e}", file=sys.stderr)
        return 2

    dsn = parse_dsn(dsn_text)
    rip_up = not args.no_rip_up
    max_passes = args.max_passes if args.max_passes is not None else 10

    if args.engine == "exact":
        result = build_exact_routing_result(
            dsn,
            layers=layers,
            shove=args.shove,
            diagonal=args.diagonal,
            rip_up=rip_up,
            max_passes=max_passes,
        )
    elif args.engine == "room":
        result = build_rooms_routing_result(dsn, layers=layers, shove=args.shove, pack=args.pack)
    else:
        result = build_routing_result(dsn, layers=layers, rip_up=rip_up, max_passes=max_passes)

    ses_text = write_ses(dsn, result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(ses_text)
    else:
        sys.stdout.write(ses_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
