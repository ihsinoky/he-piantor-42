# Pinned supported routing surface

Inspected 2026-10-05: Python 3.14.2, jitx 4.4.3, jitxlib-standard 4.4.0,
runtime 4.4.2. [Installed signatures, module hashes and CLI help](routing-surface.json)
are primary evidence. Current official pages are corroboration, not evidence
that a different release's features exist in these pins. Installed official
jitx and physical-layout skills plus control-points reference were inspected;
their 4.2+ claims were checked against installed imports/signatures and builds.

A documented public; B supported experimental; C interactive/manual-only;
D private/unsupported; E unavailable in the inspected pinned public surface.

| Mechanism | Class | Installed evidence / applicability |
| --- | --- | --- |
| `jitx.circuit.Route(source, destination, layer, sketch=None)` | A | circuit.py:466; ports, physical pads, vias and route points accepted; actual builds/capture demonstrate single-layer pathfinding; no user-authored copper segments required for successful requests |
| `Route.Sketch`, sequence of points, `Route.traces` | A | circuit.py:476 onward; terminal/turn hints and computed shapes present; sketch is intent, not a guaranteed connection; captured copper separately observed |
| `jitx.via.Via`, substrate-owned `ThroughVia` | A | via.py; source placement fixes geometry and layer span; full via definitions inherited unchanged; actual two-/four-via experiments |
| `jitx.net.PortAttachment` / `Net += via` | A | net.py; attach signal escapes to ports, plain net membership for power/ground; attachments do not themselves create pad-to-via copper |
| `jitx.controlpoint.RoutePoint`, `PairInsertion`, `PairPoint` | A | controlpoint.py imports/signatures inspected; single/differential route endpoints/control geometry; not a complete-board planner; differential APIs not required/tested on this fixture |
| `Net`, `TopologyNet`, `>>`, SI `Constrain`, routing structures | A | net.py, si.py, constraints.py; connectivity/order, width/clearance/timing/structure intent; neither netting nor topology constraints alone request complete copper; accepted topology/rules unchanged |
| `.at()`, `Circuit.place()` | A | circuit.py; source placement versus deferred relative placement; runtime can adapt routes after movement; no guarantee of routing closure; fixed historical placement retained |
| `jitxlib.via_structures.SingleViaStructure`, `DifferentialViaStructure`, ground cage/antipad helpers | A | installed jitxlib/via_structures/__init__.py; local via construction/placement helpers, not netlist-level placement/fanout/layer planning; not used |
| `jitx.runtime` submit/capture and `RuntimeDesign.query` | B | run/__init__.py explicitly warns experimental; runtime.py public submit/capture/query/nets operations; existing project export observer reused unchanged |
| `jitx design build` / public export plugins / `legacy-kicad` | A | installed help: find/build/export; real non-dry builds and exports; source Route intent regenerates without GUI |
| UI `route`, manual routing, auto-via, interactive move/reposition | C | official board commands and native `jitx ui open`; selection/current layer and user interaction; no documented public headless UI command dispatcher found; not invoked |
| Automatic multilayer netlist planner / public headless auto-via / route-all source helper | E | no such public method found in installed circuit/design/run/CLI or jitxlib helper search; absence is bounded to inspected pins, not a claim about future JITX or physical routability |
| `_websocket`, `_translate`, protobuf messages or direct runtime requests | D | private transport/translation implementation; read-only discovery only; no calls, imports, patches or workarounds used |

Official references:

- [Route / sketches](https://docs.jitx.com/en/latest/api/jitx.circuit.html)
- [Via](https://docs.jitx.com/en/latest/api/jitx.via.html),
  [net / attachment / topology](https://docs.jitx.com/en/latest/api/jitx.net.html),
  [control points](https://docs.jitx.com/en/latest/api/jitx.controlpoint.html)
- [Topological autorouter](https://docs.jitx.com/en/latest/essentials/physical_design/autorouter.html):
  selected objects, one layer at a time; sketches guide topology, runtime computes legal geometry;
  search can fail despite possible alternative routes.
- [UI route](https://docs.jitx.com/en/latest/user-interface/ui-commands/board/route.html),
  [Auto-Via](https://docs.jitx.com/en/latest/user-interface/board-view/auto-via.html)
- [Placement](https://docs.jitx.com/en/latest/essentials/physical_design/kinematic-tree.html),
  [design constraints](https://docs.jitx.com/en/latest/essentials/physical_design/design-constraints.html)
- [Experimental runtime](https://docs.jitx.com/en/latest/api/jitx.run.html)

Early strategy: source `Route` already drives the supported single-layer engine.
Use deterministic nearest-pad trees rather than specifying segment coordinates.
This compact systematic endpoint strategy scales to all required physical pad
islands, including the USB semantic singleton. It does not solve global layer
allocation, fanout, crossing avoidance, reroute ordering or via placement.
After actual downstream failure, test one explicit two-via source escape before
considering expansion. No absence of a single CLI route-all command is used as
the capability verdict.

GUI state is unnecessary for the attempted source workflows. Interactive routing
would instead need a qualified source round-trip: no supported conversion of a
whole GUI-routed board to tracked Python routing intent was established here.
This investigation does not assert that UI routing is impossible or unsupported.
