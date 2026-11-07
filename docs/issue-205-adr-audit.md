# Issue #205 ADR 整合監査

監査日：2026-11-08。対象：[decisions.md](decisions.md) の D-001〜D-034。
起点は `7a3cbbe7517e8fe14fe445ea0c2a86ab94524932`（PR #204）。
[Issue #205][I205] の要件と、PMO から渡されたマージゲート記録を、本文・関連文書・Git 履歴に照合した。
全34件、欠番0、ID重複0。D-030 は **未確認（PO 判断待ち）**、D-032 は **採択後に D-034 で部分置換**、D-033／D-034 は **採択済み** と判定する。
初期記録 D-004／D-005／D-006／D-011 の PO 採択根拠も未確認として分離する。

## 監査の基準と根拠

- ID は `^## D-[0-9]{3}` の主見出しだけを抽出する。`### D-021 Amendment` は同じ D-021 の改定であり、新しい ADR ではない。
- 状態欄は今回の監査判定。原文の Status と異なる場合はその違いを明記する。採択の根拠は PO の判断・作業契約・明示的マージゲートとし、実装マージや検証合格だけで採択済みにはしない。
- 決定日は明示された日だけを採用する。日付がないときは「未確認」とし、追跡可能な記録日を別記する。記録日は Git の author date の日付であり、PO 決定日の代用ではない。GitHub コメント取得結果で日時が null のものにも日時を補わない。
- 下表の C 番号は `git log --reverse -- docs/decisions.md` と該当 diff を確認した記録コミット、I 番号は判断または作業契約の Issue。既存 ADR と関連成果物を突き合わせ、部分置換と単なる継承を区別した。「なし」は後継 ADR を特定していない意味で、永久に不変という意味ではない。
- GitHub connector で Issue #205、#7／#17／#41／#123／#127／#135／#143／#145／#155／#160／#163／#167／#178／#182 の本文、#7／#13／#19／#41／#55／#57／#71／#127 のコメント、PR #18／#187／#195／#197／#201 のコメントを読み取り確認した。#195／#197 は取得したコメントが bot のみ、#201 には採択前の完了報告が残る。これらを PO の採択コメントと取り違えない。
- D-032／D-033／D-034 の決定日は、作業指示書 `.p2-runtime/instructions.md` の「PMO から渡す事実」にある **2026-11-07、PR #195／#197／#201 の PO マージゲート採択**に基づく。D-032 は Issue #205 本文でも確認でき、D-033／D-034 は既存 Status と整合する。Git のマージ履歴は成果物取り込みの裏付けとして用いる。

スクラッチと取得結果は `.p2-runtime/` に置き、コミット対象には含めない。報告書は既存の `docs/issue-*.md` 形式に合わせた。`git ls-remote` で GitHub の main が上記起点と一致することを確認した。ローカルクローンの origin はこのチェックアウトであり、複製された古い `origin/main` の参照値を監査起点にはしていない。

## 全34件の監査一覧

関連成果物のリンクはその判断を追跡する入口であり、製造リリースの指定ではない。「照合済」は ADR 主見出し、引用文書の実在と後継欄の参照先を確認した意味で、PO 根拠未確認を解消するものではない。

| ID | 状態（監査判定） | 決定日 | 対象／適用範囲 | PO 根拠と記録コミット | 後継 ID・継承範囲 | 関連成果物 | 参照照合 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [D-001](decisions.md#d-001---one-piece-geometry) | Provisional | 未確認（初出記録 2026-09-25） | 一体型の120度逆V、左右±30度の座標解釈 | 明示採択は未確認。[C01] 初出、[C02] 座標補足 | D-015：Main/Wing 分離。D-020：旧代表 Wing の幾何前提。D-032→D-034：後続 Wing 版。幾何全体の一括採択とはしない | [幾何](layout-geometry.md) | 照合済 |
| [D-002](decisions.md#d-002---key-pitch) | Historical provisional、固定ピッチを再開 | 未確認（初出記録 2026-09-25、再開記録 2026-10-04） | 旧17mm固定案。現行の量産ピッチ決定ではない | [C01] 初出、[I41]／[C06] で比較評価へ | D-015：17／16.5／16mm の比較へ。D-028：Matrix の16／17mm評価、量産選定とは別 | [評価計画](../hardware/rev-m1/evaluation-plan.md) | 照合済 |
| [D-003](decisions.md#d-003---magnetic-switch) | Provisional baseline | 未確認（初出記録 2026-09-25） | Gateron Magnetic Jade Pro／KS-20参照。実測前の量産GOは禁止 | 明示採択は未確認。[C01] は参照候補の記録 | D-032→D-034：当該 Wing の Jade Pro 脚穴・検出点設計へ具体化。実物適合の包括承認ではない | [Wing Rev.2 報告](issue-194-wing-rev2-stage2.md) | 照合済 |
| [D-004](decisions.md#d-004---power-indication) | **未確認**（原文 accepted） | 未確認（記録 2026-09-25） | MCU と独立した電源LED | [C01] に記録。PO の判断／マージゲートを特定できず | なし | [仕様](specification.md) | 照合済 |
| [D-005](decisions.md#d-005---layer-indication) | **未確認**（原文 accepted） | 未確認（記録 2026-09-25） | MCU 制御の4層表示RGB LED | [C01] に記録。PO の判断／マージゲートを特定できず | なし | [仕様](specification.md) | 照合済 |
| [D-006](decisions.md#d-006---manufacturing-strategy) | **未確認**（原文 accepted） | 未確認（記録 2026-09-25） | JLCPCB PCBA と初期筐体のFDM | [C01] に記録。後続の個別製造方針は存在するが、本項全体の PO 採択根拠は未特定 | D-015／D-017：DFM 方針を具体化。D-022：旧Main工程、D-032→D-034：Wing両面 Standard PCBA。初期筐体を含む全体の置換ではない | [DFM方針](../hardware/rev-m1/dfm-policy.md)、[ケース最終](issue-198-case-final.md) | 照合済 |
| [D-007](decisions.md#d-007---project-tracking) | Accepted（現行の正本／read model 境界） | 未確認（現行内容の記録 2026-09-27） | docs が正本、Dashboard は提案／マージ後状態を表示 | [I7] が D-007 更新と PO レビューを明示。[C03]／PR #8 で記録。初出版は [C01] | なし。PR #204 は Dashboard 用途の追加方針であり新 ADR ID ではない | [ガバナンス](governance.md)、[整理計画](repo-cleanup-plan.md) | 照合済 |
| [D-008](decisions.md#d-008---pcb-thickness) | Provisional baseline（後続で1.2mmを維持） | 未確認（初出記録 2026-09-26） | Hall評価／量産PCBの1.2mm厚 | [C02] 初出。[I57] は G0B 範囲の1.2mmを明示採択 | D-012／D-017／D-019／D-021：1.2mmを継承、厚さの置換なし | [DFM方針](../hardware/rev-m1/dfm-policy.md) | 照合済 |
| [D-009](decisions.md#d-009---hall-analog-power-rail) | Provisional baseline、直結VBUS方式は後続版で置換 | 未確認（初出記録 2026-09-26） | GPIO7 制御TPS22919でVBUSをHALL_5Vへ | [C02] 初出。後続変更は [I167] の PO 決定 | D-026：5.2V変換器＋共通 default-off U5。D-027：入力境界。スイッチ制御自体は継承 | [2 Wing 電源比較](issue-165-dual-wing-power-study.md) | 照合済 |
| [D-010](decisions.md#d-010---hall-multiplexing-topology) | Provisional baseline（後続で電気契約を具体化） | 未確認（初出記録 2026-09-26） | 6 TMUX1208、2×7 address×3 ADC、分圧／フィルタ | [C02] 初出。[I57] の3 MUX／3 ADC採択、[I160] の2 Wing契約と照合 | D-017：GH14へ具体化。D-024：共通生ADCバス＋独立enable。D-028：Matrixの6入力／MUXのみ別構成 | [インターフェース](../hardware/rev-m1/main-wing-interface.md) | 照合済 |
| [D-011](decisions.md#d-011---evaluation-board-before-main-pcb) | **未確認**（原文 accepted measurement intent、物理形態は部分置換） | 未確認（初出記録 2026-09-26） | 量産前のHall実測。旧一体4キー形態 | [C02] 初出。初期採択ゲートは未特定。[I41]／[C06] は形態変更、[I57] は後続の測定枠組み採択 | D-015：旧一体4キー形態を Main＋Evaluation Wing へ。D-017：測定枠組み。量産前実測の意図は失効しない | [評価計画](../hardware/rev-m1/evaluation-plan.md) | 照合済 |
| [D-012](decisions.md#d-012---pcb-layer-baseline) | Accepted、Mainのみ部分改定 | 未確認（記録 2026-09-30） | 評価／量産の2層基準。1.2mm維持 | [I17] の Product Owner Human Gate／PCB layer policy、[C04]／PR #18 | D-019：Mainのみ4層。D-021：代表Wingの2層とルールを別途確定。D-028：Matrixへ拡張 | [DFM方針](../hardware/rev-m1/dfm-policy.md) | 照合済 |
| [D-013](decisions.md#d-013---eda-backend-evaluation-strategy) | Accepted evaluation baseline（歴史的評価方針） | 未確認（記録 2026-09-30） | importerを正本とせず stock native TSX を評価。fork等禁止 | [I13-Gate]、[I17] の明示方針。[C04]／PR #18 | D-014：凍結fixtureの電気正本。D-016：物理候補復帰。D-018：追加router探索を終了し代替経路を計画 | [native spike](tscircuit-native-spike-report.md) | 照合済 |
| [D-014](decisions.md#d-014---native-tscircuit-is-the-m1-electrical-source) | Accepted（永久fixtureの歴史的電気正本） | 未確認（記録 2026-10-02） | M1四キー電気回路の native TSX 正本。製造／配置承認を含まない | [I19-Gate] の GO。[C05]／PR #27 | D-015：物理製品を別設計に分離、fixtureは置換しない | [native spike](tscircuit-native-spike-report.md) | 照合済 |
| [D-015](decisions.md#d-015---revm1-reusable-main--evaluation-wing-architecture) | Accepted architecture baseline、後続で部分改定 | 未確認（記録 2026-10-04） | 再利用Main＋Evaluation Wing、左右21キー、比較実験、DFM | [I41] の rebaseline 作業契約、[C06]／PR #42。JITX採用判断とは別 | D-017：接続・評価凍結。D-019／D-021：Main／Wingの層とルール。D-028：Matrix評価構成。D-033／D-034：版別形状／両面工程 | [構成](../hardware/rev-m1/architecture.md)、[評価計画](../hardware/rev-m1/evaluation-plan.md) | 照合済 |
| [D-016](decisions.md#d-016---jitx-physical-backend-no-go-native-tscircuit-resumes-as-active-revm1-eda-candidate) | Accepted（JITX physical backend NO-GO） | 未確認（記録 2026-10-05） | 固定環境でのRev.M1／Rev.A物理EDA選定、証跡保存 | [I55-Gate] の PO NO-GO。[C07]／PR #56 | D-017：G0B完了。D-018：後続評価手順を更新。JITX NO-GOを撤回しない | [JITX評価](jitx-evaluation.md) | 照合済 |
| [D-017](decisions.md#d-017---revm1-mainwing-architecture-and-interface-freeze) | Accepted G0B、適用範囲別に部分更新 | 2026-10-06 | GH14／6帰線／100mm、外付けEN pull-down、評価・DFM境界 | [I57] の PO GO と本文に明示日。[C08]／PR #60 | D-018：次工程。D-019／D-021：基板条件。D-024：2ポート。D-028：Matrix。D-033：Main Rev.4の200mm、D-034が保持 | [G0B受入記録](../hardware/rev-m1/g0b-freeze-proposal.md) | 照合済 |
| [D-018](decisions.md#d-018---bounded-alternate-physical-backend-qualification-planning) | Accepted planning only | 未確認（計画本文の参照日 2026-10-07、記録 2026-10-08） | tscircuit内蔵router探索終了、代替backendの限定評価計画。実行／採用は別許可 | [I71-Gate] の GO。[C09]／PR #72。コメント取得の日時は未提供 | D-019：Mainの層・ルールのみ更新。後続のKiCad実装履歴を新たなbackend採用ADRと見なさない | [限定評価計画](alternate-physical-backend-qualification-plan.md) | 照合済 |
| [D-019](decisions.md#d-019---revm1-main-four-layer-and-010-mm-design-rule-baseline) | Accepted（Main限定） | 2026-11-04 | Main4層／1.2mm、幅・間隙0.10mm、via0.60/0.30mm | [I123] の PO 決定、[C10]／PR #126。実証 PR #122 | D-022：未決だったPOFV／J1工程を確定。D-033：4層等を継承。Wingへ拡張しない | [#121実証](issue-121-full-auto-conditions.md) | 照合済 |
| [D-020](decisions.md#d-020---representative-21-key-wing-100-x-100-mm-requirement-relaxation) | Accepted（旧代表21キーWingの寸法） | 2026-11-05 | 16mm＝110×100、17mm＝116.5×104.75mm。pitch9対象外 | [I127-Decision] の PMO記録、原文の明示日、[C11]／PR #128 | D-032→D-034：新Wingの版別形状。旧代表寸法を全版共通条件にしない | [#127設計](issue-127-wing-design.md) | 照合済 |
| [D-021](decisions.md#d-021---revm1-wing-two-layer-and-010-mm-design-rule-baseline) | Accepted、同日Amendmentあり | 2026-11-05（改定も同日） | representative21 Wing2層／1.2mm、信号0.10・電源GND0.30、間隙0.10、via0.60/0.30、KRT escalation off | [I135]→[C12]／PR #136、[I143]→[C13]／PR #146内の改定。実証 PR #132／#142 | 同一IDのAmendmentが一律幅のみ置換。D-028でMatrixへ明示拡張、D-032／D-034で新Wingへ継承 | [#131](issue-131-wing-condition-search.md)、[#141](issue-141-wing-power-integrity.md) | 照合済 |
| [D-022](decisions.md#d-022---revm1-main-order-specifications-pofv-vias-and-j1-economic-pcba) | Accepted（旧Main版の注文仕様） | 2026-11-05 | via-in-pad POFVとオンボードUSB J1の同一Economic PCBA | [I145] の明示採択、[C13]／PR #146。調査 PR #139 | D-029：Matrix限定の別方針（Mainを置換しない）。D-030：Main Rev.3の提案、採択未確認。D-033：Main Rev.4でJ1分離、POFVなしは同版の提案 | [製造レビュー](issue-137-main-manufacturing-review-prep.md) | 照合済 |
| [D-023](decisions.md#d-023---revm1-main-mounting-revision-plan-a-retained-48-x-44-mm-outline) | Accepted（旧Main取付案A） | 2026-11-06 | 48×44mm、4 NPTHと全層銅予約 | [I155] の案A採択、[C14]／PR #156 | D-024：第2ポート例外。D-025：外形のみ48×52へ、4穴維持。D-033：Main Rev.4の三角形・3穴へ | [#153案](issue-153-main-mounting-stage1.md)、[#155実装](issue-155-main-mounting-stage2.md) | 照合済 |
| [D-024](decisions.md#d-024---revm1-main-two-wing-interface-and-plan-a--plan-c-fallback) | Accepted scope、部分置換 | 2026-11-06 | 共通電源／アドレス／3ADC＋独立EN、初期配置A、条件付きC提案 | [I160] の PO 決定、[C15]／PR #162 | D-025：配置C。D-026：機構ゲートと電源方式。D-027：入力境界。D-033：外形／200mm／UDB。GH14電気契約は継承 | [#157定義](issue-157-main-dual-wing-stage1.md)、[#160停止](issue-160-main-dual-wing-stage2.md) | 照合済 |
| [D-025](decisions.md#d-025---revm1-main-two-wing-plan-c-outline-and-j3-placement) | Accepted、形状は後続版で置換 | 2026-11-06 | 案C48×52mm、J3=(105,73)、4穴保持 | [I163] の PO 切替承認、[C16]／PR #164 | D-026：実機機構ゲートを後段へ。D-033：Main Rev.4の外形／配置／穴 | [#163報告](issue-163-main-dual-wing-plan-c.md) | 照合済 |
| [D-026](decisions.md#d-026---main-two-wing-implementation-design-first-mechanics-and-regulated-52-v) | Accepted scope、入力条件は部分置換 | 2026-11-06 | 設計先行、5.2V強制PWM、127mA/Wing、4.60V目標、共通／枝50mΩ | [I167] の明示 PO 決定、[C17]／PR #168 | D-027：変換器入力4.75V要件を置換。D-033：形状／ハーネス更新、5.2V骨格維持 | [電源比較](issue-165-dual-wing-power-study.md)、[#167](issue-167-main-dual-wing-stage2.md) | 照合済 |
| [D-027](decisions.md#d-027---main-usb-input-requirement-at-the-board-connector) | Accepted requirement redefinition | 2026-11-06 | Main USBコネクタ入力4.50–5.25V、構成許可500mA、出力目標維持 | [再開指示](../hardware/kicad/qualification/issue-167-main-dual-wing-stage2/resume/instructions-167-resume.md) の PO 承認、[C17]／PR #168 | D-033：UDB分離。新C3/SH配線は完成抵抗等の別確認。入力要件を独断で緩和しない | [#167報告](issue-167-main-dual-wing-stage2.md) | 照合済 |
| [D-028](decisions.md#d-028---dual-pitch-matrix-rev2-evaluation-board-naming-per-issue-179-convention) | Accepted scope（Matrix Rev.2） | 2026-11-06 | 16／17mm各3×3、18キー、3 MUX、GH14、D-021条件拡張 | [I178] の訂正済み本文、[C18]／PR #181。古いIssue題名を仕様にしない | D-029：Matrix Rev.3のvia非重複／POFV不要。18キー構成は継承 | [Matrix Rev.2](issue-178-m1-matrix-board.md) | 照合済 |
| [D-029](decisions.md#d-029---matrix-rev3-keep-every-via-clear-of-component-pads-no-pofv) | Accepted design policy（Matrix Rev.3のみ） | 2026-11-06 | 全via–全pad銅間隔≥0.10mm、当該版POFV不要 | [I182] の明示 PO 判断、[C19]／PR #186 | なし。D-030はMainの別提案。D-022の旧Main仕様には遡及しない | [Matrix Rev.3](issue-182-matrix-rev3.md) | 照合済 |
| [D-030](decisions.md#d-030---main-rev3-via-relocation-to-remove-the-pofv-design-requirement) | **未確認（PO 判断待ち）** | 採択日未確認（提案・実装記録 2026-11-06） | Main Rev.3のvia移設に伴うPOFV要求撤回提案 | [C20]／PR #187は実装マージ。[I205] とPMO引継ぎが方針の明示採択未了を指定 | D-033：後続Main Rev.4は別版。D-030の遡及採択ではない | [Main Rev.3報告](issue-185-main-rev3.md) | 照合済 |
| [D-031](decisions.md#d-031---knowledge-recording-adr-finding-records-and-promotion) | Accepted PO decision | 2026-11-07（記録コミットは11-08） | ADR／Finding／プロセス・skill昇格、確定ADR不変 | 原文の明示日、[整理計画§5.1](repo-cleanup-plan.md#51-pr-192-を最初に取り込む)の採用済み方針、[C24]／PR #192 | なし | [findings](findings.md)、[整理計画](repo-cleanup-plan.md) | 照合済 |
| [D-032](decisions.md#d-032-draft---wing-rev2-baseline-issue-194) | **Accepted → Superseded（D-034の指定範囲）**、原文Draftは旧表記 | 2026-11-07 | Wing Rev.2、16／17mm左右、下面Hall、locator、2層、両面パネル | PMO引継ぎと [I205]：PR #195 の PO マージゲート採択。[C21] と報告書で実装を照合 | D-034：外形／GH・サービス部品／南側穴／100mm前提を置換。キー中心・Hall姿勢・locator等は継承 | [Wing Rev.2](issue-194-wing-rev2-stage2.md) | 照合済 |
| [D-033](decisions.md#d-033---main-rev4-triangular-baseline-and-separated-udb) | **Accepted（Main Rev.4）** | 2026-11-07 | 三角Main、3穴、UDB C3／J4分離、GH200mm×2、4層 | PMO引継ぎ：PR #197 の PO マージゲート採択。原文Status、[C22]、報告書と整合 | なし。D-034は200mmを保持しWing側を更新、Mainを置換しない | [Main Rev.4 Phase B](issue-196-main-rev4-phaseb.md) | 照合済 |
| [D-034](decisions.md#d-034-draft---wing-rev3-baseline-issue-200) | **Accepted（Wing Rev.3）**、見出しdraftは表記不整合 | 2026-11-07 | 北サービス域／南trim、16／17mm左右、200mm、2層、非POFVパネル | PMO引継ぎ：PR #201 の PO マージゲート採択。原文Status、[C23]、[ケース最終](issue-198-case-final.md)の200mmと照合 | なし。D-032の明示範囲のみ置換 | [Wing Rev.3](issue-200-wing-rev3-stage2.md)、[確定CSV](../hardware/case/issue-200-rev3/README.md) | 照合済 |

## 適用範囲を限定した置換関係

| 系統 | 置換・継承の判定 | 保持する境界 |
| --- | --- | --- |
| 層・ルール | D-012→D-019はMainだけ4層。D-021は代表Wingの独立した2層決定。同IDのAmendmentで幅だけクラス分け。D-028がMatrixへ明示拡張し、D-032／D-034は新Wingへ適用 | Main4層をWingへ適用しない。厚さ1.2mmを変えない。D-021の旧一律0.10mmを現行電源幅にしない |
| Main/Wing接続 | D-017→D-024で2ポートへ拡張。D-033はMain Rev.4の100mm前提を200mm×2へ置換。D-034が200mmを保持 | GH14のpin配置・6帰線・独立enableを維持。旧評価用100mmを全履歴から削除しない |
| Main機構／電源 | D-023の4穴・外形→D-024の第2ポート→D-025の案C→D-026の設計先行／5.2V→D-027の入力境界再定義。D-033は三角形／3穴／UDBへ | 電気契約、出力目標、実機検証項目を一括失効させない。D-027はD-026全体の取消ではない |
| POFV／J1 | D-022は旧MainのPOFVとJ1 Economic工程。D-029はMatrix Rev.3のみPOFV不要。D-030はMain Rev.3だけの撤回提案で採択未確認。D-033はMain Rev.4からJ1を除きUDBへ分離 | Matrixの決定をMainへ横展開しない。D-033の通常tented／非POFVは当該版の提案・業者DFM待ちという限定を保持。UDB全体の製造工程をこの監査で確定しない |
| Wing版 | D-032は採択済みのRev.2履歴。D-034はRev.3の外形、GH／サービス域、南穴、100mm前提を置換 | キー中心、Hall姿勢、locator、電気契約、実物fit・磁気／電源評価等は継承。200mmの余長処理はケースの別確認 |
| ピッチ／fixture | D-002→D-015で固定ピッチを再開。D-011の旧4キー物理形態はD-015へ。D-014の永久4キーfixtureはそのまま | 16／17mm設計の存在を量産ピッチ採択やHall実測合格と解釈しない |

## 注記案と今回の変更

`decisions.md` に付けた引用形式の「監査注記（2026-11-08、Issue #205）」が PR 用の注記案である。既存の Status、本文、見出しは変更しない。この報告書への冒頭案内、根拠未確認4件、主要な部分置換と D-030／D-032／D-033／D-034 の状態補足を追加する。

D-032／D-034 の主見出しは **draft を含む原文のまま**保持する。これにより、既存の `#d-032-draft---wing-rev2-baseline-issue-194` と `#d-034-draft---wing-rev3-baseline-issue-200` を含む見出しアンカーを維持する。新しい別名アンカーや見出しの改名は不要と判断した。注記自体は見出しにせず、D-021 Amendment を含む既存の全見出しと出現順も維持する。

## 未確認事項と PO への確認事項

| 項目 | 確認が必要な内容 | 今回の扱い |
| --- | --- | --- |
| D-030 | Main Rev.3のPOFV要求撤回を方針として採択したか。採択する場合は適用版・日付・判断根拠を提示すること | 未確認（PO 判断待ち）。PR #187の実装マージ、同PRの見積コメントを採択の代用にしない。D-033で遡及確定しない |
| D-004／D-005／D-006 | 初期の電源LED／RGB／PCBA＋FDM方針の採択判断と日付。参照できるPRゲートまたはPO判断を特定できるか | 原文 accepted を保存し、監査判定は未確認。新たにAcceptedにはしない |
| D-011 | 初期の量産前実測方針の採択根拠と日付 | 初期採択は未確認。後続G0Bの測定枠組み採択と、実測完了を区別する |
| 初期・日付未記載ADR | D-001〜D-016の決定日（D-007の現行改定を含む）と、D-018のPO判断日。暫定ADRは採択済みへ昇格させる意図があったか | 表の「未確認」を保持。記録日・Issue作成日・マージ日から判断日を捏造しない。D-003／D-008等は後続の採択範囲だけを示す |
| D-032／D-033／D-034の注記と本変更のマージ | 引継ぎ済みゲート事実を用いた状態注記と旧見出し保持の妥当性 | 注記案をコミットしてPOレビューへ渡す。設計採択と製造GOを混同しない |

採択の明示根拠が不足する項目は上記5件である。暫定／歴史的暫定6件（D-001／D-002／D-003／D-008／D-009／D-010）は暫定のままとし、その初期採択も未確認と記録した。残り23件は記載した判断・作業契約・ゲートを根拠として、それぞれの限定範囲で採択を確認した。決定日の不明だけでは、根拠のある採択まで取り消していない。

## 対象外の発見と引継ぎ

- `decisions.md` の D-029 と D-030 の間に `=======`／`>>>>>>> origin/main` の残骸がある。[C19]（PR #186）の追加時からの履歴で、今回作った差分ではない。確定本文の削除を伴うため今回は保持し、別途最小修正の候補として報告する。
- `project-status.md` に D-032／D-034 draft 等の旧状態があり、Main／Wing報告書にも採択前の草案・長さ未決という記述が残る。これらは当時の記録として本監査の判断と区別する。現行案内・Dashboard同期は整理計画P3の対象であり、今回更新しない。
- PR #187 の [見積コメント](https://github.com/ihsinoky/he-piantor-42/pull/187#issuecomment-6686129886) は当該時点の見積情報。D-030の提案本文や新Main Rev.4の価格／製造条件を今回それに合わせて書き換えない。

## 検証結果

- 主見出し34件、期待集合D-001〜D-034と完全一致、欠番0・重複0。D-021 Amendmentは1件の補助見出し。
- 一覧34行、7必須項目と参照照合欄の空欄0。全後継IDが監査対象内に存在する。
- 追加した監査注記と冒頭案内を除くと `decisions.md` は起点版とバイト単位で一致する。既存Status／全見出しとその順序を保持し、旧アンカーを変えていない。
- 報告書と注記の相対リンク97箇所の実在、指定がある場合の対象見出しアンカーを確認。参照コミット24件はローカルのGit objectを確認した。追加は監査注記15件と冒頭案内1件。
- `git diff --check` 合格。変更対象は `docs/decisions.md` と本報告書だけ。CAD／CAM／製造データ／Dashboardへの差分なし。ハードウェア再生成・配線・実機検証は伴わない文書監査である。

再検証には、起点に対して `git diff 7a3cbbe7 -- docs/decisions.md`、`git diff --check 7a3cbbe7`、`git log --reverse --format='%h %as %s' -- docs/decisions.md` を使用できる。採択の是非を文字列検査だけで自動判定せず、上表の判断根拠と限定範囲もレビューする。

[I205]: https://github.com/ihsinoky/he-piantor-42/issues/205
[I7]: https://github.com/ihsinoky/he-piantor-42/issues/7
[I17]: https://github.com/ihsinoky/he-piantor-42/issues/17
[I13-Gate]: https://github.com/ihsinoky/he-piantor-42/issues/13#issuecomment-5899763565
[I19-Gate]: https://github.com/ihsinoky/he-piantor-42/issues/19#issuecomment-5939376616
[I41]: https://github.com/ihsinoky/he-piantor-42/issues/41
[I55-Gate]: https://github.com/ihsinoky/he-piantor-42/issues/55#issuecomment-5991285003
[I57]: https://github.com/ihsinoky/he-piantor-42/issues/57#issuecomment-6010634587
[I71-Gate]: https://github.com/ihsinoky/he-piantor-42/issues/71#issuecomment-6046244229
[I123]: https://github.com/ihsinoky/he-piantor-42/issues/123
[I127-Decision]: https://github.com/ihsinoky/he-piantor-42/issues/127#issuecomment-6640507686
[I135]: https://github.com/ihsinoky/he-piantor-42/issues/135
[I143]: https://github.com/ihsinoky/he-piantor-42/issues/143
[I145]: https://github.com/ihsinoky/he-piantor-42/issues/145
[I155]: https://github.com/ihsinoky/he-piantor-42/issues/155
[I160]: https://github.com/ihsinoky/he-piantor-42/issues/160
[I163]: https://github.com/ihsinoky/he-piantor-42/issues/163
[I167]: https://github.com/ihsinoky/he-piantor-42/issues/167
[I178]: https://github.com/ihsinoky/he-piantor-42/issues/178
[I182]: https://github.com/ihsinoky/he-piantor-42/issues/182
[C01]: https://github.com/ihsinoky/he-piantor-42/commit/42caa276
[C02]: https://github.com/ihsinoky/he-piantor-42/commit/79ff8929
[C03]: https://github.com/ihsinoky/he-piantor-42/commit/0168de45
[C04]: https://github.com/ihsinoky/he-piantor-42/commit/44735c75
[C05]: https://github.com/ihsinoky/he-piantor-42/commit/795479ea
[C06]: https://github.com/ihsinoky/he-piantor-42/commit/8f6c401a
[C07]: https://github.com/ihsinoky/he-piantor-42/commit/7d7f3cff
[C08]: https://github.com/ihsinoky/he-piantor-42/commit/d97414b1
[C09]: https://github.com/ihsinoky/he-piantor-42/commit/20b25914
[C10]: https://github.com/ihsinoky/he-piantor-42/commit/22d25dd7
[C11]: https://github.com/ihsinoky/he-piantor-42/commit/96166d3f
[C12]: https://github.com/ihsinoky/he-piantor-42/commit/8a4c3d32
[C13]: https://github.com/ihsinoky/he-piantor-42/commit/f2a6c138
[C14]: https://github.com/ihsinoky/he-piantor-42/commit/a11c1f7d
[C15]: https://github.com/ihsinoky/he-piantor-42/commit/58a654cf
[C16]: https://github.com/ihsinoky/he-piantor-42/commit/aa39da38
[C17]: https://github.com/ihsinoky/he-piantor-42/commit/c3e913f8
[C18]: https://github.com/ihsinoky/he-piantor-42/commit/d9b18da0
[C19]: https://github.com/ihsinoky/he-piantor-42/commit/b2d74508
[C20]: https://github.com/ihsinoky/he-piantor-42/commit/f04ef1b7
[C21]: https://github.com/ihsinoky/he-piantor-42/commit/a313ca4f
[C22]: https://github.com/ihsinoky/he-piantor-42/commit/90c8314b
[C23]: https://github.com/ihsinoky/he-piantor-42/commit/932b880c
[C24]: https://github.com/ihsinoky/he-piantor-42/commit/57e12a33
