# Issue #248 — B2 Pico-EZmate 7+7 feasibility screen

2026-11-14. **7+7 is a documented mating system, including a seven-circuit housing.**
The screen gives **B ≥6.70 mm; plate top ≥Z12.90 mm**, saving **0.65 mm** from
Phase A's GH-bound Z13.55. At that board datum the proposed Main envelopes
clear the **unmodified B0 roof by +2.000000 mm** on both sides. This is a
conditional engineering screen, not Phase B, a board redesign, or an adoption.
**Procurement is not ready:** JLCPCB header stock/presale are both zero;
distributors flag seven-way obsolescence; a compliant ≤200 mm harness needs
custom termination rather than the located 300 mm standard leads.

All roof-related Z remain **provisional on q=1.50 mm**. Existing boards,
B0/B1, decision records, roof solid and production CAD are unchanged.
Dimensions below distinguish Molex drawing references from engineering
allowances. STEP solids are **occupied envelopes**, including voids; they
are not reconstructed mouldings or a fully routed harness.

## 1. Parts reality and cable procurement

### Exact system and source register

| Item | Exact Molex order number | Manufacturer evidence |
|---|---|---|
| Seven-way SMT header | **781715007** (78171-5007 / 0781715007) | [Molex product record](https://www.molex.com/en-us/products/part-detail/781715007?display=pdf); D1 seven-way table |
| Seven-way crimp housing | **781725007** (78172-5007 / 0781725007) | [Molex housing record](https://www.molex.com/en-us/products/part-detail/781725007?display=pdf); D2 explicitly lists seven circuits |
| AWG28 terminal used for this screen | **781720410** (78172-0410 / 0781720410), reeled | [Molex terminal record](https://www.molex.com/en-us/products/part-detail/781720410); D3 §§2.1,4.3 |
| Alternative terminal | **781720411**, copper-alloy version | [Molex terminal drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/781/78172/781720411_sd.pdf), 781720400-SD A; D3 explicitly includes both |

**D1:** Molex [781710001-SD, revision C, 2025-02-27](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/781/78171/781715006_sd.pdf), sheets 1–2, *6–7 CKT plug assembly*. The download named for six circuits contains both sizes. [Archived Molex revision A](b2/sources/header-mirror.pdf), distributed by [Global-IC](https://www.global-ic.com/pdf-4c/0781715007.pdf), was also downloaded and its seated side view visually inspected; the dimensions used agree. Current revision C governs. Its revised D-column is not used to size this model.

**D2:** Molex [781720001-SD, revision B, 2025-02-27](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/781/78172/781725007_sd.pdf?inline=), sheet 1, *6–7 CKT receptacle housing*. Its seven-way row is **781725007**, A=8.54, B=7.20 mm. **The housing does exist in Molex documentation.** The older six-way catalogue ceiling is not a proof of absence. D3 §2.1 independently lists 78172500* housings for six/seven circuits.

**D3:** Molex [781721000-PS revision B1](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/781/78172/781721000-PS-000.pdf), printed sheets 3–7: AWG28 rating 1.5 A/contact, AWG30 1.0 A; 50 V; wire OD0.60–0.70 mm; −40…+105°C; ten mating cycles. Initial contact resistance ≤20 mΩ; crimp resistance separately ≤5 mΩ. Some environmental tests allow 40 mΩ. These replace the older catalogue's less complete statements. D1/D2 and product descriptions establish vertical mating and friction retention.

**D4:** Molex [AS-78172-001 revision C](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationspecificationspdf/781/78172/AS-78172-001-001.pdf), printed sheet 43, §10-3/Figs10–11: give wires room to curve and prevent load at their roots. This supplies handling guidance, **not a numerical minimum bend radius**.

Thus **7+7 is buildable from documented parts**, subject to obtaining genuine
stock. 6+8 is impossible within this family because an eight-way system was
not found. If seven-way supply cannot be secured, **6+6+2** is a documented
three-connector fallback (781715006/781725006 twice and
781710002/781720002 once at each end), requiring another placement screen.
Alternatively 5+5+4 uses catalogue sizes. Neither fallback inherits a stock or
placement PASS here; neither is a two-connector 14-circuit solution.

### Stock screen, including spares

The existing connector guideline is documented in
[issue-240 stock.json](../../kicad/qualification/issue-240-main-rev7/connector/stock.json)
and [issue-235 SOURCES](../../kicad/qualification/issue-235-wing-round2/connector/SOURCES.md):
about **10× the quantity required including spares**. For a transparent batch
assumption consistent with the former Main requirement of 30 GH headers, use
**15 complete keyboards including spare sets**. Each now takes eight headers,
eight housings and 56 terminals: required **120 /120 /840**, preferred available
stock **1200 /1200 /8400**. A different batch scales these thresholds linearly.
There are 28 double-ended leads per keyboard: 420 needed, preferred 4200.

Direct HTTP observations and compressed source HTML are in
[b2/sources](b2/sources), with dates/errors in
[http-observations.json](b2/sources/http-observations.json) and
[stock-b2.json](b2/stock-b2.json). Browser/search-index observations are labelled
below; their counts are **indicative cached availability, not fresh inventory
qualification**. Counts from different regions or stock fields are not added.

| Part | LCSC | JLCPCB direct component record | DigiKey fallback | Mouser fallback | 10× result |
|---|---|---|---|---|---|
| 781715007 | **C564184**; direct HTTP403, live stock unknown | [C564184](https://jlcpcb.com/partdetail/MOLEX-781715007/C564184), SMT Economic/Standard; overseas **0**, presale **0**, preorder minimum24 | [0781715007](https://www.digikey.com/en/products/detail/molex/0781715007/5116447): obsolete; WEC marketplace **540,000** shown | [78171-5007](https://www.mouser.com/en/ProductDetail/Molex/78171-5007?qs=hs2naT6Fjs8k%252BSxGH2tacg%3D%3D): **5,567** shown, minimum1; discontinuance links | **FAIL current JLC route**; fallback indicative count sufficient |
| 781725007 | **C588525**; direct403; [indexed image page](https://www.lcsc.com/product-image/C588525.html) says0 | [C588525](https://jlcpcb.com/partdetail/MOLEX-781725007/C588525): overseas **1**, presale **1**, preorder minimum42 | [0781725007](https://www.digikey.com/en/products/detail/molex/0781725007/5116448): obsolete; WEC marketplace **554,443** shown | [78172-5007](https://www.mouser.de/en/ProductDetail/Molex/78172-5007?qs=sGAEpiMZZMvlX3nhDDO4AFQMIinqq1eaKHotTahkSpo%3D): **48,311** shown, minimum1 | **FAIL JLC/LCSC demonstrated supply**; fallback indicative count sufficient |
| 781720410 | **C505105**, direct403; [indexed product](https://www.lcsc.com/product-detail/C505105.html) **24,900**, minimum20 | [C505105](https://jlcpcb.com/partdetail/MOLEX-781720410/C505105): overseas **12,680**, presale **12,680**, preorder minimum141 | [0781720410](https://www.digikey.com/en/products/detail/molex/0781720410/2421925): **139,621** shown, CT minimum1 | [loose piece](https://www.mouser.com/en/ProductDetail/Molex/78172-0410-Loose-Piece?qs=8%252Bu%2FV6%2FT1OqdpCfa9Spkzw%3D%3D) **23,210**; [cut strip](https://www.mouser.com/en/ProductDetail/Molex/78172-0410-Cut-Strip?qs=bMdCYdYIhWpKAyK%2FXF2N7g%3D%3D) **35,500**, minimum100 | Counts exceed8400; crimp procurement still separate from PCBA |

JLC's overseas/presale fields are separate descriptions, not additive stock.
Its parts-library purchase is for PCBA and cannot be assumed shippable as loose
harness parts. Housings/terminals require a harness-parts order. The alternate
[781720411/C565266](https://www.lcsc.com/product-detail/C565266.html) is indexed
out of stock; substituting it does not solve the header/housing shortage.

**Lifecycle warning is material:** DigiKey calls both seven-way parts obsolete;
Mouser links a 2023-03-17 discontinuance notice. Molex retains drawings and
limited-information product records, with 2025 drawing revisions. That is
conflicting lifecycle evidence, **not proof of current manufacture**. Obtain
Molex/distributor confirmation and acceptable lot quantities before selecting
these for a new design. No purchase, supplier contact or stock reservation was
made. The stock gate remains **FAIL/unresolved**, even though fallback inventory
could support prototypes.

### The PO's cable concern, directly

Molex **797581010 / 79758-1010 / 0797581010** is a real double-ended AWG28
pre-crimped lead. [Molex product record](https://www.molex.com/en-us/products/part-detail/797581010)
and [drawing 2012341212](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/797/79758/797581010_sd.pdf)
identify **300±5 mm**, 781720410 terminals, white ETFE UL1516, **OD0.57 mm**.
The specific factory lead drawing establishes that thin-wire combination;
it must not be generalized to arbitrary OD0.57 wire in another terminal setup.
[Mouser's series listing](https://www.mouser.es/es/c/tools-supplies/prototyping-products/?series=79758)
shows **14,947** leads (cached), exceeding the4200 indicative target, but they
**do not meet the ≤200 mm finished-conductor gate**. Cutting one end and
re-crimping it can produce a compliant lead; cutting/splicing in the middle
would introduce an unassessed splice. Simply storing 300 mm is not compliant.

The [Molex 36920 OTS series](https://www.molex.com/en-us/products/series-chart/36920)
lists assembled two-to-five-way cables, including150 mm options; it does not
establish a ready-made seven-way harness. No ≤200 mm double-ended seven-way
standard cable or shorter loose EZmate lead was located. A150 mm alternative
would also need the end-to-end route plus30.2 mm reserve proven.

**Recommended feasible harness process:** obtain genuine housings and terminals;
have a cable shop crimp AWG28 thin-wall wire to the measured ≤200 mm length,
with both ends cavity-checked. Hand building is possible with Molex
**2133096500**, whose [tool specification](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationtoolingspecificationpdf/213/213309/2133096500-000.pdf?inline=)
([downloaded copy](b2/sources/tool-current.pdf)) covers781720410/0411,
AWG28–30, OD0.50–0.70, strip0.90–1.30 mm and cut-off tab≤0.05 mm.
[DigiKey lists the tool](https://www.digikey.ie/en/products/detail/molex/2133096500/16187749)
with9 in stock (cached). Molex's terminal page lists **638194800** (AWG28,
reeled) and **638194300** (loose parts) under *previously available tooling*;
these are legacy options, not the preferred new-tool purchase.
Do not assume a generic small-contact crimper qualifies. Require visual/crimp
height inspection, continuity/cavity mapping and AWG28 pull acceptance to the
Molex10 N requirement (D3 §6.2.2), followed by finished loop resistance.
**Cable availability is conditional custom-build availability, not a plug-in
stock cable solution.**

## 2. Pin split and electrical screen

D-024 has **14 electrical contacts but only nine distinct electrical nets**;
its six GND positions repeat the same net. **MP-NC is a mechanical solder land,
not a fifteenth conductor or a spare contact.** Both new headers' reinforcement
lands stay MP-NC. The proposed mapping preserves all six returns and every
signal; each cable is1:1 and both boards use the same cavity numbering.

| New cavity | Connector A | Original GH pin | Connector B | Original GH pin |
|---|---|---:|---|---:|
| 1 | HALL_5V | 1 | GND | 8 |
| 2 | GND | 2 | MUX_OUT_A | 9 |
| 3 | MUX_A0 | 3 | GND | 10 |
| 4 | GND | 4 | MUX_OUT_B | 11 |
| 5 | MUX_A1 | 5 | GND | 12 |
| 6 | MUX_A2 | 6 | MUX_OUT_C | 13 |
| 7 | WING_EN | 7 | GND | 14 |
| mechanical | MP-NC | MP | MP-NC | MP |

The six returns work in parallel, with GND adjacent to the three raw outputs.
**There is no spare contact to parallel HALL_5V in7+7 while retaining the six
returns.** Repurposing a GND as a second supply would amend the D-024 contract;
it is not assumed. A/B are identical-size connectors and can be interchanged
incorrectly, so require durable labels, cable restraint and assembly cavity
checks. Preserve independent left/right enable and power-off service.

Use each conductor's **full200 mm electrical length**, including reserve;
AWG28-equivalent minimum copper area0.0804 mm², rho20=1.7241e−8 Ωm,
alpha=0.00393/K, as [Rev7's budget](../../kicad/qualification/issue-240-main-rev7/power-budget.json).
Use D3's20 mΩ per mating contact at **both** ends; conservatively add its
separate5 mΩ crimp allowance at both ends. Assume equal-length returns and
low enough PCB spreading resistance for parallel sharing. No current-rating
problem at127 mA supply /nominal21.17 mA per return; AWG30 is not substituted
into this resistance calculation.

`Rwire(T)=rho20*0.200/area*(1+alpha*(T−20))`

`Rloop=(Rwire+2*(0.020+0.005))*(1+1/6)`

| Wire temperature | Each wire mΩ | Loop, contact only mΩ | Loop incl. crimp mΩ | Drop incl. crimp at127 mA |
|---|---:|---:|---:|---:|
| 20°C | 42.888 | 96.703 | **108.369** | **13.763 mV** |
| 105°C | 57.215 | 113.417 | **125.084** | **15.886 mV** |
| 125°C sensitivity | 60.586 | 117.350 | **129.017** | **16.385 mV** |

[Computed rows](b2/electrical-b2.json) include a40 mΩ environmental-contact
sensitivity: loop175.683 mΩ /22.312 mV at125°C. **125°C is the inherited
copper sensitivity corner, above EZmate's105°C operating ceiling; this is not
an operating-temperature qualification or an assumption that the supplier's
20 mΩ rating extends to125°C.** The conservative crimp sum may double-count
part of a test path; it avoids understating loss.

Replacing only Rev7's187.350 mΩ GH harness model with129.017 mΩ gives
**Vfar=4.800366 V**, margin **200.366 mV** to4.60 V. This intentionally retains
Rev7's pessimistic legacy Wing drop147.710 mV, the5.2 V rail−2%,50 mV dynamic
allocation, U5 Ron0.25Ω, both Wings powered and125°C/80%-width Main copper.
Using the actual Rev4 worst distributed drop19.329 mV instead gives about
**4.928748 V** with that same pessimistic Main branch. Both are conditional
frozen-copper estimates; the re-spin needs fresh extraction.

**50 mΩ has two different interpretations:** the harness itself is **not≤50 mΩ**,
even at20°C. The project's existing Main common and branch copper targets
are separate: [Rev7 extraction](../../kicad/qualification/issue-240-main-rev7/resistance-summary.json)
gives49.491 /20.961 /43.051 mΩ (common/J2/J3), all≤50 mΩ, with only
**0.509 mΩ common margin**. Connector substitution leaves that frozen model
unchanged, but a reroute cannot inherit its PASS. If≤50 mΩ for the entire
200 mm harness is imposed as a new requirement, **this7+7 allocation fails**.

## 3. Wing underside geometry and new deck bound

| Drawing feature | Molex value mm | Source / view |
|---|---:|---|
| Pitch; seven-pin span | 1.20;7.20 | D1 sh1/sh2 pitch and B column; D2 sh1 |
| Header overall width/depth | 10.20±0.25;4.50 | D1 sh1 A column and side/plan dimensions |
| Housing width/depth/height | 8.54;3.97;1.40 | D2 sh1 seven-way A row and side views |
| Seated bounding depth/height | **(4.83);(1.65)** | D1 sh2 *Mated connectors*, side view; **reference dimensions** |
| Header land pattern | pitch1.20±0.05; contact land0.80±0.05×0.85±0.05; row spacing3.75±0.05 | D1 sh2 recommended component-side PCB layout |
| Nail land | 0.70±0.05×0.80±0.05; seven-way E7.80 | D1 sh2 land layout/table; preserve hatched no-pattern area |
| Thin wire envelope | OD≤0.70 | D3 §4.2; smaller standard lead OD0.57 from2012341212 |

The model uses a **10.20×4.83×1.65 seated occupied bound**. D1's side view
shows the wires leave **horizontally**, although mating is vertical. On Wing
B.Cu the mating normal points down; the seated wire direction lies in the PCB
plane. On both Wings place two bodies in the existing J_WING zone, pin-row
centres±6.10 mm from the old origin, giving2.00 mm body separation.
The actual frozen Rev4 definition and #232 assembly transform put their
assembly centres at **X−20.90/−33.10,Y−41.00** left and
**X+33.10/+20.90,Y−41.00** right. Full poses are in the JSON.

For the first dress reserve a2 mm straight, an **R5,30° turn in XY away from
the other connector**, then2 mm straight. These are explicit engineering
choices, not Molex radii or strain-relief lengths. All seven0.70 mm wires
start at1.20 pitch. The short turn retains approximately
`1.20*cos(30°)−0.70 =0.339 mm` separation; later fanout is not proved.
The conservative wire rectangle includes the whole0.70 OD around those paths.
The **outlet-axis height is not dimensioned**, so its entire occupied Z band
is retained within the full1.65 mm seated band rather than assigning a precise
axis from a picture. A numerical supplier minimum bend radius was not found;
R5 must be validated with the selected wire and D4 root-load guidance.

In each connector's local frame u along the pins, v toward the wire exit:
body u±5.10,v−1.60…3.23; wires begin atv3.23, first bend starts5.23 and
ends7.73; terminal straight ends9.462051. Wire bound reachesv9.812051,
u±3.95 plus1.669873 on the turning side. The occupied union is
**10.719873×11.412051×1.65** per connector. These coordinates define the
STEP datum; they are a proposed placement, not a Molex footprint origin.
The full two-connector dress spans **23.439746 mm** along the row.

`B_EZmate = 2.00 floor +1.65 bound +0.50 allowance +0.50 free gap =4.65`

`B_new=max(4.65 EZmate,5.90 Hall,3.90 MUX,3.50 capacitor,6.70 tie/root)=6.70`

`plate top =6.70+1.20 PCB+3.50 spacer+1.50 plate=12.90`

At B6.70, connector/dress bottomZ5.05; allowance bottomZ4.55;
**residual floor gap2.55 mm**, exceeding the retained0.50 requirement.
Hall bottomZ3.30 leaves1.30 mm. The tie tip is exactlyZ1.20, retaining the
Phase A minimum root thickness; this constraint now binds. Posts would become
**5.50 mm overall** from Phase A's6.15; their sockets/root design still needs
structural/CAD validation. A tight vertical R5 turn downward would not fit this
bound; it is not the proposed pose. The in-plane first bend does fit the Z
cavity, without adding R5 beneath the PCB.

[Wing assembly STEP](b2/wing-ezmate-screen.step),
[local section context STEP](b2/wing-underside-section-context.step),
[dimensioned section/plan PNG](b2/wing-underside-fit-b2.png).
Board outlines and first-dress bounds are contained in both Rev4 Wing polygons;
nearby conservative component reservations have no XY overlaps; the minimum gap
is **1.387949 mm** to C_MUX_B/C_MUX_C, recorded in the JSON.
This proves a **local envelope screen**, not complete fanout, service access,
full harness routing or every tolerance/physical wire behavior.

## 4. Main geometry against the unchanged B0 roof

Use the existing Rev7 J2/J3 XY zones and angles, top-face mounting, vertical
mating, and **horizontal outward exit with the first turn in XY**. This avoids
the unnecessary up-then-out R5 rise. A forced immediate vertical rise could
consume over5 mm and restore a roof conflict. Roof-off access is needed to
press/unmate each housing; the seated result does not certify service motion.

| Header centre, assembly mm | X | Y | Row/mating-zone angle inherited from GH |
|---|---:|---:|---:|
| J2-A | −14.052146 | 36.792246 | −120° |
| J2-B | −20.152146 | 47.357756 | −120° |
| J3-A | +20.152146 | 47.357756 | +120° |
| J3-B | +14.052146 | 36.792246 | +120° |

New Main underside follows Wing B6.70; topZ7.90; seated/dress top**Z9.55**.
[Placed Main STEP](b2/main-ezmate-screen.step) and
[roof plus Main STEP](b2/roof-main-ezmate-screen.step) include four independently
named envelopes. The solver imports `b0/roof-b0.step` **without changing it**;
eight valid solids, volume32001.277514 mm³, original SHA256 retained.

| Comparison | Nominal minimum vertical gap | With0.50 assembly allowance |
|---|---:|---:|
| **New B6.70 boards vs unmodified B0 roof** | **+2.000000 mm** | **+1.500000 mm** |
| B1 board height B7.35 vs same B0 roof, connector change alone | **+1.350000 mm** | **+0.850000 mm** |
| New boards and a hypothetical roof translated down0.65 to follow new deck | **+1.350000 mm** | **+0.850000 mm** |

All four have **zero OCCT Common volume**; true BRep distance to the unmodified
roof is also2.000000 mm. Worst support occurs under the low-south underside
Z11.55, not merely at an arbitrary slope sample. The signed vertical test
clips each envelope with the imported roof's actual underside-face footprint,
then optimizes its support under that affine plane. Independent exported-STEP
readback repeats the test. **The B1 GH−1.35 conflict disappears for these
explicit bounds/poses.** Positive nominal results do not certify the reference
height as a production maximum; the retained0.50 allowance and physical fit
validation remain necessary. No blister or pocket is needed for these EZmate
bounds. B0 south screw and Fly conflicts remain separate.

## 5. Placement screen; no board rerouting

| Per Wing link / per Main side | Along-row width | Depth / reserved area | Interpretation |
|---|---:|---|---|
| One GH14 header | 20.75 | header4.05; mated7.15 | B1 JST drawing bounds |
| Existing Main GH courtyard | **21.96** | **6.40** | Read directly from frozen Rev7 F.CrtYd (u±10.98,v±3.20) |
| Two EZmate7 headers, touching | 20.40 | header4.50; mated4.83 | Arithmetic lower width only; not a usable service placement |
| **Screened pair,2 mm body gap** | **22.40** | seated4.83 | +1.65 vs GH body; +0.44 vs old Main courtyard |
| Proposed0.50 perimeter margin | **23.40** | **5.83** | Engineering planning margin, **not a Molex courtyard** |
| Full first-dress occupied pair bound | **23.439746** | **11.412051** | In-plane gentle bend; later route and vertical service space additional |

D1 sh2 governs contact/nail lands and its hatched no-pattern region;
its layout is referenced to a1.0 mm PCB/0.1 mm stencil. The retained1.20 mm
PCB and actual solder process need assembly review. A new library footprint
must be checked against the drawing; **no new production footprint is issued**.
Wing's GH model uses the same20.75 body and7.15 seated depth; the comparison
therefore applies on B.Cu as well, with opposite mating normal.

All four proposed Main bodies have **0 mm² outside the Main outline**;
both Wing bodies and full first-dress bounds stay inside their respective
17 mm polygons. This and the small along-row increase make **same-zone
placement plausible**, not a pad-compatible replacement. The Wing nearby-part
reservation check is reported numerically with the artifacts. Horizontal wire
exit into the board-side bay must not be mistaken for edge-hanging cable space.

A full re-spin must prove the land/nail/keepout pattern, neighbour/TP/via/NPTH
clearance, power/GND redistribution, signal return/ADC settling, four Wing
variants (16/17 mm×L/R), actual solder and assembly access, and distinguishable
A/B and L/R harnesses. It must re-run ERC, native DRC, independent net/cavity
connectivity, via-pad spacing, copper resistance extraction, complete collision
checks, ≤200 mm per conductor,30.2 mm reserve and service/removal motion. No
copper changes or reroutes were attempted, and no existing qualification is
silently transferred.

## 6. Impact and feasibility verdict

Adoption requires a successor Main Rev7 and successor Wing Rev4 (all four
variants): two connectors replace each GH interface, new symbols/footprints,
cavity mapping, local placement and whatever wider routing is necessary.
The actual Rev7 GH change previously affected16 nets, so local physical size
is no assurance of local copper impact. D-040 and D-039 need successor
qualification/decision entries; D-024's GH14 physical pin contract and D-033's
GH harness specification need explicit interface amendments. Electrical bus,
load, six returns, independent enables and power-off service remain.
B2 does not amend those records itself.

The harness becomes **eight mutually interchangeable seven-way housings
per complete keyboard** (four per Wing link), with custom crimp length, A/B and
L/R identification, strain restraint and acceptance tests. Friction retention
and **ten rated mating cycles** limit repeated servicing. Do not use the wires
as a handle or infer GH-style positive latch behavior. Allow housing access
with roof removed and enough cycle budget for manufacture/testing/service.
Existing Fly EZmate usage provides useful terminal/tool/wire and assembly
familiarity; it does not establish a seven-way cable supply or remove Fly170's
own storage conflict.

| Area | Verdict | Basis / remaining gate |
|---|---|---|
| Parts reality | **7+7 documented; supply conditional** | Seven-way header AND housing exist; obsolete flags and current JLC zero header stock block adoption |
| Electrical | **Voltage screen PASS; harness≤50 mΩ FAIL if required** | ~4.800 V conservative; frozen Main copper targets pass, reroute must re-prove |
| Wing Z geometry | **Local screen PASS** | B6.70, plate12.90;2.55 floor gap after allowance; tie/root binds |
| Main roof geometry | **Local screen PASS** | +2.000000 unmodified B0; +1.350000 on B1 datum or roof-following translation |
| Placement | **Plausible, conditional** | Envelope within board outlines; neighbour and full route/assembly qualification still required |
| Overall | **Technically promising; do not adopt yet** | Only0.65 mm stack saving; supply/harness and re-spin/service work are material |

**Top three risks:** (1) seven-way lifecycle and assembly stock, plus no located
compliant ready-made cable; (2) a two-board-family re-spin must preserve power,
ADC behavior and full harness routing/service reserve despite the small height
saving; (3) actual wire root/bend handling and repeated service with friction
retention/ten-cycle durability. Separately, B0's south openings and Fly relief
or reroute remain mandatory topics; this substitution does not close them.

## Evidence and reproduction

[Dimensions/poses/gaps](b2/clearances-b2.json),
[electrical calculations](b2/electrical-b2.json),
[stock evidence](b2/stock-b2.json),
[independent STEP replay](b2/verification-b2.json),
[Main placement PNG](b2/main-placement-b2.png).
Independent exported-STEP readback **PASS**: every exported solid valid, eight
roof underside faces screened, all four Main gaps2.000000 mm and Common0;
Wing nominal minimumZ5.05 and allowance floor gap2.55 mm. Both PNGs were
visually inspected. Individual Wing and Main connector envelope STEPs are also in `b2/`.
The report, scripts, inputs and artifacts are bound by
[artifact-sha256-b2.json](artifact-sha256-b2.json).

```bash
export TMPDIR="$PWD/.issue248-runtime"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2
/home/hatch/workspace/tools/cad-venv/bin/python hardware/case/issue-248-lowdeck-raise/study-b2.py
/home/hatch/workspace/tools/cad-venv/bin/python hardware/case/issue-248-lowdeck-raise/verify-b2.py
/usr/bin/python3 hardware/case/issue-248-lowdeck-raise/plot-b2.py
```

Cached web stock is retained as dated indicative evidence, not a reproducible
promise. Direct manufacturer PDF HTTP downloads timed out in this session;
manufacturer web-reader text and the archived manufacturer drawing supplied
the documented dimensions. Direct LCSC requests returned403. These limitations
are recorded instead of treating an inaccessible count as zero. All scratch,
caches and dependency reuse remain under `.issue248-runtime/`.
