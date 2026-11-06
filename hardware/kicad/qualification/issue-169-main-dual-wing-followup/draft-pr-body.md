Issue #169 の配置・seed・部品見直しを実施した。**未完了・製造GOではない。** 全体配線2回の上限に達して停止した。

| 全44-net独立直接観測 | seed-a | 選定品更新後seed-b |
| --- | ---: | ---: |
| 未接続 | 0 | 2 |
| 異ネット接触 | 0 | 2 |
| 物的違反 | 0 | 4 |
| 保持配線転送差分 | 0 | 7 |

共通正側抵抗は60.674mΩから33.295/32.123mΩへ改善。PGND基準のGNDを含む共通ループはモデル43.211/40.904mΩ。既存53部品とJ3の座標、D-019条件を保持。局所rip-up0回。

出力CをTDK C3225X7R1C226K250AC、精密RをTNPW060354K9BEEA/10K0BEEAへ具体化した。しかしseed-bはXIN未接続2、C26/SW2接触2、HALL保持差分7で不合格。準備preflight失敗後もシェル列がルータを起動した実行ミスを記録し、試行を帳消しにしていない。ガード修正後の追加配線はない。

seed-aのみのレビューCAM/BOM/CPLを再生成・Gerbonara照合。seed-bの最終CAMとPCBA確定見積は資格ゲート未通過で保留。POFVはA110/28、B127/40。発注・課金・mergeなし。D-019緩和の必要性は今回の結果から導けず、新しい有限枠等の判断をPOへ戻す。

報告: docs/issue-169-main-dual-wing-followup.md
証跡: hardware/kicad/qualification/issue-169-main-dual-wing-followup/

Refs #169. #167ブランチをbaseとするDraft。自動close・mergeは行わない。
