# リポジトリ整理・ナレッジ整理 実行計画案

作成日：2026-11-08。対象：origin/main = `8ef9efb2feac52cf7158d3e559b4dbd73cf880af`（PR #203 まで）。本書は計画であり、設計変更・再生成・発注・マージの許可ではない。今回の変更は本書の追加だけとする。

## 1. 調査範囲と判断の前提

このチェックアウトの追跡対象14,920ファイルを `git ls-files` で抽出し、分類単位の実在、最新成果物の具体的なファイル、各 README・報告書との対応を確認した。全既存追跡ファイルの SHA-256 を作業用に保存した。棚卸しは付録A・Bで追跡対象全体を覆い、最新成果物は2節でファイルまで絞る。ディレクトリの件数は配下の追跡ファイル数で、部分列挙を全数と誤認しないために示す。未追跡の作業領域は棚卸しの件数に含めない。

根拠は `docs/decisions.md`、`docs/project-status.md`、各成果物の README と対応する Issue 報告書、Git履歴である。2026-11-08 に GitHub CLI で [PR #192](https://github.com/ihsinoky/he-piantor-42/pull/192) を読み取り確認した結果は OPEN / Draft / 未マージ、head は `findings-ledger`、`627fdcf83391a112a74f8a367b5e52a3bd0a8794`。ローカルの同コミットから D-031 と F-001 の全文も確認した。外部状態は実行開始時に再確認する。

「最終」は現時点の設計・検証パッケージの正本を意味する。製造GO、量産ピッチの決定、実機合格は別である。過去の不合格試行、凍結入力、独立検査コードも設計根拠として保存する。ディレクトリ名に Issue 番号があっても不要物とは判定しない。

## 2. 最新成果物の正の場所（実在確認済み）

以下のパスはすべてリポジトリroot基準。略号はこの節で定義する実在ディレクトリへの参照であり、別の保存先ではない。

| 対象 | 正本ディレクトリ | 設計・製造の入口と根拠 |
| --- | --- | --- |
| Main Rev.4（M） | `hardware/kicad/qualification/issue-196-main-rev4-phaseb/` | 同ディレクトリの README、`docs/issue-196-main-rev4-phaseb.md`、D-033。Phase A/A-2 は入力・設計履歴 |
| Matrix Rev.3（X） | `hardware/kicad/qualification/issue-182-matrix-rev3/` | 同 README、`docs/issue-182-matrix-rev3.md`、D-029。18キー・16/17mm混載評価基板で、製品 Wing と別物 |
| Wing Rev.3（W） | `hardware/kicad/qualification/issue-200-wing-rev3/` | 同 README、`docs/issue-200-wing-rev3-stage2.md`、D-034。16/17mm×左右4基板と2パネル |
| Wing→ケースの確定インタフェース | `hardware/case/issue-200-rev3/` | 同 README と生成器、outline/holes/keys の12 CSV。ケース形状そのものではない |
| ケース最終（C） | `hardware/case/issue-198-final/` | 同 README、`docs/issue-198-case-final.md`。17mm版が正、16mm版は再生成・検証済み。固定点15、GH200mm |

### 2.1 Main Rev.4

- 基板：`hardware/kicad/qualification/issue-196-main-rev4-phaseb/inspection/final/main.kicad_pcb`。同所の `main.kicad_pro`、`fp-lib-table`、`Rev4.pretty/` と組にする。
- 回路源：`hardware/kicad/qualification/issue-196-main-rev4-phaseb/schematic/`（native回路図・XML・論理契約）。
- 製造：`hardware/kicad/qualification/issue-196-main-rev4-phaseb/manufacturing/`。`main-rev4-fabrication-review.zip`、`BOM.csv`、`CPL.csv`、`gerber/`、`paste/`。ZIPだけで実装データ一式とは扱わない。
- 引継ぎ：`hardware/kicad/qualification/issue-196-main-rev4-phaseb/manufacturing/quote-handoff.md`。検証：同証跡rootの `verification.json`、`export-provenance.json`、`cam-check.json`、`inspection/final/assessment.json`。
- D-033 は Accepted。再見積、BOM調達、業者受入れ、USB・電源・実組立評価は別ゲート。旧Mainの見積や旧Wing抵抗モデルを新パッケージに流用しない。

### 2.2 Matrix Rev.3

- 基板：`hardware/kicad/qualification/issue-182-matrix-rev3/board/m1-matrix18.kicad_pcb`。同所の `m1-matrix18.kicad_pro`、`fp-lib-table` を保持する。旧命名が残るが、ファイル名だけで版を判定しない。
- 製造：`hardware/kicad/qualification/issue-182-matrix-rev3/manufacturing/`。`FABRICATION.md`、`m1-matrix18-gerber-review.zip`、`BOM.csv`、`CPL.csv`、Gerber/drill/paste、組立図、`manufacturing-check.json`。
- 検証：`hardware/kicad/qualification/issue-182-matrix-rev3/verification.json`、`manifest.json`、`inspection/final/assessment.json`。158 via、最小パッド銅間隔約0.10746mm。Rev.3パッケージのPOFV不要という判断を旧版に遡及しない。

### 2.3 Wing Rev.3

単板の正本は次の4ディレクトリ内の `main.kicad_pcb` と対応 `main.kicad_pro`。同所の `qualification.json` が基板hashと検査を結ぶ。`input.kicad_pcb` は入力契約、`routed.kicad_pcb` は途中結果であり、製造入力に選ばない。

- `hardware/kicad/qualification/issue-200-wing-rev3/wing-rev3-16mm-left/`
- `hardware/kicad/qualification/issue-200-wing-rev3/wing-rev3-16mm-right/`
- `hardware/kicad/qualification/issue-200-wing-rev3/wing-rev3-17mm-left/`
- `hardware/kicad/qualification/issue-200-wing-rev3/wing-rev3-17mm-right/`

製造・実装の正本は次の左右一体パネル。各所に `main.kicad_pcb`、`main.kicad_pro`、`fabrication.zip`、`bom.csv`、`cpl.csv`、`pin1.csv`、`cam-manifest.json`、`drc.json` がある。両面実装の Standard PCBA 前提と、左右を分離する工程を案内に残す。

- `hardware/kicad/qualification/issue-200-wing-rev3/panel-16mm/`
- `hardware/kicad/qualification/issue-200-wing-rev3/panel-17mm/`

ケースへ渡す CSV の正本は `hardware/case/issue-200-rev3/`。例えば `holes-17mm-left.csv`、`outline-17mm-left.csv`、`keys-17mm-left.csv` が実在する。16/17mm・左右を欠かさず一覧化する。D-034 本文は Accepted・200mm維持だが、見出しと Stage 2 報告・README には draft/未決が残る。原記録を消さず最新状態への案内で解決する。

### 2.4 ケース最終

- パラメトリック源：`hardware/case/issue-198-final/generate.py`、`base.py`、`details.py`、`requirements.txt`、`verify.py`。
- 凍結入力：`hardware/case/issue-198-final/inputs/rev3-final/` の12 CSV と `hardware/case/issue-198-final/inputs/wing-rev3-geometry.json`。参照元は Wing 確定CSVと `hardware/case/issue-200-stage1/geometry.json`。
- 出力：`hardware/case/issue-198-final/17mm/` と `hardware/case/issue-198-final/16mm/`。各所の `assembly.step`、左右トレー・連結板2点・ラックの STEP/STL、`harness.step`、`storage-200mm.step`、`dimensions.json`、`exports-sha256.json`、`verification.json`、`review.svg`。
- 例えば印刷用は `hardware/case/issue-198-final/17mm/tray-left.stl`。組立STEPと印刷5ピースを分けて案内する。南辺フラッシュの最終判断、保持力・クリープ・足位置・実ハーネスの物理評価は未了。17mm版が正であることは量産ピッチ確定を意味しない。

## 3. それ以外の棚卸しと扱い

### 3.1 設計履歴・検討記録

`docs/` は82ファイル、うち Issue 別報告は付録Bに実パスで全列挙する。Main単Wing→2 Wing→Rev.3→Rev.4、Matrix Rev.1→Rev.2→Rev.3、Wing Rev.1→Rev.2→Rev.3、ケース Stage 1→Stage 2→最終という系列を索引で結ぶ。Issue #87〜#121 の反証・条件探索は手法履歴、#124以降のBOM・製造・電源・機構は対象基板ごとの履歴として横断参照する。

`hardware/kicad/qualification/` の12,204ファイルは付録Aの各実在単位で分類する。最新パッケージ内にも `runs/`・`processes/`・途中の `inspection/` が含まれる。現行成果物と設計履歴は「ディレクトリ単位で完全分離されている」と仮定せず、最終パスを指定する索引で区別する。検査プログラム、manifest、入力hash、失敗ログを含む証跡一式は保存する。

### 3.2 旧世代・実験系

- `hardware/sensor-test/`：初期Hall評価回路・部品表・native設計。現行Matrixの代用品ではない。
- `hardware/rev-m1/`：旧名称のアーキテクチャ、インタフェース、ゲート根拠。履歴名を一括置換しない。
- `hardware/jitx/`：JITX源、geometry/parity、physical、wing、テスト。物理経路NO-GOの検証記録であり、ライブラリ等も含む。一般的なツール能力の否定に広げない。
- `hardware/tscircuit/`：native四キーfixture、spikes、qualification、スクリプトとlock。D-014の永久凍結電気源と、その後の不採用物理試行を区別して保存する。まとめて「不要な旧ツール」としない。
- `hardware/layout/`：旧レイアウト生成源・CSV・SVG。最新Wing/ケース寸法の正本と取り違えない。
- 旧Main・Matrix・Wing・ケースは付録Aの履歴区分。最新から外れていても再現入力や原価・採用判断の根拠として残す。

### 3.3 その他・重複・スクラッチ相当・所属不明

| 実在対象 | 現状・扱い |
| --- | --- |
| `manufacturing/README.md`、`mechanical/README.md` | 将来配置を説明するプレースホルダ。現時点で製造/ケース正本を収容していない。最新実パスへの案内へ更新する候補 |
| `hardware/main/README.md`、`hardware/README.md` | 一体42キー基板など旧説明が残る。現行モジュール構成への案内を直す候補 |
| `hardware/lib/`、`LICENSE.md`、`LICENSES/` | 共通・第三者資産と権利関係。整理時にも通知・パス別ライセンス・出典を保持 |
| `firmware/` | センサ試験用C実装と説明。完成した製品Vialファームウェアと表示しない |
| `task/` | ダッシュボード、データ、スクリーンショット。`task/data/project-status.js` は docs の手動同期read model。正本は docs |
| `.github/`、`.gitignore` | テンプレート、CI、除外規則。移動時の参照影響調査対象 |
| `hardware/case/issue-198-final/inputs/rev3-final/` と `hardware/case/issue-200-rev3/` | 12 CSVは全数バイト一致を確認。消せる重複ではなく、再現用凍結コピーと供給側正本 |
| `hardware/case/issue-198-final/17mm/cable-rack.stl` と `hardware/case/issue-198-stage2/17mm/cable-rack.stl` | SHA-256一致。ピースが同じでも入力・検証世代が違うため一式を統合しない |
| `hardware/kicad/qualification/issue-196-main-rev4-phaseb/inspection/paste01/` と同 `inspection/final/` | READMEに最終byte一致の記載。工程段階と最終受入れの役割差がある。削除可とは判定しない |

追跡対象に対して、証拠なく削除できるスクラッチや所有者不明ファイルは今回確定していない。raw、process、失敗試行、スナップショットを一律スクラッチ扱いしない。未追跡の `.cleanup-runtime/` は指示書・gitローカルクローン・調査用スクラッチで、本PRの成果物ではない。今回これを削除・コミットしない。実行時に他の未追跡領域を見つけた場合も追跡対象と分離し、担当者確認前に触らない。

## 4. 目標状態と配置案

### 4.1 推奨：現在のパスを保持し、案内と索引を整える

rootの `README.md` から「最新設計・製造データ」一覧へ1回で到達し、そこから対象基板・版・ピッチ・左右別の正本へ直接進める状態にする。新設案は **`docs/artifacts-index.md`（未作成）** と **`docs/history-index.md`（未作成）**。棚卸しで実在確認したパスとは別の、将来の追加先である。

成果物索引は対象、版、用途、CAD/回路源、製造ZIPとBOM/CPL、ケース出力、検証結果/hash、採択D番号、未了ゲート、置換元を列に持つ。索引自身はナビゲーションであり設計データの新しい正本ではない。M/X/W/Cの現行パスを唯一の参照先とし、最新という名前でファイルを複製したり、可変symlinkを作ったりしない。CSV供給側と凍結入力の役割を明記する。

履歴索引は基板別の版・Issue・PR・入力/最終/失敗の役割を示す。既存報告の結論は書き換えず、必要なら索引側に「記録当時の状態」と「後続採択」を併記する。README、hardware案内、manufacturing/mechanical案内、project-status と相互リンクする。

根拠：最新データと独立証跡は相対パス・hardcodeされたroot・hash manifestで強く結びつく。14,920ファイルの大規模移動より、数個の索引と案内の変更で最終位置を明確にする方が、再現性を保った小さなPRになる。

### 4.2 代替：物理再配置（PO判断・別途詳細化）

新設する基板別のdesign領域とarchive領域へ実体を分ける案もあるが、今回は推奨しない。移動を選ぶ場合、最終基板だけを抜き出さず、参照ライブラリ・入力・検査器・manifest・ライセンスも依存単位として調べる。移動元→移動先対応表、参照元一覧、旧URL案内、再現手順の修正範囲を先に別PRでレビューする。移動先パスはその時点のPO判断と依存調査後に確定する。

実施手段は `git mv` と通常コミット。履歴書換え、filter-repo、force push、過去コミットの削除は使わない。移動と内容修正を別コミットにし、rename検出と旧コミット参照を確認する。バイナリ/凍結入力は移動前後hash一致、manifestがパスを含む場合は元manifestを保持して新しい配置との対応を別記録にする。旧raw証跡の絶対パスを改変して「当時の実行」としてしまわない。

### 4.3 削除は独立判断

現時点の削除推奨対象は **なし**。3.3節の一致データも役割があるので保存する。将来削除候補が生じたら「対象実パスとhash」「不要とする理由」「参照/再現/法務への影響」「代替保存先・復旧元コミット」を別表にし、保持・移動・削除の選択をPOに求める。POが削除を承認した対象だけを専用PRにする。履歴に残ることだけを削除の理由にしない。

## 5. ナレッジ整理の段取り

### 5.1 PR #192 を最初に取り込む

1. PMOが最新のPR状態・差分・headを再確認。D-031は2026-11-07採用済み方針、main上にないのは実装の未取り込みとして扱う。ADR、Finding、教訓のプロセス/skill昇格という3形式を再発明しない。
2. PR #192は現mainより前のD-030末尾にD-031を追加するため、後続D-032〜D-034との末尾追加競合を見込む。別の作業環境で解消し、既存D本文を保持して番号順にD-031を挿入する。取り込み手段は通常のブランチ更新・squash mergeで、現行成果物を巻き戻さない。
3. **PO判断：PR #192のDraft解除・マージ**。レビューでは変更を D-031 と `docs/findings.md` の追加に限定し、F-001をそのまま保持する。今回の計画PRにこれらを先取り実装しない。
4. mainへの取り込み確認後に遡及Findingを追加する。もし実行前に#192がマージ済みなら重ねてcherry-pickせず、マージ済み本文を基準にする。

`docs/findings.md` は現mainには存在せず、PR #192で追加予定のファイルである（棚卸しの実在パスには含めていない）。

F-001は「2026-11-06時点のJLCPCB 27Ω/0603 Basic代替なし」の既登録知見として扱い、登録候補から除外する。現在の在庫や分類への一般化・再調査は本計画に含めない。

### 5.2 遡及Finding候補（採番は取り込み後）

以下は登録済み事実の追加実装ではなく候補リスト。K番号は本計画内の整理番号で、F番号ではない。各候補を原証跡までたどり、結論、確信度・試行数、正確な版/commit/条件/日付、失敗試行、適用範囲・無効化条件・再検証トリガー、証拠リンク、Promoted toを埋める。分からない試行数や版は推測せず、調査未了として登録を保留する。

| 候補 | 実証知見と原典（実在） | 登録時の範囲・注意 |
| --- | --- | --- |
| K01 | KiCad importerはkeepoutを失い角丸半径も不一致：`docs/tscircuit-kicad-importer-requalification.md`、`hardware/tscircuit/spikes/eda-003a/evidence/` | importer 0.0.117/0.0.142、固定footprint条件に限定。将来版への能力断定をしない |
| K02 | 固定環境でのJITX物理配線NO-GO：`docs/jitx-evaluation.md`、`hardware/jitx/physical/`、D-016 | 電気graph parityの成功と物理配線未達を分ける。NO-GOはADR、観測と条件だけFindingへ |
| K03 | KRTのexit0と独立合格は異なる。offでもproject設定追加が起きた：`docs/issue-113-kicad-routing-tools-falsification.md`、`docs/issue-115-kicad-routing-tools-escalation-off.md` | v0.23.8、固定2層0.20mm条件。#115は未配線28件・全4指標null。別条件での後続合格も明記 |
| K04 | 配線幅/層数と引き出し混雑の関係：`docs/issue-103-fab-router-falsification.md`、`docs/issue-117-four-layer-main-and-wing-outlook.md`、`docs/issue-121-full-auto-conditions.md` | 対象形状・固定配置・ツールごとに条件表を作る。全ツールが同条件で不可能との一般化をしない |
| K05 | 電源/GND 0.30mm化と信号0.10mm分離の効果：`docs/issue-138-wing-manufacturing-review-prep.md`、`docs/issue-141-wing-power-integrity.md` | 16/17mm各1回合格、ただし最悪電圧未達条件あり。旧Wingモデルであり新Rev.3実測値ではない |
| K06 | keepout対象の意味と全層予約・量子化：`docs/issue-129-wing-2layer-routing.md`、`docs/issue-131-wing-condition-search.md`、`docs/issue-155-main-mounting-stage2.md` | NPTH自体のpads禁止と銅禁止を区別。#155は4nm外接補正、閾値緩和で解決したと記さない |
| K07 | 局所退避が保持配線を壊し得る：`docs/issue-155-main-mounting-stage2.md`、`docs/issue-167-main-dual-wing-stage2.md` | #155局所差分68→範囲固定の全体再配線合格。局所修正一般の禁止にはしない |
| K08 | 比較境界を保証要件へ転記したため停止：`docs/issue-165-dual-wing-power-study.md`、`docs/issue-167-main-dual-wing-stage2.md`、D-027 | 入力位置・電圧・設計負荷/ストレスを記録。D-027の採用判断自体はADRに残す |
| K09 | 同ネットvia–padも製造監査が必要：`docs/issue-183-via-pad-audit.md`、`docs/issue-182-matrix-rev3.md`、`docs/issue-185-main-rev3.md` | annulus外周から測定。全via・全padの対象数と名目寸法の限界を記す。POFV不要を業者保証と同一視しない |
| K10 | 製造方式・面付けで見積前提が変わる：`docs/issue-133-wing-cost-check.md`、`docs/issue-147-wing-order-prep.md`、`docs/issue-194-wing-rev2-stage2.md` | 当時の日付・枚数・版・片/両面・費目で固定。旧裸基板価格をRev.3 Standard PCBAへ流用しない |
| K11 | 新基板の実銅抵抗抽出で旧Wing電圧予算が変わった：`docs/issue-196-main-rev4-phaseb.md`、`docs/issue-200-wing-rev3-stage2.md` | 127mA、200mm、Main Rev.4＋Wing Rev.3。4.9429V等はモデル値。125°C感度をGH動作温度認定にしない |
| K12 | ケース入力更新時は固定点集合まで照合が必要：`docs/issue-198-case-stage2.md`、`docs/issue-198-case-final.md`、`hardware/case/issue-198-final/verify.py` | Stage 2の13点→最終15点。17/16mm、入力hash・ボス・下穴開口・穴逆変換まで。実造形保持力は未評価 |

優先順位はK03/K08/K09/K12（再作業・誤発注防止）、次にK05/K06/K07/K11（設計検証）、最後にK01/K02/K04/K10（手法履歴・見積）。1PRの候補を原則4件以内にし、条件が混ざるものは小さいFindingへ分ける。F-001との重複と新しいmain上の番号競合を毎回確認する。

### 5.3 ADRのD-001〜D-034整合確認

- 見出しのIDを抽出し、現mainはD-001〜D-030とD-032〜D-034の33件、重複見出しなし、欠番はD-031だけであることを再確認する。#192取り込み後は34件・欠番/重複0を合格条件にする。本文中の参照やD-021 Amendmentを新IDと誤カウントしない。既存番号を振り直さない。
- D-030は「pending PO review / merge」のままなのに実装はPR #187で履歴にある。報告受領と方針採択を分け、POの明示根拠を確認して状態注記を提案する。マージ済みという事実だけで製造GOへ昇格しない。
- D-032はDraft表記、D-033はAccepted、D-034は見出しdraft・本文Accepted。D-032が歴史的草案のまま置換されたのか採択済みだったのか、#195/#201のPO根拠を確認する。D-034の見出しとリンクアンカーの修正案をPOレビューに出す。
- D-017の100mmをD-033がMain Rev.4に限って200mmへ置換し、D-034がそれを保持する関係を表にする。D-022のPOFV/J1方針→D-029 Matrix限定→D-030 Main Rev.3→D-033分離UDBの適用範囲を分ける。D-012の2層→D-019 Main4層、D-021 Wing2層も同様。
- D-024→D-025→D-026→D-027、D-023→D-033、D-032→D-034の部分置換を追跡。電気契約・機構・入力境界を一括supersedeしない。D-002のピッチ再開、D-011/D-014の測定意図と永久fixtureも保持。
- 各IDに状態、決定日、対象/適用範囲、PO根拠、後継ID、関連成果物、相互リンクのチェック欄を設ける。確定本文は書換えず訂正・後続注記で示す。状態注記やアンカーを直す必要があれば旧リンクの維持方法も併記し、**PO判断**を経る。根拠が不足する採択状態は未確認とする。

### 5.4 教訓の昇格

`docs/lessons-learned-device-development.md` は既存の横断ノートとして保存し、新しい教訓台帳は増設しない。D-031採用後は新知見をFindingへ記録し、手戻り防止策を判断が必要なプロセス定義、またはエージェントが実行するskillへ昇格する。既存ノートには記録時点と現行方式への案内を追加する候補を出す。古いPOFV推奨や「ケース未着手」等を現状説明に転用しない。

具体的な昇格候補はK03/K07/K09→検証手順の独立判定・保持差分・全via監査、K08→Issueテンプレートの測定境界/設計負荷/ストレス欄、K12→基板–ケース引継ぎのCSV/hash/固定点集合照合。まず `docs/development-workflow.md`、`.github/ISSUE_TEMPLATE/engineering-work.md`、`.github/pull_request_template.md` の既存プロセスへ必要最小限の手順を組み込む案をレビューする。skill化は反復性・入出力・環境前提を定義できる場合に別途提案し、FindingのPromoted toに採用先と版を記す。今回はskillや手順を実装しない。

### 5.5 project-status最新化とread model同期

`docs/project-status.md` には版表へ最新行が追記された一方、Current situationは2026-10-14のIssue #87の未完状態、Workstreamsも過去のEDA停止を現行と記している。Main Rev.2のCurrent表記、Wing Rev.3 proposed/draft・長さ未決・ケース未着手も現行D-033/D-034と#203に整合させる必要がある。

最新節をMain Rev.4／Matrix Rev.3／Wing Rev.3／ケース最終に置き換える計画とし、旧EDA停止は当時の範囲・日付付き履歴として保存する。製品開発の現在位置、技術検証の結果、未実測事項、次の責任者/着手条件を分ける。200mm、ケース15点、17mm正/16mm検証済み、別UDB、再見積や物理評価待ちを反映する。G1/G2等の完了を計画書作成者が推定しない。

同じPRで `task/data/project-status.js` を手動同期する（既存workflowの要件）。`task/README.md` のread model規約を守り、docsを正とする。root READMEのJITXゲート未解決等も旧状態があれば訂正する。履歴の技術的STOPを消したり「現行基板合格だから旧手法も合格」に変えたりしない。物理未検証・量産ピッチ・BOM・DFM/発注・南辺仕様の残件とPOゲートが明記されれば合格とする。

### 5.6 ダッシュボード（task/）の用途変更 — PO決定（2026-11-08）

`task/` の Project Dashboard は Issue #87/#88 時点で更新が止まっており、表示内容は当時の未完状態のまま置き去りになっている。設計上は `docs/project-status.md` の手動同期 read model（正は docs 側）だが、その同期自体が止まっている。

PO 判断（2026-11-08）：詳細な状態管理は PMO（コマ）が担っているため、状態の写しとしてのダッシュボードの必要性は大きく下がっている。存続・廃止ではなく**用途変更**とし、ダッシュボードは「マイルストーン計画と、それに対する現在位置」を大局的に見るためのビューにする。

- 新しい役割：プロジェクトのマイルストーン（計画）と現在位置（完了／進行中／次のゲート）を一画面で示す。詳細ステータスの複写はしない
- マイルストーンの一覧そのものは P3 で PMO が提案し、P3 の PO ゲートで確認する（例：各基板のベースライン確定、発注1、Matrix 実測とピッチ決定、Wing 発注、組立、FW 検証といった粒度を想定するが、確定は P3）
- データの正は従来どおり docs 側（project-status 等）とし、ダッシュボードはその大局ビューの read model とする。P3 の合格条件には「ダッシュボードを実際に開いて、マイルストーンと現在位置が現行状態と一致することの確認」を含める
- `task/data/runtime-status.js` と `task/screenshots/` は棚卸し対象とし、現行の表示資産か履歴かを履歴索引（P4）で区分する

## 6. 実行フェーズ（各行おおむね1PR）

今回の計画PR（P0）を先にレビューし、実行Issueは以下の依存順でPMOが分割する。全PRは既存workflowどおりPMOレビュー→PO承認→squash merge。pushはPMOが行う。承認の対象を曖昧にしたまま次の設計・削除へ進まない。

| フェーズ・依存 | 作業範囲 | 合格条件 | POゲート |
| --- | --- | --- | --- |
| P0 本計画 | 本書の追加のみ | 要件1〜4、実在パス、現行正本、候補と実績の区別、変更1ファイルを確認 | 本計画のマージと索引方式の採否 |
| P1 P0後：既存PR #192 | main差分を確認しD-031/F-001を保ったまま競合解消 | D-031とfindings追加以外の既存記録・成果物不変、F-001一度だけ、34IDの集合が揃う | #192のDraft解除・採択済み方式の実装マージ |
| P2 P1後：ADR整合 | 5.3節の全34件一覧・状態/置換関係監査、根拠付き注記 | 欠番/重複0、対象範囲とPO根拠が追跡可能、未確認をAcceptedにしない、リンク維持 | D-030/D-032等の未確認状態、D-034表記調整の判断・マージ |
| P3 P2後：最新案内・状態 | 成果物索引とroot/hardware/main/manufacturing/mechanical案内、project-statusとtaskデータ同期 | README→索引→4対象の正本を辿れる、4 Wing/2 panel/2 case版網羅、ローカルリンク存在、旧状態と現行の衝突なし、CAD/CAM不変。ダッシュボードは既存画面の最新状態を表示 | 正本一覧・残件・ゲートの確認とマージ。製造承認とは分離 |
| P4 P3後：履歴索引 | docs Issue群・EDA史・旧版・証跡を対象別/世代別で案内 | 付録A/B全分類に入口あり、最終と途中の選択が明示、元報告・証跡hash不変 | 履歴区分のレビュー・マージ |
| P5a P1/P2後：Finding優先群 | K03/K08/K09/K12を原証跡照合して登録 | 各必須欄・失敗試行・適用限界・根拠あり、F-001重複なし、新規番号衝突なし | 観測と判断の分離をレビュー・マージ |
| P5b P5a後：設計検証群 | K05/K06/K07/K11 | 同上。旧版のモデルとRev.3抽出を混同しない | Findingレビュー・マージ |
| P5c P5b後：履歴・見積群 | K01/K02/K04/K10 | 同上。正確な環境・試行数未確認は保留、価格は当時条件付き | Findingレビュー・マージ |
| P6 P3/P5a後：プロセス昇格 | 5.4節の手順/テンプレート、既存ノートへの案内、Promoted toを更新 | 各手順が具体的Findingへ遡れ、適用条件・入力・検査・停止条件・責任者を記載。新しい教訓台帳を増やさない | プロセス変更の採否・マージ。skill化は必要なら独立PR |
| P7 任意・P4後：配置変更の事前調査 | POが物理再配置を選んだ場合のみ、移動対応表・依存/権利/リンク/再現影響を作成 | 対象実パスと移動先案、影響、旧URL対策、検証手順が具体化。ここでは移動しない | 調査案のマージ、物理移動を実行するかのPO判断 |
| P8 任意・P7承認後 | 承認済み依存単位1つずつの移動（基板ごとに別PR） | git mv、移動前後hash、リンク/CI/対象の再現検査、manifest対応、ライセンス、ロールバック手順。内容修正は別コミット | 各移動PRのマージ |
| P9 任意・削除候補が具体化した後 | 削除候補表だけを先にレビューし、承認対象のみ削除専用PR | 対象・理由・非参照証拠・再現への影響・復旧元が揃い、無承認削除0 | 削除判断→対象限定PRのマージ。現時点では対象なし |

P3は案内と状態を同時に直して相互矛盾を残さない文書中心のPRとする。過大になる場合は成果物索引と状態同期を2PRへ分割するが、それぞれのマージ時点で案内先が存在し、task同期は状態更新PRと同時に行う。P5各群は条件調査が大きければ1候補/PRまで小さくする。今回の計画がマージされても、実行Issueの範囲とPOゲートを省略しない。

### 6.1 検証と戻し方

文書・索引PRでは追跡ファイルのパス/リンク存在、D/F採番、相互参照、版・左右・ピッチの網羅、差分スコープを検査する。状態PRはdocsとtaskを照合し既存ダッシュボードを確認する。実データに触れない段階ではCAD再生成を行わず、既存の検証結果とhashとの対応を確認する。

移動を実施する場合だけ、依存調査で特定したCI・生成/検査手順を隔離出力で走らせる。全生成でUUIDが変わるものは完全byte再現を要求せず、保存源の不変と意味的検査を分けて記録する。元証跡を上書きしない。参照・hash・独立検査のいずれかが崩れればマージを止め、対象を保持する。マージ後の問題は通常のrevert PRで戻し、過去コミットを書き換えない。

### 6.2 PO判断事項の一覧

| 判断 | 推奨・未決 | 判断時点 |
| --- | --- | --- |
| 目標配置 | 既存パス保持＋索引を推奨。物理移動は任意 | P0 |
| PR #192 | 方針採用済み。競合解消後に実装を取り込む | P1 |
| ADR状態 | D-030/D-032の採択根拠・D-034のdraft表記等を監査し、根拠が不足すれば未確認を保持 | P2 |
| 最新成果物・開発状態 | 正本一覧と残件を確認。G1/G2・製造GOを自動で完了扱いしない | P3 |
| ダッシュボードの用途変更 | 決定済み（2026-11-08 PO）：状態の写しではなくマイルストーン計画＋現在位置の大局ビューにする。5.6節。マイルストーン一覧は P3 で提案・確認 | P3 |
| 知見/手順の採用 | 原典と適用範囲をレビュー。skillの新設は必要性を別判断 | P5/P6 |
| 削除 | 今回候補なし。対象と理由が揃った時だけ個別判断 | P9 |
| 製品設計の残件 | 南辺フラッシュ、量産ピッチ、実ハーネス/保持力、調達・再見積・業者DFM・発注等は整理と別の設計/製造判断 | 既存/別途承認Issue。整理PRのマージで代替しない |

## 付録A. 追跡対象全体の配置棚卸し

以下は今回の基準commitで実在確認した分類単位。ディレクトリは再帰的に含む。最新パッケージ内の細分類は2節の最終パスと3節の証跡規約を優先する。件数は本書追加前のもの。

| 実在パス | 件数 | 分類・処置案 |
| --- | ---: | --- |
| `.github/` | 4 | CIと運用テンプレート。参照影響確認・昇格先候補 |
| `.gitignore` | 1 | 追跡・運用設定。保持 |
| `LICENSE.md` | 1 | 権利定義/ライセンス本文。保持 |
| `LICENSES/` | 3 | 権利定義/ライセンス本文。保持 |
| `README.md` | 1 | root入口。最新成果物と状態への案内を更新候補 |
| `firmware/` | 4 | 試験用firmwareと説明。製品完成版とは区別して保持 |
| `hardware/README.md` | 1 | 旧説明/配置予定の案内。最新実パスへ更新候補 |
| `hardware/case/issue-150-stage1/` | 19 | 旧形状・旧ケース/レイアウトの検討記録と出力。履歴保存 |
| `hardware/case/issue-188-crosscheck/` | 6 | 旧形状・旧ケース/レイアウトの検討記録と出力。履歴保存 |
| `hardware/case/issue-194-layout/` | 41 | 旧形状・旧ケース/レイアウトの検討記録と出力。履歴保存 |
| `hardware/case/issue-194-rev2/` | 14 | 旧形状・旧ケース/レイアウトの検討記録と出力。履歴保存 |
| `hardware/case/issue-198-final/` | 53 | ケース最終源/出力/凍結入力/検証。17mm正・16mm検証済み |
| `hardware/case/issue-198-stage1/` | 28 | 旧形状・旧ケース/レイアウトの検討記録と出力。履歴保存 |
| `hardware/case/issue-198-stage2/` | 55 | 旧形状・旧ケース/レイアウトの検討記録と出力。履歴保存 |
| `hardware/case/issue-200-rev3/` | 14 | 最新Wingのケース向け確定CSV/生成器 |
| `hardware/case/issue-200-stage1/` | 14 | 採択形状geometry源とStage 1検討記録。最新CSVの入力依存 |
| `hardware/jitx/` | 205 | 旧/実験JITXの源・parity/geometry/物理評価。履歴保存 |
| `hardware/kicad/qualification/eda-004e/` | 132 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/eda-004f/` | 1,005 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/eda-004g/` | 1,479 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-101-freerouting-cpp-falsification/` | 71 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-103-fab-router-falsification/` | 125 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-105-fab-router-detailed/` | 147 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-107-topola-falsification/` | 87 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-109-autoroute-falsification/` | 92 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-110-freeroute-python-falsification/` | 113 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-113-kicad-routing-tools-falsification/` | 154 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-115-kicad-routing-tools-escalation-off/` | 149 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-117-four-layer-main/` | 582 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-119-promising-tools-relaxed/` | 747 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-121-full-auto-conditions/` | 282 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-124-main-bom-pcba/` | 5 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-129-wing-2layer-routing/` | 422 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-131-wing-condition-search/` | 201 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-133-wing-cost-check/` | 17 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-137-main-manufacturing-review-prep/` | 17 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-138-wing-manufacturing-review-prep/` | 42 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-141-wing-power-integrity/` | 184 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-147-wing-order-prep/` | 144 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-149-wing-silkscreen/` | 186 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-153-main-mounting-stage1/` | 21 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-155-main-mounting-stage2/` | 400 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-157-main-dual-wing-stage1/` | 31 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-158-vera-wing-stage1/` | 20 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-160-main-dual-wing-stage2/` | 25 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-163-main-dual-wing-plan-c/` | 42 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-165-dual-wing-power-study/` | 39 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-167-main-dual-wing-stage2/` | 406 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-169-main-dual-wing-followup/` | 701 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-173-main-dual-wing-final/` | 258 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-175-main-dual-wing-final2/` | 356 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-178-m1-matrix-board/` | 312 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-182-matrix-rev3/` | 523 | 最新設計・製造パッケージと入力/検証履歴を併存。2節の最終パスを正本として案内 |
| `hardware/kicad/qualification/issue-183-via-pad-audit/` | 64 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-185-main-rev3/` | 225 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-194-wing-rev2/` | 287 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-196-main-rev4-phasea2/` | 19 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-196-main-rev4-phaseb/` | 399 | 最新設計・製造パッケージと入力/検証履歴を併存。2節の最終パスを正本として案内 |
| `hardware/kicad/qualification/issue-196-main-rev4/` | 6 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-200-wing-rev3/` | 256 | 最新設計・製造パッケージと入力/検証履歴を併存。2節の最終パスを正本として案内 |
| `hardware/kicad/qualification/issue-87-native-main-routing/` | 1,131 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-91-freerouting-v250/` | 33 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-93-freerouting-v250-jar/` | 57 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-95-freerouting-v250-run2/` | 32 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-97-fastroute-falsification/` | 87 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/kicad/qualification/issue-99-fastroute-width-floor/` | 91 | 設計履歴・検討/反証・旧版証跡。保持して履歴索引へ |
| `hardware/layout/` | 4 | 旧配置生成源とデータ。現行正本と区別 |
| `hardware/lib/` | 12 | 共通/第三者資産、通知・出典。依存と権利を保持 |
| `hardware/main/` | 1 | 旧説明/配置予定の案内。最新実パスへ更新候補 |
| `hardware/rev-m1/` | 5 | 旧名のarchitecture/interface/ゲート根拠。履歴保存 |
| `hardware/sensor-test/` | 21 | 旧Hall試験基板・回路・BOM・評価計画。履歴保存 |
| `hardware/tscircuit/` | 2,113 | 永久凍結電気fixture・実験/資格証跡・ツール。役割を区別して保持 |
| `manufacturing/README.md` | 1 | 旧説明/配置予定の案内。最新実パスへ更新候補 |
| `mechanical/README.md` | 1 | 旧説明/配置予定の案内。最新実パスへ更新候補 |
| `task/` | 12 | ダッシュボードとread model、画面確認資料。状態更新時同期 |

上表はdocs以外の14,838ファイルを重複なく分類する。次の付録Bがdocsの82ファイルを覆い、合計14,920となる。未分類の追跡パスは0。所属判定の保留（削除可否未確認）は、分類済み証跡に対して別に扱う。

## 付録B. docsの実在パス一覧

区分は移動指示ではない。報告・検討記録を全部残したうえで、現行の案内/規約と歴史的記録を索引上で分ける。

| 実在パス | 区分 |
| --- | --- |
| `docs/alternate-physical-backend-converter-repair.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/alternate-physical-backend-main-qualification-issue-draft.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/alternate-physical-backend-main-qualification.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/alternate-physical-backend-qualification-plan.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/alternate-physical-backend-smoke-requalification.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/decisions.md` | 方針・要件・状態・運用の現行参照文書（状態監査対象） |
| `docs/development-workflow.md` | 方針・要件・状態・運用の現行参照文書（状態監査対象） |
| `docs/eda-path-history.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/governance.md` | 方針・要件・状態・運用の現行参照文書（状態監査対象） |
| `docs/hall-acquisition.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/headless-schematic-qualification.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/issue-101-freerouting-cpp-falsification.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-103-fab-router-falsification.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-105-fab-router-detailed.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-107-topola-falsification.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-109-autoroute-falsification.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-110-freeroute-python-falsification.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-113-kicad-routing-tools-falsification.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-115-kicad-routing-tools-escalation-off.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-117-four-layer-main-and-wing-outlook.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-119-promising-tools-relaxed-conditions.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-121-full-auto-conditions.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-124-main-bom-pcba-estimate.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-127-wing-design.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-127-wing-parts-placement-review.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-129-wing-2layer-routing.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-131-wing-condition-search.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-133-wing-cost-check.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-137-main-manufacturing-review-prep.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-138-wing-manufacturing-review-prep.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-141-wing-power-integrity.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-147-wing-order-prep.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-149-wing-silkscreen.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-150-case-stage1.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-153-main-mounting-stage1.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-155-main-mounting-stage2.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-157-main-dual-wing-stage1.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-158-vera-wing-stage1.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-160-main-dual-wing-stage2.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-163-main-dual-wing-plan-c.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-165-dual-wing-power-study.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-167-main-dual-wing-stage2.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-169-main-dual-wing-followup.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-173-main-dual-wing-final.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-175-main-dual-wing-final2.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-178-m1-matrix-board.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-182-matrix-rev3.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-183-via-pad-audit.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-185-main-rev3.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-188-case-crosscheck.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-194-wing-rev2-stage2.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-196-main-rev4-phasea2.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-196-main-rev4-phaseb.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-196-main-rev4.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-198-case-final.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-198-case-stage1.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-198-case-stage2.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-200-wing-rev3-stage1.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-200-wing-rev3-stage1b.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-200-wing-rev3-stage2.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-87-native-main-routing.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-89-freerouting-main-analysis.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-91-freerouting-v250-reevaluation.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-93-freerouting-v250-jar-reevaluation.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-95-freerouting-v250-run2.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-97-fastroute-falsification.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/issue-99-fastroute-width-floor.md` | Issue単位の設計・検討・検証報告（最終成果物へのリンクも保持） |
| `docs/jitx-evaluation.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/layout-geometry.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/lessons-learned-device-development.md` | 既存横断ノート。歴史保存しD-031方式へ案内 |
| `docs/native-kicad-authoring-feasibility.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/native-main-routing-qualification.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/project-status.md` | 方針・要件・状態・運用の現行参照文書（状態監査対象） |
| `docs/public-release-readiness.md` | 方針・要件・状態・運用の現行参照文書（状態監査対象） |
| `docs/specification.md` | 方針・要件・状態・運用の現行参照文書（状態監査対象） |
| `docs/tscircuit-clearance-intervention-ab.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/tscircuit-kicad-importer-requalification.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/tscircuit-latest-routing-risk-qualification.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/tscircuit-main-clearance-risk-triage.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/tscircuit-native-spike-report.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/tscircuit-revm1-routing-proof.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |
| `docs/tscircuit-via-clearance-signature-probe.md` | 技術背景・手法評価・設計履歴。対象と時点を索引で案内 |

## 今回の提出・完了条件

- 指示書全文を読み、本書に棚卸し、目標案、ナレッジ整理、PR別作業/合格条件/POゲートを含める。
- 棚卸しのパスは基準commitの追跡一覧と実ファイルに照合する。将来の追加先は未作成と明記する。
- 既存追跡14,920ファイルを開始時hashと照合し、不変であることを確認する。CAD・証跡・既存文書は今回移動/削除/改変しない。
- このチェックアウトをwork-treeとして使用し、git状態はローカルクローン `.cleanup-runtime/git` の `.git` に置く。本書だけを `repo-cleanup-plan` にコミットする。通常のチェックアウトのgit状態へはコミットしない。
- 作業用データは `.cleanup-runtime/` 内に置き、コミット対象から除く。push、PR作成、マージ、実行フェーズへの着手はせず、コミット後に停止する。
