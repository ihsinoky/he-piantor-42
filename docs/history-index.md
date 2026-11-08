# 履歴索引

2026-11-08 / Issue #209（整理計画 P4）。[現行成果物索引へ戻る](artifacts-index.md) ／ [現在の状態・残件](project-status.md) ／ [ADR監査](issue-205-adr-audit.md)。

この索引は既存記録への入口であり、設計・製造データの正本を新設しない。対象別の世代順に報告・Issue・PRを結び、配置棚卸しの単位は後段の全件表で直接参照する。根拠は[整理計画](repo-cleanup-plan.md)3.1／4.1／5.6／6節、[版命名表](project-status.md)、各パッケージREADMEとローカルmainのマージ履歴。対象を先に選べる構成と、物理配置を変えず全単位へ辿れる全件表を併用した。

「旧最終」はその世代での資格済み成果で、現行製造入力を意味しない。「入力」は凍結コピー・契約・配置案、「失敗」は不合格やゲート停止を含む。未実行は失敗や合格に数えない。検査コード、manifest、hash、rawログを含む証跡一式を保持する。現行成果物の合格も製造GO・実機合格を意味しない。

- [Main](#main)：単Wing Rev.1 → 2Wing Rev.2 → Rev.3 → Rev.4
- [Matrix](#matrix)：pitch9 Rev.1 → 混載18キー Rev.2 → via非重複 Rev.3
- [Wing](#wing)：Rev.1 SILK-149A → Rev.2 → Rev.3
- [ケース](#case)：初期検討 → #198 Stage 1 → Stage 2 → 最終
- [手法履歴](#method)：EDA経路と #87〜#121 の反証・条件探索
- [横断・運用](#cross) ／ [現行パッケージ内の役割](#package-roles) ／ [付録A全件入口](#inventory-a) ／ [付録Bの補助文書](#inventory-b)

<a id="main"></a>

## Main

単Wing Rev.1は #121／D-019の4層0.10mm条件を基礎に、#124→#137／D-022→#153→#155で4穴の旧最終へ。2Wing Rev.2は #157→#160（案A停止）→#163（案C）→#165／D-026→#167／D-027→#169→#173→#175の順。#175が旧最終で、#169の初回合格を部品更新後へ流用しない。

Rev.2→Rev.3は[横断via監査 #183](issue-183-via-pad-audit.md)→#185。C26–C28／R17のBOM訂正は [PR #177](https://github.com/ihsinoky/he-piantor-42/pull/177)、C25訂正は [PR #189](https://github.com/ihsinoky/he-piantor-42/pull/189) の履歴も参照する。Rev.4は #196の旧Phase A案をA-2三角形へ更新し、Phase Bで現行最終となる。D-033／PR #197採択が後続判断であり、Phase B報告の「草案」を書き換えない。D-030／PR #187のPOFV撤回採択は依然未確認で、D-033はその遡及採択ではない。

| 報告（版・段階は原題） | Issue / PR | 入力・最終・失敗の役割 |
| --- | --- | --- |
| [docs/issue-124-main-bom-pcba-estimate.md](issue-124-main-bom-pcba-estimate.md)<br>Issue #124 — Main BOM具体化・Economic PCBA見積もり（5枚） | [#124](https://github.com/ihsinoky/he-piantor-42/issues/124) / [#125](https://github.com/ihsinoky/he-piantor-42/pull/125) | 単Wing Main Rev.1のBOM／PCBA条件付き見積。未確定費目を含む履歴。 |
| [docs/issue-137-main-manufacturing-review-prep.md](issue-137-main-manufacturing-review-prep.md)<br>Issue #137 — Main 製造前レビュー準備 | [#137](https://github.com/ihsinoky/he-piantor-42/issues/137) / [#139](https://github.com/ihsinoky/he-piantor-42/pull/139) | Main Rev.1 のvia／J1工程検討。後続 D-022 の採択根拠。 |
| [docs/issue-153-main-mounting-stage1.md](issue-153-main-mounting-stage1.md)<br>Issue #153 — Main 取付穴追加の実現性と配置案（Stage 1） | [#153](https://github.com/ihsinoky/he-piantor-42/issues/153) / [#154](https://github.com/ihsinoky/he-piantor-42/pull/154) | Main Rev.1取付穴 Stage 1の入力案。 |
| [docs/issue-155-main-mounting-stage2.md](issue-155-main-mounting-stage2.md)<br>Issue #155 — Main 機構改版 Stage 2：案Aの実装と再資格確認 | [#155](https://github.com/ihsinoky/he-piantor-42/issues/155) / [#156](https://github.com/ihsinoky/he-piantor-42/pull/156) | Main Rev.1取付穴 Stage 2。局所退避失敗、全体再配線合格、旧最終。 |
| [docs/issue-157-main-dual-wing-stage1.md](issue-157-main-dual-wing-stage1.md)<br>Issue #157 — Main 2 Wing 接続化 Stage 1：実現性とインタフェース定義案 | [#157](https://github.com/ihsinoky/he-piantor-42/issues/157) / [#159](https://github.com/ihsinoky/he-piantor-42/pull/159) | Main Rev.2（2Wing）Stage 1の電気・配置提案。機構／電源ゲート未成立。 |
| [docs/issue-160-main-dual-wing-stage2.md](issue-160-main-dual-wing-stage2.md)<br>Issue #160 — Main 2 Wing Stage 2：案Aの機構ゲートと案C切替提案 | [#160](https://github.com/ihsinoky/he-piantor-42/issues/160) / [#162](https://github.com/ihsinoky/he-piantor-42/pull/162) | Main Rev.2案Aの機構ゲート停止。D-024、案Cへ。 |
| [docs/issue-163-main-dual-wing-plan-c.md](issue-163-main-dual-wing-plan-c.md)<br>Issue #163 — Main 2 Wing 案C：採用記録、機構具体化と停止状態 | [#163](https://github.com/ihsinoky/he-piantor-42/issues/163) / [#164](https://github.com/ihsinoky/he-piantor-42/pull/164) | 案C採用 D-025、機構具体化後も停止。新板配線未実施。 |
| [docs/issue-165-dual-wing-power-study.md](issue-165-dual-wing-power-study.md)<br>Issue #165 — 2 Wing 電源の回路見直し：方式案と同条件の数値比較 | [#165](https://github.com/ihsinoky/he-piantor-42/issues/165) / [#166](https://github.com/ihsinoky/he-piantor-42/pull/166) | Main 2Wing電源4方式の比較入力。D-026の5.2V案へ。 |
| [docs/issue-167-main-dual-wing-stage2.md](issue-167-main-dual-wing-stage2.md)<br>Issue #167 — Main 2 Wing Stage 2 再開：D-027、実装候補と資格確認の停止 | [#167](https://github.com/ihsinoky/he-piantor-42/issues/167) / [#168](https://github.com/ihsinoky/he-piantor-42/pull/168) | D-027入力境界の再定義。候補・resumeの配線は不合格。旧要件の停止証跡も保持。 |
| [docs/issue-169-main-dual-wing-followup.md](issue-169-main-dual-wing-followup.md)<br>Issue #169 — Main 2 Wing Stage 2 フォローアップ：有限2回の結果と停止 | [#169](https://github.com/ihsinoky/he-piantor-42/issues/169) / [#172](https://github.com/ihsinoky/he-piantor-42/pull/172) | Main Rev.2継続。seed-a合格後、部品更新した2回目は不合格。 |
| [docs/issue-173-main-dual-wing-final.md](issue-173-main-dual-wing-final.md)<br>Issue #173 — preflight 不合格で停止、合格済み seed-a を整理 | [#173](https://github.com/ihsinoky/he-piantor-42/issues/173) / [#174](https://github.com/ihsinoky/he-piantor-42/pull/174) | Main Rev.2の1210候補はpreflight停止。fallback seed-aは別の合格履歴。 |
| [docs/issue-175-main-dual-wing-final2.md](issue-175-main-dual-wing-final2.md)<br>Issue #175 — C26配置成立、全体配線1回で独立4指標0、確定見積は未取得 | [#175](https://github.com/ihsinoky/he-piantor-42/issues/175) / [#176](https://github.com/ihsinoky/he-piantor-42/pull/176) | Main Rev.2最終履歴。1210出力C、44ネット・4指標0。見積／製造GOは別。 |
| [docs/issue-185-main-rev3.md](issue-185-main-rev3.md)<br>Issue #185 — Main Rev.3：35 via を移設し POFV 不要化の設計条件を達成 | [#185](https://github.com/ihsinoky/he-piantor-42/issues/185) / [#187](https://github.com/ihsinoky/he-piantor-42/pull/187) | Main Rev.3旧最終。35via移設、POFV撤回はD-030提案（採択未確認）。 |
| [docs/issue-196-main-rev4.md](issue-196-main-rev4.md)<br>Issue #196 — Main Rev.4 Phase A：配置・面取り外形案 | [#196](https://github.com/ihsinoky/he-piantor-42/issues/196) / [#197](https://github.com/ihsinoky/he-piantor-42/pull/197) | Phase A旧配置・面取り案。A-2三角形案へ更新された履歴入力。 |
| [docs/issue-196-main-rev4-phasea2.md](issue-196-main-rev4-phasea2.md)<br>Issue #196 — Main Rev.4 Phase A-2：UDB 分離・三角形配置案 | [#196](https://github.com/ihsinoky/he-piantor-42/issues/196) / [#197](https://github.com/ihsinoky/he-piantor-42/pull/197) | Phase A-2三角形・UDB分離の配置入力。100mm不達と200mm候補。配線合格ではない。 |
| [docs/issue-196-main-rev4-phaseb.md](issue-196-main-rev4-phaseb.md)<br>Issue #196 Phase B — Main Rev.4 配線・製造データ・再見積準備 | [#196](https://github.com/ihsinoky/he-piantor-42/issues/196) / [#197](https://github.com/ihsinoky/he-piantor-42/pull/197) | Phase B現行最終。40ネット・4指標0、製造パッケージ。記録時の草案は後続D-033／PR #197で採択。 |

<a id="matrix"></a>

## Matrix

Rev.1は #127のピッチ別3×3（各9キー）、#129入力停止→#131配線条件の系列。[Wing節](#wing)に共通報告を置く。Rev.2 #178／D-028は16/17mm混載の18キー1枚へ置換。Rev.3 #182／D-029は全via非重複化で当該版のみPOFV不要。製品用21キーWingと区別する。Rev.2の146viaへの工程注記をRev.3の158viaに持ち込まず、Rev.3の結論をRev.2へ遡及しない。

| 報告（版・段階は原題） | Issue / PR | 入力・最終・失敗の役割 |
| --- | --- | --- |
| [docs/issue-178-m1-matrix-board.md](issue-178-m1-matrix-board.md)<br>Issue #178 — M1 16mm／17mm 一体18キー評価基板 | [#178](https://github.com/ihsinoky/he-piantor-42/issues/178) / [#181](https://github.com/ihsinoky/he-piantor-42/pull/181) | Matrix Rev.2最終履歴。両ピッチ18キーの一枚基板、D-028。Rev.1を置換。 |
| [docs/issue-182-matrix-rev3.md](issue-182-matrix-rev3.md)<br>Issue #182 — マトリクス基板 Rev.3：via とパッドの重なり排除 | [#182](https://github.com/ihsinoky/he-piantor-42/issues/182) / [#186](https://github.com/ihsinoky/he-piantor-42/pull/186) | Matrix Rev.3現行。158via非重複、D-029で当該版のみPOFV不要。 |

<a id="wing"></a>

## Wing

Rev.1は #127の代表21キー入力→#129ゲート停止→#131合格→#133原価→#138製造検討→#141電源/GND拡幅→#147シルクなしCAM→#149 SILK-149A旧最終。Matrix Rev.1と共有する評価入力は同じ報告から辿る。D-021の2層条件をMainのD-019と混同しない。

Rev.2は #158標準搭載計画→#190配列検討→#194 Phase A/B。Rev.3は #200 Stage 1→1b（北肩R5形状）→Stage 2（4単板、2パネル、確定CSV）。[ケース](#case)の凍結入力供給元となる。#194のD-032 draftは記録当時の表記で、後続PR #195で採択後、D-034により指定範囲を置換。#200 Stage 2／READMEのD-034草案・長さ未決は記録当時の状態。後続D-034／PR #201で採択、D-033の各200mmを維持し、約124mmは比較候補に留まる（[監査](issue-205-adr-audit.md)）。#141の旧WingモデルをRev.3の電源結果へ流用しない。

| 報告（版・段階は原題） | Issue / PR | 入力・最終・失敗の役割 |
| --- | --- | --- |
| [docs/issue-127-wing-parts-placement-review.md](issue-127-wing-parts-placement-review.md)<br>Issue #127 Stage 1 — Wing 部品寄せの見直し | [#127](https://github.com/ihsinoky/he-piantor-42/issues/127) / [#128](https://github.com/ihsinoky/he-piantor-42/pull/128) | Matrix Rev.1 pitch9 と代表21キー Wing Rev.1の設計入力・部品寄せ検討。 |
| [docs/issue-127-wing-design.md](issue-127-wing-design.md)<br>Issue #127 Stage 2 — Evaluation Wing 設計入力 | [#127](https://github.com/ihsinoky/he-piantor-42/issues/127) / [#128](https://github.com/ihsinoky/he-piantor-42/pull/128) | Matrix Rev.1 pitch9 と代表21キー Wing Rev.1の設計入力・部品寄せ検討。 |
| [docs/issue-129-wing-2layer-routing.md](issue-129-wing-2layer-routing.md)<br>Issue #129 — Wing 2層配線評価 | [#129](https://github.com/ihsinoky/he-piantor-42/issues/129) / [#130](https://github.com/ihsinoky/he-piantor-42/pull/130) | Matrix/Wing入力構築の等価性ゲート停止。配線未実行。 |
| [docs/issue-131-wing-condition-search.md](issue-131-wing-condition-search.md)<br>Issue #131 — Wing 自動配線の実現条件探索 | [#131](https://github.com/ihsinoky/he-piantor-42/issues/131) / [#132](https://github.com/ihsinoky/he-piantor-42/pull/132) | 16/17mm、2層0.10mm合格セルと失敗セル。D-021へ。 |
| [docs/issue-133-wing-cost-check.md](issue-133-wing-cost-check.md)<br>Issue #133 — Wing 合格条件（2層・0.10mm）の費用確認 | [#133](https://github.com/ihsinoky/he-piantor-42/issues/133) / [#134](https://github.com/ihsinoky/he-piantor-42/pull/134) | 当時の素基板・手はんだ前提の価格比較。Rev.3 PCBA見積へ流用しない。 |
| [docs/issue-138-wing-manufacturing-review-prep.md](issue-138-wing-manufacturing-review-prep.md)<br>Issue #138 — Wing 発注前製造レビュー準備 | [#138](https://github.com/ihsinoky/he-piantor-42/issues/138) / [#140](https://github.com/ihsinoky/he-piantor-42/pull/140) | Wing Rev.1の形状加算・電流／発熱検討。電源最低保証は未確定。 |
| [docs/issue-141-wing-power-integrity.md](issue-141-wing-power-integrity.md)<br>Issue #141 — Wing 電源インテグリティのフォローアップ | [#141](https://github.com/ihsinoky/he-piantor-42/issues/141) / [#142](https://github.com/ihsinoky/he-piantor-42/pull/142) | Wing Rev.1の電源/GND0.30mm化。旧電圧モデルの条件付き結果。 |
| [docs/issue-147-wing-order-prep.md](issue-147-wing-order-prep.md)<br>Issue #147 — Wing 素基板の発注準備 | [#147](https://github.com/ihsinoky/he-piantor-42/issues/147) / [#148](https://github.com/ihsinoky/he-piantor-42/pull/148) | Wing Rev.1、両ピッチのシルクなし製造候補。#149で置換。 |
| [docs/issue-149-wing-silkscreen.md](issue-149-wing-silkscreen.md)<br>Issue #149 — Wing シルク追加の改版 | [#149](https://github.com/ihsinoky/he-piantor-42/issues/149) / [#151](https://github.com/ihsinoky/he-piantor-42/pull/151) | Wing Rev.1 最終履歴 SILK-149A。両ピッチのシルク・CAM再検証。 |
| [docs/issue-158-vera-wing-stage1.md](issue-158-vera-wing-stage1.md)<br>Issue #158 — ver.A Wing 標準実装化 Stage 1：設計計画 | [#158](https://github.com/ihsinoky/he-piantor-42/issues/158) / [#161](https://github.com/ihsinoky/he-piantor-42/pull/161) | Wing Rev.2に向けた下面Hall・locator・左右一体パネルの計画入力。未配線。 |
| [docs/issue-190-wing-layout-stage1.md](issue-190-wing-layout-stage1.md)<br>Issue #190 — Wing 配列 Stage 1：Cantor 原典からの再導出 | [#190](https://github.com/ihsinoky/he-piantor-42/issues/190) / [#193](https://github.com/ihsinoky/he-piantor-42/pull/193) | Cantor由来21中心のStage 1検討。外形拡張・狭幅キャップは条件付き。 |
| [docs/issue-194-wing-rev2-stage2.md](issue-194-wing-rev2-stage2.md)<br>Issue #194 — Wing Rev.2 Stage 2 / Phase A・B | [#194](https://github.com/ihsinoky/he-piantor-42/issues/194) / [#195](https://github.com/ihsinoky/he-piantor-42/pull/195) | Wing Rev.2、配置案からPhase B最終4単板／2パネルまで。D-032。 |
| [docs/issue-200-wing-rev3-stage1.md](issue-200-wing-rev3-stage1.md)<br>Issue #200 Wing Rev.3 — Stage 1 形状の実現性検討 | [#200](https://github.com/ihsinoky/he-piantor-42/issues/200) / [#201](https://github.com/ihsinoky/he-piantor-42/pull/201) | 北タブ移設・南トリム形状案。基板未配線の入力検討。 |
| [docs/issue-200-wing-rev3-stage1b.md](issue-200-wing-rev3-stage1b.md)<br>Issue #200 Wing Rev.3 — Stage 1b 北側拡張の再考 | [#200](https://github.com/ihsinoky/he-piantor-42/issues/200) / [#201](https://github.com/ihsinoky/he-piantor-42/pull/201) | 北肩を広くし入隅R5へ。Stage 2に渡す確定形状入力。 |
| [docs/issue-200-wing-rev3-stage2.md](issue-200-wing-rev3-stage2.md)<br>Issue #200 Wing Rev.3 — Stage 2（レイアウト・再適格化・製造データ） | [#200](https://github.com/ihsinoky/he-piantor-42/issues/200) / [#201](https://github.com/ihsinoky/he-piantor-42/pull/201) | 現行最終4単板・2パネルとケース確定CSV。後続D-034／PR #201で採択、各200mm維持。 |

<a id="case"></a>

## ケース

初期 #150 Stage 1は旧Wingの治具提案、#188はMain Rev.3との照合。#198 Stage 1はWing Rev.2＋Main Rev.4＋UDBの基本形状と未解決ケーブル、Stage 2はWing Rev.3 Stage 1bの形状入力による詳細化（固定13点）、最終は #200の確定CSVへ入力更新（固定15点）。Stage 1（元コミット `6a596e23`）はStage 2とともに PR #202 でmainへ取り込まれ、最終は PR #203。最終17mmが正、16mmは同生成器で再生成・検証済み。組立STEPと印刷5ピースは[現行索引](artifacts-index.md)で選ぶ。

最終READMEの「南辺判断持ち越し」は記録当時の状態で、後続P3／PR #208でPO了解済みとして案内（[P3報告](issue-207-p3.md)）。印刷・保持力・クリープ等の物理評価は別ゲート。固定点や供給CSVを旧世代と混ぜない。

| 報告（版・段階は原題） | Issue / PR | 入力・最終・失敗の役割 |
| --- | --- | --- |
| [docs/issue-150-case-stage1.md](issue-150-case-stage1.md)<br>Issue #150 — 筐体設計 Stage 1：機械要件と基板インタフェース提案 | [#150](https://github.com/ihsinoky/he-piantor-42/issues/150) / [#152](https://github.com/ihsinoky/he-piantor-42/pull/152) | 初期ケース Stage 1。旧Wingの開放トレイ・治具方式提案、標準搭載未成立。 |
| [docs/issue-188-case-crosscheck.md](issue-188-case-crosscheck.md)<br>Issue #188 — Main Rev.3 発注前確認：筐体 Stage 1 データとの照合 | [#188](https://github.com/ihsinoky/he-piantor-42/issues/188) / [#191](https://github.com/ihsinoky/he-piantor-42/pull/191) | Main Rev.3と初期ケースの照合。機構の要注意／判定不能を含む。 |
| [docs/issue-198-case-stage1.md](issue-198-case-stage1.md)<br>Issue #198 一体型ケース — Stage 1 | [#198](https://github.com/ihsinoky/he-piantor-42/issues/198) / [#202](https://github.com/ihsinoky/he-piantor-42/pull/202) | Wing Rev.2入力の基本形状・分割案。GH実経路未解決。元commit 6a596e23。 |
| [docs/issue-198-case-stage2.md](issue-198-case-stage2.md)<br>Issue #198 ケース Stage 2 | [#198](https://github.com/ihsinoky/he-piantor-42/issues/198) / [#202](https://github.com/ihsinoky/he-piantor-42/pull/202) | Wing Rev.3 Stage 1b入力、固定13点の詳細モデル。最終CSV前の履歴出力。 |
| [docs/issue-198-case-final.md](issue-198-case-final.md)<br>Issue #198 ケース 最終データ | [#198](https://github.com/ihsinoky/he-piantor-42/issues/198) / [#203](https://github.com/ihsinoky/he-piantor-42/pull/203) | Wing Rev.3確定12CSV入力、固定15点。17mm正／16mm検証済みの現行最終。 |

<a id="method"></a>

## 手法履歴

[EDA経路史](eda-path-history.md)を出発点とする。tscircuitの永久凍結電気fixture（D-014）と物理配線不採用試行、JITXの電気graph parityと物理NO-GO（D-016）は役割が異なる。native KiCadのEDA-004EはPCB I/O限定合格、EDA-004Fは小回路図作成・電気検査の限定合格、EDA-004GはMain配線前DRC STOP。各世代のSTOPはその条件での記録として保持する。

#87→#89→#91/#93/#95→#97/#99→#101〜#115は固定条件の反証、#117→#119→#121は層数・線幅等の条件探索。#121の4層0.10mm合格がD-019／PR #126への根拠であり、2層0.20mm等の過去失敗を取り消さない。#124以降は[Main](#main)・[Matrix](#matrix)・[Wing](#wing)・[ケース](#case)に続く。#129/#131の2層探索はWing／Matrix対象に限定した後続履歴としてそちらに置く。

| 報告（版・段階は原題） | Issue / PR | 入力・最終・失敗の役割 |
| --- | --- | --- |
| [docs/issue-87-native-main-routing.md](issue-87-native-main-routing.md)<br>Issue #87 — fixed Main routing qualification | [#87](https://github.com/ihsinoky/he-piantor-42/issues/87) / [#88](https://github.com/ihsinoky/he-piantor-42/pull/88) | Main 入力DSN復旧と未完了・pass上限失敗。後続反証の固定入力。 |
| [docs/issue-89-freerouting-main-analysis.md](issue-89-freerouting-main-analysis.md)<br>Issue #89 — Freerouting Main 未完了の保存証拠分析 | [#89](https://github.com/ihsinoky/he-piantor-42/issues/89) / [#90](https://github.com/ihsinoky/he-piantor-42/pull/90) | Freerouting 未完了原因の分析・技術推奨。配線合格ではない。 |
| [docs/issue-91-freerouting-v250-reevaluation.md](issue-91-freerouting-v250-reevaluation.md)<br>Issue #91 — Freerouting v2.5.0 限定再評価 | [#91](https://github.com/ihsinoky/he-piantor-42/issues/91) / [#92](https://github.com/ihsinoky/he-piantor-42/pull/92) | v2.5.0 native CLI 評価の導入阻害記録。 |
| [docs/issue-93-freerouting-v250-jar-reevaluation.md](issue-93-freerouting-v250-jar-reevaluation.md)<br>Issue #93 — Freerouting v2.5.0 公式JAR限定再評価 | [#93](https://github.com/ihsinoky/he-piantor-42/issues/93) / [#94](https://github.com/ihsinoky/he-piantor-42/pull/94) | 公式JAR再評価。未完了の実行記録。 |
| [docs/issue-95-freerouting-v250-run2.md](issue-95-freerouting-v250-run2.md)<br>Issue #95 — Freerouting v2.5.0 Run 2 | [#95](https://github.com/ihsinoky/he-piantor-42/issues/95) / [#96](https://github.com/ihsinoky/he-piantor-42/pull/96) | fanout 有効でも38未配線、optimizer skip。固定条件の停止記録。 |
| [docs/issue-97-fastroute-falsification.md](issue-97-fastroute-falsification.md)<br>Issue #97 — fastroute 限定反証テスト | [#97](https://github.com/ihsinoky/he-piantor-42/issues/97) / [#98](https://github.com/ihsinoky/he-piantor-42/pull/98) | fastroute 既定条件。未配線と幅下限未達の失敗。 |
| [docs/issue-99-fastroute-width-floor.md](issue-99-fastroute-width-floor.md)<br>Issue #99 — fastroute 幅下限200µm強制の単一条件再テスト | [#99](https://github.com/ihsinoky/he-piantor-42/issues/99) / [#100](https://github.com/ihsinoky/he-piantor-42/pull/100) | 幅下限200µm再試験。幅は通過、37未配線で不合格。 |
| [docs/issue-101-freerouting-cpp-falsification.md](issue-101-freerouting-cpp-falsification.md)<br>Issue #101 — freeRouting.org C++版 v2.0.1 限定反証テスト | [#101](https://github.com/ihsinoky/he-piantor-42/issues/101) / [#102](https://github.com/ihsinoky/he-piantor-42/pull/102) | C++版スモーク SIGSEGV。Main未実行。 |
| [docs/issue-103-fab-router-falsification.md](issue-103-fab-router-falsification.md)<br>Issue #103 — fab_router の限定反証テスト | [#103](https://github.com/ihsinoky/he-piantor-42/issues/103) / [#104](https://github.com/ihsinoky/he-piantor-42/pull/104) | fab_router 既定条件、Main16未配線。 |
| [docs/issue-105-fab-router-detailed.md](issue-105-fab-router-detailed.md)<br>Issue #105 — fab_router 詳細ルーター有効の単一条件 | [#105](https://github.com/ihsinoky/he-piantor-42/issues/105) / [#106](https://github.com/ihsinoky/he-piantor-42/pull/106) | fab_router tiles、Main21未配線。中断・回復も保持。 |
| [docs/issue-107-topola-falsification.md](issue-107-topola-falsification.md)<br>Issue #107 — Topola の限定反証テスト | [#107](https://github.com/ihsinoky/he-piantor-42/issues/107) / [#108](https://github.com/ihsinoky/he-piantor-42/pull/108) | Topola スモーク未接続、Main未実行。 |
| [docs/issue-109-autoroute-falsification.md](issue-109-autoroute-falsification.md)<br>Issue #109 — AutoRoute の限定反証テスト | [#109](https://github.com/ihsinoky/he-piantor-42/issues/109) / [#111](https://github.com/ihsinoky/he-piantor-42/pull/111) | AutoRoute スモーク不合格。 |
| [docs/issue-110-freeroute-python-falsification.md](issue-110-freeroute-python-falsification.md)<br>Issue #110 — Python版 freeroute の限定反証テスト | [#110](https://github.com/ihsinoky/he-piantor-42/issues/110) / [#112](https://github.com/ihsinoky/he-piantor-42/pull/112) | Python freeroute の限定反証・スモーク停止。 |
| [docs/issue-113-kicad-routing-tools-falsification.md](issue-113-kicad-routing-tools-falsification.md)<br>Issue #113 — KiCad Routing Tools の限定反証テスト | [#113](https://github.com/ihsinoky/he-piantor-42/issues/113) / [#114](https://github.com/ihsinoky/he-piantor-42/pull/114) | KRT 既定条件の失敗・等価性ゲート限界。 |
| [docs/issue-115-kicad-routing-tools-escalation-off.md](issue-115-kicad-routing-tools-escalation-off.md)<br>Issue #115 — KRT escalation 無効の単一条件試験 | [#115](https://github.com/ihsinoky/he-piantor-42/issues/115) / [#116](https://github.com/ihsinoky/he-piantor-42/pull/116) | KRT escalation off、2層0.20mmで28未配線。 |
| [docs/issue-117-four-layer-main-and-wing-outlook.md](issue-117-four-layer-main-and-wing-outlook.md)<br>Issue #117 — 4層 Main 本試験と Wing 予備見通し（修正指示01） | [#117](https://github.com/ihsinoky/he-piantor-42/issues/117) / [#118](https://github.com/ihsinoky/he-piantor-42/pull/118) | 4層化検討。smoke通過、Main26/28未配線。 |
| [docs/issue-119-promising-tools-relaxed-conditions.md](issue-119-promising-tools-relaxed-conditions.md)<br>Issue #119 — 有望ツール × 4層・0.127mm（標準ビア） | [#119](https://github.com/ihsinoky/he-piantor-42/issues/119) / [#120](https://github.com/ihsinoky/he-piantor-42/pull/120) | 3ツール×4条件セル探索。4層0.127mmでも未完成。 |
| [docs/issue-121-full-auto-conditions.md](issue-121-full-auto-conditions.md)<br>Issue #121 — 完全自動配線を実現する条件の探索 | [#121](https://github.com/ihsinoky/he-piantor-42/issues/121) / [#122](https://github.com/ihsinoky/he-piantor-42/pull/122) | 4層0.10mm KRT/offで独立4指標0。入力・未実行セルを保持。D-019への根拠。 |

<a id="cross"></a>

## 横断・運用

[via監査 #183](issue-183-via-pad-audit.md)はMain／Wingに横断適用し、Matrixの当該版採択はD-029を参照する。[ADR](decisions.md)は判断、[Finding](findings.md)は観測知見、[既存教訓ノート](lessons-learned-device-development.md)は歴史的横断記録。D-031／PR #192の方式に従い、P4ではFinding追加やプロセス昇格を行わない。運用・初期センサ・firmware・共通ライブラリ・ライセンスの入口も後段の棚卸し表に含める。

| 報告（版・段階は原題） | Issue / PR | 入力・最終・失敗の役割 |
| --- | --- | --- |
| [docs/issue-183-via-pad-audit.md](issue-183-via-pad-audit.md)<br>Issue #183 — Main Rev.2／Wing Rev.1 の via–パッド重なり監査 | [#183](https://github.com/ihsinoky/he-piantor-42/issues/183) / [#184](https://github.com/ihsinoky/he-piantor-42/pull/184) | Main Rev.2／Wing Rev.1のvia-pad監査。不適合と後続改版への入力。 |
| [docs/issue-205-adr-audit.md](issue-205-adr-audit.md)<br>Issue #205 ADR 整合監査 | [#205](https://github.com/ihsinoky/he-piantor-42/issues/205) / [#206](https://github.com/ihsinoky/he-piantor-42/pull/206) | 全34 ADRの採択・適用範囲監査。記録当時と後続採択の根拠。 |
| [docs/issue-207-p3.md](issue-207-p3.md)<br>Issue #207 — 整理計画 P3 | [#207](https://github.com/ihsinoky/he-piantor-42/issues/207) / [#208](https://github.com/ihsinoky/he-piantor-42/pull/208) | P3現行案内・状態・マイルストーン用途変更の報告。 |

<a id="package-roles"></a>

## 現行パッケージ内の最終と工程

ディレクトリ全体を「最終」と扱わない。以下は保存済みREADMEに基づく選択規則。最終CADに付随するproject・ライブラリ・検証hashを一組で辿る。工程検査に合格した別候補から製造データを選ばない。

| パッケージ | 現行最終／製造への入口 | 入力・途中・失敗・工程検査（保存する履歴） |
| --- | --- | --- |
| [Matrix Rev.3 README](../hardware/kicad/qualification/issue-182-matrix-rev3/README.md) | [board/m1-matrix18.kicad_pcb](../hardware/kicad/qualification/issue-182-matrix-rev3/board/m1-matrix18.kicad_pcb) と同所project。[manufacturing](../hardware/kicad/qualification/issue-182-matrix-rev3/manufacturing/)はRev.3製造一式。[inspection/final](../hardware/kicad/qualification/issue-182-matrix-rev3/inspection/final/)は最終検査であってCAD選択元はboard。 | [cell-inputs](../hardware/kicad/qualification/issue-182-matrix-rev3/cell-inputs/)は入力、[runs](../hardware/kicad/qualification/issue-182-matrix-rev3/runs/)は候補／失敗を含む。[processes](../hardware/kicad/qualification/issue-182-matrix-rev3/processes/)はargv・時刻・stdout/stderr。[inspection](../hardware/kicad/qualification/issue-182-matrix-rev3/inspection/)のfinal以外は候補の受入結果。baseline／resume-stateは凍結入力・再開状態。 |
| [Main Rev.4 Phase B README](../hardware/kicad/qualification/issue-196-main-rev4-phaseb/README.md) | [inspection/final/main.kicad_pcb](../hardware/kicad/qualification/issue-196-main-rev4-phaseb/inspection/final/main.kicad_pcb) とproject、rootのRev4.pretty。[manufacturing](../hardware/kicad/qualification/issue-196-main-rev4-phaseb/manufacturing/)は最終CAM／BOM／CPL。schematicとrootのlogical-contract.jsonは回路契約。 | [runs](../hardware/kicad/qualification/issue-196-main-rev4-phaseb/runs/)・[processes](../hardware/kicad/qualification/issue-196-main-rev4-phaseb/processes/)はauto01〜04、power01、paste01等の入出力と実行履歴。[inspection](../hardware/kicad/qualification/issue-196-main-rev4-phaseb/inspection/)のfinal以外は工程別検査。[paste01](../hardware/kicad/qualification/issue-196-main-rev4-phaseb/inspection/paste01/)と最終がbyte一致でも役割は工程／最終で異なる。Phase A/A-2は配置入力で、製造入力ではない。 |
| [Wing Rev.3 README](../hardware/kicad/qualification/issue-200-wing-rev3/README.md) | `wing-rev3-16mm-left/`、`wing-rev3-16mm-right/`、`wing-rev3-17mm-left/`、`wing-rev3-17mm-right/`内の各 `main.kicad_pcb` とproject・qualification.json。[現行索引の4単板・2パネル](artifacts-index.md)に全件直接リンク。製造・実装は `panel-16mm/` と `panel-17mm/` の `main.kicad_pcb`／fabrication.zip／bom.csv／cpl.csv。 | 各単板の `input.kicad_pcb` は配置・外形契約、`routed.kicad_pcb` はルータ出力の途中状態。各単板の修復ログ／plane-repairs.jsonは過程。このパッケージに `processes/` ディレクトリはなく、入力・途中PCBと各修復記録を同じ単板ディレクトリ内で区別する。最終4基板は独立検査hashで識別し、単板CAMと左右一体Standard-PCBAパネルCAMを混用しない。 |

<a id="task-assets"></a>

## task資産：現行表示と履歴

| 実在資産 | 区分と確認根拠 |
| --- | --- |
| [task/index.html](../task/index.html)、[task/dashboard.js](../task/dashboard.js)、[task/style.css](../task/style.css)、[task/data/project-status.js](../task/data/project-status.js) | 現行表示資産。HTMLがCSSと2本のJSを読み込み、dashboard.jsはwindow.PROJECT_STATUSを使って8マイルストーンと現在位置を描画する。データ正本はdocs、表示は手動同期read model。 |
| [task/data/runtime-status.js](../task/data/runtime-status.js) | 履歴（旧表示用補助データ）。window.RUNTIME_STATUSを定義するが、現行HTMLでロードされず、現行JS/CSS/read modelからも参照されない。現行プロジェクト状態の正本や表示入力ではない。 |
| [task/screenshots/](../task/screenshots/) | 履歴（旧ダッシュボードの画面確認資料）。構成要素は [dashboard-1440.png](../task/screenshots/dashboard-1440.png)、[dashboard-320.png](../task/screenshots/dashboard-320.png)、[dashboard-320-details.png](../task/screenshots/dashboard-320-details.png)、[dashboard-320-text-200pct.png](../task/screenshots/dashboard-320-text-200pct.png)、[dashboard-390.png](../task/screenshots/dashboard-390.png)、[dashboard-390-text-200pct.png](../task/screenshots/dashboard-390-text-200pct.png) の6枚。現行HTML／JS／CSS／read modelに画像参照はない。現行画面の証明として流用しない。 |

確認はREADMEの宣言だけでなく、HTMLのscript/linkとJS/CSS・データの全文を読み、動的読込（fetch/import/画像生成/URL参照）がないことを照合した。[task規約](../task/README.md)のP3用途変更とも一致する。ファイルは変更・移動・削除しない。

<a id="inventory-a"></a>

## 付録A：全配置単位への入口

整理計画付録Aをパス単位で全列挙する。ディレクトリのリンクは配下全体への入口で、ファイルを選別・移動する指示ではない。対象・役割は系列節と併読し、現行パッケージは上の最終パス規則を優先する。付録Aの件数は計画時点の値なので、現チェックアウトの件数とは分ける。

| 配置単位（root基準） | 対象・系列 | 役割 |
| --- | --- | --- |
| [.github/](../.github/) | [横断・運用](#cross) | CI・Issue／PRテンプレート。運用資産、将来の知見昇格先。 |
| [.gitignore](../.gitignore) | [横断・運用](#cross) | 追跡・ランタイム除外の運用設定。 |
| [LICENSE.md](../LICENSE.md) | [横断・運用](#cross) | リポジトリのライセンス本文。履歴・現行の依存先を保持。 |
| [LICENSES/](../LICENSES/) | [横断・運用](#cross) | パス別の第三者ライセンス・権利通知。 |
| [README.md](../README.md) | [横断・運用](#cross) | 現行構成・成果物索引・状態へのroot案内。 |
| [firmware/](../firmware/) | [横断・運用](#cross) | センサ試験用C実装と説明。完成製品FWではない。 |
| [hardware/README.md](../hardware/README.md) | [横断・運用](#cross) | 現行ハードウェア構成・成果物の案内。 |
| [hardware/case/issue-150-stage1/](../hardware/case/issue-150-stage1/) | [ケース](#case) | 旧Wingの機構方式検討。 |
| [hardware/case/issue-188-crosscheck/](../hardware/case/issue-188-crosscheck/) | [ケース](#case) | Main Rev.3との照合証跡。 |
| [hardware/case/issue-194-layout/](../hardware/case/issue-194-layout/) | [Wing](#wing) | Wing Rev.2の形状・CSV入力履歴。 |
| [hardware/case/issue-194-rev2/](../hardware/case/issue-194-rev2/) | [Wing](#wing) | Wing Rev.2の形状・CSV入力履歴。 |
| [hardware/case/issue-198-final/](../hardware/case/issue-198-final/) | [ケース](#case) | Wing Rev.3確定CSVの凍結入力と固定15点の最終源・出力。17mm正／16mm検証版。 |
| [hardware/case/issue-198-stage1/](../hardware/case/issue-198-stage1/) | [ケース](#case) | Wing Rev.2入力のケース基本形状。GH実経路未解決の履歴出力。 |
| [hardware/case/issue-198-stage2/](../hardware/case/issue-198-stage2/) | [ケース](#case) | Wing Rev.3 Stage 1b形状入力、固定13点の詳細出力。 |
| [hardware/case/issue-200-rev3/](../hardware/case/issue-200-rev3/) | [Wing](#wing) | 配線済みWing Rev.3の確定12CSVと生成器。ケース凍結コピーの供給側正本。 |
| [hardware/case/issue-200-stage1/](../hardware/case/issue-200-stage1/) | [Wing](#wing) | Stage 1／1bのgeometry源・比較記録。確定CSVとケース最終の入力依存。 |
| [hardware/jitx/](../hardware/jitx/) | [手法履歴](#method) | JITX電気graph parity・geometry・物理NO-GO履歴と、後続Wing／Matrixの定義源を併存。採用範囲は各報告で確認。 |
| [hardware/kicad/qualification/eda-004e/](../hardware/kicad/qualification/eda-004e/) | [手法履歴](#method) | EDA-004E／PR #80。PCB I/O限定合格、frontend未資格の証跡。 |
| [hardware/kicad/qualification/eda-004f/](../hardware/kicad/qualification/eda-004f/) | [手法履歴](#method) | EDA-004F／PR #84。headless小回路図・電気検査の限定資格証跡。 |
| [hardware/kicad/qualification/eda-004g/](../hardware/kicad/qualification/eda-004g/) | [手法履歴](#method) | EDA-004G／PR #86。resumeを含むMain配線前物的DRC STOP、Main未資格。 |
| [hardware/kicad/qualification/issue-101-freerouting-cpp-falsification/](../hardware/kicad/qualification/issue-101-freerouting-cpp-falsification/) | [手法履歴](#method) | C++版スモーク SIGSEGV。Main未実行。 |
| [hardware/kicad/qualification/issue-103-fab-router-falsification/](../hardware/kicad/qualification/issue-103-fab-router-falsification/) | [手法履歴](#method) | fab_router 既定条件、Main16未配線。 |
| [hardware/kicad/qualification/issue-105-fab-router-detailed/](../hardware/kicad/qualification/issue-105-fab-router-detailed/) | [手法履歴](#method) | fab_router tiles、Main21未配線。中断・回復も保持。 |
| [hardware/kicad/qualification/issue-107-topola-falsification/](../hardware/kicad/qualification/issue-107-topola-falsification/) | [手法履歴](#method) | Topola スモーク未接続、Main未実行。 |
| [hardware/kicad/qualification/issue-109-autoroute-falsification/](../hardware/kicad/qualification/issue-109-autoroute-falsification/) | [手法履歴](#method) | AutoRoute スモーク不合格。 |
| [hardware/kicad/qualification/issue-110-freeroute-python-falsification/](../hardware/kicad/qualification/issue-110-freeroute-python-falsification/) | [手法履歴](#method) | Python freeroute の限定反証・スモーク停止。 |
| [hardware/kicad/qualification/issue-113-kicad-routing-tools-falsification/](../hardware/kicad/qualification/issue-113-kicad-routing-tools-falsification/) | [手法履歴](#method) | KRT 既定条件の失敗・等価性ゲート限界。 |
| [hardware/kicad/qualification/issue-115-kicad-routing-tools-escalation-off/](../hardware/kicad/qualification/issue-115-kicad-routing-tools-escalation-off/) | [手法履歴](#method) | KRT escalation off、2層0.20mmで28未配線。 |
| [hardware/kicad/qualification/issue-117-four-layer-main/](../hardware/kicad/qualification/issue-117-four-layer-main/) | [手法履歴](#method) | 4層化検討。smoke通過、Main26/28未配線。 |
| [hardware/kicad/qualification/issue-119-promising-tools-relaxed/](../hardware/kicad/qualification/issue-119-promising-tools-relaxed/) | [手法履歴](#method) | 3ツール×4条件セル探索。4層0.127mmでも未完成。 |
| [hardware/kicad/qualification/issue-121-full-auto-conditions/](../hardware/kicad/qualification/issue-121-full-auto-conditions/) | [手法履歴](#method) | 4層0.10mm KRT/offで独立4指標0。入力・未実行セルを保持。D-019への根拠。 |
| [hardware/kicad/qualification/issue-124-main-bom-pcba/](../hardware/kicad/qualification/issue-124-main-bom-pcba/) | [Main](#main) | 単Wing Main Rev.1のBOM／PCBA条件付き見積。未確定費目を含む履歴。 |
| [hardware/kicad/qualification/issue-129-wing-2layer-routing/](../hardware/kicad/qualification/issue-129-wing-2layer-routing/) | [Wing](#wing) | Matrix/Wing入力構築の等価性ゲート停止。配線未実行。 |
| [hardware/kicad/qualification/issue-131-wing-condition-search/](../hardware/kicad/qualification/issue-131-wing-condition-search/) | [Wing](#wing) | 16/17mm、2層0.10mm合格セルと失敗セル。D-021へ。 |
| [hardware/kicad/qualification/issue-133-wing-cost-check/](../hardware/kicad/qualification/issue-133-wing-cost-check/) | [Wing](#wing) | 当時の素基板・手はんだ前提の価格比較。Rev.3 PCBA見積へ流用しない。 |
| [hardware/kicad/qualification/issue-137-main-manufacturing-review-prep/](../hardware/kicad/qualification/issue-137-main-manufacturing-review-prep/) | [Main](#main) | Main Rev.1 のvia／J1工程検討。後続 D-022 の採択根拠。 |
| [hardware/kicad/qualification/issue-138-wing-manufacturing-review-prep/](../hardware/kicad/qualification/issue-138-wing-manufacturing-review-prep/) | [Wing](#wing) | Wing Rev.1の形状加算・電流／発熱検討。電源最低保証は未確定。 |
| [hardware/kicad/qualification/issue-141-wing-power-integrity/](../hardware/kicad/qualification/issue-141-wing-power-integrity/) | [Wing](#wing) | Wing Rev.1の電源/GND0.30mm化。旧電圧モデルの条件付き結果。 |
| [hardware/kicad/qualification/issue-147-wing-order-prep/](../hardware/kicad/qualification/issue-147-wing-order-prep/) | [Wing](#wing) | Wing Rev.1、両ピッチのシルクなし製造候補。#149で置換。 |
| [hardware/kicad/qualification/issue-149-wing-silkscreen/](../hardware/kicad/qualification/issue-149-wing-silkscreen/) | [Wing](#wing) | Wing Rev.1 最終履歴 SILK-149A。両ピッチのシルク・CAM再検証。 |
| [hardware/kicad/qualification/issue-153-main-mounting-stage1/](../hardware/kicad/qualification/issue-153-main-mounting-stage1/) | [Main](#main) | Main Rev.1取付穴 Stage 1の入力案。 |
| [hardware/kicad/qualification/issue-155-main-mounting-stage2/](../hardware/kicad/qualification/issue-155-main-mounting-stage2/) | [Main](#main) | Main Rev.1取付穴 Stage 2。局所退避失敗、全体再配線合格、旧最終。 |
| [hardware/kicad/qualification/issue-157-main-dual-wing-stage1/](../hardware/kicad/qualification/issue-157-main-dual-wing-stage1/) | [Main](#main) | Main Rev.2（2Wing）Stage 1の電気・配置提案。機構／電源ゲート未成立。 |
| [hardware/kicad/qualification/issue-158-vera-wing-stage1/](../hardware/kicad/qualification/issue-158-vera-wing-stage1/) | [Wing](#wing) | Wing Rev.2に向けた下面Hall・locator・左右一体パネルの計画入力。未配線。 |
| [hardware/kicad/qualification/issue-160-main-dual-wing-stage2/](../hardware/kicad/qualification/issue-160-main-dual-wing-stage2/) | [Main](#main) | Main Rev.2案Aの機構ゲート停止。D-024、案Cへ。 |
| [hardware/kicad/qualification/issue-163-main-dual-wing-plan-c/](../hardware/kicad/qualification/issue-163-main-dual-wing-plan-c/) | [Main](#main) | 案C採用 D-025、機構具体化後も停止。新板配線未実施。 |
| [hardware/kicad/qualification/issue-165-dual-wing-power-study/](../hardware/kicad/qualification/issue-165-dual-wing-power-study/) | [Main](#main) | Main 2Wing電源4方式の比較入力。D-026の5.2V案へ。 |
| [hardware/kicad/qualification/issue-167-main-dual-wing-stage2/](../hardware/kicad/qualification/issue-167-main-dual-wing-stage2/) | [Main](#main) | D-027入力境界の再定義。候補・resumeの配線は不合格。旧要件の停止証跡も保持。 |
| [hardware/kicad/qualification/issue-169-main-dual-wing-followup/](../hardware/kicad/qualification/issue-169-main-dual-wing-followup/) | [Main](#main) | Main Rev.2継続。seed-a合格後、部品更新した2回目は不合格。 |
| [hardware/kicad/qualification/issue-173-main-dual-wing-final/](../hardware/kicad/qualification/issue-173-main-dual-wing-final/) | [Main](#main) | Main Rev.2の1210候補はpreflight停止。fallback seed-aは別の合格履歴。 |
| [hardware/kicad/qualification/issue-175-main-dual-wing-final2/](../hardware/kicad/qualification/issue-175-main-dual-wing-final2/) | [Main](#main) | Main Rev.2最終履歴。1210出力C、44ネット・4指標0。見積／製造GOは別。 |
| [hardware/kicad/qualification/issue-178-m1-matrix-board/](../hardware/kicad/qualification/issue-178-m1-matrix-board/) | [Matrix](#matrix) | Matrix Rev.2最終履歴。両ピッチ18キーの一枚基板、D-028。Rev.1を置換。 |
| [hardware/kicad/qualification/issue-182-matrix-rev3/](../hardware/kicad/qualification/issue-182-matrix-rev3/) | [Matrix](#matrix) | Matrix Rev.3現行。158via非重複、D-029で当該版のみPOFV不要。 |
| [hardware/kicad/qualification/issue-183-via-pad-audit/](../hardware/kicad/qualification/issue-183-via-pad-audit/) | [横断・運用](#cross) | Main Rev.2／Wing Rev.1のvia-pad監査。不適合と後続改版への入力。 |
| [hardware/kicad/qualification/issue-185-main-rev3/](../hardware/kicad/qualification/issue-185-main-rev3/) | [Main](#main) | Main Rev.3旧最終。35via移設、POFV撤回はD-030提案（採択未確認）。 |
| [hardware/kicad/qualification/issue-194-wing-rev2/](../hardware/kicad/qualification/issue-194-wing-rev2/) | [Wing](#wing) | Wing Rev.2、配置案からPhase B最終4単板／2パネルまで。D-032。 |
| [hardware/kicad/qualification/issue-196-main-rev4-phasea2/](../hardware/kicad/qualification/issue-196-main-rev4-phasea2/) | [Main](#main) | Phase A-2の三角形・UDB分離配置入力。配線済み最終ではない。 |
| [hardware/kicad/qualification/issue-196-main-rev4-phaseb/](../hardware/kicad/qualification/issue-196-main-rev4-phaseb/) | [Main](#main) | 現行最終と工程履歴が併存。上のpackage役割表でfinal／runs等を区別。 |
| [hardware/kicad/qualification/issue-196-main-rev4/](../hardware/kicad/qualification/issue-196-main-rev4/) | [Main](#main) | Phase A旧配置・面取り案。後続A-2／Phase Bへの履歴入力。 |
| [hardware/kicad/qualification/issue-200-wing-rev3/](../hardware/kicad/qualification/issue-200-wing-rev3/) | [Wing](#wing) | Wing Rev.3 Stage 1→1b形状入力→Stage 2最終4単板／2パネル・確定CSV。D-034。 |
| [hardware/kicad/qualification/issue-87-native-main-routing/](../hardware/kicad/qualification/issue-87-native-main-routing/) | [手法履歴](#method) | Main 入力DSN復旧と未完了・pass上限失敗。後続反証の固定入力。 |
| [hardware/kicad/qualification/issue-91-freerouting-v250/](../hardware/kicad/qualification/issue-91-freerouting-v250/) | [手法履歴](#method) | v2.5.0 native CLI 評価の導入阻害記録。 |
| [hardware/kicad/qualification/issue-93-freerouting-v250-jar/](../hardware/kicad/qualification/issue-93-freerouting-v250-jar/) | [手法履歴](#method) | 公式JAR再評価。未完了の実行記録。 |
| [hardware/kicad/qualification/issue-95-freerouting-v250-run2/](../hardware/kicad/qualification/issue-95-freerouting-v250-run2/) | [手法履歴](#method) | fanout 有効でも38未配線、optimizer skip。固定条件の停止記録。 |
| [hardware/kicad/qualification/issue-97-fastroute-falsification/](../hardware/kicad/qualification/issue-97-fastroute-falsification/) | [手法履歴](#method) | fastroute 既定条件。未配線と幅下限未達の失敗。 |
| [hardware/kicad/qualification/issue-99-fastroute-width-floor/](../hardware/kicad/qualification/issue-99-fastroute-width-floor/) | [手法履歴](#method) | 幅下限200µm再試験。幅は通過、37未配線で不合格。 |
| [hardware/layout/](../hardware/layout/) | [横断・運用](#cross) | 旧レイアウト生成源・CSV・SVG。現行Wing／ケース寸法の正本ではない。 |
| [hardware/lib/](../hardware/lib/) | [横断・運用](#cross) | 共通・第三者資産。通知・出典・依存関係を保持。 |
| [hardware/main/](../hardware/main/) | [横断・運用](#cross) | Main現行版への案内。CADの格納先ではない。 |
| [hardware/rev-m1/](../hardware/rev-m1/) | [横断・運用](#cross) | 旧Rev.M1名のアーキテクチャ・インタフェース・ゲート記録。名前を維持。 |
| [hardware/sensor-test/](../hardware/sensor-test/) | [横断・運用](#cross) | 初期Hall評価回路・部品表・native設計。現行Matrixの代用品ではない。 |
| [hardware/tscircuit/](../hardware/tscircuit/) | [手法履歴](#method) | D-014永久凍結電気fixtureと後続の物理配線不採用試行・ツール。能力一般の否定に広げない。 |
| [manufacturing/README.md](../manufacturing/README.md) | [横断・運用](#cross) | 製造正本への現行案内。製造データ本体は各パッケージ内。 |
| [mechanical/README.md](../mechanical/README.md) | [横断・運用](#cross) | ケース最終源・出力への現行案内。ケースデータ本体はhardware/case内。 |
| [task/](../task/) | [横断・運用](#cross) | 現行表示4ファイル＋規約READMEと、未参照runtime／screenshots履歴。上のtask資産表で区分。 |

<a id="inventory-b"></a>

## 付録B：補助文書と横断参照

付録BのIssue報告は上の対象別表で全件を直接リンクした。残る文書は以下。現行規約・状態文書は現行として参照し、技術背景・手法評価の結論は記録時点の範囲で読む。計画時点後の追加文書も末尾に明示する。

| 文書（root基準） | 位置づけ |
| --- | --- |
| [docs/alternate-physical-backend-converter-repair.md](alternate-physical-backend-converter-repair.md) | EDA-004D／PR #78。footprint library identityで変換修復停止。 |
| [docs/alternate-physical-backend-main-qualification-issue-draft.md](alternate-physical-backend-main-qualification-issue-draft.md) | 代表Main資格試験のIssue草案・計画入力。実行結果ではない。 |
| [docs/alternate-physical-backend-main-qualification.md](alternate-physical-backend-main-qualification.md) | EDA-004B／PR #74。executor smoke捕捉失敗の部分証跡・訂正された時系列。 |
| [docs/alternate-physical-backend-qualification-plan.md](alternate-physical-backend-qualification-plan.md) | EDA-004A／PR #72、D-018の条件付き資格計画。候補採用やMain実装承認ではない。 |
| [docs/alternate-physical-backend-smoke-requalification.md](alternate-physical-backend-smoke-requalification.md) | EDA-004C／PR #76。duplicate GND handoffでCONVERSION_BLOCKED。 |
| [docs/decisions.md](decisions.md) | 現行の判断・要件・運用・状態参照。過去節は記録時点の履歴。 |
| [docs/development-workflow.md](development-workflow.md) | 現行の判断・要件・運用・状態参照。過去節は記録時点の履歴。 |
| [docs/eda-path-history.md](eda-path-history.md) | tscircuit→JITX→native KiCad／ルータ探索の経路史。D-019の条件採択までを横断。 |
| [docs/governance.md](governance.md) | 現行の判断・要件・運用・状態参照。過去節は記録時点の履歴。 |
| [docs/hall-acquisition.md](hall-acquisition.md) | Hall取得方式の設計背景。試験意図と現在の押下推定方式確定を区別。 |
| [docs/headless-schematic-qualification.md](headless-schematic-qualification.md) | EDA-004F／PR #84。小回路図・ERC等の限定合格。Main配線の合格ではない。 |
| [docs/jitx-evaluation.md](jitx-evaluation.md) | EDA-002の電気parityと物理評価系列。D-016で物理経路NO-GO、電気成功は保持。 |
| [docs/layout-geometry.md](layout-geometry.md) | 旧配置座標・変換の設計根拠。現行Wing／ケース寸法は成果物索引を参照。 |
| [docs/lessons-learned-device-development.md](lessons-learned-device-development.md) | Issue #170／PR #171の既存横断ノート。新規記録方式はD-031へ。 |
| [docs/native-kicad-authoring-feasibility.md](native-kicad-authoring-feasibility.md) | EDA-004E／PR #80。native PCB I/O合格、frontend未資格。 |
| [docs/native-main-routing-qualification.md](native-main-routing-qualification.md) | EDA-004G／PR #86。fresh Mainの配線前DRC STOPとresume記録。 |
| [docs/project-status.md](project-status.md) | 現行の判断・要件・運用・状態参照。過去節は記録時点の履歴。 |
| [docs/public-release-readiness.md](public-release-readiness.md) | 現行の判断・要件・運用・状態参照。過去節は記録時点の履歴。 |
| [docs/specification.md](specification.md) | 現行の判断・要件・運用・状態参照。過去節は記録時点の履歴。 |
| [docs/tscircuit-clearance-intervention-ab.md](tscircuit-clearance-intervention-ab.md) | EDA-003F／PR #70。介入でwrong-net回帰、INTERVENTION_UNSAFE_REGRESSION。 |
| [docs/tscircuit-kicad-importer-requalification.md](tscircuit-kicad-importer-requalification.md) | EDA-003A／PR #59。importer不一致とupstream fix候補、電気源と物理出力を分離。 |
| [docs/tscircuit-latest-routing-risk-qualification.md](tscircuit-latest-routing-risk-qualification.md) | EDA-003C／PR #64。wrong-net解消後も物的リスク残存、production更新なし。 |
| [docs/tscircuit-main-clearance-risk-triage.md](tscircuit-main-clearance-risk-triage.md) | EDA-003D／PR #66。clearanceの分散リスク分類、修復未実証。 |
| [docs/tscircuit-native-spike-report.md](tscircuit-native-spike-report.md) | Issue #19のnative spike。初期電気fixture／後続凍結源に至る入力評価。 |
| [docs/tscircuit-revm1-routing-proof.md](tscircuit-revm1-routing-proof.md) | EDA-003B／PR #62。代表配線はwrong-net接触等でBLOCKED。 |
| [docs/tscircuit-via-clearance-signature-probe.md](tscircuit-via-clearance-signature-probe.md) | EDA-003E／PR #68。via-clearance数値signature、修復範囲未資格。 |

計画後の追加入口：[docs/artifacts-index.md](artifacts-index.md) · [docs/findings.md](findings.md) · [docs/publication-discussion.md](publication-discussion.md) · [docs/repo-cleanup-plan.md](repo-cleanup-plan.md) · [docs/work-layer-discussion.md](work-layer-discussion.md)。

付録Aの計画後追加：[hardware/case/issue-190-layout/](../hardware/case/issue-190-layout/)（#190／PR #193、Wing配列検討）。検証方法・被覆結果・元データ不変の確認は [P4作業報告](issue-209-p4.md)。
