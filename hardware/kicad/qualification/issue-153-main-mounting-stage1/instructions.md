# Issue #153 指示：Main 機構改版 Stage 1

GitHub Issue #153「Main 機構改版 Stage 1：取付穴追加の実現性と配置案（ver.A 流用前提）」を取得し、その内容を実行してください。作業ブランチは issue-153-main-mounting-stage1 を切ってください。

## 入力
- #121 の合格 Main 基板（hardware/kicad/qualification/ 配下の該当証跡）と #137 の via／J1 調査結果
- docs/decisions.md の D-019（Main 基準）・D-022（発注仕様）・D-017（インタフェース凍結）
- Issue #150 の筐体 Stage 1 報告書（Main に取付穴がないことの確認、トレイ固定の代案を含む）
- Wing の取付穴前例：NPTH φ2.2mm、周囲 φ5.0mm キープアウト

## 作業
1. 現行 Main 実データから取付穴の候補位置を洗い出す（部品・配線・ビア・パッドとの干渉、穴キープアウト、板端距離を寸法で示す）
2. 穴仕様案（個数・位置・径）と、外形 48×44mm 維持可否（拡張が必要なら寸法案）
3. 再配線の影響範囲と、D-019 条件での再配線・再資格確認の手順見通し
4. D-017 凍結項目との整合確認
- 報告書 docs/issue-153-main-mounting-stage1.md と証跡を新規フォルダに追加のみで置く

## 制約
- 基板データの変更・再配線はしない（Stage 2 の範囲）
- 発注・課金は行わない。Draft PR を作成し、merge はしない
- 一時ランタイムは .issue153-runtime/ に置く（/tmp は 512MB）
