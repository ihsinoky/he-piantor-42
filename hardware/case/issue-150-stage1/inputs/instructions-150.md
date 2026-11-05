# Issue #150 指示：筐体設計 Stage 1

GitHub Issue #150「筐体設計 Stage 1：機械要件と形状設計の提案（基板インタフェース確定のため）」を取得し、その内容を実行してください。作業ブランチは issue-150-case-stage1 を切ってください。

## 入力として使う一次情報
- docs/hall-acquisition.md（スイッチ前提：Gateron Magnetic Jade Pro HE、磁束条件は板厚1.2mm の基板前提。全体構成 §9 付近）
- hardware/rev-m1/main-wing-interface.md、docs/decisions.md（D-017 のインタフェース凍結、G0B ハーネス）
- Wing 両ピッチの外形・取付穴座標：hardware/kicad/qualification/issue-149-wing-silkscreen/ の報告書（座標表）と証跡、#141 の合格基板
- Main の外形・構成：hardware/jitx/ の設計定義と関連文書
- 必要に応じてスイッチ（Gateron Magnetic Jade Pro HE）とキーキャップの公開寸法情報を Web で確認し、出典を記録する

## 成果物
1. 機械要件一覧：基板保持方法、スイッチプレートの要否とキー位置穴形状、磁石〜センサの距離チェーンと公差配分、コネクタ／ケーブルの取り回し、高さ方向の積み上げ
2. キーピッチ 16mm／17mm とスイッチ・キーキャップ寸法の適合確認（干渉有無を寸法で示す）
3. 筐体構成の選択肢比較（3Dプリント／積層アクリル／CNC 等）と M1 試作としての推奨案
4. 基板インタフェース確定案：現在の取付穴位置・外形を採用できるか。変更が必要なら変更点と基板への影響（再配線の要否）
5. 両ピッチ分の扱い（ピッチごとに必要な部品と共通化できる部分）
- 報告書 docs/issue-150-case-stage1.md と寸法根拠の証跡を hardware/case/ または適切な新規フォルダに置く

## 制約
- 提案文書まで。CAD の本設計は Stage 2（方式採用後）
- 既存ファイルの変更はせず追加のみ。Draft PR を作成し、merge はしない
- 一時ランタイムは .issue150-runtime/ に置く（/tmp は 512MB）
