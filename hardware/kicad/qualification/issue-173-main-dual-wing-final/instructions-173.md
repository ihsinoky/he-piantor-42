# Issue #173 指示：Main 2 Wing 化 Stage 2 限定継続

GitHub Issue #173「Main 2 Wing 化 Stage 2 限定継続：C26 衝突の解消と最終配線1回」を取得し、その内容を実行してください。

## 起点
- Issue #169 のブランチ issue-169-main-dual-wing-followup（Draft PR #172）の head を起点に、新ブランチ issue-173-main-dual-wing-final を切る
- #169 の到達点：seed-a は全44ネット・4指標0で合格（inspection/final/ は seed-a の paste 整備板）。seed-b（出力 C を TDK 1210 品へ更新）は C26 と SW2 の接触と XIN 分断で不合格。報告書 docs/issue-169-main-dual-wing-followup.md と証跡フォルダを参照

## 作業（この範囲に限る）
1. 衝突の解消：追加部品（C26 を中心に C23〜C28／L1／U6）の範囲で配置を調整し、C26 と SW2 の接触を解く。#155 由来の既存部品は動かさない
2. preflight 必須：配線前に準備 DRC を実行し、衝突・短絡があれば配線に入らず止める（#169 で修正したガードを使う）
3. 全体配線1回のみ（D-019 条件：4層・1.2mm・信号 0.10mm・via 0.60/0.30・In1 GND 専用・escalation off）。局所 rip-up は行わない
4. 合格した場合のみ：独立資格確認（4指標すべて0、全44ネット）、実抵抗の再抽出、製造データ再生成、POFV 再分類、PCBA 見積確定
- 報告書 docs/issue-173-main-dual-wing-final.md と証跡を新規フォルダに追加

## 制約
- この1回で成立しない場合は止め、seed-a（合格済み）を成果物として整理し、出力容量の余裕の弱さを既知の制限として明記した報告書を出す
- D-019 の条件緩和は行わない。発注・課金は行わない。Draft PR を作成し、merge はしない
- 一時ランタイムは .issue173-runtime/ に置く（/tmp は 512MB）
