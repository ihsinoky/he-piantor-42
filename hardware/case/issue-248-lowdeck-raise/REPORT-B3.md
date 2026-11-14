# Issue #248 — B3 alternative connector survey

2026-11-14. **Carry Hirose DF52 14-way forward to an adoption feasibility round.**
Its drawing-based seated envelope is **1.75 mm**, it accepts AWG28, its header
has a demonstrated JLCPCB procurement path, and no discontinuance flag was
found for the screened system. JST SH side-entry 14-way is the runner-up.
Both reach **B=6.70 / plate top Z12.90 mm**. Against the **unmodified B0 roof**,
DF52 clears by **+1.900000 mm**, SH by **+0.700000 mm**, on both Main sides.
These are exact results on stated occupied bounds, not production moulding
tolerances. **All roof Z are provisional on q=1.50 mm.**

DF52 improves the combined choice: the same 0.65 mm deck saving as EZmate 7+7,
one connector instead of two at each endpoint, better lifecycle evidence, and
stocked Main headers. It is **not an adoption approval or a fully secured BOM**:
loose housing inventory and a qualified custom cable shop are still gates.
It does not lower the deck below EZmate: the unchanged M2 tie/root binds next.
This deliverable is Phase B3 only; no board, production footprint, roof,
decision record, or Phase B design is changed.

## Basis, evidence dates, and rules

The link remains D-024: fourteen conductors, one HALL_5V at **127 mA**, six GND,
MUX_A0/A1/A2, WING_EN, MUX_OUT_A/B/C. All cavities remain 1:1; mechanical
reinforcement lands are not contacts. No ground is reassigned to power.
Finished conductor length, including service reserve, must be **≤200 mm**.
AWG28 is a preference; thinner wire is not automatically a hard failure.
The electrical and mechanical methods and frozen input references come from
[B2](REPORT-B2.md), [B1](REPORT-B1.md), and Phase A/A4.

Wing: `B=max(2.00 floor + seated envelope E + 0.50 allowance + 0.50 gap,
5.90 Hall, 3.90 MUX, 3.50 capacitor, 6.70 tie/root)`.
Plate top is `B+1.20 PCB+3.50 spacer+1.50 plate = B+6.20`.
Thus **E≤3.70 mm cannot improve B below 6.70** without a legitimate tie/root
change, which is outside this survey. Main is top mounted in the frozen J2/J3
zones. Retaining B2's **0.50 mm assembly allowance**, the local low-south
ceiling Z11.55 at Main top Z7.90 gives a preliminary **E≤3.15 mm** screen.
This is a conservative fixed-zone elimination rule; it is not a universal
impossibility statement about every possible placement or future board.
Only the best two get exact BRep roof clipping below.

All source observations below were made **2026-11-14 UTC**. Manufacturer PDF
revision/printed dates are specified when available; a web crawl date is not
a manufacturer revision. Direct HTTP inventory is in the archived HTML and
JSON under [b3/sources](b3/sources). Web-reader/search-index inventory is
explicitly **cached/indicative**, even when a page says “ships now”.
Direct LCSC requests returned HTTP403: inaccessible stock means **unknown,
not zero**. JLC's `overseasStockCount` and `canPresaleNumber` are recorded
separately, never added; they do not establish immediately usable in-house
assembly stock. The latter field is pre-purchase availability, not a promise
of delivery. Related-product `stockCount` fields are deliberately excluded.
JLC library parts cannot be assumed shippable loose for making harnesses.

For B2's **15 keyboards including spares**, a single 14-way system requires
**60 headers, 60 housings, 840 terminals** (four endpoint headers per keyboard).
The inherited 10× preference is **600 /600 /8400**. A two-connector split needs
120 /120 /840 total, with thresholds applied separately to each exact SKU;
three connectors need 180 /180 /840. This is a survey supply comparison, not
an inventory reservation. Obsolete/discontinuance evidence is an automatic
red flag for that exact SKU; “no flag found” is not a manufacturer guarantee.

## Manufacturer source register

| ID | Manufacturer document, revision/date and used views |
|---|---|
| SH | JST [current eSH](https://www.jst.com/wp-content/uploads/2025/06/eSH.pdf), four pages, retrieved through web reader; p1 assembly side entry, p2 housing table, p3 headers. Independent manufacturer-hosted [JST France catalogue](https://www.jst.fr/doc/jst/family/pdf/eSH.pdf), archived [sh-fr.pdf](b3/sources/sh-fr.pdf), two-page edition without a printed revision; p1 assembly, p2 fourteen-way rows. The 2.95/6.25 assembly dimensions were visually checked. |
| SUR | JST [eSUR](https://www.jst-mfg.com/product/pdf/eng/eSUR.pdf), p1 ratings, p2 sockets, p3 assembled top/side drawings and header table; no printed revision in web reader. |
| ACH | JST [eACH](https://www.jst-mfg.com/product/pdf/eng/eACH.pdf), p1 seated layout/ratings/tooling, p2 size/order table; no printed revision. JST [product record](https://www.jst-mfg.com/product/index.php?lang=2&series=9) confirms top mating, side feed and friction retention. |
| PB-D | Molex [532610001-SD](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/532/53261/532610871_sd.pdf), seated side view and table, revision E1, 2025-10-28 (PCN515981 removed selected obsolete order numbers); [51021 housing drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/510/51021/510210500_sd.pdf), fourteen-way row. |
| PB-S | Molex [PS-51021-024-001 revision AD](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/510/51021/PS-51021-024-001.pdf), 2022-06-03, explicitly lists53261**71,51021**00 and500588*00; §§3–4 give matching tin ratings, resistance and30 cycles. Do not substitute the gold510211001-PS document. |
| ML-D | Molex [5055670000-SD D3](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/505/505567/5055670471_sd.pdf), approved 2026-09-18, sh1/header and sh3/mated, fourteen-way table; [505568 vertical drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/505/505568/5055681671_sd.pdf). |
| ML-S | Molex [5055650000 D](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/505/505565/5055650000-000.pdf), 2023-02-16, §§3–4: wires, resistance, crimp resistance, lock and cycles. [5054311000-SD G](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/505/505431/5054311000_sd.pdf), 2023-09-12, terminal/wire table. |
| CM | Molex [5025851470 product sheet](https://www.molex.com/en-us/products/part-detail/5025851470?display=pdf) and [502585 drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/502/502585/5025850872_sd.pdf), selected right-angle 6.40 mm system; [5025780001-PS B](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/502/502578/5025780001-PS-000.pdf?inline=), 2021-08-31, ratings/platform context. This latter spec identifies 503339/503340 SMT receptacles; do not assume its qualification automatically covers 502585. |
| PC-D | Molex [2023960000-SD D](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/202/202396/2023960707_sd.pdf?inline=), sh3 assembled 2–5 and 6–15 circuits; [501331 vertical drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/501/501331/5013311407_sd.pdf), 2017-08-04. |
| PC-S | Molex [5013301000-PS-001 B](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/501/501330/5013301000-PS-001.pdf?inline=), 2021-06-25, tin version; [gold version -002 B1](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/501/501330/5013301000-PS-002.pdf), 2025-04-24. Keep headers/terminals plating matched. |
| DF13 | Hirose [DF13 catalogue](https://www.hirose.com/product/document?documentid=en_DF13_CAT&documenttype=Catalog&lang=en&series=DF13), manufacturer document; archived [distributor-hosted manufacturer copy](b3/sources/df13.pdf), from [LCSC CDN](https://atta.szlcsc.com/upload/public/pdf/source/20230612/560DCB94E448C371AF41FE6A4EBF20E5.pdf). Ratings, single-row assembly, contacts/tooling; [current 14-way housing record](https://www.hirose.com/en/product/p/CL0536-0013-3-00), updated 2026-07-09. |
| DF14 | Hirose [D31686_en](https://www.hirose.com/en/product/document?clcode=&documentid=D31686_en&documenttype=Catalog&lang=en&productname=&series=DF14), Apr.2025 edition, printed 2025-09-01; pp2–3 assembly/ratings, pp5–6 housing/contacts, subsequent header tables. |
| DF52 | Hirose [DF52 catalogue](https://www.hirose.com/en/product/document?clcode=&documentid=en_DF52_CAT&documenttype=Catalog&lang=en&productname=&series=DF52), indexed Apr.2026, direct endpoint404. Numerical screen uses archived manufacturer [catalogue copy](b3/sources/df52.pdf) from [LCSC CDN](https://atta.szlcsc.com/upload/public/pdf/source/20240705/F8048CFA8CA38915C03406E9857DD465.pdf), cover Jun.2023: pp2,4–6,8–9. Hirose **EDC3-356517-01**, 2017-03-10, [manufacturer drawing mirror](https://www.rxelectronics.kr/datasheet/ce/DF52-8S-0.8H%2821%29.pdf), [archive](b3/sources/df52-drawing.pdf), mating figure **(4.1)×(1.75)** and fourteen-way width row **13.4**. Visually checked. [Current terminal record](https://www.hirose.com/product/p/CL0668-0030-5-00), updated 2026-02-07. |
| FFC | Hirose [FH12 D31648_en](https://www.hirose.com/en/product/document?clcode=CL0586-0819-2-98&documentid=D31648_en&documenttype=Catalog&lang=en&productname=FH12-36S-0.5SVA%2898%29&series=FH12), printed Apr.2026, ratings/durability and horizontal assembly. Molex [SD-15266-001 F](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/152/15266/152660321_sd.pdf?inline=), 2023-08-08, cable length/type table; [Premo-Flex manufacturer datasheet](https://www.content.molex.com/dxdam/2d/2d73ee52-1c37-44c5-8b5e-787e4af51b13/987650-6631.pdf). |

Manufacturer documents mirrored by distributors remain manufacturer evidence;
the mirror does not establish a current revision. PDF fetch failures and archive
provenance are retained. Unknown ratings below are deliberately not filled from
generic connector comparison blogs.

## Every family: mechanical, electrical, cable and durability screen

Heights are **seated system envelopes above the mounting face**, not the pitch
or bare-header height. V=vertical mating; H=horizontal/side mating. H exit is
parallel to the board. On an underside Wing the normal flips, not the height.

| Family / pitch | Maximum documented circuits and 14-conductor choice | Selected seated envelope / options and wire exit | Electrical per contact; wire fit; initial contact R | Lock / rated cycles |
|---|---|---|---|---|
| **JST SH /1.0** [SH] | 20; **single14**, SM14B-SRSS-TB + SHR-14V-S-B | **2.95 high ×6.25 deep** H; V assembly **6.3** high with normal wire exit. H screened, including protruding housing width17.0 | **1 A at AWG28**; AWG32–28, OD0.4–0.8; **20 mΩ**, after tests40 | Friction; catalogues reviewed do **not state a cycle rating**. Supplier qualification required; do not borrow GH's rating |
| **JST SUR /0.8** [SUR] | 22 side /20 top; **single14** SM14B-SURS-TF +14SUR-32S | **1.75 high ×3.9 deep** H; V3.9 high; H wires parallel, V normal | **0.5 A AWG32 /0.2 A AWG36**; **no AWG28**; specified 7-strand OD0.39; **20 mΩ**, after tests40. IDC sockets, not loose crimp contacts | Friction; rated cycles **not published in reviewed catalogue** |
| **JST ACH /1.2** [ACH] | **5 maximum**; **5+5+4** (or4+4+3+3) | **1.40 high ×4.30 deep**; V mating but **horizontal side feed**; no H-mating version proved | 4/5-way **1.5 A AWG28**, smaller2 A; AWG32–28 with correct terminal, AWG28 OD0.50–0.63; **10 mΩ**, after tests20 | Friction; rated cycles **not published in reviewed catalogue** |
| **Molex PicoBlade /1.25** [PB-D/PB-S] | Current 53261 drawing through17; **single14** 532611471 +510211400 | H **3.40 high**, mated depth **5.2+1.0=6.2**; vertical 53398/53047 options have normal exit; do not use bare vertical header height as mated height | AWG28 supported by500588000 (28–32) or50079 (26–28); terminal OD0.5–1.0. Platform rated1 A at AWG28. **20 mΩ**, post-cycle40; separately5 mΩ crimp [PB-S] | Friction windows; tin **30 cycles** [PB-S] |
| **Molex Micro-Lock Plus /1.25** [ML-D/ML-S] | **42 maximum dual-row**, single-row2–16 per [Molex family table](https://www.molex.com/en-us/products/connectors/wire-to-board-connectors/micro-lock-plus-connectors); **single14** 5055671471 +5055651401 selected | H **(4.20) high ×(7.40) deep**, **not bare-header3.90**; V505568 available, normal wire exit; H screened | AWG26–30; AWG28 **1.8 A** in ML-S (product listing more conservatively1.5 A); OD0.78–1.02; **20 mΩ + separately5 mΩ crimp** | Positive latch; **30 cycles** |
| **Molex CLIK-Mate /1.5** [CM] | **40 dual-row maximum** per [Molex core-products table](https://www.content.molex.com/dxdam/91/91bdeab4-67b2-46be-aef3-ba038fc289e3/Wire-to-Board%20Signal%20Core%20Products%20987651-9152.pdf); single-row2–15, **single14** 5025851470 +5025781400 selected | Selected H system **6.40 high**; V and lower-profile SMT receptacle subseries exist. Even a bare3.8-high alternative cannot pass the3.15 screen; do not claim3.8 is its mated height | Selected product **2 A max**, actual wire/circuit derating required. Platform AWG24–30 with matching502579/503429 terminals; AWG28 reference1 A; platform contact20 mΩ/crimp5 mΩ; exact502585 qualification cross-check open | Positive latch; selected product **30 cycles** |
| **Molex Pico-Clasp /1.0** [PC-D/PC-S] | Single-row through15, dual-row through50; **single14** or5+5+4 | 6–15-way H inner-lock drawing **5.0 overall /4.7 body**; small2–5 H **3.2**; V501331 is taller. **Do not apply the small-circuit3.2 to14-way** | AWG28–32, OD0.4–0.8; **1 A AWG28**, **20 mΩ**, tin/gold specification selected separately | Inner positive lock6–15; friction small-circuit versions; tin **30 cycles** |
| **Hirose DF13 /1.25** [DF13] | Single-row15 /dual-row40; **single14** | H body alone **3.6** (mated system cannot be lower); V assembly **5.8**. H parallel exit, V normal. Body-only lower bound already rejects fixed-zone Main | **1 A conservative14-way housing rating**; AWG26–30 on2630 terminal includes28 (other contact30–32); OD0.56–1.0; **30 mΩ** | Friction; **30 tin /50 gold cycles** |
| **Hirose DF14 /1.25** [DF14] |30; **no exact14 row in catalogue**: **7+7**, or15 housing with one unpopulated position (only14 conductors) | On-board H **2.50 high ×7.30 deep**; offset DF14H advertises1.6 above PCB but penetrates board datum/needs edge geometry. **Offset height is not a free underside stack reduction** | **1 A**, AWG28 onDF14-2628SCF (26–28), alternate30–32; OD0.54–1.0; **30 mΩ** | Friction; **30 tin /50 gold cycles** |
| **14-pin FFC +Hirose FH12 ZIF /0.5** [FFC] | FH12 through53; **single14**, FH12-14S-0.5SH(55) | H **2.0** seated; flat cable exits parallel; top/bottom contacts and vertical types require different orientation/cable checks. Actuator-open/service envelope additional | **0.5 A/contact**, **50 mΩ**; **0.30±0.05 mm** FFC tail, AWG is inapplicable. Cable trace resistance and current separately qualify | Flip-lock **ZIF actuator,20 cycles**; not a wire-housing latch |
| **Added: Hirose DF52 /0.8** [DF52] |20 catalogue; **single14** DF52-14S-0.8H(21) +DF52-14P-0.8C | **1.75 high ×4.10 deep**, H mating and horizontal exit, width13.40. No V alternative assumed | **1.2 A at14-way AWG28** (2.5 A applies to2-way only); AWG28–32, thin-wall OD0.50–0.60; **10 mΩ**, after durability/environment20 | Friction retention; **20 cycles** |

DF52 was added because it combines an actual14-way mating pair, AWG28, a
height close to EZmate, and a demonstrated JLC header path. A generic “0.8 mm
connector” or clone is not accepted as a qualified cross-mate. In particular,
JLC “JST compatible” substitutes are not genuine JST SH inventory.

## Supply, lifecycle and cable construction

In the following table **O/P** means the exact part's direct JLC overseas /
presale counts, on2026-11-14, linked to archived HTTP observations. These are
not LCSC loose-part counts. LCSC IDs are explicit; **U** means the exact ID or
inventory could not be established, not that the product does not exist.
All cached counts are indicative and excluded from claims of fresh stock.

| Family | Header: exact SKU, LCSC ID, supply / JLC assembly | Housing/socket: exact SKU, LCSC ID and supply | Terminal: exact SKU, LCSC ID and supply | Lifecycle and supply conclusion |
|---|---|---|---|---|
| SH | SM14B-SRSS-TB(LF)(SN), **C160413**, **O0/P1342**, pre-min13; SMT Economic/Standard library. [Cached LCSC page](https://lcsc.com/product-detail/wire-to-board-connector_jst-sm14b-srss-tb-lf-sn_C160413.html) says out of stock; do not infer an immediate PCBA build | SHR-14V-S-B, **C265413**, **O3183/P3183**; [LCSC record](https://www.lcsc.com/product-detail/Rectangular-Connectors-Housings_JST-SHR-14V-S-B_C265413.html), loose stock U | SSH-003T-P0.2-H, **C263995**, **O343070/P343070**; [cached LCSC image](https://www.lcsc.com/product-image/C263995.html)221550 | No obsolete flag located; pre-purchase header quantity exceeds600, actual in-house stock not demonstrated. Housing/terminal loose order separate. **Conditional survivor** |
| SUR | SM14B-SURS-TF, **C595176**, **O29/P23**; SMT library, below60 endpoint requirement; [cached LCSC](https://lcsc.com/product-detail/Wire-To-Board-Connector_JST-SM14B-SURS-TF-LF-SN_C595176.html)0 |14SUR-32S, **C17262614**, **O0/P0**; [record](https://www.lcsc.com/ko/product-detail/idc-connectors_jst-14sur-32s_C17262614.html); assembled IDC socket | Contacts integral to socket: **N/A separate terminal** | No obsolete flag found; insufficient demonstrated header/socket supply. **Procurement gate fails now**, electrical not killed |
| ACH | BM05B-ACHSS-A-GAN-ETF, **C5304901**, **O117/P106**; BM04B-ACHSS-A-GAN-TF **C5246838 O0/P0**. Both SMT library; complete5+5+4 JLC set unavailable | ACHR-04V-A-S **C566315 O18840/P18840**; ACHR-05V-A-S exact LCSC ID **U**, [JST/GAM listing](https://gam-gec.com/product/achr-05v-a-s/) **837 cached** | SACH-003G-P0.2 **C567010 O32696/P32696** (AWG28); P0.2B/C595019 is thinner-wire terminal, not AWG28 rescue | [Older four-way ETF record](https://partstack.com/p/j-s-t-mfg/bm04b-achss-a-gan-etf/1463988091) flags discontinued: **automatic red flag on that SKU**; do not apply this flag blindly toTF or whole ACH family. CurrentTF [Mouser series](https://www.mouser.in/en/c/connectors/?m=JST&series=ACH)4561 cached, but current JLC0. **Hold complete-system supply/lifecycle** |
| PicoBlade |532611471 **C505101 O97/P0**, SMT library; [cached LCSC](https://www.lcsc.com/zh-CN/product-detail/wire-to-board-connector_molex-532611471_C505101.html)1556 conflicts with direct availability |510211400 exact LCSC ID **U**; [Özdisan](https://www.ozdisan.com/p/housing-konnektorler-307/molex-molex-510211400-349016) **2892 cached**, active listing |500588000 **C293573 O187599/P187599**; [cached LCSC](https://www.lcsc.com/de/product-detail/C293573.html)241900 | PB-D contains an obsolete-SKU removal note (PCN515981); selected532611471 remains in its table, so exact-SKU lifecycle confirmation is required, not a blanket family obsolete claim. Header supply is weaker than cached count implies; **geometry eliminates selected system** |
| Micro-Lock Plus |5055681471 vertical **C17698157 O10/P10**, SMT library. Selected H5055671471 LCSC ID/JLC availability **U**; [DigiKey](https://www.digikey.com/en/products/detail/molex/5055671471/7914334) **4331 cached** |5055651401 **C5382678 O553/P553**; [DigiKey](https://www.digikey.sg/en/products/detail/molex/5055651401/7914315) **15110 cached**, active |5054311000 **C385112 O80620/P80620**; [LCSC image](https://www.lcsc.com/product-image/C385112.html?whichImg=sch)219900 cached | [Molex vertical record](https://www.molex.com/en-us/products/part-detail/5055681471)active; selected H distributor active. Good alternate distribution, exact H JLC route unproved; **geometry eliminates** |
| CLIK-Mate |5025851470 **C5527870**; [direct LCSC China record](https://item.szlcsc.com/6444044.html) `stockNumber=24000`, `productCycle=normal`; JLC **O0/P0**, pre-min5 (direct follow-up) |5025781400 LCSC ID **U**; [DigiKey](https://www.digikey.com/en/products/detail/molex/5025781400/2819010) **15435 cached** |5025790000 **C293594 O338500/P338500**; loose LCSC current count U | No discontinuance flag found on selected SKU; Molex limited-information page is not itself an obsolete flag. Supply cannot fix **height failure** |
| Pico-Clasp |5013311407 **C724096 O2493/P2418**, SMT Economic/Standard; [cached LCSC](https://www.lcsc.com/product-detail/C724096.html)3223 |5013301400 **C504830 O32427/P32427**; [cached LCSC feed](https://www.oemstrade.com/search/30-140)32425 |5013340000 **C127374 O35261/P35261**; [cached LCSC](https://www.lcsc.com/de/product-detail/housing-contact_molex-5013340000_C127374.html)122700 | [Header active at Molex](https://www.molex.com/en-us/products/part-detail/5013311407). Some small-circuit housing suffixes removed byPCN516693: do not use a family-wide lifecycle assertion. Good selected14-way supply, **height eliminates** |
| DF13 |DF13-14P-1.25H(75) **C17465383 O0/P0**, SMT library |DF13-14S-1.25C exact LCSC ID **U**; current Hirose product remains documented |DF13-2630SCF **C88344 O71765/P71765**; [LCSC](https://www.lcsc.com/pt/product-detail/Housing-Contact_HRS-Hirose-DF13-2630SCF_C88344.html) loose current U | No obsolete flag established; **bare-header lower bound already fails Main allowance**, header availability also0 |
| DF14 |DF14-7P-1.25H(52), exact LCSC ID/count and JLC route **U**; [DigiKey product record](https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/DF14-7P-1-25H-52/13626958), no dependable count extracted |DF14-7S-1.25C, or current(10) suffix: LCSC ID/count **U**; current manufacturer table documents7. Do not substitute JMEconn DF14-07AWB/C56260750 as genuine Hirose |DF14-2628SCF **C88353**, [LCSC record](https://www.lcsc.com/product-detail/C88353.html), **O7698/P7698** in direct JLC follow-up; loose LCSC stock U | No obsolete flag located, but exact header/housing procurement **unproved**. 7+7 also has substantially larger width than DF52; **hold**, not electrical kill |
| FFC/ZIF |FH12-14S-0.5SH(55) **C5378715 O3919/P3909**, SMT library |No crimp housing. Molex **152660149**, same-side tails, **152±4 mm**, active; [DigiKey](https://www.digikey.com.au/en/products/detail/molex/0152660149/3160884) **8 direct-distributor /455 marketplace cached**, not summed. LCSC SHOU HAN FFC-0.5-14P-150mm **C6936336** listing, stock U, not prequalified equivalent |Integral cable lands, **N/A loose terminals** | No selected obsolete flag found. Header supply strongest; cable thickness/contact plating/resistance and actual route need qualification. **Third-ranked conditional alternative** |
| **DF52 added** |DF52-14S-0.8H(21) **C5343398 O5084/P5082**, pre-min20, SMT Economic/Standard library. [LCSC feed](https://www.lcsc.com/brand/793-1007.html)5079 cached; [DigiKey](https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/DF52-14S-0-8H-21/5721379)2550 cached |DF52-14P-0.8C **C2904692 O4/P4**, pre-min35; [cached LCSC](https://www.lcsc.com/pl/product-detail/Housings-Wire-To-Board-Wire-To-Wire_HRS-Hirose-DF52-14P-0-8C_C2904692.html)out of stock. **[DigiKey840 cached](https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/DF52-14P-0-8C/5721346)** exceeds600 preference, active; loose fallback is essential |DF52-2832PCF **C506724 O129490/P129490**; [TME28795 cached](https://www.tme.com/us/en-us/details/df52-2832pcf/other-hirose-connectors/hirose/), regional sale restriction shown, so not an unconditional order path | Active distributor records, current manufacturer documentation, no discontinuance found. **Best conditional survivor**; housing is an identified supply bottleneck, not hidden by header stock |

Direct records: [initial](b3/sources/http-observations.json),
[DF52/FFC](b3/sources/http-more.json), [remaining families](b3/sources/http-final.json), [follow-up](b3/sources/http-followup.json).
No number in the JLC columns is represented as fresh LCSC loose inventory.
The remaining **U** entries mean this survey has not secured those supply
paths; they prevent declaring a procurement PASS and are not invented zeros.

### Harness paths, separately from PCB assembly

| Family | ≤200 mm lead / harness evidence, or documented construction path |
|---|---|
| SH | No genuine14-way ≤200 mm ready-made1:1 cable with demonstrated stock was qualified. Make custom AWG28 leads with **SSH-003T-P0.2-H, reeled23000**, JST **AP-K2N +APLMK SSH/L003-02**, per SH contact/tool table. Small off-the-shelf SH/Qwiic cables are not evidence for fourteen conductors or AWG28. Harness shop is preferable to an unqualified generic hand crimper. |
| SUR | **IDC**, so no crimp terminal or crimp-tool shortcut. Custom fourteen-way AWG32,7-strand OD0.39 cable requires the matching JST IDC applicator/process; exact tooling order number and a compliant stock assembly were **not established**. Integrated socket stock0 is a present procurement failure. Compatible SUH crimp sockets are a different system and were not silently substituted. |
| ACH | Custom AWG28 OD0.50–0.63, **SACH-003G-P0.2 reel30000**, **AP-K2N +APLMK SACH003-02** [ACH]. JST/GAM [GAM-045](https://gam-gec.com/wp-content/uploads/2018/10/GAM-045.pdf) documents ASACHSACH28W305 double-ended leads, **304.8±5 inside /310.6±5 overall mm**: these fail≤200 as sold. Re-crimp to custom length; no mid-wire splice assumed. |
| PicoBlade | Custom AWG28 with500588000 (chain/reel), or manufacturer pre-crimp leads after checking exact length. Molex [151341400 cable drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/151/15134/151341400_sd.pdf),2012343242, documents14-way AWG28 but maps **A1→B14**, not required cavity1→1. Cannot buy it on appearance alone. Molex [tool2002181900 ATS revision B,2023-08-18](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationtoolingspecificationpdf/200/200218/2002181900-000.pdf) explicitly covers500588000, AWG28–32, **OD0.67–1.00** for this hand tool; that narrower OD range governs hand construction. |
| Micro-Lock Plus | Reel **5054311000**, AWG26–30/OD0.78–1.02 [ML-S]. [Manufacturer housing information](https://www.mouser.com/datasheet/2/276/2/5055651401_CRIMP_HOUSINGS-1914850.pdf) lists pre-crimp series797581148/1149/2143/2144; no≤200 mm exact double-ended lead was qualified. Molex [hand tool2002180300 ATS C,2021-03-03](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationtoolingspecificationpdf/200/200218/2002180300-000.pdf) explicitly covers5054311000; cut from reel with carrier tab limit0.10 mm. A terminal/tool-specific path exists; an EZmate crimper is not interchangeable. |
| CLIK-Mate | Reel **5025790000** for AWG24–28 (or5034290000 for26–30), appropriate insulation perCM. Custom1:1 cable≤200; exact ready-made14-way cable **unverified**. Molex [hand tool2002187400](https://www.molex.com/en-us/products/part-detail/2002187400) explicitly lists5025790000,28–24 AWG; follow its ATS and wire insulation limits. |
| Pico-Clasp | Reel **5013340000**, AWG28–32, tin matched to501331; custom≤200. Legacy hand tool638191500 is a candidate (manufacturer product page remains, direct ATS not retrieved); its exact501334/wire qualification is still open. Use a cable shop with the501334 ATS rather than assuming the gold501193 tool qualification transfers. No matching≤20014-way stock cable qualified. |
| DF13 | **DF13-2630SCF reel10000**; **AP105-DF13-2630S +CM-105C**, or **DF13-TB2630HC** for the specified terminal/wire, perDF13 catalogue. Documented DF13-2630S1-26A9-300 pre-crimp leads are300 mm, fail as sold; custom AWG28 length needed. |
| DF14 | **DF14-2628SCF reel10000**, **AP105-DF14-2628S +CM-105C**, manufacturer **DF14-2628/CR-HT** manual option; contacts cut sequentially with carrier [DF14]. No≤2007+7 stock cable qualified. A15-way cable with unused cavity must still map all fourteen1:1. |
| FFC/ZIF | **152660149 is a genuine ready-made14-conductor152±4 mm cable** [FFC]; no crimping. It meets the length cap including tolerance, but a152 mm cable must prove the actual path plus30.2 mm reserve. A203±4 mm item fails. Custom FFC length/tail contact orientation possible; use a rated maker, not scissors to create unstiffened tails. |
| **DF52** | Custom AWG28 thin-wall **OD0.50–0.60**, **DF52-2832PCF reel40000**; **AP105-DF52-2832P +CM-105C**, or J.A.M. **DHS877900H-UP**, perDF52 p9. No specified hand crimper appears in that table; use a cable shop with qualified applicator. Terminal extraction **DF-C-PO(B)** is not a crimper. No genuine stock≤200 mm double-ended14-way harness was qualified. |

These are different questions: Main SMT assembly, Wing SMT/hand assembly, and
wire harness production. A JLC page offering “SMT assembly” for a loose crimp
contact does not mean JLC crimps the harness. For both finalists specify finished
length with tolerance **upper limit≤200**, cavity-to-cavity mapping, insulation
OD, crimp-height/pull acceptance to supplier process, continuity, short check,
and measured completed power-loop resistance. No supplier was contacted and
no purchase or reservation was made.

## Ranking and elimination

This is an ordinal engineering ranking, not a weighted numerical score that
would give equal value to an obsolete part and a fraction of a millimetre.
“Hold” means an open adoption gate, “killed” means a demonstrated failure of the
screened configuration. FFC is allowed as the requested wildcard; AWG28 is not
reinterpreted as mandatory to exclude it.

| Rank | Family | Thinness | Supply security | Cable path | Lock/durability | Electrical fit | Decision / kill reason |
|---:|---|---|---|---|---|---|---|
| **1** | **DF52** |1.75; tie-limited deck | Main header strong; genuine loose housing fallback must be secured | Single14, custom thin-wall28; applicator shop needed | Friction/20 |1.2 A vs0.127 A, lowest contact R of finalists | **Carry forward**, conditional supply/harness |
| **2** | **SH side14** |2.95; same deck, tight roof | Header pre-purchase1342; overseas0; mature part ecosystem, no lifecycle flag found | Single14, wider wire pitch, custom28 | Friction; cycle rating unresolved |1 A vs0.127 A | **Survives**; exact roof only0.20 after allowance |
| **3** | **FFC +FH12** |2.0; same arithmetic deck | Header strong; genuine compliant-length cable exists, cached stock limited | Fast assembly, but flat cable cannot fan or bend edgewise like loose wires | ZIF20; fragile actuator/service handling |0.5 A sufficient; trace/loop R must be specified | **Conditional alternate**; route/service and cable construction unproved |
|4|ACH |1.4 gains no additional deck saving | Complete5+5+4 default JLC set fails; exact legacy ETF flag | Three connectors, same-sized5-way interchange risk; custom crimp | Friction, cycles unverified |AWG28/10 mΩ good | **Hold**, legacy flagged SKU killed; whole family not declared obsolete |
|5|DF14 on-board |2.5; tie-limited |7-way genuine header/housing JLC not established | Two connectors, pair minimum27.4 mm before spacing; alternatively15-way one unused |30/50 friction |AWG28/30 mΩ good | **Hold** supply/placement; offset version needs different board-edge geometry |
|6|SUR |1.75, electrically possible |Header29/socket0 demonstrated, fails batch supply |IDC AWG32, exact qualified process unproved |Friction/cycles unknown |Voltage still passes; more loss than28 | **Hold procurement**; not killed by wire gauge/current |
|—|PicoBlade |3.4 H |Supply alternatives exist |Single14 custom or reversed factory harness |Friction/30 |Current adequate | **Killed for retained fixed-zone Main allowance**: nominal roof ceiling budget0.25<0.50; −0.25 after allowance |
|—|Micro-Lock Plus |4.2 H mated |Active, good alternate distribution |Single14, larger wire OD |Positive/30 |Adequate | **Killed Main height**: at least4.2 exceeds3.15; Wing would also bind atB7.2 |
|—|CLIK-Mate |6.4 selected H |Some strong inventory |Single14 but bulky |Positive/30 |Adequate | **Killed Main height / thickness objective**; lower-profile subseries not a proved escape below3.15 |
|—|Pico-Clasp |14-way H5.0; small-circuit3.2 |Good selected14-way supply |Single14 or three small connectors |Positive14-way/30 |Adequate | **Killed Main height** for14-way; even small5+5+4 nominal0.45<0.50 allowance (short0.05), before extra cable/placement work |

Families killed on the retained Main clearance allowance are not asserted to
be electrically bad or unavailable. If that allowance is explicitly changed,
or a future board legitimately moves the system away from the low roof, these
configuration-specific eliminations would need reconsideration.

### FFC power, mechanics and service trade-offs

FH12's0.5 A/contact exceeds0.127 A on one supply contact; six ground lanes remain
separate. **Paralleling power is not necessary on contact rating and is not
available within the unchanged14-way allocation.** Repurposing a GND violates
the retained contract. A connector rated0.1 A/contact would fail on the single
supply lane; a larger-count FFC with additional power lanes is a contract change.
FH12's50 mΩ/contact contributes `(2×0.050)×7/6=116.667 mΩ` to the loop before
cable copper. A cable maker must specify conductor cross section/resistance;
a “150 mm FFC” marketplace description is insufficient for an AWG28-equivalent
claim. At200 mm, for illustration only, a0.035 mm² lane gives wire98.52 mΩ
at20°C and loop231.61 mΩ/contact-only: about29.41 mV at127 mA. This is an
**assumed lane area sensitivity**, not a rating of152660149.

The flat cable preserves lane ordering but may reverse apparent cavity mapping
when connector faces rotate; prove1→1 electrically for the chosen Type A/D and
top/bottom contact configuration. The gold FH12 tail requirements versus a
tin Premo-Flex candidate also require a compatible finish selection. A flat
service loop needs broad-face bending space, actuator access, retained
stiffeners and strain relief away from the contact area; no sharp fold, cable
twist, edgewise R5 route, or a20-cycle rating is treated as an unlimited hinge.
The2.0 mm closed connector height is not its open-actuator or loop height.
Those route/service uncertainties keep it below the two discrete-wire finalists.

## Top two: drawing envelopes, Wing bounds and Main roof

The **same frozen Rev7 J2/J3 zone centres/angles** and Rev4 Wing J_WING centres
are read from the native board/definitions. One connector replaces each14-way
interface in the model; no pads/copper are altered. A proposed seated-box centre
is placed at the old zone origin; this is **not pad compatibility or a claim
that the new footprint datum equals GH's**.

| Proposed centre, assembly mm | X | Y | Main inherited rotation |
|---|---:|---:|---:|
|J2|−17.102146|42.075001|−120°|
|J3|17.102146|42.075001|120°|
|Left Wing|−27.000000|−41.000000|native Rev4 transformed frame|
|Right Wing|27.000000|−41.000000|native Rev4 transformed frame|

| Drawing-bound or engineering term | DF52 | SH |
|---|---:|---:|
|Seated body width×depth×height mm|**13.40×4.10×1.75**|**17.00×6.25×2.95**, includes protruding SHR housing|
|Pitch /wire OD maximum used mm|0.80 /0.60|1.00 /0.80|
|Local body u range mm|±6.70|±8.50|
|Local body v range mm|±2.05|±3.125|
|Full first-dress local u range mm|−6.70…7.169873|−8.50…8.569873|
|Full first-dress local v range mm|−2.05…8.582051|−3.125…9.757051|
|Connector-only B:2+E+0.5+0.5|4.75|5.95|
|`max(connector,Hall5.90,tie/root6.70,others)`|**6.70**|**6.70**|
|Wing connector/dress bottom Z|4.95|3.75|
|Wing bottom after0.50 allowance|4.45|3.25|
|Residual clearance above floor topZ2 after allowance|**2.45**|**1.25**|
|Required free gap retained|0.50|0.50|
|Plate topZ = B+6.20|**12.90**|**12.90**|
|Main PCB topZ|7.90|7.90|
|Main connector/dress topZ|9.65|10.85|
|**Exact Main vertical gap, J2 and J3 vs unchanged B0**|**+1.900000**|**+0.700000**|
|After0.50 assembly allowance|**+1.400000**|**+0.200000**|
|BRep Common volume, each Main envelope mm³|**0**|**0**|
|True BRep minimum distance mm|1.900000|0.700000|

The1.75 and2.95 heights are drawing **reference assembled** values. Retaining
0.50 engineering allowance is essential; it does not turn a reference into a
manufacturer guaranteed maximum. First dress uses B2's engineering assumption:
**2 mm straight, R5/30° XY turn,2 mm straight**, with all fourteen wires at
their native pitch. This is not a supplier-specified minimum radius. Outlet
axis height is not independently dimensioned, so the **entire seated Z band**
is retained around the wire path. A vertical downward Wing bend or upward Main
bend would require a new envelope and could erase the advantage. Approximate
wire-to-wire separation in the bend is at least `pitch*cos30°−OD`:
DF52 **0.09282 mm**, SH **0.06603 mm**. The conservative rectangular occupied
union includes wire voids and is used in the STEP tests; no detailed moulding
or free terminal float is reconstructed.

Both Wing bodies and dress bounds fit the frozen17 mm outlines. There are no
overlaps with the same nearby conservative component reservations as B2;
minimum XY gaps are **DF52 2.617949 /SH1.442949 mm**. Main bodies also remain
inside the outline. **Main wires exit beyond the PCB into the side bay**:
first-dress projected area outside PCB is DF52 about44.21 mm² per side and
SH72.16 mm². A wire leaving the PCB outline is not an edge collision by itself;
the full first-dress solid is included in the roof test. Complete case/wire,
component, floor, service-motion and end-to-end harness routing remain open.
This is not B2's two-connector inboard placement.

The solver imports `b0/roof-b0.step` unchanged: **eight solids**, volume
**32001.277514 mm³**, SHA256
`40f275f1f48a42fa0ee383f67ed0925eaa900bdc9508e9eafe1c2df51b466dc6`.
It clips each occupied envelope by all eight actual underside-face footprints
and optimizes signed vertical clearance under the corresponding affine planes.
Worst support is the low-south Z11.55 face. Exported STEP reimport independently
repeats the test: **PASS**, all solids valid, roof hash unchanged. No translated
or pocketed roof was substituted.

If the roof later follows the0.65 lower deck, the gaps become **DF52+1.25 /
SH+0.05 nominal**, or+0.75 /−0.45 after allowance. Thus **SH's present PASS
must not be carried into a lowered-roof design**. At the old B7.35 Main board
datum the same nominal gaps also decrease by0.65. The requested comparison in
this report is expressly the unmodified B0 solid at newB6.70.

The unchanged Hall and tie/root constraints still give Hall bottomZ3.30,
tie tipZ1.20 and post overall5.50, as in B2. No structural justification for
thinning the root was introduced. These results save **0.65 from Phase A's
GH Z13.55**, and **zero versus B2 EZmate'sZ12.90**.

Artifacts:

- DF52: [local envelope](b3/df52-local-envelope.step), [Wing context](b3/df52-wing-screen.step), [roof/Main context](b3/df52-roof-main-screen.step), [section PNG](b3/df52-sections-b3.png).
- SH: [local envelope](b3/sh-local-envelope.step), [Wing context](b3/sh-wing-screen.step), [roof/Main context](b3/sh-roof-main-screen.step), [section PNG](b3/sh-sections-b3.png).
- Individual Main J2/J3 and left/right Wing envelopes, [poses/clearances](b3/clearances-b3.json), [STEP replay](b3/verification-b3.json), and [electrical calculation](b3/electrical-b3.json) are in `b3/`.

## Electrical loop comparison, including thinner-wire sensitivity

Use B2's conservative AWG28 minimum copper area **0.0804 mm²**, not a claim
that every thin insulation28-AWG wire has that minimum. DF52's specified
7×0.127 mm strand construction is larger, so the retained minimum is
conservative. At each endpoint use the manufacturer's initial contact maximum:
**DF52 10 mΩ /SH20 mΩ**. Add **5 mΩ/crimp per end as an engineering acceptance
allowance**, retained for comparison with B2; it is **not a published JST or
Hirose crimp-resistance rating**. Supplier test methods may include part of
this path already. Finished-loop measurement closes that uncertainty.

`Rwire(T)=1.7241e−8×0.200/(area_mm2×1e−6)×(1+0.00393×(T−20))`

`Rloop=(Rwire+2×(Rcontact+0.005))×(1+1/6)`

One supply conductor carries127 mA; equal-length parallel grounds nominally
21.167 mA each, assuming adequately low board spreading resistance. The three
analogue returns and all other ground positions are preserved.

| System /wire | Loop20°C mΩ | Drop20°C mV | Loop125°C sensitivity mΩ | Drop125°C mV | Farthest V, frozen Rev7 pessimistic copper/legacy Wing model |
|---|---:|---:|---:|---:|---:|
|DF52 AWG28|85.036|10.800|105.683|13.422|**4.803330 V**|
|SH AWG28|108.369|13.763|129.017|16.385|**4.800366 V**|
|B2 EZmate AWG28|108.369|13.763|129.017|16.385|4.800366 V|
|SUR AWG32, assumed minimum0.032 mm²|184.049|23.374|235.926|29.963|**4.786789 V**|
|SUR AWG36, assumed0.0127 mm²|375.097|47.637|505.810|64.238|**4.752514 V**|

All exceed the inherited4.60 V far-end minimum in this frozen model; **SUR
is not electrically killed**, even though its supply and tooling are worse.
Its actual seven-strand copper construction must be checked, not replaced
by nominal AWG arithmetic. Current ratings0.5/0.2 A also exceed127 mA.
At the manufacturer's85°C upper operating temperature the finalists' loops
are **DF52 97.818 mΩ /SH121.151 mΩ**, with drops12.423 /15.386 mV.
**125°C is a copper sensitivity corner, above both finalists'85°C rating**;
it is not an operating-temperature qualification. The same caution applies
to SUR and B2's105°C-rated EZmate. The JSON includes20/85/125 rows and
environmental-contact sensitivities. At125°C with DF52's20 mΩ post-test
contact value its loop becomes129.017 mΩ; with SH's40 mΩ it becomes175.683 mΩ.

As in B2, replace only Rev7's187.350 mΩ harness term. Keep rail5.2 V−2%,
50 mV dynamic allocation, U5 Ron0.25 Ω, both Wings powered, pessimistic Main
branch and147.710 mV legacy Wing drop. This is a comparison, not a new copper
qualification. Neither harness achieves a hypothetical whole-loop≤50 mΩ
target. Frozen Main copper targets remain separate; any board reroute must
repeat extraction and cannot inherit its0.509 mΩ common-path margin.

## Verdict and what an adoption round must prove

**Yes, DF52 beats the current combined choice set for carrying forward:**
it obtains EZmate's tie-limited thin deck with stronger nonobsolete header
procurement evidence, a single documented14-way pair and20 rated mating
cycles, while clearing the unchanged roof without GH's slope blister.
It is0.10 mm taller than EZmate's seated reference, so this is **not a claim
of component-height dominance**; the deck result is identical and supply is
better. SH is a workable second choice if pre-purchase succeeds and the
unmodified roof stays; FFC is the third candidate if its routing/service
trade-offs are accepted. **No surveyed option legitimately beats B6.70 or
plateZ12.90 under the unchanged tie/root geometry.**

An adoption round must first turn DF52's housing fallback into an actual
genuine-stock lot, reserve/pre-purchase the exact Main headers for PCBA and
spares, confirm manufacturer lifecycle and the current drawings, and qualify
a shop using the specified AWG28 thin-wall wire/applicator. The200 mm limit,
30.2 mm reserve,1:1 cavity map, pull/continuity/loop resistance and physical
wire-root float must be demonstrated on the complete left/right harnesses.

Then prove new symbols, lands/hold-downs/no-pattern areas and solder access on
successor Main and all four Wing variants (16/17 mm, L/R); neighbour/TP/via/
NPTH clearance; full harness and housing insertion/removal with roof off;
friction retention/strain restraint and a20-cycle manufacturing/service budget.
Re-run ERC, native DRC, independent net/cavity checks, copper resistance,
power margins, ADC settling/return integrity and full case collisions at the
actual roof datum. Confirm PCB thickness/stencil and Wing assembly route.
Amend the physical-interface/harness decision records explicitly rather than
silently changing D-024/D-033. B0's south-opening and Fly conflicts are still
separate work. This survey authorizes none of those design changes by itself.

## Reproduction and verification

```bash
export TMPDIR="$PWD/.issue248-runtime"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2
/home/hatch/workspace/tools/cad-venv/bin/python hardware/case/issue-248-lowdeck-raise/study-b3.py
/home/hatch/workspace/tools/cad-venv/bin/python hardware/case/issue-248-lowdeck-raise/verify-b3.py
/usr/bin/python3 hardware/case/issue-248-lowdeck-raise/plot-b3.py
```

Both section PNGs and both source assembled-drawing views were visually
inspected. Verification reimports every exported STEP, checks validity,
independently clips the roof and checks the Wing Z bounds/floor allowance.
This verifies the stated survey model; no native PCB design check is claimed.
[artifact-sha256-b3.json](artifact-sha256-b3.json) binds deliverables and inputs.
All scratch, downloads in progress and caches were confined to
`.issue248-runtime/`; retained source evidence is under `b3/sources/`.
