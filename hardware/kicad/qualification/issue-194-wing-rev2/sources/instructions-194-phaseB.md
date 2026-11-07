# Issue #194 Wing Rev.2 Stage 2 — Phase B 指示書（PMO GO）

Phase A（PR #195）の配置・外形案を PMO がレビューし承認した。この案を正として Phase B を実施する。

## 着手前に解消すること
- DRV5055（DBZ）の検出点オフセット δ をデータシートから確定し、検出点→ランド原点の校正（F=K−R(θ)δ）を配置変換に組み込む。根拠（データシートの該当図・寸法）を報告書に残す
- Phase A の脚穴仮説（±5.08／φ1.70）は Jade Pro の図面・実績データで検証し、製造値として採るかどうかを明記する

## Phase B 本体
1. Phase A の4配置（16/17mm × 左右）を source／generator へ反映し、下面 Hall＋局所C を含む新 PCB（Wing Rev.2）を両ピッチで構築する。左右は別基板として扱い、それぞれ検査する
2. D-021（2層 1.2mm、信号 0.10mm／電源・GND 0.30mm、via 0.60/0.30）で全面配線。自動配線を最優先する（PO 方針）。#165 宿題の Wing 側導体低抵抗化（HALL_5V／GND 経路）を含む
3. 検証：DRC 4指標オール0（両ピッチ×左右）、via-パッド間隔は全数 ≥0.10mm を必須とし最小値を報告する（境界に張り付く設計は避け、余裕の分布も示す）
4. 製造データ再生成：#158 の標準実装計画（左右1パネル、無銅タブ分離、下面実装＝Standard PCBA 前提の記録）に沿った Gerber／BOM／CPL
5. #150 のキー計測 CSV を新座標・新外形・新穴位置で再生成する（ケース側の入力として hardware/case/ 配下に置く）
6. D-032 草案（Wing Rev.2 ベースライン）と docs/project-status.md 改訂表への Wing Rev.2 行の追加案
7. 報告書（docs/issue-194-wing-rev2-stage2.md）に Phase B の結果を追記する

## 規約
- 作業は `.issue194-runtime/git` のブランチ `issue-194-wing-rev2-stage2`（PR #195）で継続する。push は PMO が行うのでコミットまで
- スクラッチは `.issue194-runtime/` 内。/tmp は使わない
- 完了したら報告書末尾に完了を明記して停止する
