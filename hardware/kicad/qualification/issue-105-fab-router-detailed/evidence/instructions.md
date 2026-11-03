# Issue #105 指示書：fab_router 追加テスト（詳細ルーター有効の単一条件）

- 発行：PMO（2026-11-04）。PO 承認済み（「詳細ルーター有効の条件で追加テストを Issue 化して」）
- ワーカー：Codex
- タイムボックス：**条件特定・実行・独立検査・記録すべて含めて2時間**
- 前提：Issue #103 の結果（Draft PR #104）。未配線16件・幅適合だったが、実効設定は API デフォルト相当で `detailedRouter: "off"` / `globalPlan: "off"` / `fanoutEnabled: false` だった

## 目的

#103 からの変更を「配線モードに関する設定」だけに限定した単一条件で、開発元が本来の配線向けに用意した条件での fab_router の成否を確定させる。これは #97→#99（幅下限の執行）と同じ「実条件での再判定」であり、無目的なパラメータ探索ではない。追加はこの1セルで最後とする前提で実施する。

## 条件の定義（最重要）

1. まず一次情報（対象リポジトリの README、`spec/`、ソース内のプロファイル定義）から、開発元が完全配線向けに用意した条件を特定する：
   - 名前付きプロファイル（例：tiles 系や slow-tier 等）が存在すれば、それを採用する
   - プロファイルが存在しない場合は、`detailedRouter` を有効化するために必要な最小の文書化されたスイッチだけを変更する（`globalPlan` が詳細ルーターの前提として文書化されている場合はそれも含む）
2. 特定した条件について、**Main 実行前に**実効設定の全項目 readback を証跡に記録し、#103 の readback との差分が「配線モードに関するものだけ」であることを示せるようにする
3. それ以外の設定（`seed: 1`、コスト類、`timeBudgetMs: 1800000`、`useFileSettings` 未指定など）は #103 と同一に保つ
4. 適用した条件での実行は Stage 1 で1回のみ。再実行・追加調整は禁止

## #103 と同一に保つもの

- 対象コミット `69cf598db98c136bff16bbe02bccdded95674b18`（GPL-3.0-only 側で利用、ルーター本体 `src/`・`spec/` は無改変）
- Bun・ドライバの基本形（設定を渡すための変更はハーネス変更として可。変更後のドライバも証跡に含める）
- 入力 DSN（Main）：`hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/main-restore/corrected.dsn`（SHA256 `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2`、実行前に照合）
- スモーク DSN：同 `smoke-restore/corrected.dsn`（SHA256 `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9`）
- 配置固定、配線幅・クリアランス 0.20mm、2層。tscircuit アダプタ経路は使わない

## 実行手順

### Stage 0（スモーク）
- 新条件でスモーク DSN を実行し、SES 生成・KiCad import・独立検査（#93〜#103 の手順）で4指標すべて0、自前 checkDrc との一致を確認する
- 失敗したら Main に進まない

### Stage 1（Main）
- 新条件で1回だけ実行する

## 判定

成功条件（すべて）：
- 未配線 0
- 最終 SES の全 path が 0.20mm 以上（#97 以降の静的実測方式）
- KiCad import 成功、独立検査で4指標すべて 0

失敗条件（いずれか1つ）：
- 未配線が残る／0.20mm 未満の path がある／SES が出ない・import できない／headless 実行不可／2時間内に結論が出ない

4指標の扱い：未配線が残る場合は **null** とし、未配線件数を実測報告する

## 記録すべき観点

- #103 との比較表：未配線件数、実効設定の差分（全項目）、passes と pass ごとの残接続推移、停止理由、所要時間、SES 幅分布、via 数
- 自前 checkDrc の判定と、保存 SES 再適用での整合。Main の独立検査との一致は、未配線が残る場合は「未確認」と明記する（スモークの一致を転用しない）
- 詳細ルーター有効化で悪化した場合は、その事実をそのまま記録する

## 成果物

- 分析・判定文書：`docs/issue-105-fab-router-detailed.md`（新規追加のみ）
- 証跡一式：`hardware/kicad/qualification/issue-105-fab-router-detailed/` 配下（#103 の証跡構成を踏襲。ドライバを含む。依存パッケージ本体は含めない）
- 作業ブランチから **Draft PR** を作成する。main への直接 push・merge は禁止
- 既存ファイルの変更は禁止（追加のみ）
