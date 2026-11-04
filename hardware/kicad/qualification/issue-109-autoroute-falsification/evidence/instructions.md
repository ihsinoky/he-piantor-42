# Issue #109 指示書：AutoRoute の限定反証テスト

- 発行：PMO（2026-11-04）。PO 承認済み（「残りの AutoRoute と Python版 freeroute も安く試して一巡させる」）
- ワーカー：Codex
- タイムボックス：**取得・ビルド・実行・独立検査・記録すべて含めて2時間**
- 検討メモ：`~/workspace/goals/he-piantor-42-keyboard-pmo/files/auto-routing-candidates-2026-11-04.md` §2（共通骨格）・§3.3（AutoRoute 差分）

## 目的

AutoRoute（Rust、negotiated-congestion A* の独立実装）を同一 DSN・固定条件で反証テストする。公開以降（2026-09-27）更新がなく外部検証もないため実力は未知数。事実の記録が目的で、設定探索はしない。

## 対象と導入

- 公式リポジトリ https://github.com/pingpongshow/AutoRoute を clone し、使用コミット SHA を記録する。MIT ライセンス
- `cargo build --release` でビルドする。ビルド済みバイナリ自体は成果物に含めない。導入手順とツールバージョンは証跡に残す

## 固定条件

- 入力 DSN（Main）：`hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/main-restore/corrected.dsn`（SHA256 `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2`、実行前に照合）
- スモーク DSN：同 `smoke-restore/corrected.dsn`（SHA256 `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9`）
- 配置固定、配線幅・クリアランス 0.20mm、2層。条件の緩和・変更は禁止

## 実行手順（二段構え）

### Stage 0（スモーク）
- `autoroute corrected.dsn -o out.ses --check` を headless で実行する
- SES 生成・KiCad import・独立検査（#93〜#107 の手順）で4指標すべて0を確認する。失敗したら Main に進まない

### Stage 1（Main）
- 同一コマンド・デフォルト条件で1回だけ実行する。追加オプションでの調整はしない

## 判定

成功条件（すべて）：
- 未配線 0
- 最終 SES の全 path が 0.20mm 以上（#97 以降の静的実測方式）
- KiCad import 成功、独立検査で4指標（required unconnected / wrong-net contacts / material violations / unexplained transfer changes）すべて 0

失敗条件（いずれか1つ）：
- 未配線が残る／0.20mm 未満の path がある／SES が出ない・import できない／headless 実行不可／2時間内に結論が出ない

終了コードの扱い：AutoRoute は 0=完了／2=未完了を返す。2 の場合は部分 SES が出力されるので、その未接続数を独立検査側（KiCad DRC の unconnected_items）でも数えて記録する（#107 の Topola スモークでの数え方に準じる）。4指標は null のまま合否には使わない

## 固有の着眼点（メモ §3.3）

1. グリッドピッチは幅+クリアランス（0.40mm 相当）から導出される。細いパッド・障害物が正しく障害物化されているか（部分 SES が得られたら wrong-net 的な接触の有無を可能な範囲で確認する）
2. 内蔵 `--check`（厳密幾何 DRC）の自己判定と独立検査の関係（一致／不一致を事実として記録する）
3. 比較表に Freerouting v2.5.0 Run 2（38件）・fastroute #99（37件）・fab_router #103（16件）を含める

## 成果物

- 分析・判定文書：`docs/issue-109-autoroute-falsification.md`（新規追加のみ）
- 証跡一式：`hardware/kicad/qualification/issue-109-autoroute-falsification/` 配下（#97 以降の証跡構成を踏襲。バイナリ自体は含めない）
- 作業ブランチから **Draft PR** を作成する。main への直接 push・merge は禁止
- 既存ファイルの変更は禁止（追加のみ）
