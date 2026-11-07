# Issue #194 Wing Rev.2 Stage 2 — Phase A 指示書（配置・外形の確定案まで）

## 作業規約（必読）
- 作業用 git コピーは `.issue194-runtime/git` に作る（サンドボックスでは .git が読み取り専用のため）。origin/main を基底とし、ブランチ名は `issue-194-wing-rev2-stage2`。push は PMO が行うので、コミットまで完了させればよい
- スクラッチ／ランタイムは `.issue194-runtime/` 内に置く。/tmp は使わない（512MB tmpfs で消える）
- KiCad ランタイムは既存の `.issue129-runtime/kicad/` を読み取り専用で再利用してよい
- Phase A の範囲だけを行う。配線（Phase B）は PMO GO まで着手しない

## 入力
- Issue #194 本文（前提・PO判断）
- Stage 1 成果物は PR #193 のブランチ `issue-190-wing-layout-stage1` にある。作業コピーに fetch して読むこと：
  - `docs/issue-190-wing-layout-stage1.md`（報告書）
  - `hardware/case/issue-190-layout/coordinates-u.csv`（u比・原典角度）
  - `hardware/case/issue-190-layout/coordinates-{16,17}mm.csv`（再アンカー済み中心座標）
  - `hardware/case/issue-190-layout/geometry-summary.json`, `definition-{16,17}mm.proposal.json`
- 現行 Wing 設計データ（#131/#141/#151 の definition・配置・製造データ一式）は origin/main 内の既存データを正とする

## Phase A で確定させること
1. 両ピッチ（16/17mm）× 左右のキー配置確定案：中心は Stage 1 座標、姿勢は親指に原典角度（左 T0 +5°／T1 −10°／T2 −25°、右は鏡像符号反転）。センサー（DRV5055）位置はスイッチ姿勢に追随させる
2. C0 列の 180°（Piantor）：Hall 基板のセンサー配置・フットプリントに影響するか評価する。採用できない場合は理由を報告書に明記し 0° とする
3. 外形：Jade Pro 全平面包絡（保守値 15.8mm 角、回転した親指キー込み）を全キー基板内に収め、四隅の位置決め穴（φ2.2 NPTH、φ5 keepout、#158 の位置決め計画に沿う）も収まる最小の矩形外形を両ピッチで決める。旧政策寸法（119.8×104／126.9×109）は使わない
4. J1（BM14B-GHS-TBT、GH14）とテストパッド等のサービス要素の配置案：新外形・新キー包絡と干渉しない置き場を数値で示す
5. 検証：全キーの包絡が外形内にあること、穴 keepout と包絡が重ならないこと、隣接スイッチ包絡同士が重ならないことを数値（最小間隔つき）で示す

## 成果物（ブランチにコミット）
- 配置確定案データ（既存 Wing definition の形式に合わせた更新ファイル、またはそれに準ずる機械可読ファイル）
- 報告書 `docs/issue-194-wing-rev2-stage2.md`：配置表、外形寸法と根拠、J1 等の配置案、検証数値、C0 180° の評価、Phase B への引き継ぎ事項と未決事項
- 報告書の末尾に「Phase A はここで停止し PMO レビュー待ち」と明記する
