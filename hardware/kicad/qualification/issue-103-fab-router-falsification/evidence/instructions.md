# Issue #103 指示書：fab_router の限定反証テスト

- 発行：PMO（2026-11-04）。PO 承認済み（「PR #102 を merge して C++版線を閉じ、次は fab_router を Issue 化して」）
- ワーカー：Codex
- タイムボックス：**Bun 導入・ドライバ作成・実行・独立検査・記録すべて含めて2時間**
- 検討メモ：`~/workspace/goals/he-piantor-42-keyboard-pmo/files/auto-routing-candidates-2026-11-04.md` §2（共通骨格）・§3.2（fab_router 差分）

## 目的

fab_router（格子非依存探索＋押しのけ＋引き直し。Freerouting と機構が異なる）を同一 DSN・固定条件で反証テストする。あわせて、開発元自前の checkDrc による判定と KiCad 独立検査の一致（自己判定の妥当性）を検証する。開発元は高密度基板での局所探索の限界を自己申告しており、Rev.M1 はその「密」側である前提で、事実だけを記録する。

## 対象と導入

- 公式リポジトリ https://github.com/fabPlane/fab_router を clone し、使用コミット SHA を記録する。ライセンスはデュアル（GPL-3.0 OR 商用）の **GPL-3.0 側**として利用する
- Bun（≥1.4）を導入し、`bun install` する。導入手順は証跡に残す
- 単体 CLI が配布されていないため、`src/api.ts` の `routeDsn` 等の公開 API を呼ぶ**最小ドライバスクリプトを自作してよい**。これはテストハーネスであり、**ルーター本体（src/ 配下）の改変は禁止**。ドライバのソースは証跡に含める
- 受け入れランナー（`tools/acceptance/run.ts`）が流用できる場合は使ってよいが、その場合も実行条件を記録する
- tscircuit アダプタ経路は使わない（DSN/SES 経路のみ。tscircuit 内部ルーターは D-018 で探索終了済み）

## 固定条件

- 入力 DSN（Main）：`hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/main-restore/corrected.dsn`（SHA256 `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2`、実行前に照合）
- スモーク DSN：同 `smoke-restore/corrected.dsn`（SHA256 `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9`）
- 配置固定、配線幅・クリアランス 0.20mm、2層。条件の緩和・変更は禁止

## 実行手順（二段構え）

### Stage 0（スモーク）
- ドライバ経由でスモーク DSN を配線し、SES 生成・KiCad import・独立検査（#93〜#101 の手順）で4指標すべて0を確認する
- 自前 checkDrc の判定結果も記録し、独立検査と一致するか照合する
- 失敗したら Main に進まない

### Stage 1（Main）
- デフォルトプロファイル相当の設定で1回だけ実行する。`timeoutSeconds` 等、デフォルトから設定した値はすべて証跡に記録する（設定探索は禁止。再実行で条件を変えない）

## 判定

成功条件（すべて）：
- 未配線 0
- 最終 SES の全 path が 0.20mm 以上（#97/#99 と同じ静的実測方式）
- KiCad import 成功、独立検査で4指標（required unconnected / wrong-net contacts / material violations / unexplained transfer changes）すべて 0

失敗条件（いずれか1つ）：
- 未配線が残る／0.20mm 未満の path がある／SES が出ない・import できない／headless 実行不可／2時間内に結論が出ない

4指標の扱い：未配線が残る場合は **null** とし、未配線件数を実測報告する

## 固有の着眼点（メモ §3.2）

1. 自前 checkDrc の「違反なし」と KiCad 独立検査の結果が一致するか（自己判定の妥当性そのものが検証対象。不一致があればその内容を具体的に記録する）
2. 未完了のまま打ち切られる場合、その旨がレポート・出力に正直に現れるか
3. 比較表に Freerouting v2.5.0 Run 2（未配線38）・fastroute #99（未配線37、幅適合）を含める

## 成果物

- 分析・判定文書：`docs/issue-103-fab-router-falsification.md`（新規追加のみ）
- 証跡一式：`hardware/kicad/qualification/issue-103-fab-router-falsification/` 配下（#97 以降の証跡構成を踏襲。ドライバスクリプトを含む。node_modules 等の依存パッケージ本体は含めない）
- 作業ブランチから **Draft PR** を作成する。main への直接 push・merge は禁止
- 既存ファイルの変更は禁止（追加のみ）。対象リポジトリ（he-piantor-42）以外の場所への成果物混入もしない
