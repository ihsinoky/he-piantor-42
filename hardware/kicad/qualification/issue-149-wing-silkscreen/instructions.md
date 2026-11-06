# Issue（シルク追加の改版）指示

GitHub の最新 Issue「Wing シルク追加の改版：部品配置・キー位置を含むシルクを入れて製造データを再検証する」を取得し、その内容を実行してください。作業ブランチは issue-149-wing-silkscreen を切ってください。

## 対象と方法
- 対象基板は Issue #141 の合格出力（hardware/kicad/qualification/issue-141-wing-power-integrity/ の runs/KRT-16-2L-P0300 と KRT-17-2L-P0300 の out.kicad_pcb）
- 銅箔・配線・ビア・パッド・穴は一切変更しない。F.Silkscreen（必要なら B.Silkscreen）に図形と文字を追加するだけの派生基板を作る
- 追加内容：全搭載部品の Reference、21キー位置へのキースイッチ位置枠（ピッチ通りの正方形）、pin1／極性マーク、J_WING の向きと pin1、取付穴の表示、基板名・ピッチ・リビジョン文字
- 配置データ（placements／definition.json）は hardware/jitx/wing/ の生成物と #141 証跡の inventory を使う

## 検証
- 追加前後で銅箔（配線・ビア・パッド・穴・外形・マスク開口）が同一であることを解析照合する
- DRC 再実行で違反0（シルクのパッド干渉を含む）
- 製造データ（Gerber 一式＋Excellon、#147 と同じ構成）を両ピッチで生成し、ビューア描画でシルクが印刷像として現れることを確認する
- 取付穴4点の座標表（位置・径・キープアウト径）を報告書に残す

## 成果物・制約
- 報告書 docs/issue-149-wing-silkscreen.md と、改版基板・製造データ・証跡を hardware/kicad/qualification/issue-149-wing-silkscreen/ に追加のみで置く
- #147 の製造 ZIP が本改版に置き換わる旨を報告書に明記する
- 発注・課金・アップロードは行わない。Draft PR を作成し、merge はしない
- 一時ランタイムは .issue149-runtime/ に置く（/tmp は 512MB）
