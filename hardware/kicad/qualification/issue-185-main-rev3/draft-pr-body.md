Main Rev.2 の35個の via を部品配置固定で移設し、Main Rev.3 の全113 via をパッド銅から0.10mm以上離した。33個の直線接続候補を先に適用し、C5.2/GND と C4.1/V3V3 を最後に局所接続した。既存693 segmentを保持し94 segmentを追加、全体再配線0回・rip-up0回。

Closes #185

- GND zone再fill後、全44ネット・独立4指標すべて0。凍結回路契約／schematic／PCBの245論理pinも差分0。
- #183と同じnative監査で全113 via合格、最小間隔0.100000mm。両面pasteとのvia銅／drill重なり0。
- 抵抗モデル（125°C・配線幅−20%）：共通41.135mΩ、J2分岐24.834mΩ、J3分岐26.095mΩ。50mΩ目標を維持。
- Gerber／drill／paste／BOM／CPLを再生成しCAM照合済み。D-030にRev.3のPOFV指定を外す提案を追記。D-019、66部品の配置、J1 Economic PCBA工程を保持。
- `PYTHONDONTWRITEBYTECODE=1 python3 hardware/kicad/qualification/issue-185-main-rev3/verify.py`：PASS。保存証跡・hash・変更範囲・文書リンク・manifestも確認。CSVのCRLFを保持し `git -c core.whitespace=cr-at-eol diff --check` を使用。

詳細：[報告書](docs/issue-185-main-rev3.md)、[証跡](hardware/kicad/qualification/issue-185-main-rev3/)、[製造引継ぎ](hardware/kicad/qualification/issue-185-main-rev3/manufacturing/quote-handoff.md)。PR #176の上に積むため、baseは `issue-175-main-dual-wing-final2`。

製造GOではない。名目0.10mmには製造公差保証を含めず、DFM受入れ・tenting・新見積・調達・材料最小値・実機検証は残る。USB入力抵抗は約5mΩ増加し、電源budgetを再計算済み。既存印刷警告61件を保持。repository BOMへ見積上の代替部品は採用しない。project-status.md／Dashboard変更なし。

Draftのまま提出。発注・課金・メーカーへのアップロード・mergeは行っていない。
