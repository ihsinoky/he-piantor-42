# Issue #169 指示：Main 2 Wing 化 Stage 2 フォローアップ

GitHub Issue #169「Main 2 Wing 化 Stage 2 フォローアップ：配置・seed 見直しと再配線」を取得し、その内容を実行してください。

## 起点
- Issue #167 のブランチ issue-167-main-dual-wing-stage2（Draft PR #168）の head を起点に、新ブランチ issue-169-main-dual-wing-followup を切る。同ブランチには回路・基板候補、D-024〜D-027、#167 の報告書（docs/issue-167-main-dual-wing-stage2.md）と証跡が入っている
- #167 の失敗内容：全体配線で V1V1／V3V3 が分断し未接続 3。局所修正が QSPI の保持配線を壊した（転送差分 24、dangling via 2）。レール共通部の正側抵抗 60.674mΩ（目標 50mΩ 超過）

## 作業
1. 配置と seed の見直し：追加部品の配置と電源 seed で U1 周りの電源ネット混雑を解き、レール共通部の正側を 50mΩ 目標内へ。既存部品の移動は原則なし（必要な場合は対象と理由を明示）
2. 部品確定：コンデンサと帰還用精密抵抗の具体的型番を確定し BOM へ反映
3. 再配線：D-019 条件（4層・1.2mm・信号 0.10mm・via 0.60/0.30・In1 GND 専用・escalation off）で全体配線を最大2回（seed を変える）。保持ネットを壊す局所 rip-up は採らない
4. 独立資格確認（4指標すべて0、全44ネット）、実抵抗の再抽出（GND 側を含む）、製造データ再生成、POFV 再分類、PCBA 見積確定
- 報告書 docs/issue-169-main-dual-wing-followup.md と証跡を新規フォルダに追加。決定記録の追記は不要（新たな決定が生じた場合のみ）

## 制約
- D-019 の条件緩和は行わない。成立しない場合は、条件変更の要否として PO へ上げる形で報告して止める
- 発注・課金は行わない。Draft PR を作成し、merge はしない
- 一時ランタイムは .issue169-runtime/ に置く（/tmp は 512MB）
