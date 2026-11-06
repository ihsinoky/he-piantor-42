# Issue #178 指示（訂正版）：M1 評価基板 — 16mm／17mm 両ブロック 18キー

GitHub Issue #178 を再取得し、その最新内容を実行してください。構成は訂正版が正です：**16mm の 3×3 ブロック（9キー）＋ 17mm の 3×3 ブロック（9キー）＝ 計18キーを1枚に載せる**。16.5mm は対象外です。

## 起点と参照資料
- 既存の pitch9 設計：docs/issue-127-wing-design.md、hardware/jitx/wing/generated/pitch9-16mm／pitch9-17mm、hardware/jitx/he_piantor_42_jitx/evaluation_wing.py
- Wing の配線・資格確認は代表21キー Wing の手順（#129〜#141、D-021）を踏襲する

## 成果物
1. 18キー評価基板の設計定義と基板データ：2ブロック×（3列×3行）。MUX は3バンク、各バンク6入力（両ブロックの同じ列：16mm 側アドレス 0–2、17mm 側アドレス 3–5）。GH14 インタフェースは pitch9 と同一
2. ブロック間の最近接キー距離（目標34mm以上）の達成値と根拠
3. D-021 条件での配線結果と独立資格確認（4指標すべて0、全ネット）
4. 製造データ（Gerber）と PCBA 用 BOM／CPL（JLCPCB 形式）
5. decisions.md への D-028 追記（バージョン定義と本基板の目的・構成）
6. 報告書 docs/issue-178-m1-matrix-board.md と証跡フォルダ

## 制約
- GH14 インタフェースは変更しない。D-021 の条件緩和は行わない
- 発注・課金は行わない。Draft PR を作成し、merge はしない
- 一時ランタイムは .issue178-runtime/ に置く（/tmp は 512MB）
