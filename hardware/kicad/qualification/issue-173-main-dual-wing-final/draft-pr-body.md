C26を(91.8,77.5)から(94.5,77.2)mmへ移動した。SW2との接触は解消したが、移動先でC26.2とJ3.15の接触を作り、preflightがclearance1／solder_mask_bridge1を検出した。必須停止条件に従って停止し、全体配線0回（上限1）、局所rip-up0回。配置の不備であり、D-019の限界とは判断しない。1210最終候補は未成立、製造GOではない。

ガードがDRC失敗時に実ルータ起動前に拒否することを実測。既存53部品を含むほか65部品の座標・角度と種配線の全segment/viaを保持した。KRT2055 source hashesも変更なし。

不合格時の指示に従い、#169の合格済みseed-a（0805、全44ネット・4指標0）を対応BOM/CPL・レビューCAM・資格証跡と共に変更せず整理した。116コピーを起点コミットのGit blobとハッシュ照合。0805出力Cの実効容量の余裕が弱く、動特性保証がないことを既知の制限として明記した。1210 BOMと旧CAMを混用しない。採用判断はPOへ戻す。

新候補の資格確認以降の抵抗再抽出・製造データ生成・POFV再分類・確定PCBA見積は未実施。D-019変更・発注・課金・mergeなし。

検証: placement-check、native preflight、guard拒否、verify.py（証跡整合はPASS、候補preflightはFAIL）。

報告: docs/issue-173-main-dual-wing-final.md
証跡: hardware/kicad/qualification/issue-173-main-dual-wing-final/

Refs #173. baseはissue-169-main-dual-wing-followup。Draft、Issue自動close・mergeなし。
