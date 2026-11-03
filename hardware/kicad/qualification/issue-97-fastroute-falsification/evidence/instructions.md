# Issue #97 指示書：fastroute の限定反証テスト

- 発行：PMO（2026-11-04）。PO 承認済み（「fastroute の反証テストを Issue 化して」）
- ワーカー：Codex
- タイムボックス：**導入・実行・独立検査・記録すべて含めて2時間**
- 検討メモ：`~/workspace/goals/he-piantor-42-keyboard-pmo/files/auto-routing-candidates-2026-11-04.md` §2（共通骨格）・§3.1（fastroute 差分）

## 目的

fastroute（Freerouting の Rust 移植＋機構変更）が、Freerouting v2.5.0 で確定した失敗様式（未配線が残ると optimizer が skip される、停滞、best 38 件未配線）を、同一 DSN・固定条件で覆せるかを反証テストする。設定探索はしない。単一条件の1回実行で判定する。

## 固定条件

- 入力 DSN（Main）：`hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/main-restore/corrected.dsn`（SHA256 `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2`、実行前に照合）
- スモーク DSN：`hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/smoke-restore/corrected.dsn`（SHA256 `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9`）
- 配置固定、配線幅・クリアランス 0.20mm、2層。条件の緩和・変更は禁止

## 導入

- 公式リリース（parisxmas/fastroute、最新安定版。メモ時点では v0.1.14）の Linux x64 プリビルドバイナリを取得し、SHA256 を記録する。ソースビルドはしない
- バージョン文字列と取得元 URL を証跡に残す

## 実行手順（二段構え）

### Stage 0（スモーク）
- スモーク DSN で headless 実行し、例外なく終了して SES が生成されることを確認する
- 失敗したら Main に進まず、その時点で反証成立として記録する

### Stage 1（Main）
- コマンド（意図）：`fastroute -de corrected.dsn -do out.ses --report=report.json --max-time=1800`
- 拡張機能はデフォルト有効のまま使う。`--parity` / `--no-enhancements` は使わない（それは検討済みの Freerouting 再現になるため）
- 設定の追加変更・再実行による探索は禁止（単一条件1回のみ）

## 判定

成功条件（すべて満たすこと）：
- SES が生成され KiCad へ import でき、プロジェクト既存の独立検査（Issue #93/#95 の手順を踏襲）で4指標（required unconnected / wrong-net contacts / material violations / unexplained transfer changes）がすべて 0

失敗（反証）条件（いずれか1つ）：
- 未配線が1件でも残る、または違反が残る
- SES が生成されない／import できない
- 配線幅・クリアランスが 0.20mm を割る（`--report` の violations と独立検査・SES 内の幅実測で二重確認）
- headless で実行できない、2時間以内に結論が出ない

4指標の扱い：未配線が残る場合は従来どおり **null** とし、実測した未配線件数を別途報告する。0件の場合のみ独立検査を実測し、数値を報告する（null のまま成功としない）

## 固有の着眼点（メモ §3.1）

1. neck-down が 0.20mm を割っていないか
2. multi-start の再実行で最良結果が SES に保持されているか（report と SES の整合）
3. 終了コード・`--report` の集計が独立検査の結果と食い違わないか
4. Freerouting v2.5.0 Run 1 / Run 2 との比較（未配線件数、passes、所要時間、例外数）を結果文書に含める

## 成果物

- 分析・判定文書：`docs/issue-97-fastroute-falsification.md`（新規追加のみ）
- 証跡一式：`hardware/kicad/qualification/issue-97-fastroute-falsification/` 配下（Issue #95 の証跡構成を踏襲。バイナリ自体は含めず、取得元・バージョン・SHA256 を記録）
- 作業ブランチから **Draft PR** を作成する。main への直接 push・merge は禁止
- 既存ファイルの変更は禁止（追加のみ）
