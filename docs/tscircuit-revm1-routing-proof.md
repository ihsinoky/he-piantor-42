# EDA-003B — representative Rev.M1 routing proof

**BLOCKED — routing-caused physical errors.** The approved JST connector
prerequisite is **RESOLVED**. Both representative boards are implemented, and
the final stock router produces zero electrically required unrouted connections.
That necessary condition is insufficient: Main has seven physical copper
components joining different nets, and both boards retain material routing DRC
errors. The failed results and their manufacturing geometry reproduce exactly.
PMO review accepts this as a valid terminal **BLOCKED** result: the planned
qualification execution is complete, and Issue #61 should close when this
evidence is merged. `qualification_complete = true` means the planned
qualification reached its terminal result; `complete_routing_qualified = false`
means the tested workflow failed routing acceptance and did not achieve PASS.
Full Rev.M1 implementation remains blocked. This report authorizes no adoption,
Human Gate, order, manufacturing release or full Rev.M1 implementation.

The bounded conclusion is: stock tscircuit **0.0.2646**, under the three
representative source-controlled strategies evaluated in EDA-003B, did not
produce a physically valid representative Rev.M1 Main/Wing result. This
demonstrates router failure for the bounded design and strategies; it does not
imply that tscircuit is generally incapable of routing PCB designs.

## Recovery and authority

The original clean preflight was at `d97414b16482990452d9f7bfec9aac25bed5bbd9`,
with that same merge-base/main, the expected branch, and production
`tscircuit 0.0.2646`. The prior prerequisite-STOP commit is
`1626211d2a182a15d208b2a6b4021703e3b9d086`.

Recovery inspected pwd, branch, status, complete tracked diff, log and all
three refs before changing anything. HEAD and the remote issue branch were
`1626211`; `origin/main` remained `d97414b`. Five evidence files were modified;
the new native designs, verifiers, summaries, history copies and compressed
artifacts were untracked. The supplied `BM14B-GHS-TBT.pdf` was the only external
input. All changes were identifiable EDA-003B work. Nothing was reset, cleaned,
stashed, rebased, overwritten by a pull, or discarded. The existing physical
source and retained artifact SHA-256 values matched. Temporary outputs from
the interrupted process were absent, so retained raw artifacts were restored
byte-for-byte for read-only checks, rather than recreating routing attempt 1.

The complete [Issue #61](https://github.com/ihsinoky/he-piantor-42/issues/61),
accepted decisions/status, G0B freeze, architecture, Main/Wing interface,
evaluation plan, DFM policy, native spike, EDA-003A report and existing native
source/checkpoint verifiers were read. No applicable AGENTS.md was found.
Production manifest/lock, frozen four-key source, accepted authority and all
JITX/EDA-003A/KiCad history remain unchanged.

The previous STOP report and every original evidence JSON are preserved
byte-for-byte under [evidence/history](../hardware/tscircuit/qualification/eda-003b/evidence/history/).
The current report supersedes their prerequisite verdict without rewriting it.

## Approved connector evidence and native geometry

The PO supplied the workspace-root `BM14B-GHS-TBT.pdf`, 275,628 bytes:

`1707350a5780a7c8a7b95e67430cc0b8ddda36ebe1a6fb04d6ab4cfc536776d1`

Its manufacturer drawings are KRD-45879-4 R0 (page 1, taped
`BM( )B-GHS-TBT (LF)(SN)(N)`) and KRD-32980-5 R0 (page 2,
`BM( )B-GHS (LF)(SN)`), dated 2024-03-13. The family drawing's explicit
14-position row, the taped-part designation, LF/SN designation and PO approval
establish applicability to **BM14B-GHS-TBT(LF)(SN)**. This is a parametric
manufacturer drawing with a selected 14-position row, not a filename-only
part identification.

It was independently compared with the previously inspected
[JST GH catalogue](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf), SHA-256
`b1dcb317b6b9a4fbbedd2dbf42c64c95306a252d23de8933b85fcf161240b722`, and
with the dimensions in the prior report. No material land-pattern disagreement
was found. The accepted freeze's approximate 4.15 mm height is not used as an
exact case-clearance dimension; the drawing's 4.05 mm and 0.15 mm vertical
profile dimensions are recorded separately. Final enclosure clearance is outside
this disposable fixture.

| Feature | Independently checked native nominal geometry |
| --- | --- |
| Contacts | 14, numbered 1–14; two reinforcement lands are mechanical NCs |
| Pitch/span | 1.25 mm; outer signal centers span 16.25 mm |
| Signal lands | 0.60 × 1.70 mm, top copper; length also agrees with catalogue 5.6 − 3.9 mm |
| Signal centers | x = +8.125 to −8.125 mm in 1.25 mm steps, y = 0 |
| Reinforcement lands | Two 1.00 × 2.80 mm lands, centers (−9.975, −3.35) and (+9.975, −3.35) mm |
| Reinforcement derivation | 1.35 mm from outer signal center to land inner edge, plus half the 1.00 mm width; y from the 5.6 mm pattern and 2.8 mm land dimensions |
| A/B for 14 positions | A = 16.25 mm, B = 20.75 mm |
| Body plan | 20.75 × 4.25 mm, drawn center (0, −2.325) mm |
| Pin 1 / origin | Mounting-surface view; pin 1 at right, native No.1 mark; origin is signal-row midpoint, +x right/+y up |
| Keying/access | Top-entry keyed/shrouded GH; use the accepted 1:1 harness, not a mirrored pin assignment; insertion/latch access is above the board |

The catalogue's mated height is 7.3 mm. Neither drawing establishes an exact
cable bend radius or the product enclosure's access envelope. Main's lowest
reinforcement-land edge is 1.25 mm inside its outline; Wing's connector row
is 4 mm below its top edge, with body/lands extending inward. These fixtures
retain cable access but do not qualify final product edge or enclosure geometry.

[JstGh14.tsx](../hardware/tscircuit/src/qualification/JstGh14.tsx) is project-owned
native geometry. No KiCad footprint, importer, imported placement/routing,
generated Circuit JSON, or JITX geometry is consumed as source. The independent
[geometry verifier](../hardware/tscircuit/scripts/verify-revm1-gh14.tsx) checks
the approved PDF hash and renders a separate native fixture; its literal oracle
checks all 16 lands, signal numbering/pitch/span, reinforcement positions,
body outline and No.1 mark to 0.001 mm. Result:
[connector-geometry-check.json](../hardware/tscircuit/qualification/eda-003b/evidence/connector-geometry-check.json).
The PO-supplied PDF remains a workspace input rather than a redistributed
repository asset. Routing regeneration does not require the PDF; rechecking
its provenance requires that same approved input.

## Actual pinned routing capability

Primary authority is source/types installed by clean `npm ci` from the unchanged
lock, followed by existing Checkpoint C. No latest-version feature was assumed.
The aggregate is **0.0.2646**; the lock resolves core **0.0.1971**, props
**0.0.666**, capacity-autorouter **0.0.919**, checks **0.0.208**, Circuit JSON
**0.0.499** and CLI **0.1.2170**. Source/type hashes and supported surfaces are
in [router-capability.json](../hardware/tscircuit/qualification/eda-003b/evidence/router-capability.json).

- Ordinary `new Circuit()` plus public `autorouter="default"` selects the local
  `AutoroutingPipelineSolver9_PreloadedTraceGraph`; no cloud/network routing
  service is used. `auto`/`auto_local` are also supported presets. Cloud routing
  is a separate platform configuration and was not selected.
- Public board props support two layers, thickness, trace/pad/board-edge/via/drill
  tolerances and via diameters. The fixture uses 0.20 mm trace and trace-to-pad
  rules, 0.30 mm via holes and 0.60 mm via copper. Other rules retain stock defaults
  recorded in actual `pcb_board` data. Rules were never relaxed to obtain PASS.
- Source placement/rotation, trace width/length/via-count/path constraints,
  trace hints and routing phases exist in the installed props. Effort levels
  1x/2x/5x/10x/100x are supported; the bounded sequence used 1x then 5x.
- The router generates top/bottom wire routes and materialized through-via
  records. Blind/buried vias are not enabled. No private API is called.
- Public start/end/error/progress/solver events expose phases and failures.
  Placement errors can skip routing. `renderUntilSettled()` supplies no wall-clock
  deadline; the repository runner imposes 300 seconds and saves partial output
  on timeout. Every retained final process settled before that deadline.
- Supported physical errors cover routing/connectivity, placement/boundary,
  pad/trace/via clearance and keepouts. Warnings are also retained. A successful
  router-end event does not establish a usable PCB.
- Stock CLI Gerber export produces top/bottom copper, outline, plated/NPTH
  drill, BOM and PnP. Existing Bun handles the CLI's Node ESM directory-import
  incompatibility. Approved execution resolved its local-config filesystem
  restriction; neither environment issue is the qualification blocker.

A concrete pinned mismatch is visible in installed code: core's obstacle
conversion skips a `pcb_keepout` when `allow_traces` is true, whereas stock
checks explicitly continue rejecting vias even when `allow_placements` is true.
The unchanged HallKey's keepouts therefore permit traces/pads yet reject the
router's vias. Reading this implementation established capability; none of its
private functions was invoked or changed. No newer release was installed,
qualified or claimed to fix it. Do not continue placement tuning indefinitely
on 0.0.2646. The next investigation should be a separate, explicitly authorized
version-up qualification against these exact EDA-003B blockers, determining
whether a newer stock version fixes:

1. Main wrong-net copper / short generation;
2. Main pad/trace/via clearance failures;
3. Wing via behavior around Hall keepouts;
4. The router/check semantic mismatch where obstacle conversion permits
   behavior that stock validation later rejects.

That experiment is separate work, is not performed in Issue #61, and does not
authorize a production dependency change here.

## Representative design and placement pressure

[revm1-routing-proof.tsx](../hardware/tscircuit/src/qualification/revm1-routing-proof.tsx)
is **disposable routing qualification, non-product, representative subset,
not final Rev.M1 geometry**. Main and Wing are distinct physical boards, each
FR4, **two copper layers, 1.2 mm**.

Main is **48 × 44 mm**, with **49 components/features**. It includes RP2040,
TYPE-C-31-M-12, USBLC6-2SC6 feedthrough ESD and 27 ohm USB resistors,
W25Q16JVUXIQ QSPI flash and CS series resistor, ABM8 clock and loads/series
support, all RP2040 supply/core connections and decoupling, AP2112K 3.3 V
regulator, TPS22919 switched HALL_5V with local input/output decoupling,
three distinct 6.8k/10k/1nF ADC paths, GH14, MUX_A0/A1/A2, one physical WING_EN
with an external 100k pull-down, HALL power-enable pull-down, and SWD/RUN/
BOOTSEL-side bare test-pad access. Unused MCU pins and package NCs are explicit.
USB shield grounding is fixture intent, not a new final-product shield decision.
No unrelated LEDs or feature load was added.

MCU escape occupies the center; USB/ESD occupy the upper left, clock/regulator/
load switch the left, flash the upper region, three analogue filters the right,
and GH14 the lower right. USB, QSPI, power, ADC and shared controls contend for
real two-layer escape and connector access. The final manufacturer-native
RP2040 lands use datasheet Figure 167, page 608, 2025-02-20 build:
0.20 × 0.875 mm at 0.40 mm pitch, outer span 7.75 mm and explicitly connected
3.20 mm square pin-57 EP. Manufacturer source/hash is in environment evidence.
USB, flash and crystal geometry is transcribed from the verified project-native
fixture; the frozen fixture itself is untouched.

Wing is **44 × 44 mm**, with **15 components**: GH14, three TMUX1208PWR, four
unchanged HallKey/DRV5055 sensors, four local Hall capacitors and three local
TMUX capacitors. Hall centers retain the accepted 17 mm grid. Paths A/B/C
receive **2/1/1 sensors**, through TMUX channels rather than directly to ADC.
All muxes share MUX_A0/A1/A2 and WING_EN, with HALL_5V, common GND and distinct
MUX_OUT_A/B/C. Unused mux channels are explicit NCs.

Both GH14s use the accepted G0B pin table, including **six separate physical
return contacts on one GND net**. Wing places the connector above the sensor
array and the three mux packages across the central corridor. Connector control,
power/return and all three analogue paths interact with Hall locating holes and
keepouts. Four sensors already expose routing failures; expansion to 21 is
unjustified. The fixture is easier than full Rev.M1: one Wing enable/connector,
four rather than 21 sensors, fewer unused MCU functions, no product enclosure
or final board contour, and no final USB signal-integrity qualification.
No pours are used to substitute logical ground membership for proved physical
connections. The conclusions are bounded to these outlines and strategies,
not a theorem that other stock-source designs cannot route.

Independent [scope verification](../hardware/tscircuit/scripts/verify-revm1-scope.ts)
checks generated part identities, all GH pins/returns, external enable pull-down,
three ADC networks and the three-mux/four-Hall topology.

## Bounded routing sequence

No board was enlarged, required circuitry deleted, DRC disabled, or rule weakened.
Three materially distinct strategies were used:

| Strategy | Main outcome: unrouted / traces / vias | Wing outcome: unrouted / traces / vias |
| --- | --- | --- |
| 1: compact baseline, stock generic RP2040 QFN, 1x | 119 / 0 / 0; placement/pad overlap skips autorouting | 4 / 52 / 53; ground-land gaps and via/keepout errors |
| 2: manufacturer-native MCU EP/lands, clear initial overlaps, stagger ADC/TMUX placement, 1x | 2 / 127 / 120; shell-ground gaps, two wrong-net copper components and clearance errors | 4 / 52 / 51; ground-land gaps, keepout and hole clearance errors |
| 3: partition QSPI placement, shift central Wing mux, local ground bonds, supported 5x effort | 0 / 128 / 135; seven wrong-net copper components and 76 stock error records | 0 / 56 / 51; 13 stock error records |

The generic first QFN had overlapping peripheral/EP copper and no physical
pin-57 attachment; manufacturer-native geometry corrected that defect rather
than removing power support. Attempt 2's independent copper graph exposed
unbonded duplicate ground lands that logical internal-connection metadata hid.
Attempt 3 adds **five ordinary public source-authored bond traces**: four Hall
SMD-to-PTH bonds, **5.45 mm** distinct copper total, and one USB-shell bond,
**17.00 mm** distinct copper. These local bonds express ground-land intent;
they do not hand-route the signal/power interconnects or replace the router.

Strategy 3 had construction corrections: numeric `pcbPath` points were first
interpreted as global and then as port-relative; the installed implementation
actually transforms them in the anchor component frame. The final path uses
that frame and closes the shell bond along its existing sides, avoiding the
automatically appended endpoint crossing the USB contacts. An initial Wing
capacitor/mux courtyard collision was also cleared. Compact hashes/counts of
all four intermediate board renders are explicitly retained in
[routing-attempts.json](../hardware/tscircuit/qualification/eda-003b/evidence/routing-attempts.json).
These were corrections within the final strategy; no fourth placement search
was performed. Recovery's second fresh render repeats strategy 3 unchanged
solely for reproducibility.

## Physical verification and final metrics

The repository [physical connectivity verifier](../hardware/tscircuit/scripts/revm1-physical-connectivity.ts)
builds required groups from generated source membership, then independently
joins physical pad/trace/via copper geometrically on each layer. It does not
join copper by source trace declarations, annotated endpoints, or internal
logical connections. Thus separate physical lands need copper even when
stock metadata calls them internally connected. Explicit generated NC intent
is required for exclusion; unassigned non-NC ports fail verification.

The fixture coverage includes rectangular/circular SMT, circular/oval PTH,
capsule wire segments and top/bottom through-vias. Unsupported copper fails
closed. Layer transitions require materialized vias with valid spans/diameters.
The independent count sums missing endpoints and extra physical islands;
wrong-net joins are a separate fatal metric, because a short can reduce the
island count while making the electrical result invalid. This is fixture
verification, not a general-purpose fabrication DRC engine.

[Physical-error verification](../hardware/tscircuit/scripts/verify-revm1-routing-proof.ts)
inspects every emitted `*_error`/warning and runs public stock placement/routing
checks on an in-memory clone. The source file is hashed before/after; no repairs
or modified generated data are saved. Placement checks include boundary,
via-in-pad and copper/keepout checks. Twelve independent fault fixtures prove
that copper gaps, false endpoint annotations, missing vias, shorts, layer
mismatches, internal logical shortcuts and unsupported geometry cannot pass.

| Final metric, identical in runs 1 and 2 | Main | Wing |
| --- | ---: | ---: |
| Source nets | 37 | 13 |
| Required physical endpoints | 167 | 69 |
| PCB traces | 128 | 56 |
| PCB vias | 135 | 51 |
| Intentional NC ports | 30 | 25 |
| `electrically_required_unrouted_count` | **0** | **0** |
| Wrong-net copper components | **7** | 0 |
| Invalid layer transitions / unsupported geometry | 0 / 0 | 0 / 0 |
| Final emitted physical error records | **76** | **13** |

Main emits 2 `pcb_pad_pad_clearance_error`, 11 `pcb_pad_trace_clearance_error`,
19 `pcb_trace_error`, and 44 `pcb_via_trace_clearance_error` records. The
independent wrong-net components join: V3V3/USB_DP/QSPI_SD0/QSPI_SD2;
MUX_A0/MUX_A2; GND/ADC_A; V1V1/USB_DM; ADC_B/ADC_C;
QSPI_SD3/QSPI_SCLK; and QSPI_SD1/QSPI_SS_MCU. Stock records also explicitly
report accidental copper contact. None is an accepted product-risk exception.

Wing emits 12 `pcb_placement_error` records for **six vias**, each contacting
top and bottom Hall keepouts, plus one `pcb_trace_error`: the MUX_A2 path is
0.134 mm from a Hall locating hole under a 0.20 mm rule. These are routed via/
trace failures, not remaining initial component placement errors. Both final
boards have no emitted or stock-check board-boundary/autorouting failure and
no independent invalid via span or layer transition. Missing courtyards,
underspecified power/pin metadata and the generic connector-access warning
are retained separately; top-entry access interpretation comes from JST, not
that generic orientation warning. No diagnostic was suppressed to claim PASS.

**USB NPTH — OPEN — PRE-ORDER DFM REVIEW REQUIRED.** The accepted USB pad,
stake and NPTH geometry is unchanged. No new tool-specific geometry corruption
was found. Attempt 2's additional routed trace-to-USB-hole clearance failure
was classified as routing-created; the pre-existing product geometry risk
was not blamed for the final verdict. Final Main emits no trace-to-USB-NPTH
error, and the independent shorts alone prohibit a complete-routing
qualification PASS. They do not make the completed BLOCKED qualification
execution incomplete.

## Manufacturing and two fresh-run reproducibility

Once zero-unrouted final routing existed, stock CLI export was exercised on
both boards as **diagnostic output**, including Main's known shorts. This is
not a manufacturing release, order package or physical-validation acceptance.
The existing native export mechanism generates F_Cu, B_Cu, Edge_Cuts,
plated/NPTH drill, BOM and PnP without generated-data/Gerber edits.

The read-only [manufacturing verifier](../hardware/tscircuit/scripts/verify-revm1-manufacturing.py)
checks every routed segment's coordinates, layer and width against actual
Gerber draws: **1,135 Main segments and 482 Wing segments**. All **135/51 vias**
appear in both copper layers and plated drill; all **16 connector lands** per
board survive; the complete rectangular outline survives. Every assembly
land is checked too: **193/90 SMT lands**, and all four plated lands per board
(including Main's shell slots and Wing's Hall PTHs) survive in copper/drill.
Every assembly
component has BOM/PnP rows. Main's four source-authored bare copper test pads
need no assembly part, are intentionally absent from BOM/PnP, and their actual
copper flashes are verified separately. Gerber has no net names: checking
every source physical segment establishes that no required routed path is
lost during export. Supplier-specific PnP rotations and complete procurement
identities remain unqualified, as explicitly recorded.

Two fresh generator processes per board use identical physical source/lock
hashes. The first process's retained Circuit JSON and generation evidence were
integrity-checked and restored without modification after interruption; the
second ran in newly absent output directories, using new Circuit instances
in separate processes. It was not a second render in one in-memory process.

Raw Circuit JSON SHA-256 is **identical** across runs:

- Main: `1f9c600a0203c968f37eec4fe1d8fe49661092ee5cde1f6cd77b4cc94c8ac7b9`
- Wing: `71034f787cfc97be72436d0b20a4a01dad508fd19782f5de49119fa0a9b2e69e`

The [reproducibility verifier](../hardware/tscircuit/scripts/verify-revm1-reproducibility.py)
compares normalized board/placement/pad/route/via/layer/mechanical data,
source requirements, counts and independent connectivity. Numeric geometry
is not rounded; IDs/record order are removed and component/port identities
resolved. Manufacturing comparison retains all copper/drill/aperture instructions,
removing only the pinned exporter's creation-date lines/comments; ZIP ordering
and container timestamps are ignored. All copper, outline, drill, BOM and PnP
normalized comparisons match. Six metamorphic checks distinguish harmless
ID/order/timestamp changes from pad motion, lost vias, changed NC intent or
changed copper coordinates. Raw and material/category hashes are recorded in
[reproducibility.json](../hardware/tscircuit/qualification/eda-003b/evidence/reproducibility.json).
The physical failures reproduce too; reproducibility does not waive them.

## AI/source-control assessment

1. Placement, net intent, NCs, constraints and the small ground bonds are
   reviewable native TSX; no hidden GUI state is required.
2. Stock autorouting produces actual multilayer copper and automatic vias
   headlessly, but the representative result is **not usable** with its shorts
   and clearance/keepout errors.
3. Codex responded to observed failures through native footprint corrections,
   coherent placement changes, supported effort and local source bonds.
4. Public phases, generated errors, stock checks and an independent copper graph
   expose enough failures to guide bounded iteration. Router completion alone
   and logical internal connections are insufficient.
5. Both physical routing and downstream material exports reproduce exactly
   from the locked source in two fresh processes, including their failures.
6. Only five local bond traces were handwritten. There is no hand-built global
   route geometry; the amount needed to obtain a valid full Rev.M1 remains unknown.
7. Routine Rev.M1 maintenance without an interactive EDA is unqualified because
   these bounded stock-source strategies do not produce valid physical routing.
8. Accepted [JITX C4B5](../hardware/jitx/physical/EDA-002C4B5.md) retained 39
   downstream unconnected items and a dangling via and did not demonstrate a
   supported public headless global multilayer router. Here stock tscircuit
   demonstrates that surface, automatic vias and reproducible zero-deficit
   copper, but **does not close the project's usable complete-routing workflow
   gap** because of material shorts/DRC errors. This is a project-specific
   qualification outcome, not a general superiority or impossibility claim.

## Validation, retained evidence and review boundary

Clean `npm ci` succeeded from the unchanged lock (298 packages). Installed pin
and source hashes remain consistent after recovery; no dependency change
requires another install. Native Checkpoints A/B, Checkpoint C generation and
the frozen M1 electrical verifier all pass. Connector/scope verification,
12 physical-verifier fault fixtures, both fresh final generation processes,
diagnostic export checks and both two-run comparisons pass their respective
execution/integrity checks. Qualification physical verifiers deliberately exit
nonzero on the retained failures. `git diff --check` passes.

Manifest and lock remain byte-identical to baseline with **0.0.2646**. Frozen
`m1-four-key.tsx`, HallKey, accepted EDA-003A report/evidence, JITX evidence,
old KiCad assets and accepted authority are byte-unchanged. Historical STOP
copies are byte-verified against `1626211`. No production upgrade, generated-data
edit, external router, fork/private API or GUI state is used. No PR, new Issue,
merge, order, D-018, EVT-002 start or Human Gate change is made. Accepted
decision/project-status files remain unchanged; PMO's acceptance of this
terminal technical result does not authorize full Rev.M1 implementation.

Compact evidence includes the connector/scope results, three-strategy summaries,
final/run-2 physical summaries, source/package hashes, manufacturing summaries,
reproducibility hashes and classification. The two first-run Circuit JSONs are
retained compressed because their actual geometry proves the material errors;
small diagnostic export archives in byte-identical gzip wrappers allow
deterministic independent verification. Original local ZIPs remain preserved
and ignored; the artifact manifest records exact uncompressed hashes.
Duplicate raw run-2 boards/archives are omitted because their material hashes
match; regeneration commands follow. The approved PDF remains a preserved
user-supplied workspace input.

From `hardware/tscircuit`, with Bun 1.2.22 and Python 3 available:

```sh
npm ci
bun scripts/verify-revm1-gh14.tsx /tmp/connector-check.json
bun scripts/test-revm1-physical-connectivity.ts
bun scripts/generate-revm1-routing-proof.tsx main 3 /tmp/proof-run1-main
bun scripts/generate-revm1-routing-proof.tsx wing 3 /tmp/proof-run1-wing
bun scripts/generate-revm1-routing-proof.tsx main 3 /tmp/proof-run2-main
bun scripts/generate-revm1-routing-proof.tsx wing 3 /tmp/proof-run2-wing
bun scripts/verify-revm1-scope.ts /tmp/proof-run1-main/circuit.json /tmp/proof-run1-wing/circuit.json /tmp/scope.json
```

For each of the four generated directories, use these read-only checks/export
(the physical verifier's exit 1 is expected for this retained result):

```sh
bun scripts/verify-revm1-routing-proof.ts "$proof_dir/circuit.json" "$proof_dir/summary.json"
bun node_modules/@tscircuit/cli/dist/cli/main.js export "$proof_dir/circuit.json" --format gerbers --output "$proof_dir/manufacturing.zip"
python scripts/verify-revm1-manufacturing.py "$proof_dir/circuit.json" "$proof_dir/manufacturing.zip" "$proof_dir/manufacturing-summary.json"
```

Compare corresponding fresh runs:

```sh
python scripts/verify-revm1-reproducibility.py /tmp/proof-run1-main /tmp/proof-run2-main /tmp/main-reproducibility.json
python scripts/verify-revm1-reproducibility.py /tmp/proof-run1-wing /tmp/proof-run2-wing /tmp/wing-reproducibility.json
```

Primary classification: **BLOCKED** — current representative stock-routing
short/clearance/keepout failures after the bounded sequence. Connector evidence
is resolved. PMO accepts the terminal technical result; qualification execution
and qualification are complete with BLOCKED, while complete-routing PASS was
not achieved. Issue #61 should close when this evidence is merged (`Closes #61`).
Full Rev.M1 implementation remains blocked; any version-up qualification is
separate, explicitly authorized work.
