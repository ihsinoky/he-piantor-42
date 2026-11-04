# Issue #107 指示書：Topola の限定反証テスト

- 発行：PMO（2026-11-04）。PO 承認済み（「PR 2件を merge して fab_router 線を閉じ、次は Topola を Issue 化して」）
- ワーカー：Codex
- タイムボックス：**取得・ビルド・実行・独立検査・記録すべて含めて2時間**
- 検討メモ：`~/workspace/goals/he-piantor-42-keyboard-pmo/files/auto-routing-candidates-2026-11-04.md` §2（共通骨格）・§3.4（Topola 差分）

## 目的

Topola は位相的（topological）自動配線で、これまで評価した maze 系（Freerouting／fastroute／C++版）・グリッド＋押しのけ系（fab_router）とは機構が最も異なる。開発元自身が "work-in-progress interactive topological router" と位置づけており、完成を期待するテストではない。同一 DSN・固定条件で「どうなるか」の事実を記録することが目的。

## 対象と導入

- 公式リポジトリは **Codeberg**（codeberg.org/topola/topola。GitHub はミラー）。Codeberg から取得し、使用コミット SHA を記録する。MIT ライセンス
- `cargo install --locked --path crates/topola-cli` でビルドする。ビルド済みバイナリ自体は成果物に含めない。導入手順とツールのバージョンは証跡に残す

## 固定条件

- 入力 DSN（Main）：`hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/main-restore/corrected.dsn`（SHA256 `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2`、実行前に照合）
- スモーク DSN：同 `smoke-restore/corrected.dsn`（SHA256 `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9`）
- 配置固定、配線幅・クリアランス 0.20mm、2層。条件の緩和・変更は禁止

## 実行手順（二段構え）

### Stage 0（スモーク）
- `topola corrected.dsn -o out.ses`（コマンドファイルなしのデフォルト動作＝自動配線して SES を書く）を headless で実行する
- SES 生成・KiCad import・独立検査（#93〜#105 の手順）で4指標すべて0を確認する。失敗したら Main に進まない

### Stage 1（Main）
- 同一コマンド・デフォルト条件で1回だけ実行する。`.cmd` ファイルによるコマンド列の指定や追加オプションでの調整はしない（設定探索禁止）
- 対話前提の実装のため長時間化・無応答の可能性がある。**外側の安全上限1800秒**で監視し、到達したら打ち切って、その事実（経過時間、出力の有無）を記録する

## 判定

成功条件（すべて）：
- 未配線 0
- 最終 SES の全 path が 0.20mm 以上（#97 以降の静的実測方式）
- KiCad import 成功、独立検査で4指標（required unconnected / wrong-net contacts / material violations / unexplained transfer changes）すべて 0

失敗条件（いずれか1つ）：
- 未配線が残る／0.20mm 未満の path がある／SES が出ない・import できない／headless 実行不可／外側上限で打ち切り／2時間内に結論が出ない

4指標の扱い：未配線が残る場合は **null** とし、未配線件数を実測報告する。未配線件数の数え方（Topola 自身の出力がない場合は、SES を KiCad 側で数える等の方法を明記する）

## 固有の着眼点（メモ §3.4）

1. SES 内の配線幅が DSN 規則（0.20mm）で出力されるか（位相→幾何の具体化が最初の関門。幅が規則と異なる場合はその分布を実測する）
2. 処理が現実的な時間で終わるか（対話前提の実装のため、監視を強めに）
3. 比較表に Freerouting v2.5.0 Run 2（38件）・fastroute #99（37件）・fab_router #103（16件）を含める

## 成果物

- 分析・判定文書：`docs/issue-107-topola-falsification.md`（新規追加のみ）
- 証跡一式：`hardware/kicad/qualification/issue-107-topola-falsification/` 配下（#97 以降の証跡構成を踏襲。ビルド済みバイナリ自体は含めない）
- 作業ブランチから **Draft PR** を作成する。main への直接 push・merge は禁止
- 既存ファイルの変更は禁止（追加のみ）
