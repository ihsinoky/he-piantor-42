# Issue #175 指示：Main 2 Wing 化 Stage 2 限定継続2

GitHub Issue #175「Main 2 Wing 化 Stage 2 限定継続2：C26 配置の反復調整と最終配線1回」を取得し、その内容を実行してください。

## 起点
- Issue #173 のブランチ issue-173-main-dual-wing-final（Draft PR #174）の head を起点に、新ブランチ issue-175-main-dual-wing-final2 を切る
- #173 の到達点：C26 を (94.5,77.2) へ動かして SW2 接触は解消（1.275mm）したが、J3.15（未接続ランド）と 0.4mm² 重なり、preflight で停止。全体配線は未消費。報告書 docs/issue-173-main-dual-wing-final.md と証跡を参照
- seed-a（合格済み）は #173 ブランチの fallback-seed-a に整理済み。フォールバックとして維持する

## 作業
1. 配置調整の反復：追加部品（C26 を中心に C23〜C28／L1／U6）の範囲で配置候補を最大3つ試し、各候補で preflight（準備 DRC）を実施する。衝突・短絡・ランド重なりゼロの候補だけを進める。移動方向の変更、C27／C28 との連動も可。既存部品は動かさない
2. preflight を通過した候補に全体配線1回（D-019 条件：4層・1.2mm・信号 0.10mm・via 0.60/0.30・In1 GND 専用・escalation off）。局所 rip-up は行わない
3. 合格した場合のみ：独立資格確認（4指標すべて0、全44ネット）、実抵抗の再抽出、製造データ再生成、POFV 再分類、PCBA 見積確定
- 報告書 docs/issue-175-main-dual-wing-final2.md と証跡を新規フォルダに追加

## 制約
- 配置候補3つ・全体配線1回の枠で成立しない場合は止め、配置が成立しない幾何学的な理由を報告書に明記する（seed-a が成果物のまま残る）
- D-019 の条件緩和は行わない。発注・課金は行わない。Draft PR を作成し、merge はしない
- 一時ランタイムは .issue175-runtime/ に置く（/tmp は 512MB）
