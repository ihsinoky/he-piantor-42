# Issue #185 指示：Main Rev.3 試行 — POFV 不要化（見立てが外れたら停止）

GitHub Issue #185 を取得し、その内容を実行してください。この worktree は
PR #176 の最終基板（Main Rev.2）を起点に切ってあります。作業用ブランチは
issue-185-main-rev3-nopofv です。

## PO の進め方（厳守）
監査 #183 の見通しの範囲で試行し、難解だと分かったら一旦止まる。
- 着手順：直線接続候補がある33個 → 迂回検討が要る2個（C5.2／GND の via
  6bf1ec76…、C4.1／V3V3 の via 83b6e9ed…）の順
- 全体再配線は最大2回。壁に当たったら条件緩和も配置変更もせず、到達点と
  障害を Issue に報告して停止する

## 合格条件
- 独立4指標すべて0（全44ネット、GND zone 再fill 含む）
- 全113 via のパッド間隔 ≥0.10mm（監査 #183 と同じ物差し・手法を再利用）
- 電源抵抗の再抽出で共通・分岐とも 50mΩ 目標（モデル値）を維持

## 成果物（成立時）
- 製造データ再生成（Gerber／BOM／CPL、CAM 照合）
- decisions.md に D-030 を追記（D-028／D-029 は他 PR が使用中。この番号を
  使うこと）。project-status.md は編集しない
- 報告書 docs/issue-185-main-rev3.md と証跡、Draft PR

## 制約
- D-019 条件と部品配置は変更しない。発注・課金は行わない。merge はしない
- 一時ランタイムは .issue185-runtime/ に置く（/tmp は 512MB）
- KiCad ランタイムは ~/workspace/projects/he-piantor-42/.issue129-runtime/
  等の既設を読み取り専用で使ってよい
