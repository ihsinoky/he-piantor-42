# Finding Records

Empirical findings for he-piantor-42, per [D-031](decisions.md#d-031---knowledge-recording-adr-finding-records-and-promotion).
A Finding records what was tried, under what conditions, and where the
result is valid. Judgments and adoptions live in decisions.md, not here.
Raw logs live in the linked Issues/PRs and are not duplicated here.

## Entry template

### F-NNN — <title>

- **Conclusion:** <one or two sentences> (confidence: <low/medium/high>;
  trials: <n>)
- **Conditions tried:** <tool and exact version, target commit, parameter
  ranges, dates>
- **Failed attempts:** <one line each; "none" if none>
- **Validity scope:** <untested ranges; assumptions; invalidation
  conditions; re-verification triggers>
- **Evidence:** <links to Issues/PRs/logs>
- **Promoted to:** <process definition or skill, once promoted; empty
  until then>

## Entries

### F-001 — No Basic-classified 27Ω 0603 resistor exists in the JLCPCB SMT library

- **Conclusion:** As of 2026-11-06, every 27Ω 0603 chip resistor in the
  JLCPCB SMT parts library is Extended; there is no Basic part to
  substitute for R3/R4 (0603WAF270JT5E, C25190) to save the $3.09
  extended-parts fee. (confidence: high for the library state on that
  date; trials: 2 library-wide searches plus individual part checks)
- **Conditions tried:** JLCPCB parts library searches on 2026-11-06 —
  "27R0 0603" (172 results; filtering to Basic returned 0) and "27ohm
  0603 resistor" (3,288 results; Basic filter returned 0). Individual
  checks: C25190 (Extended), C25224 0603WAJ0270T5E (Extended), C22966
  0603WAF2700T5E (Basic).
- **Failed attempts:** 0603WAF2700T5E was initially assumed to be a 27Ω
  Basic candidate; in the Uni-Royal code "2700" is 270Ω, not 27Ω — the
  assumption was caught by checking the part page before any BOM change.
- **Validity scope:** Library contents change over time. Re-verify when a
  future BOM cost-down targets a 27Ω 0603, or when JLCPCB revises its
  Basic parts list. Applies to 0603 thick-film parts of 100mW or more;
  other packages and values were not searched.
- **Evidence:** PR #189 (amendment note in docs/issue-185-main-rev3.md).
- **Promoted to:** —

### F-002 — KRT v0.23.8 の exit 0 は固定条件での独立合格を示さない（K03）

- **Conclusion:** 固定2層・幅／間隙0.20mmのMainでは、KRTの基本CLIと
  `--escalation off` のどちらもexit 0で終了したが独立検査は不合格だった。
  offでも出力projectへの下限設定追加は起きた。
  (confidence: high for these saved outputs; trials: Main 2回＝#113/#115各1回、
  対応smoke各1回。内部rescueや設定読み戻しは配線回数に含めない)
- **Conditions tried:** 2026-11-04 UTC。KRT **v0.23.8**、commit
  `c64c0db25e6cf23afa6769ee05665c7ea22b3ff2`、Python 3.12.3、独立KiCad 9.0.9。
  Main入力PCB SHA256 `46676e57e9618940a33c5e298244e97aaec61498a87aa7c58a264e444fc71e20`、
  元project SHA256 `a5bc2aea160cc9a8b3035f77f0167c26a1de7ffdb749740c94fb7a9e9a3c87d5`。
  配置固定、F.Cu/B.Cu、幅／間隙0.20mm、via外径／穴0.60/0.30mm。
  #113は基本CLI（既定fab）、#115は追加引数をoffだけに限定し、
  保存PCBと**元project**で検査した。Main起動は各05:21:34.906482／06:06:18.182996 UTC。
- **Failed attempts:** #113は未配線5件、636 tracks中271本が0.127mm（365本は0.20mm）、
  出力projectの下限緩和もあり、独立4指標は全null。native表裏・全ネット定義の
  明示照合は事後補足のため、完全な事前ゲート手順適合も未認定。
  #115は事前ゲート完遂、全554 tracksが0.20mmでも未配線28件（24ネット）、4指標全null。
  両stageのprojectに `board.design_settings.rules.min_via_drill=0.3` と
  `kicad_routing_tools` が追加された。既存下限の緩和0件を「書き戻しなし」とは扱えない。
- **Validity scope:** この版・入力・固定条件の観測に限る。未配線時のnullを0へ置換しない。
  後続#121では**別条件**（同版、4層、幅／間隙0.10mm、via0.60/0.30mm、off、
  In1.Cu GND専用）でMain1回・smoke1回、独立4指標0を確認している。
  したがってKRT一般の配線不能やoff一般の不合格とはいえない。
  #121でもproject追加は残り、入力側projectで採点している。別版・別入力・層数・
  ルール・CLI変更時には、実効設定、保存銅箔、project全差分、独立検査を再確認する。
- **Evidence:** [#113報告](issue-113-kicad-routing-tools-falsification.md)、
  [#113実行記録](../hardware/kicad/qualification/issue-113-kicad-routing-tools-falsification/evidence/processes/main-route/record.json)、
  [#113幅全件](../hardware/kicad/qualification/issue-113-kicad-routing-tools-falsification/evidence/main-width-inspection.json)、
  [#115報告](issue-115-kicad-routing-tools-escalation-off.md)、
  [#115実行記録](../hardware/kicad/qualification/issue-115-kicad-routing-tools-escalation-off/evidence/processes/main-route/record.json)、
  [#115独立結果](../hardware/kicad/qualification/issue-115-kicad-routing-tools-escalation-off/evidence/main-independent.json)、
  [#115全差分](../hardware/kicad/qualification/issue-115-kicad-routing-tools-escalation-off/evidence/main-board-diff.json)、
  [別条件の後続合格#121](issue-121-full-auto-conditions.md)。
- **Promoted to:** [development-workflow.md — Verification evidence / Independent acceptance](development-workflow.md#independent-acceptance)、[PR template — Verification / CI](../.github/pull_request_template.md#verification--ci)。本PR（Issue #217 / `issue-217-p6`、PR番号未発行）、P6提案版。

### F-003 — 変換器入力の比較境界をUSB入力保証へ転記すると成立しない場合がある（K08）

- **Conclusion:** #165の変換器入力4.75Vは方式比較の境界であり、USB上流損失と
  Main他負荷を含む保証ではなかった。#167初回はその保証を要求され、既存USB給電では
  成立根拠がなく、基板変更・配線前に停止した。
  (confidence: high for the recorded boundary mismatch and calculation;
  trials: #165比較14,976計算ケース、#167初回上流4,320計算ケース・停止1件、配線0回。
  実機試行数ではない)
- **Conditions tried:** 2026-11-06 UTC、#165起点
  `67111c79ac2a583057cd0c81b1292cd070bf9340`。
  #165の `compare.py` / `model.json` と#167初回の計算源は本台帳登録時の基準commit
  `f43bbab6d4be50813fe801f7920e09426e3e7d23` の保存版。
  #167初回起点も同じmain、対象#155 PCB SHA256
  `fdc1a7748f94714e395eb50f3e08c43afa24192ee76eb3d1804a8cba28690222`、KiCad 9.0.9で同定。
  #165は従来U5 VIN–Main GND（新方式では変換器入力）4.75V、5/5.25V感度、
  16/17mm、20/125°C、幅100/80%、接点30/50mΩ、帰線6/1本を比較。
  設計負荷は2 Wing同時 **127mA/枚**。11mA/センサーの生包絡231.0081mA/枚と
  余裕込み278mA/枚はストレスとして区別する。
  #167初回上流掃引は3負荷×2出力×5効率×3源電圧×4上流R×3Main R×4他負荷。
  計算実行Pythonの正確な版は上記保存記録では未確認（計算源・入力・ケース数は固定）。
- **Failed attempts:** #167初回では、上流源4.75V・負荷>0・上流往復抵抗>0なら
  `Vin < 4.75V`。例として127mA×2、5.2V、効率80%、上流0.10Ω＋Main0.05Ω、
  他負荷100mAで、変換器入力4.682107V、USB合計452.619mA。
  電流が500mA未満でも入力保証は不成立だった。5V固定源を暗黙に加えず停止し、
  独立4指標は未評価null、CAM・見積も未生成とした。
- **Validity scope:** 上流源／基板コネクタ／変換器入力を分けたDC予算の観測。
  TPS63070が4.75V未満で動かないという意味ではない。
  再開時の入力定義は**基板USBコネクタ・ローカルGND基準4.50–5.25V**、
  構成許可後500mAで、基板内損失をさらに差し引く。
  採用判断は[D-027](decisions.md#d-027---main-usb-input-requirement-at-the-board-connector)に残す。
  再開#167は全体1回＋局所1回の配線上限で別理由の資格不合格となっており、
  入力再定義を電源全体の保証取得とは扱わない。効率下限、Main最大負荷、
  USB許可制御、動特性・熱・ADCは未実証。電源・ケーブル・入力位置・電流許可・負荷・
  抵抗モデルが変わるたびに予算を再評価する。125°C感度を製品温度認定にしない。
- **Evidence:** [#165比較報告](issue-165-dual-wing-power-study.md)、
  [比較モデル](../hardware/kicad/qualification/issue-165-dual-wing-power-study/model.json)、
  [比較起点](../hardware/kicad/qualification/issue-165-dual-wing-power-study/start.json)、
  [#167初回報告の保存全文](../hardware/kicad/qualification/issue-167-main-dual-wing-stage2/resume/previous-run-report.md)、
  [初回上流全4,320ケース](../hardware/kicad/qualification/issue-167-main-dual-wing-stage2/upstream-sensitivity.csv)、
  [初回検証結果](../hardware/kicad/qualification/issue-167-main-dual-wing-stage2/verification.json)、
  [#167再開報告](issue-167-main-dual-wing-stage2.md)。
- **Promoted to:** [Engineering work — Measurement boundaries and guarantees](../.github/ISSUE_TEMPLATE/engineering-work.md#measurement-boundaries-and-guarantees)。本PR（Issue #217 / `issue-217-p6`、PR番号未発行）、P6提案版。

### F-004 — 同ネットvia–padもannulus外周から全件の製造監査を要する（K09）

- **Conclusion:** #183の固定3基板では、重なるvia–padペアはすべて同ネットだったが、
  annulus外周からパッド銅まで0.10mm以上という設計監査基準に未達があった。
  重なりがないviaにも未達があり、電気接続の合格だけではこの監査を代替できない。
  (confidence: high for nominal geometry; trials: #183保存済み全件監査3基板、
  後続の比較対象としてMatrix Rev.3／Main Rev.3の最終監査各1基板。
  5基板状態の観測であり、全配線探索回数・監査再起動回数ではない)
- **Conditions tried:** 2026-11-06の#182/#185検証記録と#183監査記録
  （同日取り込みcommit `f731cdd473e461423d5b055373c13e64ecf8bff1`）。
  KiCad 9.0.9 native effective copper shape、#183環境はPython 3.12.3／Shapely 2.2.0／NumPy 2.5.4。
  Main Rev.2はcommit `dcf5c61d9b8480da9698f71c5209d516d6231898`、
  Wing Rev.1は `8a7d76651a064ec71160e84c07682aff8bd8beb4` の16/17mm。
  対象は順に **113 via×252銅パッド、196×190、198×190**（全507 via）。
  NPTHは各6/4/4を銅パッド集計から除外。via外径／穴は全0.60/0.30mm、
  Main4層／Wing2層、共通銅層で `g=中心–パッド銅距離−via半径` を測定。
  全パッドには同ネット・NC・補強ランド・裸テストパッドも含める。
  Matrix Rev.3は#182起点 `b23716a3d1e9bd1f4c1d06c62d93458797398461`、
  最終PCB SHA256 `7ad3c6e67aed41f882b87f38f7ea8f812805e56837bf15a1d21dc2479060b8db`、
  **158×178＝28,124組**、NPTH4除外。Main Rev.3は同Rev.2起点、
  最終PCB SHA256 `0e81ba42b194e03fb0422b58a64c967fe83166d0495d84f28c4171184b665bae`、**113×252**、NPTH6除外。
- **Failed attempts:** #183のMain／Wing16／Wing17は重なりvia32/28/46、
  0.10mm未達35/32/52。重なりなしでも未達が各3/4/6あり、重なりのみの解消では不足する。
  #185は最初の33個移設後に2個が残り、局所迂回後に全113 viaの未達0・最小0.100000mm。
  #182も初期全体／局所候補は不合格で、最終158 viaは未達0・最小約0.1074625mmとなった。
  詳細な配線失敗履歴は各報告に残し、本項の監査対象数へ加算しない。
- **Validity scope:** 固定基板の名目幾何と0.10mmという**本プロジェクトの設計監査基準**に限る。
  drill縁とannulusのみの重なりを区別する。#183の最小g=−0.30mmは中心がパッド内の場合の
  飽和値で侵入深さではない。ちょうど0.10mmやdrill縁から1nm外という分類は製造余裕を証明しない。
  #182/#185のPOFV不要化は対象改版の設計成果であり、業者DFM受入れ・料金削減の保証ではない。
  mask/paste、tenting、穴・位置・銅厚・めっき公差、仕上げ、実装工程・数量は別途確認する。
  PCB・パッド・via移設・銅層・製造条件の変更時は全件再監査と独立接続／DRC／CAM再確認が必要。
  #183の単独移設候補は同時成立・GND再fill・全体資格を未確認で、配置変更必須の証明でもない。
- **Evidence:** [#183報告](issue-183-via-pad-audit.md)、
  [固定commit・PCB hash](../hardware/kicad/qualification/issue-183-via-pad-audit/sources.json)、
  [監査環境](../hardware/kicad/qualification/issue-183-via-pad-audit/runtime.json)、
  [Main全件集計](../hardware/kicad/qualification/issue-183-via-pad-audit/main-rev2/summary.json)、
  [Wing16全件集計](../hardware/kicad/qualification/issue-183-via-pad-audit/wing-rev1-16mm/summary.json)、
  [Wing17全件集計](../hardware/kicad/qualification/issue-183-via-pad-audit/wing-rev1-17mm/summary.json)、
  [#182報告](issue-182-matrix-rev3.md)、
  [Matrix最終検証](../hardware/kicad/qualification/issue-182-matrix-rev3/verification.json)、
  [#185報告](issue-185-main-rev3.md)、
  [Main最終全件集計](../hardware/kicad/qualification/issue-185-main-rev3/local35/audit/via-pad/summary.json)。
- **Promoted to:** [development-workflow.md — Verification evidence / Full via-pad audit](development-workflow.md#full-via-pad-audit)、[PR template — Verification / CI](../.github/pull_request_template.md#verification--ci)。本PR（Issue #217 / `issue-217-p6`、PR番号未発行）、P6提案版。

### F-005 — ケース入力更新では外形だけでなく固定点集合とボスまで照合する（K12）

- **Conclusion:** Wing Rev.3 Stage 1bと最終CSVは外形が一致しても取付穴が異なった。
  確定入力への差し替えで固定点が13→15になり、最終版では15点の集合一致・
  ボス壁材・下穴開口・穴の逆変換まで検証された。
  (confidence: high for saved digital geometry, untested physical retention;
  trials: Stage 2／最終の17/16mm各1組、計4組の保存済み生成・検証結果。
  生成／検査の実行総回数は未確認、実造形試行0)
- **Conditions tried:** Stage 2のWing形状入力commit
  `bcb285eaa1105220aeba079c456bf56ca1827fb0`（`issue200-stage1b-v1`）、
  Main入力 `90c8314be34fcaa8582df9af5814dd6f36a87d59`、
  UDB upstream `2ecdd7e0482ecbd3ffe9af04966ab3555f7fc33c`。
  最終はmain `932b880c946f9cf6e66993e128ec7d456f311af4` の
  `hardware/case/issue-200-rev3/` 確定CSV全12本（outline/holes/keys×16/17mm×左右）を凍結コピー。
  使用源は `issue-198-stage2/` と `issue-198-final/` の各generate/base/details/verify、
  保存版は取り込みcommit各 `723a65ef1d5e31dc8f674f0c9ff80635e22ad6a6`／
  `8ef9efb2feac52cf7158d3e559b4dbd73cf880af`。
  両取り込み日時は2026-11-07 UTC（Git履歴）。個々の生成・検証実行日時と実行Python版は未確認。
  requirements指定はbuild123d 0.13.0／Shapely 2.2.0／sexpdata 1.0.2で、実環境の版証明とは区別する。
  120°逆ハの字、X=3.5mm左右分割、GH200mm、既定南辺フラッシュ、17mm正／16mm再生成検証。
- **Failed attempts:** 失敗した実行の回数・ログはこの比較資料では未確認。
  Stage 2は左H1／右H3がremovedの提案入力に対してWing各3＋Main3＋UDB4＝13点で整合し、
  当時の不合格ではない。最終入力では左H1／右H3が復活しWing各4＋Main3＋UDB4＝15点。
  Stage 2の13点をそのまま引き継ぐと2点不足するが、これは入力差分からの帰結であり、
  「不足した最終ケースを実際に生成して失敗した」という観測ではない。
- **Validity scope:** 最終外形321頂点×4形状はStage 1bと差0、keys4本はbyte一致でも、
  固定点の同一性は導けない。最終17/16mmでは入力／出力hash照合、固定点集合15点、
  各ボス壁材・下穴開口、Wing穴CSV逆変換誤差<1e-10mm、5印刷ピース、
  組立114 solidsの干渉検査を確認。ボスφ4.5／下穴φ1.7等は設計値で、
  **実造形の保持力・クリープ、印刷収縮、締付け、追加ゴム足の置き場は未評価**。
  部品高さ・束径・曲げRも設計予約。CSV・geometry・datum・座標変換・穴集合・
  材料／ねじ／造形条件変更時に入力hashと集合・ボスの再照合、必要な実物評価を行う。
- **Evidence:** [Stage 2報告](issue-198-case-stage2.md)、
  [Stage 2入力来歴](../hardware/case/issue-198-stage2/inputs/provenance.json)、
  [Stage 2 17mm寸法・固定点](../hardware/case/issue-198-stage2/17mm/dimensions.json)、
  [最終報告](issue-198-case-final.md)、
  [最終検証源](../hardware/case/issue-198-final/verify.py)、
  [最終17mm入力hash・固定点・ボス](../hardware/case/issue-198-final/17mm/dimensions.json)、
  [最終16mm入力hash・固定点・ボス](../hardware/case/issue-198-final/16mm/dimensions.json)、
  [最終17mm検証結果](../hardware/case/issue-198-final/17mm/verification.json)、
  [最終16mm検証結果](../hardware/case/issue-198-final/16mm/verification.json)。
- **Promoted to:** [development-workflow.md — PCB-to-case handoff](development-workflow.md#pcb-to-case-handoff)、[PR template — Verification / CI](../.github/pull_request_template.md#verification--ci)。本PR（Issue #217 / `issue-217-p6`、PR番号未発行）、P6提案版。

### F-006 — 旧Wingの電源／GND拡幅はDC降下を減らすが最低電圧の保証は残る（K05）

- **Conclusion:** #141の旧representative21 Wingでは、電源／GNDを0.30mm、
  信号を0.10mmに分けた2層配線が16/17mm各1回で独立4指標0・幅監査合格となった。
  #138の全線0.10mm基板とのDC比較で最大往復降下は約64–75%減ったが、
  最低局所電圧4.5Vを割る計算条件は残った。
  (confidence: high for saved routing outputs and model comparison;
  trials: 配線2回＝各ピッチ1回、DC32ケース＝2ピッチ×前後×2電流×2温度×2幅。
  実機試行数ではない)
- **Conditions tried:** 2026-11-05 UTC、配線開始02:45:37／02:48:12。
  KRT v0.23.8、commit `c64c0db25e6cf23afa6769ee05665c7ea22b3ff2`、KiCad 9.0.9。
  #131 Stage 0のpads修正済み入力から派生し、配置・ネット・外形を保持。
  保存版は本登録基準commit `a24896d2aa258371362840ee0f1f2f71cc0d7b9b` の
  #138/#141証跡。Python実行版は本照合資料では未確認。
  F.Cu/B.Cu、厚1.2mm、clearance0.10mm、via0.60/0.30mm、off、
  CLIで信号0.10mm・HALL_5V/GND各0.30mmを明示固定した。
  DCは21センサ各5/11mA＋3MUX各2.7µA、20/125°C、公称／−20%幅、
  銅35µm・barrel20µmの中心線抵抗網。Wingコネクタ到達後4.75/5.00Vを仮定。
- **Failed attempts:** CLI幅省略は信号0.127mmへのclampを事前読戻しで検出し、
  配線前に拒否（追加配線に数えない）。16mmの初回厳密project比較は実測power_widths
  記録追加を拒否したが、全設定一致を別監査し配線は再実行していない。
  17mm・11mA/個・125°C・−20%幅では、拡幅後も往復降下0.268687V、
  4.75V入力時の最低局所4.481313V（4.5V余裕−18.687mV）。
  11mAは保守包絡でありデータシート保証最大値ではない。
- **Validity scope:** 旧Wingの固定配置・保存配線と近似DCモデルに限定する。
  **現行Wing Rev.3の実測値ではない**。#138の保存10ケースの再計算一致と、
  未保存だった拡幅前6ケースの追加計算を区別する。Main・ハーネス損失、接触集中、
  製造最小銅厚、起動／過渡、GND/ADC精度はこの比較で保証しない。
  5V仮定の全ケース通過も供給最低保証の確定ではない。0.20mmは未試行。
  基板改版・配線幅・負荷・供給境界・温度・帰路・材料条件変更時に再抽出・再検査する。
  125°Cは抵抗率感度で、実機温度認定ではない。
- **Evidence:** [#138報告](issue-138-wing-manufacturing-review-prep.md)、
  [#141報告](issue-141-wing-power-integrity.md)、
  [16mm実行記録](../hardware/kicad/qualification/issue-141-wing-power-integrity/processes/KRT-16-2L-P0300-route/record.json)、
  [17mm実行記録](../hardware/kicad/qualification/issue-141-wing-power-integrity/processes/KRT-17-2L-P0300-route/record.json)、
  [16mm独立判定](../hardware/kicad/qualification/issue-141-wing-power-integrity/inspection/KRT-16-2L-P0300/assessment.json)、
  [17mm独立判定](../hardware/kicad/qualification/issue-141-wing-power-integrity/inspection/KRT-17-2L-P0300/assessment.json)、
  [前後比較16行（各行2ケース）](../hardware/kicad/qualification/issue-141-wing-power-integrity/dc-comparison.csv)、
  [DC計算源](../hardware/kicad/qualification/issue-141-wing-power-integrity/dc-model.py)。
- **Promoted to:** —（P6では昇格しない。理由・将来候補は[Issue #217 作業報告](issue-217-p6.md#昇格しないfindingの判断)を参照）

### F-007 — NPTHのpads禁止解除と全層の実銅予約は別に検証する（K06）

- **Conclusion:** #129では取付NPTH自体がpads禁止に該当し、#131でその禁止だけを
  解除すると入力DRCの当該各4件が解消した。#155では全層予約の多角形が座標量子化で
  理想φ5円をわずかに下回り、4nmの外接補正と再充填・再検査で解消した。
  (confidence: high for saved geometry and DRC;
  trials: #129修正後／#131変更後の入力DRC各3基板、#131等価性ゲート1回、
  #155補正前後各4予約。配線探索総数やDRC実行総回数とは区別する)
- **Conditions tried:** #129/#131は2026-11-04 UTC、#129起点
  `96166d3f266f6d423173fcd8cdc3a38a46a6767d`、#131起点
  `e0374fe8e72f0bfc7a4a3a816a71ae42d2c6e962`。KiCad 9.0.9、
  pitch9-16mm／representative21-16/17mm、2層・1.2mm、NPTHφ2.2×4、
  φ5予約を256辺外接多角形で表現、整数nm座標。
  #131は各4箇所のpads not_allowed→allowedのみ変更し、tracks/vias/copper pour/
  footprints禁止は保持。#155は2026-11-05 UTC、起点
  `d2139eed736984f2cda75bf2644d4a1190ece0a4`、48×44mm Main・4層・4穴、
  F.Cu/In1.Cu/In2.Cu/B.Cuへ予約を伝達。保存証跡の版は本登録基準
  `a24896d2aa258371362840ee0f1f2f71cc0d7b9b`。Python実行版と検査起動総数は未確認。
- **Failed attempts:** #129修正後も入力のitems_not_allowed各4件は残り、
  KRT smokeの物的違反4件にも数えられた（最初のLIB_ID不一致によるゲート停止とは別）。
  #155の初期多角形は最小半径2.499999728mm、理想円とGND fillの重なり約1.45×10⁻⁷mm²。
  閾値緩和はせず、対応する入力／出力の4 keepout頂点だけを半径方向に4nm拡張した。
  配線・viaの変更／配線再実行は0。最終最小半径2.5000033779mm、充填GND重なり0。
- **Validity scope:** pads allowedはNPTHオブジェクトの自己違反を避ける設定であり、
  既存銅パッドの侵入許可とは扱わない。#155は全銅層のpad/track/viaと実GND fillを
  別形状検査し、最終独立4指標0を確認した。rule areaの設定一致や2層での成功だけでは
  内層・実fill・理想円の予約を証明しない。#129の停止／配線不合格全体をpadsだけの原因としない。
  #131後の3基板入力DRC違反0は配線前の観測で、配線合格とは別。
  円近似・保存形式／座標単位・KiCad版・層・穴位置・銅箔変更時は、保存後の外接性と
  全層実銅・再fillを再照合する。4nmはこの入力の丸め補正で、製造公差の余裕ではない。
- **Evidence:** [#129報告](issue-129-wing-2layer-routing.md)、
  [#131報告](issue-131-wing-condition-search.md)、
  [pads限定差分](../hardware/kicad/qualification/issue-131-wing-condition-search/evidence/stage0-change-audit.json)、
  [変更後入力DRC](../hardware/kicad/qualification/issue-131-wing-condition-search/evidence/input-drc-summary.json)、
  [#155報告](issue-155-main-mounting-stage2.md)、
  [4nm補正原記録](../hardware/kicad/qualification/issue-155-main-mounting-stage2/reservation-quantization-guard.json)、
  [最終半径・保持・試行数検証](../hardware/kicad/qualification/issue-155-main-mounting-stage2/verification.json)。
- **Promoted to:** —（P6では昇格しない。理由・将来候補は[Issue #217 作業報告](issue-217-p6.md#昇格しないfindingの判断)を参照）

### F-008 — 局所配線の合否には保持対象の銅箔差分も必要となる（K07）

- **Conclusion:** #155の局所退避は接続・異ネット接触・物的DRCが0でも、保持配線68件の
  被覆を失い不合格となった。範囲を固定した全体再配線で合格した一方、#167の局所修正も
  対象外の保持銅を失った。局所という指定やexit 0だけでは保持を保証しなかった。
  (confidence: high for saved outputs; trials: #155局所1回＋全体1回、
  #167再開時全体1回＋局所1回。準備API失敗・読戻し・再検査は配線試行に含めない)
- **Conditions tried:** #155は2026-11-05 UTC、起点
  `d2139eed736984f2cda75bf2644d4a1190ece0a4`、#121合格板を元に48×44mm・4穴追加。
  局所はVBUS/WING_EN/GNDの直接干渉3 segmentsだけを除去。局所開始19:57:48、
  全体開始20:05:27。全体は0.10mm線537本＋via66個の除去を事前固定し、
  元0.20mm線3本をkeep-input-copperで保護した。
  #167再開は2026-11-06 UTC、head `0a1f355510e3f2fcadfdc68e7ae97ea90122eb6b`、
  #155最終板から48×52mm・2 Wing候補へ変更、全体1800秒＋局所900秒の各1回上限。
  両IssueはKRT v0.23.8、commit `c64c0db25e6cf23afa6769ee05665c7ea22b3ff2`、
  KiCad 9.0.9、4層1.2mm、幅／間隙0.10mm、via0.60/0.30mm、off、
  layer cost [1,-1,1,1]、In1.CuはGND専用。Python実行版は本照合資料では未確認。
  保存源は本登録基準 `a24896d2aa258371362840ee0f1f2f71cc0d7b9b`。
- **Failed attempts:** #155局所は独立4指標0/0/0/68。保持68 segmentsの同層・同幅・
  同ネット被覆が失われた。全体は0/0/0/0で、その後の4nm予約補正でも配線は不変。
  #167全体は直接観測3/0/0/1（保持via1個欠落）。V1V1/V3V3と診断対象XOUT/
  QSPI_SD0だけを局所ripping対象にした最終出力は3/0/2/24で、
  QSPI_SCLK/QSPI_SD2の保持20 segments＋4 viasが欠落した。
  nonroute AST追加／削除0でも保持銅の保証にはならなかった。
- **Validity scope:** 上記固定入力と有限試行の観測であり、局所修正一般の禁止や
  全体再配線一般の成功へ一般化しない。#155の68件は保持被覆差分数で、未接続数ではない。
  #167は44ネットの直接測定値と、未接続時に資格指標をnullとするassessmentを分ける。
  F-003の入力境界停止とは別の再開配線失敗である。次の変更では対象ネットだけでなく、
  保持segmentsの層・幅・ネット被覆、via一致、非配線AST、全ネット実銅接続、DRCを再検証する。
  ツール版・入力・局所／全体範囲変更時に再確認し、試行上限を結果に応じて無断拡張しない。
- **Evidence:** [#155報告](issue-155-main-mounting-stage2.md)、
  [局所独立判定](../hardware/kicad/qualification/issue-155-main-mounting-stage2/inspection/local/assessment.json)、
  [局所保持差分](../hardware/kicad/qualification/issue-155-main-mounting-stage2/inspection/local/transfer-diff.json)、
  [全体範囲の固定](../hardware/kicad/qualification/issue-155-main-mounting-stage2/global-scope.json)、
  [全体独立判定](../hardware/kicad/qualification/issue-155-main-mounting-stage2/inspection/global/assessment.json)、
  [#167再開報告](issue-167-main-dual-wing-stage2.md)、
  [再開試行数・直接観測値](../hardware/kicad/qualification/issue-167-main-dual-wing-stage2/resume/status.json)、
  [局所保持差分](../hardware/kicad/qualification/issue-167-main-dual-wing-stage2/resume/inspection/local/transfer-diff.json)。
- **Promoted to:** [development-workflow.md — Verification evidence / Retained-artifact comparison](development-workflow.md#retained-artifact-comparison)、[PR template — Verification / CI](../.github/pull_request_template.md#verification--ci)。本PR（Issue #217 / `issue-217-p6`、PR番号未発行）、P6提案版。

### F-009 — Rev.3の充填銅抽出に置換すると旧Wingの電圧予算は変わる（K11）

- **Conclusion:** Main Rev.4の共通／分岐抵抗を維持し、旧#141由来のWing内降下を
  Wing Rev.3の実形状から抽出した抵抗モデルへ置換すると、127mA/枚・2枚同時・
  200mmで最悪最遠点は4.797985Vから4.942903Vへ変わった。
  (confidence: high for saved model arithmetic, unverified physical performance;
  trials: Rev.3の4基板×2ネット×2メッシュ×2幅＝32保存抽出行、
  システム感度64計算行。配線探索・抽出再起動の総数と正確な実行環境版は未確認、実測試行数ではない)
- **Conditions tried:** Main Rev.4 Phase B保存版の取り込みcommit
  `90c8314be34fcaa8582df9af5814dd6f36a87d59`、Wing Rev.3 Stage 2保存版
  `932b880c946f9cf6e66993e128ec7d456f311af4`（ともに2026-11-07 UTC、Git履歴）。
  Main抵抗集約日時04:11:01 UTC。Wing個々の抽出実行日時・Python/SciPy/Triangleの
  正確な実行版は未確認。保存源は本登録基準 `a24896d2aa258371362840ee0f1f2f71cc0d7b9b`。
  Main最終PCB SHA256 `b361a5a010a3ae2b08e5858735d46a5662112af4241ef55bab50d1ba3187b123`。
  Wingは16/17mm×左右の最終PCBをhash束縛し、2層充填銅＋via barrelのsheet FEM、
  銅35µm／barrel20µm、メッシュ最大面積0.06/0.015mm²、track幅100/80%。
  粗細の端子ごとの大きい降下を採用し20/125°Cへ換算する。
  全行でMainは125°C・幅80%の共通37.113969mΩ／J2 3.470864mΩ／J3 28.227454mΩを保持。
  レール5.2V±2%から未モデル分50mV、U5 Ron0.25Ω、127mA/枚×2、
  GH導体各200mm・0.0804mm²・接点50mΩ×両端・帰路6本を仮定。
  感度64行は4基板×2幅×2温度×2長（124.097168/200mm）×2枝であり、
  全基板を両枝へ仮接続する感度も含む。実配置は左J2／右J3。
- **Failed attempts:** #196初期抽出はPGNDが遠方viaへ細線接続し共通約187mΩで
  50mΩ目標に未達。近傍GND via/stubと実許容幅への拡幅後に目標を満たした。
  細meshのKCL残差超過も反復改善で解消し閾値を緩めていない。
  #196最終の旧Wing項0.147710145Vは当時のモデル入力で、不合格測定ではない。
  Rev.3では17mm-right/U_HC1・125°C・幅80%の項が0.002791294Vとなる。
  旧項をRev.3へ流用するとこの置換結果を表せない。
- **Validity scope:** **4.9429V等はMain Rev.4＋Wing Rev.3・127mA・200mmのモデル値で、実測ではない**。
  同条件のハーネス降下0.023793465V、最遠点4.942903405V、4.60V余裕0.342903405V。
  124.097mmでは4.946310Vで、約3.4mV差だけから長さを決定しない。
  125°CはGHのカタログ上限105°Cを超える感度計算で、GH／組立の動作温度認定ではない。
  native fill形状の保持とtrack幅80%のモデルは、plane/spokeのエッチングや仕上り銅厚の
  保証下限ではない。理想pad接触・等しい帰線抵抗・#196上流UDB/SH/USB条件を前提とし、
  実負荷・完成ハーネス抵抗・効率・起動／過渡・ADC性能は未保証。
  PCB hash、面／thermal／via、材料、負荷、接点／長さ、レール・上流条件変更時は再抽出・予算再計算する。
- **Evidence:** [#196 Phase B報告](issue-196-main-rev4-phaseb.md)、
  [Main最終抵抗とhash](../hardware/kicad/qualification/issue-196-main-rev4-phaseb/resistance-summary.json)、
  [#200 Stage 2報告](issue-200-wing-rev3-stage2.md)、
  [17mm-right全抽出行・hash](../hardware/kicad/qualification/issue-200-wing-rev3/wing-rev3-17mm-right/resistance-extraction.json)、
  [全4基板hash・条件・集約結果](../hardware/kicad/qualification/issue-200-wing-rev3/power-summary.json)、
  [64感度行](../hardware/kicad/qualification/issue-200-wing-rev3/power-sensitivity.csv)、
  [集約計算源](../hardware/kicad/qualification/issue-200-wing-rev3/power-summary.py)、
  [FEM自己検証](../hardware/kicad/qualification/issue-200-wing-rev3/fem-selfcheck.json)。
- **Promoted to:** —（P6では昇格しない。理由・将来候補は[Issue #217 作業報告](issue-217-p6.md#昇格しないfindingの判断)を参照）

### F-010 — 固定Hall footprintのimportでkeepoutと角丸銅箔が失われた（K01）

- **Conclusion:** importer 0.0.117／0.0.142で固定Hall footprintの変換は成功したが、
  必須の銅ポア禁止keepout 2個は出力0個、SMD 3個の角丸半径は0.15→0.075mmとなり、
  いずれも個別警告なしで幾何資格に不合格だった。
  (confidence: high for saved conversions; trials: EDA-003Aの固定asset×2版の保存結果各1件。
  0.0.117のproject経路は報告上1回。0.0.142のclean install再現・合成対照は別枠で、
  全変換起動総数と過去#13の試行総数は未確認)
- **Conditions tried:** 2026-10-05、起点 `7d7f3cffe4fb98771e3ca47f800a54de22fa8c4f`。
  productionはtscircuit 0.0.2646／importer 0.0.117の既存lock、
  独立spikeはimporter 0.0.142（package報告gitHead
  `967a8c823d8d19cdf18060fd7b66ce5d79e91c12`）、kicadts 0.0.58、
  TypeScript 5.9.3、@flatten-js/core 1.6.14、circuit-json-util 0.0.120、
  transformation-matrix 2.16.1。全解決版はversion-matrixに保存。Node実行版は未確認。
  入力は `SW_MX_HE_0deg_1u.kicad_mod`、SHA256
  `168d915310d9fecaf19d33d130a9171f296b2a3aa3d0447e9f064535e406190a`、
  原点(0,0)・回転0、入力／出力補修なし、独立許容差0.001mm。
- **Failed attempts:** 両版とも `pcb_keepout=0`・`pcb_copper_pour=0`、
  `getWarnings()`・捕捉console warn/errorは空。パーサには2 zoneと12 arcsが残る。
  基本pad／PTH／NPTH／pin3重複番号／Y反転は合格しても、欠落と角丸差は残った。
  converter実行成功とfidelity gateの期待exit 1を区別する。
- **Validity scope:** このassetと版・依存環境でのstandalone変換だけ。
  source zoneの名称でなく宣言層を正とし、F.Cu側8 arcsのnotchとB.Cu側4 arcsを要求した。
  内層再利用・mask/paste・zone_connectの将来ポア挙動・基板移行は未資格。
  physical port 4個でもsource_port 0個で、電気graph parityの成功ではない。
  将来版や別footprintの能力を断定しない。importer／parser／schema／依存版・asset・
  transform・層構成が変われば、keepout形状・権限・実効ポア禁止と実銅箔を再検証する。
- **Evidence:** [原報告・歴史#13との区別](tscircuit-kicad-importer-requalification.md)、
  [版・入力hash](../hardware/tscircuit/spikes/eda-003a/evidence/version-matrix.json)、
  [0.0.117保存結果](../hardware/tscircuit/spikes/eda-003a/evidence/project-result.json)、
  [0.0.142保存結果](../hardware/tscircuit/spikes/eda-003a/evidence/upstream-result.json)、
  [原zone・幾何比較](../hardware/tscircuit/spikes/eda-003a/evidence/geometry-comparison.json)、
  [警告](../hardware/tscircuit/spikes/eda-003a/evidence/warnings.json)。
- **Promoted to:** —（P6では昇格しない。理由・将来候補は[Issue #217 作業報告](issue-217-p6.md#昇格しないfindingの判断)を参照）

### F-011 — 固定JITX fixtureでは電気graph一致後も物理未接続が残った（K02）

- **Conclusion:** C4B5の2候補は電気graph parityを保持し、非対話buildと
  legacy-kicad exportに成功したが、独立KiCadでは40／39未接続が残った。
  対象環境でsourceによる完全物理配線は実証されていない。
  (confidence: high for retained outputs; trials: C4B5のfresh候補2件＝異なるsource各1回。
  先行探索build 1件は別枠。C0〜C4B全体の配線起動総数は未確認)
- **Conditions tried:** 2026-10-05（DRC各06:19:07／06:20:21 UTC）、
  起点 `69dd846ac76d40f333b1b099a13d2a4720cfe758`、source hashはpipelineに固定。
  Python 3.14.2、JITX 4.4.3、jitxlib-standard 4.4.0、Linux runtime 4.4.2、KiCad 9.0.9。
  C4B由来の68部品・配置固定、80×60mm、名目1.2mm・2層、
  source trace幅／copper clearance各0.20mm。公開Routeの単層topological engineと
  公開pad／Net／Via／PortAttachmentを使用、capture境界は実験的RuntimeDesign。
  候補1は近接pad spanning tree＋既存H0経路、候補2はMUX_A0を明示2via escapeに置換。
  downstream入力はread-only、生成CAD編集・外部ルータ・ルール緩和なし。
- **Failed attempts:** 先行探索は111/153 requests実現・未接続42。
  fresh候補1は113/153・via2・未接続40とcopper sliver 1件。
  fresh候補2は116/155・via4・未接続39とdangling via 1件で、MCU側escapeが未達だった。
  既知USB hole clearance 4件・library登録警告68件も両方に残り、DRC exit 5。
  完全配線未達なのでC4B5のGerber/Excellonと同一候補2回成功比較は未実施。
- **Validity scope:** 電気照合は68部品・200 endpoints・43 named nets・185 edges・
  direct links 4・intentional NC 7のPASSであり、幾何／物理接続のPASSへ転用しない。
  この固定版で公開headless全体多層plannerは確認されなかったという調査結果に限り、
  全配置／順序／熟練者の手動完配や将来版の不可能性は証明しない。
  異なる2候補から決定性も認定しない。過去C4B4Bのdownstream製造経路成功と、
  誤った1.6mm overall metadata・別途1.2mm指定、USBの発注前DFM残件は別の範囲。
  採用NO-GO判断は[D-016](decisions.md#d-016---jitx-physical-backend-no-go-native-tscircuit-resumes-as-active-revm1-eda-candidate)に残す。
  package／runtime変更時はC0 graph自己検査から再確認し、routing API・配置・制約・
  export経路変更時は電気parityと独立物理検査を再実施する。
- **Evidence:** [評価履歴](jitx-evaluation.md)、
  [C4B5報告](../hardware/jitx/physical/EDA-002C4B5.md)、
  [公開surface・環境](../hardware/jitx/physical/c4b5-evidence/routing-surface.json)、
  [argv・source hash・実行](../hardware/jitx/physical/c4b5-evidence/pipeline.json)、
  [候補1 DRC/capture](../hardware/jitx/physical/c4b5-evidence/experiment-1.json)、
  [候補2 DRC/capture](../hardware/jitx/physical/c4b5-evidence/experiment-2.json)、
  [電気照合](../hardware/jitx/physical/c4b5-evidence/reconciliation.json)。
- **Promoted to:** —（P6では昇格しない。理由・将来候補は[Issue #217 作業報告](issue-217-p6.md#昇格しないfindingの判断)を参照）

### F-012 — 固定Mainでは層追加だけで完配せず、別の幅／間隔条件で完成した（K04）

- **Conclusion:** 固定Mainの0.20mm幅／間隔では、2層fab_routerと4層の
  fab_router／KRTの各保存結果に未接続が残った。一方、4層KRTの0.10mm幅／間隔では
  独立4指標0を確認した。層数追加だけでpad直近のescape成立まで保証できない。
  (confidence: high for cell outcomes, limited for congestion mechanism;
  trials: 下表Main計4回＝各セル1回。対応smokeは#103 1回、
  #117修正指示01は各ツール2回、#121 1回。過去停止・設定読戻し・内部rescueは別枠)
- **Conditions tried:** Mainは48×44mmの固定配置、49 footprints・37非空ネット。
  #103のDSN parseは197 pads、#117 native棚卸しは199物理ランドで、計数を同一視しない。
  共通via外径／穴0.60/0.30mm、板厚1.2mm。
  fab_routerはcommit `69cf598db98c136bff16bbe02bccdded95674b18`、Bun 1.4.4、
  公開routeDsn API既定（detailedRouter/globalPlan off、fanout false）、budget1800000ms。
  KRTはv0.23.8、commit `c64c0db25e6cf23afa6769ee05665c7ea22b3ff2`、
  off・寸法CLI明示・In1 layer cost −1。独立検査KiCad 9.0.9。
  KRT／検査Python実行版は本照合資料では未確認。
  #103の基準mainは `9f97ebe6626ebf0c38e030bb8c9a2b9c27fb462d`、
  Main DSN SHA256 `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2`。
  #117は前run `7917d82` の4層入力をbyte一致で再利用（native SHA256
  `33f079d07bfb2dad9a76dce0667a1fd1371c94406df16f36ae17fe559d74af01`）。
  #121は `ce2e27fe6495dbd08db86bdd9b22a3c93b002347` の#119入力を取得し、
  ルールのみ変更、逆変更byte一致で配置・部品・ネット・既存0.20mm銅箔3本を保持した。

  | 対象・実行日UTC | 固定層構成・幅／間隔 | ツール・保存観測 |
  | --- | --- | --- |
  | #103 Main、2026-11-03 22:57:23開始 | F/B 2層、0.20/0.20mm | fab_router：保存SES自己再適用未接続16、276 paths全0.20mm。Main独立import未実施、4指標null |
  | #117 Main修正01、2026-11-04 09:29:19開始 | F/In2/B信号＋In1 GND、0.20/0.20mm | fab_router：独立再fill後26未接続、4指標null |
  | #117 Main修正01、2026-11-04 09:29:20開始 | 同上（配置・ルール固定） | KRT off：独立再fill後28未接続、4指標null |
  | #121 Mainセル1、2026-11-04 10:56:42開始 | 同じ4層役割、0.10/0.10mm | KRT off：独立未接続0・4指標0、信号537本0.10mm＋保持3本0.20mm、via66個 |

- **Failed attempts:** #117の独立非印刷指摘はfab 17件（hole_to_hole 1・
  track_dangling 16）、KRT 9件（via_dangling）。未配線時のnullを0にしない。
  修正01の初回smokeはKRT thermal 1件で不合格、Nプレーンsolid化後に両方合格。
  このsmoke固有変更をMain GNDへ移さず、Main各1回を守った。
  #117以前のsmokeネットN／GND要件不整合による配線前停止は、Main配線失敗に数えない。
- **Validity scope:** 測定主体が異なる#103の16と#117の26を差分効果として比較しない。
  #121では幅とclearance、zone thermal寸法等も変わり、層数・線幅単独の因果や
  0.10〜0.127mmの成立境界は未確認。セル2〜4は準備だけで未実行、失敗扱いしない。
  #117のWing見通し（仮定mux pitch0.65／pad幅0.30なら隙間0.35に対し
  0.20線＋両側0.20は0.60mm必要）は感度例で、実Wing footprintの測定ではない。
  平均密度・層追加から局所escapeを保証できないが、混雑が全未接続の唯一原因と断定しない。
  全ツール同条件の不可能性・配置不可能性・量産DFM・別seed再現性も未実証。
  #121は生印刷指摘61件を保持し製造承認ではない。形状・配置・pad／穴keepout・
  ツール版／設定・層／寸法・銅厚変更時は入力等価性と独立検査を再実施する。
  F-002のexit／project差分の知見とは分け、本項は層・ルール別の到達条件を扱う。
- **Evidence:** [#103報告](issue-103-fab-router-falsification.md)、
  [#103保存SES判定](../hardware/kicad/qualification/issue-103-fab-router-falsification/evidence/assessment.json)、
  [#117報告・入力同定・Wing推定](issue-117-four-layer-main-and-wing-outlook.md)、
  [#117修正01判定](../hardware/kicad/qualification/issue-117-four-layer-main/evidence/amendment-01/assessment.json)、
  [#121報告・ルール差分](issue-121-full-auto-conditions.md)、
  [#121実行セル・独立合格](../hardware/kicad/qualification/issue-121-full-auto-conditions/evidence/verification.json)。
- **Promoted to:** —（P6では昇格しない。理由・将来候補は[Issue #217 作業報告](issue-217-p6.md#昇格しないfindingの判断)を参照）

### F-013 — 旧Wing裸基板価格は両面PCBAパネルの見積根拠を代替しない（K10）

- **Conclusion:** #133の旧representative21 Wingの裸基板参考価格は、
  #147の手はんだ用各5枚・別設計候補に対しても最終見積ではなかった。
  #194 Rev.2は左右ペア面付け・両面Standard PCBAへ前提が変わり、同じ価格は適用できない。
  (confidence: high for saved price and package conditions, unverified supplier total;
  trials: #133計算専用POST保存6応答＝16mm 4件・17mm 2件。
  #147新規価格取得0、#194は個別4＋パネル2の保存CAM照合結果であり価格試行ではない。
  全検査起動総数は未確認、製造／実装実績を数えたものではない)
- **Conditions tried:** #133取得は2026-11-04 UTC 23:13:11〜23:13:17、
  形状基準commit `5744eed8234a6c3a0a6a2fa36d2e7c6bb443e024`、入力PCB hashはgeometry-evidence。
  JLCPCB公開計算専用API、ログイン／ファイルupload／注文なし、USD。
  実行Python／curlの正確な版、サーバ計算機版は未確認。保存request／responseを観測対象とする。
  FR4 TG135-140、2層、1.2mm、外層1oz、緑mask／白silk、HASL有鉛、
  既定via選択、納期2 days追加$0、1設計×5枚、PCBA／stencilなし。
  #147再開は2026-11-05、#194最終Phase Bは2026-11-07。
  それぞれの保存版は取り込みcommit
  `ba4b22c3b2885cd1c55fff8c3471f6a8f5f3f54d`／`a313ca4fcf210b1947ee9981cad056077dea0cea`。

  | 記録・対象版 | 数量・面／面付け・費目の境界 |
  | --- | --- |
  | #133 representative21 16mm 110×100／17mm 116.5×104.75mm | 各5枚・単一設計の裸基板。各engineering $4＋board $5.30/$5.90＝$9.30/$9.90、計10枚$19.20（engineering計$8含む）。実装費なし、送料・税未取得 |
  | #147 #141出力KRT-16/17-2L-P0300 | 同寸法の別設計各5枚、追加面付けなし。SMD全190 padは表面・裏mask開口0、手はんだ、PCBA／stencilなし。新規価格取得なし、#133値は参考のみ |
  | #194 Wing Rev.2最終16/17mm左右 | 個別117.2×82.698516／123.2×86.698516mm。各ピッチ左右1枚ずつを上下に置くパネル133.2×168.397032／139.2×176.397032mm、3mm間隔・タブ／mouse-bite・レールあり。98実装点＝下面84＋上面14、Standard PCBA両面。発注ロット枚数・金額は本証跡では未確認 |

- **Failed attempts:** #133の先行urllib取得は接続resetで価格未取得、curl版で取得した。
  0.10／0.20mmと名付けた同ピッチrequestはbyte同一であり、線幅入力欄は存在しない。
  $0差は線幅を変えた価格応答の実験ではなく、同一入力と当時の公開能力／加算規定の
  照合結果に限る。#147の穴座標完全一致検査停止はCAM丸めの扱いで、価格取得失敗ではない。
- **Validity scope:** 当時の裸基板費用だけに限定。Keyboard Design加算
  $16.41＋$49.25/m²は未確定・上記額に含まれず、面積単位の解釈・送料統合も未確認。
  #147の無印silk受入れ・業者DFMと最終費用承認は未完了。
  #194のパネル／両面BOM・CPL整合は価格・CPL回転の業者受入れ保証ではない。
  旧裸基板価格を現行Wing Rev.3のStandard PCBAへ流用しない。
  版・外形・ピッチ／左右・ロット枚数（panel数と個片数）・面数・実装点・面付け／
  タブ・仕上げ・銅厚・工程・送料税・見積日が変われば費目別に再見積し、
  製造側のファイル審査と承認を別途確認する。
- **Evidence:** [#133報告](issue-133-wing-cost-check.md)、
  [形状・基準commit/hash](../hardware/kicad/qualification/issue-133-wing-cost-check/geometry-evidence.json)、
  [当時価格と費目](../hardware/kicad/qualification/issue-133-wing-cost-check/price-evidence.json)、
  [6取得記録・request hash](../hardware/kicad/qualification/issue-133-wing-cost-check/quote-capture/quote-records.json)、
  [元request／response](../hardware/kicad/qualification/issue-133-wing-cost-check/quote-capture/)、
  [#147対象PCB hash・発注残件](issue-147-wing-order-prep.md)、
  [#194最終仕様・面付け](issue-194-wing-rev2-stage2.md)、
  [Rev.2 panel転写照合](../hardware/kicad/qualification/issue-194-wing-rev2/panel-verification.json)、
  [Rev.2 CAM/BOM/CPL・面別点数](../hardware/kicad/qualification/issue-194-wing-rev2/cam-verification.json)。
- **Promoted to:** —（P6では昇格しない。理由・将来候補は[Issue #217 作業報告](issue-217-p6.md#昇格しないfindingの判断)を参照）
