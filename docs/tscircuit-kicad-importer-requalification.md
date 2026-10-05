# EDA-003A — KiCad footprint importer requalification

Issue [#58](https://github.com/ihsinoky/he-piantor-42/issues/58) is an isolated
footprint-import fidelity spike. The current importer still silently loses both
Hall copper-pour keepouts. It also halves the source rounded-pad corner radius.
Importer reuse is **not recommended** at this version. The defects have bounded
upstream diagnostic/conversion boundaries; a contribution is recommended in a
separately authorized issue. No upstream PR, fork, or source modification was made.

## Baseline and authority

Before editing, the working tree was clean, the branch was `main`, and HEAD,
`origin/main`, and the network remote `refs/heads/main` all matched:

`7d7f3cffe4fb98771e3ca47f800a54de22fa8c4f`

The complete Issue #58 body and all comments were read (zero comments at the
2026-10-05 inspection). Issue #13, its Human Gate comment, PR #16, D-013,
project status, the native spike report, production manifest/lock, HallKey,
Checkpoint A verifier, and the exact source asset were inspected before the
experiment. This branch is `eda-003a-kicad-importer-requalification`.

Production authority remains:

`requirements / datasheets / approved geometry -> native TSX -> stock tscircuit`

This result does not authorize full-board KiCad migration, old PCB placement or
routing reuse, Rev.M1 implementation, or a G0B decision. A future qualification
could admit only verified footprint/library asset -> qualified importer ->
validated geometry -> native design. Old KiCad boards remain historical/reference
material. No JITX execution was performed.

## Exact versions and input

| Path | Importer | Result / context |
| --- | --- | --- |
| Historical Issue #13 / PR #16 | `0.0.117` | Accepted STOP 1: two keepouts lost; basic pads, holes, duplicate numbering and Y-inverted alignment preserved |
| Production lock / installed dependency tree | `0.0.117` | Direct dependency of `tscircuit 0.0.2646`; newly inspected with the same read-only verifier |
| Published upstream experiment | `0.0.142` | Published `2026-10-02T09:38:40.520Z`; exact-pinned only in the isolated spike |
| Published tscircuit, context only | `0.0.2745` | Queried on 2026-10-05; not installed or substituted for production |

The upstream npm package reports repository
[tscircuit/kicad-to-circuit-json](https://github.com/tscircuit/kicad-to-circuit-json)
and `gitHead` **`967a8c823d8d19cdf18060fd7b66ce5d79e91c12`**. This is the
package's reported commit identity, not an inferred release tag. Tarball URL,
integrity, publication timestamp, and the complete resolved spike package version
list are in [version-matrix.json](../hardware/tscircuit/spikes/eda-003a/evidence/version-matrix.json).

The package declares only a TypeScript peer and omits its four external runtime
imports from `dependencies`. The spike explicitly supplies exact versions:
`@flatten-js/core 1.6.14`, `@tscircuit/circuit-json-util 0.0.120`,
`kicadts 0.0.58`, `transformation-matrix 2.16.1`, and `typescript 5.9.3`.
The independent lock also resolves `circuit-json 0.0.517`, `zod 3.25.76`, and
other transitive packages. These are experiment support dependencies, not a
production upgrade. Resolution assertions and a separate clean `/tmp` install
prove the upstream run does not borrow production dependencies. The project run
uses the existing production importer and its existing dependency environment.

Input, unchanged:

`hardware/lib/third_party/marbastlib-he.pretty/SW_MX_HE_0deg_1u.kicad_mod`

SHA-256: **`168d915310d9fecaf19d33d130a9171f296b2a3aa3d0447e9f064535e406190a`**.
The experiment verifies this digest before conversion. No source adjustment,
output patch, coordinate correction, replacement hole, or recreated keepout was
used. Fault injections operate exclusively on a separate synthetic test fixture.

Historical evidence was found before reproduction:
[Issue #13 Human Gate](https://github.com/ihsinoky/he-piantor-42/issues/13#issuecomment-5899763565),
[PR #16](https://github.com/ihsinoky/he-piantor-42/pull/16), and
[D-013](decisions.md#d-013---eda-backend-evaluation-strategy).
The historical verdict is retained unchanged. Since the project still resolves
that version and it is directly usable locally, the requested project-path test
was run once through the new verifier; historical CI was not recreated. The
additional rounded-copper check below is new evidence, not a rewritten claim
about what the historical verifier checked.

## Geometry comparison

The accepted native [HallKey](../hardware/tscircuit/src/components/HallKey.tsx)
and [Checkpoint A verifier](../hardware/tscircuit/scripts/verify-native-hall-checkpoint-a.tsx)
provide pad/hole dimensions and relative geometry. Absolute tolerance is
**0.001 mm**. The exact source zones, rather than the native conservative
rectangles, are the keepout polygon oracle.

Both tested versions produce the same required basic copper/drill records:

| Category | Expected and observed | Machine result |
| --- | --- | --- |
| SMD count / numbers | 3, hints `1`, `2`, `3` | PASS |
| SMD dimensions / layer / orientation | Each `1.475 x 0.6 mm`, top, zero effective rotation | PASS |
| SMD XY in importer coordinates | 1 `(-0.9375,+0.95)`; 2 `(-0.9375,-0.95)`; 3 `(+0.9375,0)` mm | PASS, Y inverted relative to native oracle |
| Rounded-pad copper | Source radius `0.15 mm`; output `corner_radius=0.075 mm` on all 3 pads | FAIL |
| PTH count / pin / plating | 1 circular `pcb_plated_hole`, hint `3`, top/bottom copper | PASS |
| PTH dimensions / XY | Drill `0.3 mm`, outer `0.6 mm`, `(2.3,0)` mm | PASS |
| NPTH count / drill / XY | 2 circular `pcb_hole`, `1.7 mm`, `(-5.08,0)` and `(+5.08,0)` mm; no copper port | PASS |
| Distinct physical pin-3 features | Separate SMD and PTH records and separate `pcb_port` IDs; both reference the same logical source-port identifier | PASS for standalone footprint physical/hint semantics |
| Origin / transform | Origin `(0,0)`, rotation `0`, X unchanged, Y inverted | PASS |
| Top / bottom keepouts | 2 required; 0 output records | FAIL |

The NPTH source pad `size=1.6 mm` is not its drill: the verified mechanical hole
is `drill=1.7 mm`. The verifier checks drill geometry and record-type plating
semantics, not an inferred copper annulus for NPTH.

KiCad defines rounded-pad radius as minimum pad dimension multiplied by radius
ratio: `0.6 * 0.25 = 0.15 mm`. Its
[primary PADSTACK implementation](https://github.com/KiCad/kicad-source-mirror/blob/master/pcbnew/padstack.cpp)
implements that calculation in `PADSTACK::RoundRectRadius`. Upstream
`process-pads.ts` instead divides the product by two. This changes physical copper
beyond the tolerance and cannot be called a non-material limitation merely
because the rectangular bounding dimensions pass. The native oracle deliberately
uses rectangular pads, so this additional source-specific check is kept separate.

The standalone importer creates four physical ports but **zero `source_port`
records**. Their logical source-port IDs are unresolved within this output. Shared
pin-3 IDs and hints preserve numbering intent; this is not a demonstrated connected
electrical circuit or parity with native Checkpoint A's resolved source ports and
`source_component_internal_connection`. No source electrical graph is repaired or
claimed qualified by this spike.

A separate synthetic input with footprint `(at 10 20 90)` and pad `(at 1 2 90)`
verifies origin normalization to `(0,0)`, component rotation `90`, pad XY `(2,1)`,
and swapped rectangular dimensions `0.6 x 1.475 mm`. The historical input has
zero rotation; the synthetic probe establishes a nontrivial transform without
editing it. No placement/routing migration is attempted.

## Keepouts and warning behavior

The pinned `kicadts 0.0.58` parser retains both zones, their permissions, and all
12 arcs. Compact start/mid/end coordinates are recorded in
[geometry-comparison.json](../hardware/tscircuit/spikes/eda-003a/evidence/geometry-comparison.json).

- `HE keepout_bot` actually declares **F.Cu**: top copper, eight arcs, with a
  right-side notch. Its name is not its layer authority.
- `HE keepout_top` declares **B.Cu and In1.Cu–In30.Cu**: bottom and internal
  copper, four outer corner arcs. On the project's two-layer baseline, bottom
  remains mandatory. No internal-layer reuse is qualified.
- Both have the outer envelope `4.0 x 3.6 mm` centered at `(0,0)`. Tracks, vias,
  pads and footprints are allowed; copper pours are not allowed.

Both importers emit **zero `pcb_keepout` and zero `pcb_copper_pour`** records.
Neither zone geometry nor copper-pour exclusion survives conversion. No downstream
pour exclusion can be demonstrated from nonexistent records. The verifier rejects
missing records, layer mistakes, warning-only records, changed permissions, and
polygon/notch discrepancies. Its polygon assertion compares sampled quarter-circle
boundaries and connecting edges bidirectionally within 0.001 mm. It never supplies
that geometry to the converter or a native design. Native conservative rectangles
are accepted historical native geometry, not exact replacements for these zones.

Answers for the current upstream importer:

1. Successful keepout conversion is **not observed**, so warnings on a successful
   keepout conversion cannot be assessed.
2. Failed/unsupported keepout conversion produces **no specific warning**.
3. `getWarnings(): string[]` is callable and can be machine-gated; this asset
   returns **`[]`**. Captured `console.warn` and `console.error` are also empty.
   Rejecting only nonempty warnings would incorrectly accept this asset.
4. Manufacturing-significant silent loss exists: both keepouts and rounded-pad
   copper geometry fail. The fidelity gate exits nonzero despite converter success.
5. Other observed omissions have no warnings: pad-3 SMD/PTH `zone_connect=2`,
   the SOT-23 STEP model, and Dwgs.User/Eco2.User reference graphics. Solid-fill
   pad connection policy is not represented in imported pad records; future
   pour behavior remains unqualified. The 3D model/reference graphics are not
   missing copper/drill features. The PTH's source layer list is `*.Cu` without
   `*.Mask`; mask/paste fabrication behavior is not qualified by this geometry
   spike. No broad claim of manufacturing equivalence is made.

A Manufacturer-property probe does produce a specific unsupported-property
warning. That verifies the warnings API is functional, while demonstrating that
it does not comprehensively report omissions. See
[warnings.json](../hardware/tscircuit/spikes/eda-003a/evidence/warnings.json).

## Reproduction and validation

Commands run from the repository root unless noted:

```sh
git status --porcelain=v1
git branch --show-current
git rev-parse HEAD
git rev-parse origin/main
git ls-remote origin refs/heads/main
gh issue view 58 --repo ihsinoky/he-piantor-42 --json title,body,comments,url
gh issue view 13 --repo ihsinoky/he-piantor-42 --json title,body,comments,url
gh pr view 16 --repo ihsinoky/he-piantor-42 --json body,comments,files
npm ls tscircuit kicad-to-circuit-json --json --prefix hardware/tscircuit
npm view kicad-to-circuit-json@latest --json
npm view tscircuit@latest version --json
```

Only discovery uses `latest`; committed dependency versions are exact and locked.
To reproduce the committed experiment:

```sh
cd hardware/tscircuit/spikes/eda-003a
npm ci --ignore-scripts --no-audit --no-fund
npm run check
npm run experiment
npm test
npm run verify
```

`experiment` records the observation and exits zero when execution succeeds;
**`verify` is the adoption safety gate and currently exits 1** for fidelity
failure. Tests assert rejection rather than confusing reproducible failure with
successful qualification. `node experiment.mjs --raw` optionally saves untouched
raw output under ignored `raw/`; it is unnecessary for committed evidence. The
project-path experiment requires the existing production install; from a fresh
checkout first run `npm ci --prefix hardware/tscircuit` without changing its lock.

Validation actually completed:

- Independent lockfile `npm ci`: PASS (12 packages); clean `/tmp` install with no
  parent node_modules and actual converter smoke: PASS, reproduces keepout loss.
- Project and upstream converter experiments: executed successfully; fidelity FAIL
  in both. Evidence retains material records/counts, not large raw output.
- Node syntax checks for all three new `.mjs` scripts: PASS. No TSX was edited;
  no new TypeScript compilation or Bun runtime is required.
- **18 Node tests PASS**, including 11 focused fault injections. Missing SMD,
  missing NPTH, both incorrect plating directions, displacement `0.002 mm`, missing
  keepout, wrong layer, ineffective keepout, wrong polygon, wrong corner radius,
  and collapsed duplicate port are all rejected. A fully synthetic positive fixture
  passes first. Additional controls check tolerated displacement, nonfinite input,
  warnings, actual loss, rotation/origin, the minimal reproducer, and a real upstream
  warning. See [negative-controls.json](../hardware/tscircuit/spikes/eda-003a/evidence/negative-controls.json).
- Strict fidelity gate: expected exit **1**, verified by the shell.
- Deterministic evidence regeneration and `git diff --check`: PASS.
- Production manifest/lock and source asset digest assertions: PASS; production
  dependency diff is empty. The native Checkpoint A regression is not required
  because no native code or shared utility was changed. Bun is absent locally;
  its historical accepted evidence is used as the oracle, not reported as rerun.

Production `package.json` SHA-256 remains
`6221aa0f87f0a13f2d4abb9824533d269b90c76d77b8db1df6de13ddb19ba467`;
production lock SHA-256 remains
`a6bd33cc9d0cfdd6f9f60fa343bf413fae4de33b62a8f4c26141857763cf9d33`.
`git diff -- hardware/tscircuit/package.json hardware/tscircuit/package-lock.json`
is empty. Production **tscircuit remains pinned to 0.0.2646**. No CI-wide or
production runtime dependency changed, and node_modules is not committed.

## Contribution-ready upstream boundary

Upstream: [tscircuit/kicad-to-circuit-json](https://github.com/tscircuit/kicad-to-circuit-json),
package **0.0.142**, reported commit **967a8c823d8d19cdf18060fd7b66ce5d79e91c12**.
Only read-only upstream source inspection was performed.

The minimal [keepout-repro.kicad_mod](../hardware/tscircuit/spikes/eda-003a/keepout-repro.kicad_mod)
is a standalone footprint with one rectangular top copper-pour-only keepout,
no pads, holes or board. It separates the missing-zone defect from arc conversion.
With the isolated package installed, reproduce with:

```sh
node --input-type=module <<'JS'
import {readFileSync} from 'node:fs'
import {KicadFootprintToCircuitJsonConverter as C} from 'kicad-to-circuit-json'
const c = new C()
c.addFile('keepout-repro.kicad_mod', readFileSync('keepout-repro.kicad_mod','utf8'))
c.runUntilFinished()
console.log(c.getOutput().filter(e => e.type === 'pcb_keepout'))
console.log(c.getWarnings())
JS
```

Exact material expected output, with implementation-generated ID:

```json
{
  "type": "pcb_keepout",
  "shape": "rect",
  "center": {"x": 0, "y": 0},
  "width": 4,
  "height": 3.6,
  "layers": ["top"],
  "allow_traces": true,
  "allow_placements": true
}
```

The record must enforce copper-pour exclusion rather than serve only as a warning;
tracks/vias/pads/placements must remain allowed. If Circuit JSON/consumers cannot
faithfully represent those distinctions, the correct minimal behavior is an
explicit unsupported-feature warning/error instead of an approximate silent
conversion. For the actual historical asset, expected geometry is two separate
keepout polygons: the transformed eight-arc top notch and four-arc bottom outer
boundary, plus explicit handling or warning for the internal-layer scope.

**Actual minimal output:** material `pcb_keepout` array `[]`; warnings `[]`;
conversion returns successfully. Missing element type: **`pcb_keepout`**.
The original asset produces the same omission. This is not a parser failure:
`parseKicadMod` retains `Footprint.zones` and the zone keepout properties.

Likely implementation boundary, inspected at the reported commit:

- `lib/KicadFootprintToCircuitJsonConverter.ts` initializes the standalone context
  and calls `processFootprint`.
- `lib/stages/pcb/CollectFootprintsStage/process-footprint.ts` processes pads,
  text and graphics, but does not process footprint zones.
- `lib/stages/pcb/CollectZonesStage.ts` handles filled board copper zones; it is
  not evidence of standalone keepout support and must not convert a keepout into
  a pour.
- `tests/kicad-footprint-converter.test.ts` is the existing standalone test area.

Smallest credible upstream contribution: inspect `footprint.zones` during footprint
processing and emit a specific warning per unsupported keepout containing its
name/UUID, layers, and copper-pour restriction. Add a regression asserting either
faithful material output **or the explicit warning**, never success with neither.
This is a small, bounded diagnostic fix and does not require a schema fork, router,
exporter, or project-specific geometry repair. Warning-only remediation prevents
silent success; it does **not** qualify import reuse or pass the project's
required-geometry gate. Full polygon conversion is a separate implementation step
that must test the notch, arc tolerance, layer mapping, permissions, and actual
stock copper-pour exclusion on both layers. No conservative rectangle should
silently replace the exact source polygon.

An additional small upstream regression should use a single SMD roundrect
`size 1.475 0.6`, `roundrect_rratio 0.25`, requiring
`pcb_smtpad.corner_radius=0.15`, actual `0.075`, warnings `[]`.
The likely boundary is `process-pads.ts`'s roundrect radius calculation. A generic
formula correction should also test other ratios and affected plated-roundrect
branches. Audit unsupported `zone_connect` diagnostics and publish the missing
runtime dependencies so a clean consumer install works without undeclared parent
packages. These remain separate upstream review items, not local fixes here.

The manufacturing-fidelity gate fails, so retain native approved geometry and do
not integrate the importer into he-piantor-42. The classification reflects a
bounded upstream contribution candidate, not permission to reuse this importer.
No upstream PR is opened by this issue.

UPSTREAM_FIX_CANDIDATE
