# EDA-004E — native KiCad authoring feasibility

**PCB_IO_PASS / FRONTEND_UNQUALIFIED — STOP recommended.** Issue
[#79](https://github.com/ihsinoky/he-piantor-42/issues/79) evaluation is complete;
Main qualification, adoption and full migration are not established.
Initial fixture acceptance is **FAIL**, despite successful PCB I/O and saved
object parity. No empty-directory confirmation was allowed after that failure.

## Difference from earlier attempts

The earlier integrated schematic and PR #10 PCB were delivered as KiCad files;
PRs #6/#10 report structural/parenthesis checks and unavailable local KiCad
validation. The original authoring scripts/commands are **unknown**: no retained
writer was found in the inspected trees. A `generator pcbnew` header is not
proof of how a file was authored. PR #6 commits include power-declaration changes,
removal of reference-only circuitry and `f6a1bbac54eb5161fa4ab785c88a3958a320b4f4`
restoring a loadable flash symbol/library identity; these changes include
semantic corrections, not just syntax. PR #10's final CI actually ran 9.0.9:
four schematic ERC reports said zero violations, while PCB DRC reported **587
violations and 40 unconnected items**, exit 1. The individual DRC report was not
retrieved; categories and root causes remain unknown. See retained
[PR metadata and CI raw](../hardware/kicad/qualification/eda-004e/evidence/).
The checker from its immutable commit is a read-only pad/keepout comparison.

**PO supplement:** initial direct KiCad authoring required repeated file-format
hand fixes. **Observed repository facts:** the above changes and failed CI.
**Unconfirmed:** full authoring procedure, every format repair and its cause.
Missing local validation alone does not explain all failures. D-014 retired
those files as fallback/reference; D-012 superseded the old four-layer baseline.

This trial uses **KiCad-owned PCB objects, `FootprintLoad`, `SaveBoard`,
`LoadBoard` and `SETTINGS_MANAGER.SaveProject`**, with one immutable official
footprint. No Circuit JSON converter, handwritten KiCad syntax or post-save
replacement is involved. KiCad owns serialization and can eliminate a class of
version/syntax/parenthesis repair. Explicit pad objects/net assignment avoid the
specific duplicate-land net inference and library-ID collision seen in EDA-004C/D.
This does not automatically solve placement, copper clearance, libraries,
schematic connectivity, pin attributes or routing; those require separate proof.

## Public functions and fixed environment

The [official PCB Python documentation](https://dev-docs.kicad.org/en/apis-and-binding/pcbnew/)
supports standalone PCB loading/saving and says bindings are PCB-only. SWIG
bindings are deprecated from 9; the current published removal plan is 11.
They expose unstable C++-derived interfaces, with no strict major-version
compatibility guarantee. This is a pinned evaluation route, not a stable new
frontend contract.

The [official IPC documentation](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/)
distinguishes 9/10 GUI-connected PCB support from later headless features.
No major-version switch or IPC/GUI trial was performed. Current website text
about later versions is informational only. The
[9.0 CLI manual](https://docs.kicad.org/9.0/en/cli/cli.html) and actual **9.0.9**
help expose `sch erc/export` and `pcb drc/export/render`, not schematic authoring.
Existing schematic ERC and netlist export are available inspection paths;
they do not create a current Main schematic, or prove PCB/schematic parity.
Current-Main ERC and parity were **NOT ENTERED**. No public standalone schematic
create/edit/save path was found for the pinned version. No generic writer was built.

No previous `/tmp/eda004d` environment existed. The unchanged EDA-004D installer
was run once against a new `/tmp/eda004e` root. Binary and binding versions both
identify 9.0.9; the downloaded KiCad package SHA-256 is
`b7e6d33867631dc44385067b703b4c39eadede2037a260790b19495fe17e43f0`.
Dependency package hashes and losslessly aggregated extraction records are
retained; mutable APT dependency availability remains a reproduction limit.
This was an initial rebuild, **not a second fresh environment confirmation**.
DISPLAY/WAYLAND_DISPLAY were unset by the existing capture wrapper.

Official `Resistor_SMD:R_0603_1608Metric` is unchanged from KiCad's official
GitHub library mirror commit `7ebfa6b23cc292a56f751b7b5f4a0e12eeef69dd`, blob
`42ca54ec3dc3f88805cc197193b9b6b463125566`, SHA-256
`effcae403a15810b3a1947b8664576270d6781e7cd525e97c47d48be0fdae8ce`.
Its two pad positions/sizes/roundrect ratios were verified against the frozen
contract after loading. This is a fixed official definition, **not a claimed
9.0.9 library release**; attempted mirror release-tag lookups returned 404.
Original CC-BY-SA 4.0 license/exception is retained with attribution.

## Fixed fixture and measured results

The [contract](../hardware/kicad/qualification/eda-004e/fixture.json) and its hash
were frozen before first creation. The disposable 30 × 24 mm board at
(100,100)..(130,124) uses two copper layers and 1.2 mm thickness. R1 at (106,106)
is rotated 90°; U1 at (115,112) is rotated 30°. Seven physical pads include
roundrect, circle, rectangle and oval shapes, three duplicate `1` GND lands,
one plated oval 0.6 × 1.6 mm drill and one unnumbered 1 mm NPTH. Two explicit
F.Cu GND tracks (2 mm and 4 mm, width 0.20 mm) join U1's GND lands. SIG and GND
each intentionally retain one unconnected cluster link to R1. No earlier
converted PCB is input.

| Item | Result / practical limit |
| --- | --- |
| PCB create/save, separate-process load/save, third-process read | **PASS**; KiCad saved both PCB and project, no syntax corrections |
| Frozen endpoints, nets, physical pads, positions, sizes, rotation, drill/plating, enabled layers, outline, thickness and local tracks | **PASS**; checked independently against fixture contract, identical normalized before/after snapshots |
| KiCad roundtrip bytes | PCB bytes identical; project bytes differ only in `meta.filename` (`fixture` → `roundtrip`); hashes and full field diff retained, no rule/geometry difference |
| Project settings | Public API saves minimum/default clearance and width 0.20 mm, via 0.60/0.30 mm, edge clearance 0.50 mm; no exclusions or severity changes |
| Effective 0.20 mm rule enforcement | **UNQUALIFIED**; predeclared 0.15 mm negative-clearance probe **NOT ENTERED** after STOP; matching project fields are insufficient |
| Actual initial DRC | Two expected unconnected records; **zero other error records, two unexpected warnings**: `silk_over_copper` at U1 default reference and `lib_footprint_issues` for unconfigured Resistor_SMD |
| Initial fixture acceptance | **FAIL**, contract required zero unexpected DRC; warnings retained, not excluded or relaxed |
| Empty-directory regeneration / meaning vs UUID differences | **NOT ENTERED**, initial acceptance did not pass |
| Schematic authoring / current Main ERC | **No public pinned headless authoring path found / NOT ENTERED** |
| Main generation/conversion/routing, Freerouting, fabrication outputs | **NOT ENTERED**, out of scope |

KiCad expands through-hole `*.Cu` layer masks to all copper IDs on load. The
checker initially compared inactive inner-layer IDs as physical board layers.
The correction compares **enabled** layers while the raw board remains unchanged;
the board still has exactly F.Cu/B.Cu. This is a checker API interpretation
correction, not a changed fixture or repaired generated file. Raw failure,
original checker and corrected result are retained.

Two earlier limited call corrections are recorded: create the work root that
the reused installer expects, and obtain design settings from `BOARD` instead
of calling their non-default constructor. Fixture author code was not changed
after first creation. U1's reference placement and project footprint-library
configuration were omitted from the initial authoring flow; the warnings are
real. They may be straightforward future authoring additions, but moving the
field/configuring a library to pass this frozen trial was not attempted.
The underlying schema was parsed successfully; no file-format failure is claimed.

## Representative Main read-only coverage

[Inventory](../hardware/kicad/qualification/eda-004e/evidence/main-inventory.json)
references immutable baseline source and EDA-003C raw by commit/path/hash.
The retained representative Main has **49 components, 197 source ports,
37 nets, 165 source traces**, 193 SMD pads, four plated holes and two NPTHs.
This is historical non-product evidence, not freshly generated or accepted Main.

| Main requirement | Demonstrated / outstanding work |
| --- | --- |
| 15 resistors, 22 capacitors (0402/0603/0805), four circular testpoints | Only one official 0603 and a circle geometry demonstrated; remaining official definitions, values, references, rotations and tolerances unverified |
| RP2040 56 perimeter pads + EP; USBLC6, AP2112K, TPS22919 | Rectangle/roundrect primitive operations demonstrated; exact manufacturer pad mapping, exposed-pad details, pin semantics, NCs and models unverified |
| TYPE-C-31-M-12: shared contacts, four shell lands, two NPTHs | Duplicate pad numbers, explicit GND bonds, one oval PTH and NPTH demonstrated; full USB geometry, shell bond topology and USB DFM remain unverified |
| W25Q16 USON, ABM8 crystal, GH14 with two mechanical lands | Primitive shapes demonstrated; exact footprints/identity, EP/NC distinction, mechanical lands and six physical common-GND returns unverified |
| USB/QSPI, VBUS/V3V3/V1V1/HALL_5V, ADC_A/B/C, WING_EN pull-down and 14-pin interface | Two-net assignment demonstrated only; all 37-net connectivity, electrical pin types/ERC and source-to-schematic-to-PCB reconciliation absent |
| 48 × 44 mm Main, 2-layer/1.2 mm, 0.20 mm physical spacing, via 0.60/0.30 | Small-board outline/thickness and setting serialization demonstrated; effective rules, real Main clearance, vias, routing, rule precedence and exports unverified |

Main source has `schematicDisabled:true`; the old four-key KiCad schematic has
a different architecture/interface and is not a verified current Main asset.
TMUX1208 and Hall keepouts belong to the separate Wing, not this Main trial.
No existing KiCad schematic is restored as authority. Additional work needs a
separately approved schematic/connectivity route first, then exact component
qualification, faithful library setup, effective-rule negative tests, initial
and conditional fresh PCB trials. Routing and manufacturing need their own gates.
Maintenance includes pinned binary/Python ABI/dependency provenance, deprecated
binding adapters, library hashes/licenses and geometry/net/rule regression checks.
Upgrade cost is unknown; no time estimate for Main implementation is asserted.

## STOP, reporting and effort

[STOP record](../hardware/kicad/qualification/eda-004e/evidence/stop-decision.json)
ends experiments at initial DRC warnings; schematic insufficiency independently
keeps the frontend unqualified. After STOP only saved-data review, history/status
updates, validation and PR publication are performed. **Recommendation: STOP
before Main; PO/PMO review this bounded result.** No adoption, Human Gate,
merge/auto-merge or candidate switch is performed.

The [effort ledger](../hardware/kicad/qualification/eda-004e/evidence/effort-ledger.json)
uses first exact clock observation **2026-10-08 22:22:01 UTC**; pre-clock tool
preparation is unknown. Conservatively allocate **0.750 h estimated AI effort**
including final reporting/commit/push/PR/CI reserve. This is not measured active
engineer-hours. Carry forward EDA-004D's **1.786 h** known cumulative estimate:
**2.536 h known cumulative**, nominal **13.464 h** left of the original 16 h.
Historical unquantified review/report corrections, human time and fully unattended
time remain unknown/null; exact totals/remainder cannot be certified. Observed
process elapsed overlaps this session and is not added again. History research
ended within the 20-minute guidance; experiment cutoff reserved reporting time.
Completion time and CI observation are recorded in the PR/ledger.

`python3 -B hardware/kicad/qualification/eda-004e/validate.py`, Dashboard syntax,
`git diff --check` and protected-byte checks validate this report/evidence scope.
They do not qualify the frontend. CI uses unchanged path filters: product
KiCad/layout/firmware checks may be SKIPPED, not a technical PASS. See the PR
for observed current-head CI; no CI configuration was changed.
