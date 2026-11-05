# Issue #157 指示：Main 2 Wing 接続化 Stage 1

GitHub Issue #157「Main 2 Wing 接続化 Stage 1：実現性とインタフェース定義案」を取得し、その内容を実行してください。作業ブランチは issue-157-main-dual-wing-stage1 を切ってください。

## 入力
- #155 改版後の合格 Main 基板と報告書（docs/issue-155-main-mounting-stage2.md、証跡 hardware/kicad/qualification/issue-155-main-mounting-stage2/）。取付穴4個（D-023）は確定済みで維持する
- docs/decisions.md の D-017（インタフェース凍結）・D-019・D-022・D-023
- hardware/rev-m1/main-wing-interface.md と G0B ハーネスの凍結資料
- #141 の電源インテグリティモデル（HALL_5V は USB VBUS→TPS22919、センサー電源の電圧降下モデル）

## 作業
1. 第2 Wing 系統に必要な信号の洗い出し（コネクタ、電源、GND、制御・読取信号、WING_EN の扱い）
2. 第2コネクタの配置実現性（48×44mm 維持可否、取付穴と予約領域との干渉、外形拡張案）
3. インタフェース定義案（ピン配列、左右対称性、誤挿入防止、ハーネス、ファームウェア走査への要求）
4. 2系統接続時の電源インテグリティ再評価（負荷スイッチ容量との照合を含む）
5. D-019／D-022 への影響と Stage 2 の手順見通し、D-017 拡張の決定記録案文
- 報告書 docs/issue-157-main-dual-wing-stage1.md と証跡を新規フォルダに追加のみで置く

## 制約
- 基板データの変更・再配線はしない（Stage 2 の範囲）
- 発注・課金は行わない。Draft PR を作成し、merge はしない
- 一時ランタイムは .issue157-runtime/ に置く（/tmp は 512MB）
