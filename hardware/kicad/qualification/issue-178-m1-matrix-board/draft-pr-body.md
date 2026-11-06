## 変更

Issue #178 の訂正版に従い、別々だった pitch9 評価候補から、16mm 3×3＋17mm 3×3の計18キーを1枚に載せるM1評価基板を追加します。同時押下時のホール効果相互作用とピッチを比較する基板です。16.5mmは対象外です。

- 128×80mm／2層／1.2mm。最近接のブロック間キー中心距離はnative基板の全81組を測定して35mm。
- 3 MUXは両ブロックの同じ列を6入力で担当。16mm=address0–2、17mm=3–5。GH14と6 GND接点は変更なし。
- D-021：信号0.10mm、電源/GND0.30mm、間隙0.10mm、via0.60/0.30mm、KRT escalation off。条件緩和なし。
- JITX定義・生成入力、最終native PCB、Gerber/PTH/NPTH、PCBAペースト、JLCPCB BOM/CPL（43部品）、実装図・製造注記・レビューZIPを追加。
- D-028にM1／ver.Aのバージョン定義と本基板の目的・構成を追記。既存の他Issue作業は含めません。

## 検証

自動配線は1回。独立DRCで検出した0.1414mmのGND不要枝1本だけを除去し、元の不合格記録を保存しています。最終は**全27ネットの独立4指標0 / 0 / 0 / 0**、シルクを含むDRC違反0、全幅・via寸法一致、指定した編集以外の転送差分0です。

Gerbonaraで全配線・pad・via・外形・146 PTH／4 NPTHをnativeと照合。BOM/CPL参照集合一致、全座標検査済み（GH14は本体中心への2.325mm補正を適用）。既存Wing回帰4テスト、新M1構成2テスト、JITX dry build、再生成一致、Ruff通過。

報告書：[`docs/issue-178-m1-matrix-board.md`](docs/issue-178-m1-matrix-board.md)

証跡：[`hardware/kicad/qualification/issue-178-m1-matrix-board/`](hardware/kicad/qualification/issue-178-m1-matrix-board/)

## レビュー事項

全146 plated viasに樹脂充填・銅キャップ／めっき（POFV / Type VII）を要求します。`manufacturing/FABRICATION.md` と全via一覧を必ず製造データと一緒に確認してください。工場受入・費用・assembler固有の部品角度／中心は未承認です。

磁気相互作用、治具、ADC settling・電源／GND共有・校正は実機評価が必要です。幾何／PCB資格確認はこれらの実測を代替しません。発注・課金は実施していません。**Draftのまま、mergeはPO判断です。**

Closes #178
