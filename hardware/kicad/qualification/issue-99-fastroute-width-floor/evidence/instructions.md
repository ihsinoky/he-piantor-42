# Issue #99 指示書：fastroute 再テスト（幅下限200µm強制）

- 発行：PMO（2026-11-04）。PO 承認済み（「幅下限を強制して再テストを Issue 化して」）
- ワーカー：Codex
- タイムボックス：**導入・実行・独立検査・記録すべて含めて2時間**
- 前提：Issue #97 の結果（Draft PR #98）。fastroute v0.1.14 は未配線1件まで到達したが、デフォルト automatic_neckdown により SES に 0.20mm 未満の path が71本（最小0.10mm）生じ、固定条件違反で不合格だった

## 目的

#97 からの変更を「幅下限 200µm の強制」だけに限定した単一条件で再テストし、プロジェクトの固定条件の下での fastroute の成否を確定させる。条件緩和ではなく固定条件の執行である。設定探索はしない。

## 変更点（#97 との差分はこれだけ）

- `--router.min_trace_width_um=200` を指定する
- 一次情報（help 出力・公式ソース）で neckdown がなお 200µm を割りうると判明した場合は、automatic_neckdown の無効化も「下限強制」の一部として併用してよい。その場合は根拠（どのコード／ドキュメントで確認したか）と正確な argv を証跡に記録すること
- 上記以外の router 設定変更は禁止

## #97 と同一に保つもの

- 公式リリース v0.1.14 の Linux x64 プリビルドバイナリ（SHA256 を公式 SHA256SUMS と照合して記録。ソースビルド禁止）
- 入力 DSN（Main）：`hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/main-restore/corrected.dsn`（SHA256 `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2`、実行前に照合）
- スモーク DSN：同 `smoke-restore/corrected.dsn`（SHA256 `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9`）
- コマンド意図：`fastroute -de corrected.dsn -do out.ses --report=report.json --max-time=1800` ＋ 上記の下限強制指定のみ
- 拡張機能デフォルト有効、multi-start デフォルト、`--parity` / `--no-enhancements` 禁止、単一条件1回のみ（再実行による探索禁止）
- 配置固定、配線幅・クリアランス 0.20mm、2層。入力・配置・ルールの変更禁止

## 実行手順

### Stage 0（スモーク）
- 新条件でスモーク DSN を実行し、SES 生成・KiCad import・独立検査4指標すべて0を確認する（#97 のスモークゲート手順を踏襲）
- 失敗したら Main に進まず、その時点で不合格として記録する

### Stage 1（Main）
- 単一条件1回のみ実行する

## 判定

成功条件（すべて）：
- 未配線 0
- 最終 SES の全 path が 0.20mm 以上（#97 と同じ静的実測スクリプト方式で全件確認）
- KiCad import 成功、独立検査で4指標（required unconnected / wrong-net contacts / material violations / unexplained transfer changes）すべて 0

失敗条件（いずれか1つ）：
- 未配線が残る／0.20mm 未満の path が1本でもある／SES が出ない・import できない／headless 実行不可／2時間内に結論が出ない

4指標の扱い：未配線が残る場合は **null** とし、未配線件数と幅分布を実測報告する。成功の場合のみ4指標を実測値で報告する

## 記録すべき観点

- #97 との比較表：未配線件数、幅分布（0.20mm 未満の本数）、autorouter passes、multi-start の variant 別結果、optimizer の挙動、所要時間、例外数
- 下限強制の設定が実際に効いた証跡（help／設定の読み戻し、ログ、SES 幅実測）
- 下限強制によって未配線が増えた場合は、そのトレードオフを事実として記録する（解釈でごまかさない）

## 成果物

- 分析・判定文書：`docs/issue-99-fastroute-width-floor.md`（新規追加のみ）
- 証跡一式：`hardware/kicad/qualification/issue-99-fastroute-width-floor/` 配下（#97 の証跡構成を踏襲。バイナリ自体は含めない）
- 作業ブランチから **Draft PR** を作成する。main への直接 push・merge は禁止
- 既存ファイルの変更は禁止（追加のみ）
