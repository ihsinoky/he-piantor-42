# Issue #233 — Wing Rev.4 single-sided assembly study

Study only · 2026-11-13 · `issue-233-wing-single-sided` · base `3c4d01bc245d8719facd0fb7f27c2db704c1a82f` (includes D-038).

**Single-sided placement is possible, but this study does not demonstrate a qualified Rev.4 or an installable underside GH harness.** All four independently generated placements put every purchased part and test pad on B.Cu while preserving the fixed geometry. The bounded routing trial fails acceptance on every variant. Separately, the inverted top-entry GH plug plus the inherited R5 cable exit cannot fit above the existing Z2 floor. An internal tray-wall passage is also needed. These are documented failures, not evidence that every possible bottom-side placement is unroutable.

Main Rev.6 is unchanged. Its 62 footprints are on F.Cu, including J2/J3; there are zero B.Cu footprints ([native check and source hash](main-unchanged.json)). Each harness rises at its Main end only. Nothing is ordered, printed, uploaded, pushed or proposed for manufacturing release. D-021, D-033, D-034, D-038 and existing production trees are unchanged. Assembly method remains a later PO decision after Matrix evaluation.

## Inputs and deliverables

Read the [Issue and binding scope comment](issue233.json), `docs/decisions.md` D-021 including its width amendment, D-033/D-034/D-038, and `hardware/case/issue-230-mount-study/REPORT.md`. The latter supplies the E-R post definitions and coordinates; the current case is `hardware/case/issue-228-final/`. Source hashes are in [verification.json](verification.json) and [case input hashes](case/inputs-sha256.json). The current case's separate Fly/USB source-model limitations remain unresolved; this study does not convert its original connector-internal overlaps into an assembly approval.

This REPORT is the entry point. Each `wing-rev4-{16,17}mm-{left,right}/` contains:

- `input.kicad_pcb` / project and `definition.json`: Rev.4 placement contract.
- `routed.kicad_pcb` / project and full `route.log`: raw KRT attempt, **not accepted**.
- `main.kicad_pcb` / project: power-width-normalized, filled diagnostic candidate, **not accepted**.
- `drc.json`, `qualification.json`, `via-pad-all-pairs.csv.gz`, `via-pad-nearest.json`: native and independent results bound to the candidate SHA-256.
- `blocking-regions.json`, `congestion-map.svg`: disconnected pad groups, copper bounds and spatial evidence. Native KiCad coordinates are mm, X right/Y down; Wing-local coordinates are X−100, 100−Y.

The `case/{16,17}mm/` directories contain diagnostic STEP overlays, original-floor GH exit sweeps, conditional under-board routes, study-only tray passage candidates, obstacle-map SVGs, post rescreens and Fly checks. These STEP files are review geometry, not print/order files. No Rev.4 panel/Gerber/CPL package is issued for failing boards.

## Placement, routing and electrical gates

`build.py` starts from each independently generated Rev.3 placement. It flips native footprints at their anchors, preserving pin numbers and nets, rather than mirroring board copper. Hall sensors, their capacitors, key/locator coordinates, four mounting holes, the full mounting copper reservations and every outline segment remain invariant. J_WING is rotated 180° after flipping so its asymmetric mounting lands stay inside the unchanged north tab. MUXs and their capacitors retain their anchors and use physical bottom-side pad transforms. All 15 test pads also move down; probing now requires Wing removal. There are 49 purchased placements and 15 bare test pads per Wing, all on B.Cu. The magnetic switches have no soldered electrical contacts and are installed on top after reflow.

[Placement verification](placement-verification.json) checks all four native inputs against Rev.3. The connector's corrected bottom orientation keeps its mounting lands inside the north tab without moving the outline or a fixed feature.

The routing trial uses the proven KRT front end with escalation off, two copper layers, 1.2 mm PCB, 0.10 mm signals/clearance and ordinary 0.60/0.30 mm vias, plus a 0.15 mm same-net pad target. HALL_5V and GND require 0.30 mm. As in Rev.3, a native normalization step enforces that floor even if KRT rescue emits narrower segments; three GND segments on 16-right and two on 17-right were widened before acceptance checks. No narrow power segment is accepted. Complementary front HALL_5V/back GND pours are filled natively; they are counted as actual copper polygons, never ideal net-name connections. The inherited southern signal/via restriction is retained.

The independent gate is the unmodified Rev.3 `verify.py`, invoked on the study directories by `diagnose.py`. It checks physical required-pad connectivity through tracks, vias and filled zones; wrong-net contacts; material violations; unexplained placement/outline/project transfer; physical pin transforms; width/via floors; and every via against every pad, including same-net, test and NPTH pads. The router's exit status or last reconciliation-subset summary is not acceptance.

| Variant | Native DRC violations¹ / opens | Independent four metrics² | Vias | Minimum via–pad gap, mm | Native ERC | Result |
|---|---:|---|---:|---:|---|---|
| 16mm-left | 1 / 6 | 6 / 0 / 1 / 0 | 117 | 0.120716 | Not run | FAIL |
| 16mm-right | 2 / 0 | 0 / 0 / 2 / 0 | 135 | 0.121002 | Not run | FAIL |
| 17mm-left | 1 / 5 | 5 / 0 / 1 / 0 | 124 | 0.153003 | Not run | FAIL |
| 17mm-right | 0 / 1 | 1 / 0 / 0 / 0 | 133 | 0.119091 | Not run | FAIL |

¹ All severities included: the single violations on the two left boards are dangling-via warnings; the two 16-right violations are clearance errors after enforcing the power width. No exclusion is used to call a board passing. ² Required unconnected / wrong-net contact / material violation / unexplained transfer change. All four final candidates have zero widths below the required floors and zero via–pad pairs below 0.10 mm. Each audit includes all 236 pads. The 17-right minimum meets the requested 0.10 mm yardstick but misses Rev.3's practical 0.125 mm-class target.

**Stop condition:** full routing has not closed at the specified floors. No further local repair or width/clearance relaxation is attempted. Native schematic ERC 0 is **not established**: the inherited Wing package has no native schematic, and these candidates fail the earlier routing gate. [electrical-contract.json](electrical-contract.json) independently verifies GH14 pin order, six returns, three seven-channel MUX groups, NC/S8, supply pins and local decoupling against `hardware/jitx/wing/definition.py`; it is explicitly not a substitute for ERC. Rev.3's extracted resistance and 4.943 V result are not transferred to these boards. Copper resistance, coarse/fine mesh convergence, 127 mA distributed-load voltage and the 200 mm worst-corner power qualification must be rerun after a board actually passes. No Rev.4 voltage margin is claimed.

### Blocking regions

- **16-left, north service fanout:** isolated U_MUX_A.14/GND, U_MUX_B.13/HALL_5V, U_MUX_A.1/MUX_A0, U_MUX_B.16/MUX_A1 and U_MUX_A.2 / U_MUX_C.2/WING_EN. The latter forms three required-pad copper components. A WING_EN via at (131.7,39.0) is dangling. The exact pad/copper groups and bounds are in its `blocking-regions.json`.
- **16-right, Hall-field power corridor:** no disconnected nets, but the required 0.30 mm GND route collides in clearance with the H_B5_RAW via at (83.9,82.1). The two offending GND segments start at (83.5,81.6) and (84.1,81.6). Leaving them at 0.10 mm would conceal the failure.
- **17-left, north service fanout:** GND has three required-pad components, including isolated U_MUX_B.14 and U_MUX_C.14. MUX_A2 has four, including each MUX's pin 15. A MUX_A2 via at (122.9,44.7) is dangling.
- **17-right, north service power escape:** U_MUX_B.14 is isolated from the other GND pads. The nominal zone anchor in native DRC does not identify the physical island; the independent copper groups do.

These results bound one reasonable placement/routing trial. A future attempt may relocate/rotate service MUXs and rebuild their escapes within the invariant geometry, reusing Rev.3's local A* repair pipeline. It must retain the floors and repeat every gate. A right-angle Wing GH header is another mechanical alternative, but changes the footprint/BOM and needs a separate reviewed implementation; it is not silently substituted here.

## North-tab stack and mating procedure

All heights below use PCB underside Z10, PCB top Z11.2 and case floor top Z2. The [JST GH drawing, assembly layout on page 2](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf) gives the top-entry nominal 7.3 mm mated reference. This is not a tolerance-certified complete harness model.

| Underside envelope | Depth below PCB, mm | Lowest Z, mm | Floor gap, mm |
|---|---:|---:|---:|
| Hall field, inherited conservative reservation | 3.4 | 6.6 | 4.6 |
| TMUX, 1.2 body + 0.2 solder allowance | 1.4 | 8.6 | 6.6 |
| Local capacitors, planning reservation | 1.0 | 9.0 | 7.0 |
| GH header + mated housing, nominal | 7.3 | 2.7 | 0.7 |
| GH inherited design reservation | 8.0 | 2.0 | 0.0 |
| Ø5 cable, immediate downward R5 quarter bend | 14.8 | −4.8 | **−6.8** |

The last row is computed by `10−7.3−5−2.5`; even **zero straight lead extension** is assumed. The exact R5 swept diagnostic intersects the original tray at each tab (about 43.781 mm³). The existing 8 mm mated reservation already consumes the entire cavity before a cable bend or tolerance allowance. Premating solves access, not this final seating collision. The Ø5/R5 envelope and a 0.5 mm free-space target remain conservative inherited design requirements; actual wires/plug/latch tolerances have not been measured.

Concrete procedure for an eventual corrected geometry: keep the Wing outside the tray, underside facing up; identify L/R and pin 1, mate the GH housing axially by its housing until latched, then dress and strain-relieve the conductors without pulling contacts. Keep the Main plug free. Lay the harness into the lower channel, seat the prewired Wing on its four bosses/six E-R supports, then install the ties/plate/fasteners. Bring only the Main end upward through the central bay and mate J2/J3 from above. Service requires lifting the Wing before unlatching its underside plug; there is no tool-access opening through the floor. **This sequence cannot presently reach the seated step:** the modeled exit hits the floor. Require at least 0.5 mm clearance around the complete mated/exit envelope, with tolerance allowance, before adopting it.

A floor recess contained within the current 2 mm floor cannot recover 6.8 mm. Changing connector entry direction or the stack/case geometry is a real follow-up decision. Neither raising the PCB/plate nor adding a protruding floor well is treated as authorized baseline work.

## Under-board route, posts, split and slack

[Case summary](case/summary.json) gives exact R5 paths and collisions for both pitches/sides. The conditional floor channel starts at (±27,−41,Z5), passes under the Wing north service field and through the pocket wall, then rises in the central bay at (±7,−20), at the Main end of the route. Its upper approach is Z28.5 and terminates at unchanged Main J2/J3 (±15.5,43,Z18.5). The Ø5 channel has 0.5 mm nominal floor clearance at its horizontal Z5 transit. These paths **do not connect to the actual inverted GH wire exit at Z2.7**; their start represents a hypothetical corrected exit and must not be mistaken for a complete harness.

Checks include the unmodified tray STEP solids (floor, walls, joining bosses and Main ribs), PCB solids, all 42 conservative keycap blocks, underside component envelopes, E-R posts, inherited Main envelopes and actual Main Rev.6 footprint bounds with conservative heights. Intended Main connector terminations are excluded only for their own mating volume. Physical harness OD, actual cap skirts, conductor fanout/latch and the source Fly connector-internal fit remain physical acceptance limits.

The channel hits each internal pocket wall near **|X|=10.50–12.50, Y=−24.89…−18.91, Z=2.50…7.62**, about 31.941 mm³ per side. `tray-*-channel-candidate.step` demonstrates a concrete study-only passage: sweep a 6 mm cutter around the R5 path (0.5 mm radial clearance around Ø5). It removes about 46.85 mm³ per tray; the channel then has zero overlap, the tray remains one valid solid, and removal from Z0–2 is zero. This does **not** fix the north-tab GH exit. Original trays are untouched.

**No E-R post needs moving for this trial.** Each original six-post layout is screened against the new native pad/NPTH map, underside MUX/connector bodies and cable channel. Shafts are Ø3 at Z2.5–10; collars Ø4.5 at Z2–2.5. Minimum contact-to-pad/drill gap is 0.460 mm at 16 pitch and 0.627 mm at 17 pitch; all component/channel overlaps are zero. Exact positions and individual gaps are in each pitch's `post-rescreen.json`. These conclusions apply to this service placement/channel; rerun if either moves. No blind sockets are cut into production floors.

**Split X=3.5 and joining plates:** neither GH route crosses the split, including its Ø5 sweep: the right riser centre is X7, leaving 1.0 mm between tube edge and split. The routes have zero overlap with both bottom splice plates, their raised bosses and the other tray. The study wall opening is away from the bottom joining hardware. No harness is trapped in a joint or routed beneath an external joining plate. The shortened Fly proposal stays at X0 (Ø2), also clear of the split. Case halves can be joined before installing these harnesses; separate/remate the Main plugs before lifting a Wing or splitting the case.

Both pitches have the same conditional GH centreline length **124.355 mm**. Adding 30 mm service/handling allowance gives **154.355 mm** before resolving the actual plug-exit transition. A 200 mm assembly would have **75.645 mm beyond the centreline**, including the 30 mm service allowance, leaving **45.645 mm without modeled storage**. The above-deck rack and GH storage loops are absent from every overlay. No closed loop is counted as connected stored cable. **200 mm storage is not verified.** Flag D-033/D-034's 200 mm procurement specification for a later decision after the exit is resolved; do not order a shortened length from this conditional estimate. There is no valid actual installed length for the blocked current connector geometry.

### Fly EZmate cable

Removing the GH rack also removes the old shared elevated storage arrangement. Each `fly.json` checks a connected Ø2/R5 candidate from the existing underside Fly EZmate endpoint, along the central lower bay, then rising near Y−12 to Z18.2 before approaching Main J4. The shorter candidate clears the original trays/joining hardware, Main/component envelopes, new Wing envelopes/posts and conditional GH paths with zero modeled collision. Length is **71.385 mm (16 pitch)** / **72.765 mm (17 pitch)**; with 30 mm service allowance, **101.385 / 102.765 mm**. The stock 170 mm cable leaves **98.615 / 97.235 mm beyond the centreline**, with no modeled storage. Thus this is a demonstrated shorter route, **not a qualification of the full 170 mm installed cable**. Retaining that cable needs a connected storage design; shortening it needs its own decision. The first low route at X7 hit an internal wall near Y0 and was replaced by this central rise; no source case was edited.

## Deck confirmation

Under the all-B.Cu scheme, **Issue #232's full-cover Wing plate needs no GH connector opening**: the connector, plug and Wing cable transition are below Z10 while the plate occupies Z14.70–16.20, and the 3.50 mm plate-to-PCB-top spacing is unchanged. The outline implication is to derive the full-cover perimeter from the D-037 case exterior, with no north-tab GH notch at (−27,−41)/(27,−41) and no PCB-derived scallops; retain the fixed switch apertures and four tie holes per Wing, plus independently necessary case/split/palm features. This confirms removal of the connector-driven opening, not the yet-unimplemented plate's full case/skirt qualification. It remains conditional on resolving the underside installation blockers; Issue #232 is not implemented here.

## Assembly cost comparison — later PO input, USD

Planning basis: **five left/right paired panels at ONE selected pitch = ten Wings**, 98 purchased placements/panel. This is not an order quote. [costs.py](costs.py) reads the Rev.3 panel BOM and emits [costs.json](costs.json); both pitches have identical part counts. The published [JLCPCB assembly rates](https://jlcpcb.com/help/article/pcb-assembly-price) and [capability table](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) support comparing single-side Economic with double-side Standard. Specific BOM availability, finish, panel acceptance and temperature compatibility have not been approved.

| Method | Cash budget, five paired panels | Cash per Wing pair | Additional owner work |
|---|---:|---:|---|
| Rev.4, Economic, one underside pass | $245.83–482.60 | $49.17–96.52 | File/part acceptance, incoming checks and electrical test |
| Current Rev.3, Standard, two sides | $317.54–551.24 | $63.51–110.25 | Same acceptance/test; double-side process |
| Hand assembly, hot plate/tools owned | $235.90–494.60 | $47.18–98.92 | Assumed 15–30 h for batch, including inspection/rework |
| Hand assembly, buy reflow kit | $275.90–614.60 | $55.18–122.92 | Same labor; $40–120 one-time kit allowance included |

Basis and sensitivity:

- Bare paired-panel allocation is $30–60/batch. Repo quote history (#133) was $9.30/$9.90 per five older **single** Wings; it is an area/lot sanity reference, not a Rev.4 panel quote. Rev.3 panels fit the 250 mm envelope; final Rev.4 panel/DFM/locator-hole pricing needs a new quote.
- Explicit analyst unit ranges: Hall $0.80–1.60, MUX $0.25–0.80, GH $0.80–2.00, capacitor $0.01–0.04. At 42/6/2/48 per panel, parts consume $185.90–389.60 per batch. These are planning assumptions, not current vendor unit-price or stock claims. The same parts allocation is used for all methods.
- Economic includes $8.18 setup, $1.53 stencil, $8.21 multi-design panel fee, three to four Extended feeders at $3.07/type and $2.80 SMT labor. Standard includes $51.12 double-side setup, $16.42 stencils, $8.21 panel fee, four feeders at $1.53/type, $16.42 rigid fixtures, $0.55 packing allowance and the same SMT labor. Joint count is 350/panel, including GH mounting solder lands and excluding bare test pads/NPTH. No leadless-package X-ray allowance is assumed for this exposed-lead BOM. Conditional fees remain subject to vendor review.
- Hand cash includes $10–20 standalone stencil and $10–25 batch consumables. The factory's $1.53 stencil is not supplied to the owner. The **reflow kit note** is material: if a controlled hot plate, thermocouple, paste tools and inspection equipment are not already available, the $40–120 kit allowance is additional; a small heater alone is not a complete process. One-sided boards can sit with the empty top against the hot plate; install switches after soldering. Verify the actual temperature profile and component limits. No kit is selected or purchased. The current double-sided board would need a support fixture/second operation or hand completion and is not assigned the same easy one-pass labor assumption.
- Valuing the assumed 15–30 owner hours at $15–30/h adds $225–900/batch. Hand totals become $460.90–1,394.60 with owned tools, or $500.90–1,514.60 with a new kit. Factory budget savings are mainly process fees; the identical Hall BOM dominates both PCBA ranges.

Exclude freight, tax/import, live MOQ/attrition/stock premiums, keyboard surcharge, design rework/failures, training, switches/plate/case/harness/Main and test equipment beyond the kit allocation. Economic's published single-side capability is not automatic acceptance of a particular panel or part. No assembly method is selected.

## Reproduction, verification and remaining decisions

From repository root:

```bash
E=hardware/kicad/qualification/issue-233-wing-single-sided
python3 "$E/reproduce.py"
# Recheck saved evidence and all pinned inputs without routing or changing CAD:
python3 "$E/verify-study.py"
```

`setup-runtime.py` makes `.issue233-runtime/run` and records the exact KRT source/core hashes and KiCad identity in `toolchain.json`. Defaults reuse the installed read-only `.issue194-runtime` KiCad/KRT/scientific stores and the workspace CAD venv. On another host, override `KICAD_ROOT`, `GEOMETRY_SITE`, `ROUTER_PYTHON`, `KRT_HOME`, `CAD_PYTHON` before running. Required tools are KiCad/pcbnew 9.0.9, the pinned KRT implementation, Shapely/NumPy and build123d/OCP. Logs, XDG data and temporary files remain inside `.issue233-runtime/`. `reproduce.py` runs native generation/normalization/DRC, the unchanged Rev.3 independent audit, placement/logical checks, congestion extraction, case overlays and arithmetic. Rerouting is not needed to inspect the saved failures.

[verification.json](verification.json) distinguishes **evidence consistency** from **design qualification**. Regeneration and checks do not turn expected failing boards/case routes into passing designs. Remaining work before adoption is concrete: a bottom GH exit that fits the fixed stack or an explicitly approved mechanical/connector change; service-fanout/power-corridor routing closure followed by ERC and fresh power extraction; the internal wall passages; and connected storage or revised-length decisions for both GH and Fly cables. The later PO assembly-method and plate/order gates remain separate.
