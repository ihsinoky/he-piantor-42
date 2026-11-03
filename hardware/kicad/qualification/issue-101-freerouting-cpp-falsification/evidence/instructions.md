# Issue #101 指示書：freeRouting.org C++版 v2.0.1 の限定反証テスト

- 発行：PMO（2026-11-04）。PO 承認済み（「PR 2件を merge して fastroute 線を閉じ、次は C++版 freerouting.org を Issue 化して」）
- ワーカー：Codex
- タイムボックス：**取得・ビルド・実行・独立検査・記録すべて含めて2時間**
- 検討メモ：`~/workspace/goals/he-piantor-42-keyboard-pmo/files/auto-routing-candidates-2026-11-04.md` §2（共通骨格）・§3.6（C++版差分）

## 目的

freeRouting.org の C++版 v2.0.1 は GitHub の Freerouting（Java）とは別系統で、v2.0.1 で自動配線エンジンが新規実装に置換された。公式サポートの headless 実行で、保存済み同一 DSN・固定条件・デフォルト条件の単一実行により反証テストする。設定探索はしない。

## 対象の特定と導入

- 公式サイト https://freerouting.org/ から `freeRouting-2.0.1.tar.gz`（ソース tarball）を取得し、取得元 URL と SHA256 を記録する。公開 Git リポジトリは存在しない。この配布物以外（非公式ミラー等）は使わない
- 公式の Building from Source 手順に従ってビルドする（Qt が必要）。ビルド手順・使用したパッケージ・ビルドログは証跡対象とする。システムへの恒常的な変更は最小限にし、何を導入したか記録すること
- ビルドが2時間の時間箱内に終わらなければ、その時点で「結論未達（ビルド不能／時間内未完了）」として記録し、無理に続けない

## 固定条件

- 入力 DSN（Main）：`hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/main-restore/corrected.dsn`（SHA256 `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2`、実行前に照合）
- スモーク DSN：同 `smoke-restore/corrected.dsn`（SHA256 `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9`）
- 配置固定、配線幅・クリアランス 0.20mm、2層。条件の緩和・変更は禁止

## 実行手順（二段構え）

### Stage 0（スモーク）
- `freeRouting --autoroute corrected.dsn`（出力は同名 `.ses`）を headless で実行する
- SES 生成・KiCad import・独立検査（#93〜#99 の手順）で4指標すべて0を確認する。特に **unexplained transfer changes**（DSN 読込・SES 書出での受け渡し時のデータ変化）に注意する
- 失敗したら Main に進まない

### Stage 1（Main）
- 同一コマンド、デフォルト条件（45°、optimizer 有効。`--angle` や `--no-postroute` 等の追加オプションは使わない）で1回だけ実行する

## 判定

成功条件（すべて）：
- 未配線 0
- 最終 SES の全 path が 0.20mm 以上（#97/#99 と同じ静的実測方式）
- KiCad import 成功、独立検査で4指標すべて 0

失敗条件（いずれか1つ）：
- 未配線が残る／0.20mm 未満の path がある／SES が出ない・import できない／headless 実行不可／ビルド不能／2時間内に結論が出ない

4指標の扱い：未配線が残る場合は **null** とし、未配線件数を実測報告する

## 固有の着眼点（メモ §3.6）

1. 未完了で終わった場合でも `.ses` が書かれ、未接続数が数えられるか
2. 2.0系の DSN 読込・SES 書出で受け渡し時のデータ変化が出ないか（スモークの4指標で判定）
3. 結果の比較表に Freerouting v2.5.0 Run 2（38件）・fastroute #99（37件、幅適合）を含める

## 成果物

- 分析・判定文書：`docs/issue-101-freerouting-cpp-falsification.md`（新規追加のみ）
- 証跡一式：`hardware/kicad/qualification/issue-101-freerouting-cpp-falsification/` 配下（#97/#99 の証跡構成を踏襲。ビルド済みバイナリ自体は含めず、取得元・tarball の SHA256・ビルド手順とログを記録）
- 作業ブランチから **Draft PR** を作成する。main への直接 push・merge は禁止
- 既存ファイルの変更は禁止（追加のみ）
