# EDA-004G — native Main routing qualification

**CONVERSION_BLOCKED / ERC_UNQUALIFIED — selected-library prerequisite not established; Stage 1 STOP.**
[Issue #85](https://github.com/ihsinoky/he-piantor-42/issues/85) authorized the
non-product `RepresentativeMain strategy=3` evaluation. Complete Main pin-model
coverage was not established in the selected pinned-library/public-API reuse
path. No Main schematic or PCB was generated; no routing was launched.
Main initial/confirmation counts are **0/0**, small transport trials **0**.
The classification concerns the selected prepared library configuration only,
not method-wide failure or proof that large custom implementation is required.
See the [PMO read-only supplement](#pmo-read-only-supplement-2026-10-14-merge-hold)
for existing reuse candidates and limits; PMO review currently holds merge.
All Main acceptance metrics are **null**, not zero or PASS.

This is a **partial prerequisite evaluation and submitted STOP report**. It is
not Main routing failure, proof of general tool incapability, adoption, a Human
Gate, or authorization to start product design. PMO/reviewer is ChatGPT; PO is
the user. Codex implemented/evaluated and made the execution stop; PMO reviews
the evidence and PO owns acceptance and any subsequent investment decision.

## Authority, initial state and changed hypothesis

At **2026-10-14 01:17:56 UTC**, cwd was `/workspaces/he-piantor-42`, branch
`eda-004g-native-main-routing-qualification`, HEAD
`4a96d6ff6ddca3fd19330e392ae8cf91c39f6b6c`, and worktree clean. GitHub's current
main also pointed to that HEAD. The retained [Issue snapshot](../hardware/kicad/qualification/eda-004g/evidence/issue85.json)
was updated **01:13:12 UTC**. Issue #85 is the execution/acceptance/stop authority;
earlier permissions were not inherited. All required workflow/history, D-014–18,
planning, EDA-004E/F, status and Dashboard instructions were read.

[PR #84](https://github.com/ihsinoky/he-piantor-42/pull/84) merged at
**00:39:55 UTC**, with the above merge commit. EDA-004F is an **accepted historical
report**, with its original small-fixture results unchanged. Its initial warning
failure and configured subsequent success remain distinct. That acceptance does
not qualify Main or adopt the method.

Earlier Circuit JSON converters stopped on duplicate-land connectivity/library
identity and meaningful schematic/ERC failures. EDA-004E passed small-board I/O
but failed initial DRC and had no schematic route. EDA-004F subsequently qualified
only six symbols/16 pins. The changed mechanism here was fixed kicad-sch-api
public schematic calls plus KiCad-owned public PCB serialization, with no earlier
converter. The first hypothesis was that bounded model/connection correspondence
and existing public facilities could represent the complete fixed Main. That
prerequisite was not established; the later Freerouting hypothesis was not tested.

## Fixed source and partial independent expectation

The immutable source authority is commit
`b84585ecc2cf32000285bbf389d9fea255436980` in the
[qualification plan](alternate-physical-backend-qualification-plan.md#exact-representative-main-baseline).
All five listed source/transitive/isolated-lock hashes match immutable commit,
current main and worktree individually; see
[input freeze](../hardware/kicad/qualification/eda-004g/evidence/input-freeze.json).
Production tscircuit **0.0.2646**, product source authority and source bytes were
not changed. The isolated frontend was not installed/executed. Historical routed
Circuit JSON was inspected read-only during source review; none was copied,
stripped or used to generate a new input or copper.

[Partial source intent](../hardware/kicad/qualification/eda-004g/source-intent.partial.json)
is a manual transcription independent of any schematic/PCB generator. It records
each of 49 identities, source values/packages, strategy-3 positions/rotations,
pin aliases/numbers, named-net membership and NC intent. Its hash was frozen
before the captured public model assessment and has not changed. It is expressly
**not a complete accepted geometry/role expectation or proof of source parity**.

Counting conventions are explicit: **193 logical pin numbers**, plus three extra
USB shield lands and one extra GH mechanical land, produce **197 physical endpoint
intents**: **167 required + 30 NC**. There are **29 logical NC pin numbers**; the
two GH `MP` lands explain the additional physical NC. These are different from
runtime `source_port` counts, which include generated internal duplicate ports.
The 37 named nets and six separate GH GND return contacts are recorded individually.
Counts alone are not acceptance.
A post-STOP [read-only comparison](../hardware/kicad/qualification/eda-004g/evidence/retained-intent-comparison.json) corroborates each identity/value, logical alias/net/NC, duplicate-port count and component anchor/rotation against retained source records. It reads no route copper for reuse and qualifies neither physical shapes nor Main generation/checks.

The table retains 48×44 mm, two layers, 1.2 mm, width/material spacing 0.20 mm,
via 0.60/0.30 mm and the source USB shield bond's complete anchor-frame path,
top layer, 0.20 mm width and 17 mm distinct length. Full per-pad shape/drill/layer,
stock-footprint expansion, outline reconciliation and the bond's frame transform/
physical attachment remain **unqualified**. Same pin numbers are not physical
connections. No material geometry was changed or accepted by inference.

## Public-model assessment and first stop

The [captured assessment](../hardware/kicad/qualification/eda-004g/evidence/processes/public-model-assessment-corrected/public-model-assessment.json)
used public `SymbolLibraryCache.discover_libraries/get_symbol` and
`components.add`. Available definitions exposed RP2040's individual supply,
GPIO, USB, QSPI, crystal and debug roles, AP2112K and USBLC6 pins, crystal,
passives and testpoint definitions. These are retained observations, not an
accepted complete Main role mapping. Manufacturer TI SLVSEN5B p.3 also confirms
TPS22919 IN/GND/ON/NC/QOD/OUT and that QOD may be left floating; verified
repository component-source/model records were read as references. No all-passive
Main mapping, guessed role or ungrounded power declaration was created.

| Selected snapshot observation | Required additional qualification |
| --- | --- |
| No `Power_Management:TPS22919`; public addition with valid `U1` reference raises `LibraryError` | A faithful six-pin TPS22919 definition with verified roles, loaded through supported facilities. |
| No exact `W25Q16JVUXIQ`; inspected `W25Q16JVSS` has eight pins | Exact UX identity, eight signals and separate unassigned EP, with manufacturer-backed disposition. No SOIC footprint substitution. |
| No exact `TYPE-C-31-M-12`; inspected official USB symbol has A/B/S numbers | Explicit mapping of combined source contacts, NC SBU contacts and four distinct shield lands. |
| No exact `BM14B-GHS-TBT`; generic inspected connector has fourteen pins | Fourteen contact meanings and two separate mechanical MP lands without dropping or electrically joining them. |

The pinned cache/collection public methods load definitions from existing library
files and instantiate components. No public symbol-definition author/register
method was found in those inspected classes. External custom symbol libraries
can be loaded; **their absence here does not prove a small custom library, another
verified library, or a different bounded model preparation could never work**.
Those alternatives were not implemented or exhaustively searched. No measured
large-implementation requirement or budget exhaustion is claimed.

At **01:31:39.130453 UTC**, Codex stopped on **incomplete faithful Main pin-model
coverage / ERC_UNQUALIFIED**, based on the bounded reuse assessment. This is the
executor's stop/disposition of an unestablished prerequisite, not a demonstrated
universal API limitation. The public `LibraryError` is the first terminal probe
result; incomplete checker/geometry coverage is a separate constraint.
No generic model substitution, private cache injection, validation-level change,
fork, GUI, generated-file format correction or expected-table revision followed.
[STOP ledger](../hardware/kicad/qualification/eda-004g/evidence/stop-decision.json).

Two preparation mistakes are preserved in
[corrections](../hardware/kicad/qualification/eda-004g/evidence/preparation-corrections.json):
the symbol download initially used the binary package directory and returned
HTTP 404; APT's public URI identified `kicad-library-symbols`, retaining the same
pinned package hash. The first component-add probe used source alias `U_LOAD`;
reference validation rejected that before lookup. The corrected feasibility
probe used `U1`, with identical symbol ID/value, then obtained the `LibraryError`.
The first failure is **not** evidence of a missing symbol. Both script versions,
both raw probe results and commands remain retained. A future Main source-ID to
valid KiCad-reference correspondence would itself need independent verification.

## Checker scope, negative tests and engineering stages

[Checker coverage](../hardware/kicad/qualification/eda-004g/evidence/checker-coverage.json)
records predecessor hashes and their actual limits. EDA-004F reads its unrotated
wire-stub/local-label small schematic/XML; it has no PCB copper reader.
EDA-004E checks two fixed footprints/seven pads/two tracks and configured rule
values, not general physical islands or effective spacing. The existing Main
Circuit JSON copper verifier has relevant algorithms, but no separately reviewed
KiCad adaptation. None is generalized or promoted to Main acceptance here.

The four required Main fault tests—actual wrong-net copper short, missing required
pad, duplicate-number land's missing physical connection, and missing effective
0.20 mm rule—are all **NOT ENTERED / UNQUALIFIED**. Historical small-fixture fault
detections are not substitutes. No fault-detection PASS is reported for Main;
insufficient validation independently prevents any MAIN_PASS.

| Issue #85 stage | Result |
| --- | --- |
| 1. Independent expectation/model/checker | **PARTIAL; prerequisite FAIL / STOP.** Input hashes and individual source-intent inventory recorded; complete roles/geometry/checker and required negative detections not established. |
| 2. Schematic and genuinely unrouted PCB | **NOT ENTERED.** No Main generation, ERC, schematic/PCB parity, geometry/layer/outline or copper inventory acceptance. |
| 3. Effective rules and DSN/SES | **NOT ENTERED.** Public bridge signatures observed during preparation only; neither transport fidelity nor effective 0.20 mm enforcement tested. Small transport attempts 0. |
| 4. Initial Main route | **NOT ENTERED, attempts 0.** No DSN/SES, routed PCB or post-route inspection. All four metrics null. |
| 5. Conditional confirmation | **NOT ENTERED, attempts 0.** First-run pass absent; no first/confirmation differences exist. |
| Complete environment reconstruction confirmation | **UNQUALIFIED.** Initial tool re-preparation is not a second full environment reconstruction or same-environment Main confirmation. |
| Product design, Wing, manufacturing, adoption/Human Gates | **NOT ENTERED / NOT APPROVED.** |

USB NPTH remains **OPEN — PRE-ORDER DFM REVIEW REQUIRED**. No KiCad Main DRC was
run, so no existing-versus-new USB violation conclusion is available. No exclusion
or manufacturing exception was added. Connection/shape/role uncertainty and
checker insufficiency were not waived to route.

## Environment, evidence and maintenance boundary

No earlier `/tmp/eda004e/f` environment remained. The unchanged EDA-004D installer
was reused under `/tmp/eda004g` and a new capture root. KiCad CLI identifies
**9.0.9**; binding **9.0.9-9.0.9~ubuntu24.04.1**. Binary package hash is
`b7e6d33867631dc44385067b703b4c39eadede2037a260790b19495fe17e43f0`;
official 9.0.9 symbol package hash is
`73bc5b5f7ada14abcbe324c5f289c6cf807db379a9ffaaaecc877df1b619bd0a`.
Dependency-package hashes, public bridge probe, environment overrides and all
process records are retained. DISPLAY/WAYLAND_DISPLAY were unset by capture.

kicad-sch-api source commit **505bca23e91cf3fa6e3b66976e529e775eada3ba** was
reinstalled from EDA-004F's immutable archive, hash
`fa7508829945457f9824ae3490bddfb81718f3cacedaeaa6ee6515c030ef398c`.
EDA-004F's unchanged hash-locked dependencies were reused. Installed Python source
matches the archive individually; build report/dependency freeze and selected
official symbol files, raw decompressed hashes and original license are retained.
Build-isolation tooling and mutable APT availability remain reproduction limits;
there is no full environment-reconstruction certification.

Host Python is 3.14.2 on Linux x86_64/glibc 2.39; Node/npm and host Microsoft
Java 25.0.4.1+1-LTS observations are in process records. Freerouting **v2.1.0**
was discovery only: its [release README](https://github.com/freerouting/freerouting/blob/v2.1.0/README.md)
selects Java 21 and its [build definition](https://github.com/freerouting/freerouting/blob/v2.1.0/build.gradle)
targets Java 21. A compatible Java distribution/build/hash, router artifact/hash,
help/settings, timeout/passes/threads/seed and input/config hashes were **not frozen
or executed before STOP**. Host Java is not declared qualified for routing.
This incomplete environment/run-contract preparation is disclosed, not a hidden
use of defaults. No route could be authorized without the prerequisites.

[Evidence/code root](../hardware/kicad/qualification/eda-004g/README.md) contains
the partial expectation, source/model freeze, versions/dependencies/library hashes,
preparation and feasibility code, commands/exit codes/raw stdout/stderr, individual
model observations, limits, attempt/effort/STOP records and submission verification.
No Main-generation code or generated Main schematic/unrouted PCB/DSN/SES/routed
PCB is present: those stages did not start. Lossless gzip/archive organization
does not change raw evidence. Saved-state verification does not launch experiments.

Maintenance remains unresolved: exact custom Main symbol definitions and their
electrical provenance, composite logical-to-physical mapping, full independent
pad/drill/copper extraction and negative checks, pinned rule/library registration,
DSN/SES fidelity, and deprecated SWIG bindings. The assessment did not measure
their implementation cost. PMO/PO must review this limited stop and the possible
boundedness of missing work; this report does not select or authorize a retry.

## Effort and submission

The six-hour issue frame ends **07:17:56 UTC**, with experiments cut off by
**06:47:56 UTC** to preserve the last 30 minutes. The recorded actual interval
from session start to experiment STOP is **13 min 43.130 s**; this is wall-clock,
not measured active engineer time. Preparation and process durations are retained
separately in the [effort ledger](../hardware/kicad/qualification/eda-004g/evidence/effort-ledger.json).
Unattended time and historical human/review/reporting time remain unknown.

Carry forward **3.286 h** known cumulative AI estimate. This evaluation uses a
conservative **0.750 h AI allowance**, including reporting/submission/CI reserve,
not measured engineer-hours: known cumulative estimate **4.036 h**. The original
16 h convention's nominal arithmetic remainder is **11.964 h**, not certification
of an exact remaining budget. Process times overlap session effort and are not
added twice. No budget reset, exhaustion or six-hour overrun is claimed.

Status/history/Dashboard synchronize the EDA-004G proposed STOP and PR #84's
accepted historical record. Prior reports/evidence, decisions, product sources,
production dependencies and CI experiment conditions remain unchanged. Submission
checks cover saved raw hashes, frozen partial inventory and probe, scope/old-file
preservation, JavaScript syntax and latest-record substitution, and whitespace.
**Required Main error detection remains unqualified**, regardless of those
submission checks. Actual latest PR-head CI observation is recorded in the PR
body after publication; successful management jobs or skipped experimental jobs
are not technical acceptance. Commit/push and Draft PR submit this report;
merge/auto-merge, adoption, Human Gate and product design are not performed.

Saved-state submission verification passed: **287 process records** (including
267 losslessly aggregated package-extraction records), all raw/artifact hashes,
input and frozen partial/probe hashes, distinct first/corrected failures, and
individual retained source-intent corroboration. Dashboard JavaScript syntax and
Node VM DOM latest-record substitution passed; no browser visual test is claimed.
Scope/previous-file preservation and `git diff --check` passed. These checks do
not supply the four missing Main fault detections or technical acceptance.

## PMO read-only supplement (2026-10-14; merge HOLD)

PMOレビュー後の追加調査は**読み取りと報告補足のみ**です。停止の解釈を
**「選択したライブラリで前提未成立」**に限定します。固定snapshotでの名前検索・
公開追加の失敗だけでは、Issue #85の「大きな独自実装が必要」を実証しません。
その停止条件を満たしたとの判定はありません。初回調査は過去KiCad回路図の
埋め込み定義を再利用候補として確認しておらず、探索範囲に不足がありました。
以下はその補足であり、初回STOP・失敗・hash・未実施記録は書き換えません。

**CONVERSION_BLOCKEDの対象・意味:** EDA-004G工程1における、選択した公式9.0.9
symbol snapshot＋固定kicad-sch-apiの**準備済み再利用構成**で、Main全モデルの
対応と前提検査が成立していないという作業状態です。Circuit JSON converterは
実行しておらず、変換欠落・保存失敗・方式全体の不成立・Main配線失敗を観測した
分類ではありません。別の検証済み定義を登録した経路の可否は未試験です。
未確認モデルで配線へ進めなかった判断と、大規模実装必須の立証は区別します。

### 4部品の情報・再利用範囲と不足

すべて**候補調査**で、採用・生成・ERC/DRC実験は行っていません。
部品名の完全一致は必要な検索条件の一つであって、端子機能の同等性の判定そのもの
ではありません。既存シンボルの端子を検証して使うことと、そのデフォルトfootprint
を使うことは別です。製品MPN・固定sourceの銅箔/穴/配置は置換しません。

| 対象 | 既に使える情報・repoでの再利用候補 | Manufacturer提供情報・検証可能な既存library | 回路図の不足範囲 | PCB物理形状の不足範囲 | 限定対応/個別定義か、汎用writer/forkか・根拠 |
| --- | --- | --- | --- | --- | --- |
| `U_LOAD` TPS22919DCKR | [旧KiCad回路図](../hardware/sensor-test/kicad/integrated-sensor-test.kicad_sch)の`HEP:TPS22919DCKR`に既存6端子定義。1 IN power_in、2 GND power_in、3 ON input、4 NC passive、5 QOD output、6 OUT power_out。[JITXモデル](../hardware/jitx/he_piantor_42_jitx/components/power/texas_instruments_tps22919dckr.py)・[構造試験](../hardware/jitx/tests/test_ti_m1_components.py)にも個別1〜6対応がある。 | [TI SLVSEN5B p.3](https://www.ti.com/lit/ds/symlink/tps22919.pdf)に1〜6機能とNC/QOD浮遊条件。番号/機能は旧定義と対応。[TI製品ページ](https://www.ti.com/product/TPS22919)からDCK/6-pin [Ultra Librarian](https://vendor.ultralibrarian.com/TI/embedded/?gpn=TPS22919&package=DCK&pin=6)へリンク。表示は`PTPS22919DCKR`、KiCad v6+選択肢あり。export実ファイル・variant・型属性は未取得/未検証。 | 6端子情報自体は欠落していない。旧embedded定義の独立library登録用パッケージ化、出典/版/権利・完全role検証、source識別との対応、4 NC/5 QODの明示NC保持、実際の公開経路でのERCが未確認。近似`TPS22917DBV`は4 CT outputでありTPS22919の4 NCとは異なるため無変更代替不可。 | 固定Mainは`sot363`。形状の根拠は固定lockの`@tscircuit/footprinter 0.0.430`とsource。TI DCK図/JITX generator/旧symbol default `SOT-363_SC-70-6`は寸法参照候補で、固定sourceとの各pad/穴/層の一致は未検証。既存footprintを代入してよいとの判定なし。 | **6-pin個別定義の再利用・登録で済む候補が存在**。外部symbol fileを読む公開APIがあり、汎用Main writer/fork必須の根拠なし。libraryパッケージ化・検査が限定範囲で完了するかは実装しておらず不明。 |
| `U_FLASH` W25Q16JVUXIQ | 旧回路図の`HEP:W25Q16JVUXIQ`は8信号＋EP9を既に定義。[JITXモデル](../hardware/jitx/he_piantor_42_jitx/components/memory/winbond_w25q16jvuxiq.py)・[試験](../hardware/jitx/tests/test_remaining_components.py)に8信号/独立EPの対応。**旧symbolはpin4 GNDとpin9 EPが同じ座標(0,-10.16)**で、独立NCを保つ無変更再利用候補ではない。 | 固定公式`Memory_Flash:W25Q16JVSS`（親`W25Q32JVSS`）の1 CS、2 IO1、3 IO2、4 GND、5 IO0、6 CLK、7 IO3、8 VCCと型は8信号の検証候補。UX pin mapの根拠は[repoメーカーsource記録](../hardware/jitx/component-sources.md)のWinbond Rev J p.5/67。[公式PDF](https://www.winbond.com/resource-files/W25Q16JV%20SPI%20RevJ%2005202026%20Plus.pdf)とindexは今回web readerでInternal Error。再取得・メーカーECAD exportの確認なし。 | **8信号は個別番号/機能対応で既存symbol再利用を検討できる**。exact UX MPN/value、IO3 mode等を検証。sourceの9 EPは独立物理portの番号で、メーカーの第9信号pinを意味しない。EPの電気的根拠・NC表示・PCB parityでの扱いは未確認。旧EP passiveやGNDとの重なりを根拠に短絡/NCを正当化しない。 | 固定`flashFootprint`は8 land `.8128×.254`、EP `.254×1.651`。JITXは信号land約`.7118034×.22`、EP `.20×1.60`で**違う**。公式SS symbolのSOIC defaultも採用不可。UXパッケージ図だけでは固定land一致の証明にならず、固定sourceを保持する個別形状照合が必要。 | 8信号の有限対応とEPの**個別定義/物理NC対応**が不足単位。汎用writer/forkが必要との証拠なし。EP/接続検査がこの個別対応だけで成立するかは不明。メーカー再確認を伴うので、現段階で無変更再利用PASSではない。 |
| `J_USB` TYPE-C-31-M-12 | 旧回路図に**13論理端子**の`HEP:HRO_TYPE-C-31-M-12`がある。複合power/GND名、CC1/2、D+/D−、SBU1/2、S1 shieldを含む。[JITXモデル](../hardware/jitx/he_piantor_42_jitx/components/connectors/hro_type_c_31_m_12.py)は12接点land＋4 shield＋2 NPTHを個別記録。固定native `usbFootprint`と`USB_SHELL_BOND`も既存。 | [HRO製品ページ](https://en.krhro.com/Product-Details/726.html)の検索indexはexact M-12/PDFリンクあり、直接readerはInternal Error。2020-12-08 M-12 sheet4のメーカー出典はrepo source manifestに記録済み。固定公式`USB_C_Receptacle_USB2.0_16P`は17論理番号で機能照合候補。`_14P`はSBUを持たず、sourceのA8/B8 NC物理端子を欠落させてよい候補ではない。独立メーカーECAD定義の取得は未確認。 | 旧13端子定義ならsource 1〜13から複合名/S1への有限対応候補。公式17端子ならA1+B12など4 pairのcollapse対応が必要で、表だけでKiCad parityまで済むか不明。電気型の検証、SBUの明示NC、SHIELDと4物理landの対応が必要。名称一致/同じpin番号を実銅箔接続の代用にしない。 | 固定銅箔・slot・2 NPTH・回転・位置・17 mm bondを保持。メーカー/JITX参照はNPTH `.60`に対し固定source `.65`などの既知差がある。manufacturer推奨footprintや旧symbol defaultへの**置換は不可**。独立anchor変換・各land接続/穴/層の照合は未実施。 | **既存13-pin個別定義＋対応表**という具体的候補がある。外部library登録とピン番号対応は限定データだが、4 landの実銅箔検査は別作業。汎用writer/fork必須の根拠なし。実効検査を含めた総範囲が限定実装で済むかは不明。 |
| `J_WING` BM14B-GHS-TBT(LF)(SN) | [JstGh14.tsx](../hardware/tscircuit/src/qualification/JstGh14.tsx)にPO確認済み図面hash、14接点/2 MPのshape/位置と番号向きがある。D-017/interfaceに各P1〜P14と6本のGND returnを記録。source MP15は2個の機械landで、追加の第15 electrical contactではない。 | 固定公式`Connector_Generic:Conn_01x14`は1〜14、各passiveで、**受動接点**としての番号/役割検証候補。[JST GH製品ページ](https://www.jst-mfg.com/product/index.php?lang=2&series=105)はexact品の2D/3D CAD経路あり。[図面リンク](https://www.jst-mfg.com/product/index.php?doc=4&filename=BM14B-GHS-TBT.pdf&series=105&type=10)は連絡先入力/メール配送画面。申請・送信・新規図面取得はしていない。exact新規KiCad ECAD exportは不明。 | exact名symbolがないことと、14接点の型/番号が使えないことは別。generic14pin＋exact MPN/source mapping候補を検証し、MP2landの独立NC台帳とschematic/PCB照合を保持する必要がある。MPを電源/接点扱いしたり、表から消してはいけない。generic受動connectorの型を検証して使うことはMain全端子passive化ではない。 | fixedsourceが14矩形land＋2 MPの寸法/座標・silkscreenを持つ。メーカーCADは原図照合の参照であり、generic connector付属footprintへの置換ではない。各physical pad/MP/層/向き/配置の独立一致は未実施。 | **14接点の有限対応＋2 MPの個別物理NC管理**が具体的候補。symbol model移植全般や汎用writer/forkが必要との証拠なし。14-pin symbolだけでMP込みparityが成立するか、追加個別symbolが必要かは未確認。 |

旧回路図の保存形式・電気型・使用条件はhistorical referenceであり、その過去ERCや
failed PCB全体を今回の合格証拠にはしません。旧Flash EPの重なりも、本補足で見つけた
**静的な注意点**で、生成/電気検査で新たに発生させたshortではありません。
既存symbolを外部libraryに登録する候補と、個別pin定義を作る候補は区別します。
固定kicad-sch-apiの公開`add_library_path/discover_libraries`は既存symbol fileを
読み、公開`components.add(..., footprint=...)`はsymbolのdefault footprintと別の
footprint指定を受け取る構造です（ソース読み取りのみ）。この構造はsymbolと形状を
分離する候補根拠ですが、登録・再生成・parityが成功するとの証明ではありません。
embedded定義のstandalone化/差分、EP/MPの扱い、実銅箔checkerの有効性は未試験です。

### 探索範囲・未取得・工数

読み取り開始 **2026-10-14 01:58:57 UTC**、ソース/サイト調査終了
**02:04:04.278895 UTC**（wall **5分7.279秒**、最大30分）。調査対象は
過去sensor-test KiCad embedded symbols、JITXの3部品モデル/source manifest/構造試験、
固定Main TSX/GH/interface、固定公式9.0.9 symbol pin tables/継承、固定lockのfootprinter、
固定kicad-sch-apiの公開library/instance読込インターフェース、TI製品/datasheet/CADリンク、
Winbond公式index/PDF、HRO製品ページ、JST exact品CADリンクです。

未取得はTI CAD export実ファイル（表示品名PTPS variantを含め未検証）、Winbond公式PDFの
再取得、HRO現在PDF/独立ECAD、JSTメール配送CAD、その他のthird-party libraryの網羅的検索。
到達した画面とtransport失敗を記録して終了しました。登録・連絡先入力・メール送信や
申請は行っていません。別candidateを採用したり、探索用Mainを作ったりしていません。
[読み取り記録・source hash・旧pin表/位置](../hardware/kicad/qualification/eda-004g/evidence/pmo-read-only-supplement.json)。

**実装工数の測定値・見積時間は提示しません。** 数えられる不足単位は上表の個別pin/
land対応・登録・検証ですが、symbolパッケージ化やMain checkerを実装/測定しておらず、
そこから時間や「大規模」を推定できません。上のwall時間は読み取り調査の実測であって
実装時間・active engineer時間・無人時間ではありません。既知累積AI推定 **4.036 h**は
前回提出時の数値として保持し、今回の追加調査/補足のactive AI/human工数は未計測・
未推定として別記します。予算をリセットしたり、調査wallをengineering時間に加算して
残予算を認定したりしません。

PMOの**merge HOLD**は解消したとの判定をしていません。現在のSTOPを維持し、Main初回/
確認0/0、小規模transport0、全Main指標null、4負例未実施も不変です。汎用writer/forkの
必要性を実証した証拠はなく、方式全体は未評価です。この補足は実験再開、merge、
方式採用、Human Gate、製品設計やIssue closeの承認ではありません。
