# Issue #137 指示書：Main 製造前レビュー準備

- 発行：PMO（2026-11-05）。PO の Codex 回復・GO 指示と PMO-GO 権限委譲に基づく
- ワーカー：Codex
- タイムボックス：**2時間**

## 目的

D-019 で「Undecided order specifications」として残った2件について、PO が発注仕様を決めるための判断材料（選択肢・費用影響・推奨案）を用意する。決定はしない。発注・課金は行わない。

## 対象1：via-in-pad / paste opening（25箇所）

- 出発点：`docs/issue-121-full-auto-conditions.md` と、その証跡（`hardware/kicad/qualification/issue-121-full-auto-conditions/`）にある KRT の via-in-pad／paste opening 自己検出25箇所の structured log
- 実配線済み基板（#121 の合格出力）と突き合わせて内訳を分類する：
  - ビアが部品パッド上に実際に乗っている箇所（部品参照・座標・ネット）
  - ペースト開口（F.Paste）との重なり等の、その他の箇所
- JLCPCB の一次情報（公式の製造能力ページ、追加料金ページ、via の扱いに関する公式ヘルプ）で確認する：
  - filled via／capped via の工程の有無と指定方法、費用影響（追加料金の規定）
  - 指定なしで発注した場合に製造側でどう扱われるか（DFM 審査で差し戻し・確認が発生するか）
- 選択肢表を作る：(a) 現状のまま、(b) filled／capped 指定、(c) 設計側回避（この場合は #121 の合格配線を作り直すことになり再評価が要る旨を明記）。各選択肢に費用・リスク・手間と、PMO への推奨案を付ける

## 対象2：USB J1 の PTH 固定脚

- 前提：J1 は SMD 信号パッド＋PTH 固定脚×4＋NPTH×2（#124 報告書で確認済み）。Main の PCBA 見積もり（#124）は片面 SMD 実装前提
- JLCPCB の一次情報（PCBA の公式ページ・ヘルプ）で確認する：
  - スルーホール部品／PTH 脚を持つ部品を同一 PCBA 発注で実装できるか、工程（手はんだ工程の有無等）と追加料金の規定
  - Economic PCBA と Standard PCBA での扱いの差
- 選択肢表を作る：(a) PCBA で一括実装、(b) J1 の脚のみ受領後に手はんだ（信号パッドは PCBA 実装済みの前提で、脚だけの後付けが工程として成立するかも含めて検討）、(c) その他現実的な案。各選択肢に費用・現実性と推奨案を付ける

## 制約・成果物

- 一次情報は取得記録（URL・取得時刻・該当箇所）として証跡に残す。取得できない項目は推測で埋めず未取得と明記する
- 報告書：`docs/issue-137-main-manufacturing-review-prep.md`（新規追加のみ）
- 証跡：`hardware/kicad/qualification/issue-137-main-manufacturing-review-prep/`
- 作業ブランチ `issue-137-main-manufacturing-review-prep` から Draft PR を作成する（push できない場合はコミット済みの状態で報告。PMO がホスト側から push する）。merge は禁止
- 既存ファイルの変更は禁止（追加のみ）
- 一時ランタイムは作業ディレクトリ内の `.issue137-runtime/` に置く（/tmp は 512MB しかない）
