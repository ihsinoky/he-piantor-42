# Issue #155 指示：Main 機構改版 Stage 2（案A 実装）

GitHub Issue #155「Main 機構改版 Stage 2：案A の実装・再配線・再資格確認」を取得し、その内容を実行してください。作業ブランチは issue-155-main-mounting-stage2 を切ってください。

## 採用案（PO 決定済み）
- 外形 48×44mm 維持。NPTH φ2.2mm 取付穴×4、非矩形配置：H1 (79,92)／H2 (121,81)／H3 (79,119)／H4 (102,111.5)（KiCad 絶対座標）。全銅層に φ5.0mm 予約領域
- 詳細は docs/issue-153-main-mounting-stage1.md（特に §2 と §5）と、その証跡 hardware/kicad/qualification/issue-153-main-mounting-stage1/ の plans.json／measurements.json

## 作業の要点
1. docs/decisions.md に D-023（案A採用）を追記する。この Issue では decisions.md の追記が認められる変更である
2. 改版入力の構築：#121 合格出力と対応入力側 project を起点に hash 保存。穴・全層 keepout・シルク逃げだけを追加し、部品・ネット・J1/J2 位置は不変。NPTH の rule-area 扱いは Wing の前例（#131 で修正した扱い）に従う
3. 再配線：D-019 条件（4層、F.Cu 信号／In1.Cu GND plane／In2.Cu 信号／B.Cu 信号、厚さ 1.2、幅／clearance 0.10、via 0.60/0.30、KRT v0.23.8・escalation off）。まず干渉3セグメント（VBUS／WING_EN／GND）の局所退避を試み、ダメなら未配線入力の範囲を明示して全体再配線
4. 独立資格確認：GND 再充填→DRC→独立4指標すべて0、全37ネット確認、穴の読戻し
5. 製造データ（Gerber／ドリル）生成と、POFV 対象ビアの再分類、J1 工程・BOM/CPL の再確認。報告書 docs/issue-155-main-mounting-stage2.md と証跡を新規フォルダに追加

## 制約
- 条件緩和と無制限の再試行は禁止。時間枠内に再配線が成立しない場合は状態を報告して止める
- 発注・課金は行わない。Draft PR を作成し、merge はしない
- 一時ランタイムは .issue155-runtime/ に置く（/tmp は 512MB）
