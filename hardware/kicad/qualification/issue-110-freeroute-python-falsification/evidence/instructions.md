# Issue #110 指示書：Python版 freeroute の限定反証テスト

- 発行：PMO（2026-11-04）。PO 承認済み（「残りの AutoRoute と Python版 freeroute も安く試して一巡させる」）
- ワーカー：Codex
- タイムボックス：**導入・2構成の実行・独立検査・記録すべて含めて2時間**
- 検討メモ：`~/workspace/goals/he-piantor-42-keyboard-pmo/files/auto-routing-candidates-2026-11-04.md` §2（共通骨格）・§3.5（Python版 freeroute 差分）

## 目的

Python版 freeroute（Freerouting の Python 再実装、開発元が Alpha と明記）を同一 DSN・固定条件で反証テストする。開発元は「密な基板では Freerouting JAR より完了ネット数が少ない見込み」と明言しており期待値は低い。固有の確認価値は、exact エンジンの設計主張「違反を出すくらいならネットを落とす（自己検証で違反ゼロを守る）」が事実かどうかである。

## 対象と導入

- PyPI の freeroute **version 2026.7.14** を固定し、`pip install freeroute==2026.7.14` で導入する（GPL-3.0-or-later）。導入した配布物のファイル名と SHA256 を記録する。Python バージョンも記録する

## 固定条件

- 入力 DSN（Main）：`hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/main-restore/corrected.dsn`（SHA256 `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2`、実行前に照合）
- スモーク DSN：同 `smoke-restore/corrected.dsn`（SHA256 `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9`）
- 配置固定、配線幅・クリアランス 0.20mm、2層。条件の緩和・変更は禁止

## 実行手順（2構成 × 二段構え）

対象構成は次の2つ（検討メモ §3.5 の定義どおり）。デフォルトの grid エンジンは、開発元自身がクリアランスについて最も不正確と明記しているため対象外とする。

- 構成A：`freeroute corrected.dsn --engine exact --shove -do out.ses`
- 構成B：`freeroute corrected.dsn --engine room --pack --shove -do out.ses`

各構成とも：
1. Stage 0：スモーク DSN で実行し、SES 生成・KiCad import・独立検査（#93〜#107 の手順）で4指標すべて0を確認する。失敗した構成は Main に進まない
2. Stage 1：Main DSN を同一構成で1回だけ実行する

実際のコマンドライン引数の正確な形（フラグ名・順序）は `--help` で確認し、証跡に残すこと。引数の意味を変える追加調整は禁止。

処理時間の監視：Python 実装のため低速な可能性がある。各 Stage は外側の安全上限（目安1800秒、ただし2構成合計で2時間の箱に収めること）で監視し、到達したら打ち切って記録する。

## 判定（構成ごと）

成功条件（すべて）：
- 未配線 0
- 最終 SES の全 path が 0.20mm 以上（#97 以降の静的実測方式）
- KiCad import 成功、独立検査で4指標（required unconnected / wrong-net contacts / material violations / unexplained transfer changes）すべて 0

失敗条件（いずれか1つ）：
- 未配線が残る／0.20mm 未満の path がある／SES が出ない・import できない／時間内に結論が出ない

4指標の扱い：未配線が残る場合は **null** とし、未配線件数を実測報告する

## 固有の着眼点（メモ §3.5）

1. exact の自己検証どおり、出力に違反が本当にないか。部分結果でも幅・クリアランス違反が出れば、自己検証の主張自体が反証されたことになるので、違反の有無は未配線件数と切り分けて実測する（SES の静的幅実測＋、可能なら KiCad DRC の violations 件数を診断値として記録する。4指標の合否値とは区別する）
2. Python 実装の処理時間（構成ごと・Stage ごと）
3. 比較表に Freerouting v2.5.0 Run 2（38件）・fastroute #99（37件）・fab_router #103（16件）を含める

## 成果物

- 分析・判定文書：`docs/issue-110-freeroute-python-falsification.md`（新規追加のみ）
- 証跡一式：`hardware/kicad/qualification/issue-110-freeroute-python-falsification/` 配下（構成A/Bを分けて記録。配布物自体は含めない）
- 作業ブランチから **Draft PR** を作成する。main への直接 push・merge は禁止
- 既存ファイルの変更は禁止（追加のみ）
