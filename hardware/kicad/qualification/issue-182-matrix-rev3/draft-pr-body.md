Issue #182 のマトリクス基板 Rev.3。Rev.2 のパッド上 via を除去し、全 via がパッド銅から 0.10 mm 以上離れる配線へ変更した。

- 全158 via × 全178銅パッドを独立監査。重なり0、間隔不足0、最小銅間隔 **0.107462501 mm**。解析距離と KiCad native shape の双方で確認。
- 全27ネットの独立4指標は **0 / 0 / 0 / 0**。最終製造用 PCB の DRC も違反・未接続0。
- D-021 不変：2層／1.2 mm、信号0.10 mm／電源0.30 mm、間隙0.10 mm、via 0.60/0.30 mm、KRT escalation off。部品配置・外形・GH14・電気構成・非配線 AST と元プロジェクトは Rev.2 のまま。
- Gerber／ドリル／ペースト／BOM／CPL を再生成し、CAM の幾何・穴・マスクを読み戻して照合。BOM/CPL は Rev.2 とバイト一致し再利用可能。
- Rev.3 の `manufacturing/FABRICATION.md` で POFV 要求を取り下げ。D-029 を追記。`project-status.md` は未変更。

起点は PR #181 の `issue-178-m1-matrix-board` (`b23716a`)。この PR は同ブランチを base とする後続 PR で、Rev.3 の差分だけを表示する。PR #181 は未 merge。

報告書: `docs/issue-182-matrix-rev3.md`
証跡・製造パッケージ: `hardware/kicad/qualification/issue-182-matrix-rev3/`

再起動前に完了した段階は再利用し、中断段階を再開。失敗候補・局所修復・最終資格確認の証跡を含む。旧シルクの ISSUE178 表記は配線/via 以外を変えない制約に従い継承し、Rev.3 はパッケージと SHA と製造注記で識別する。

発注・課金・manufacturer preview・merge は行っていない。メーカー最終DFM、実装方向照合と実機評価は別工程。**Draft として提出し、merge は行わない。**
