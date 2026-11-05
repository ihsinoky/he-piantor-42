Closes #141

HALL_5V/GNDを0.30mm、信号を0.10mmに分けたWing再配線を評価。16mm・17mmともKRT escalation offの単一runで独立4指標0とクラス別幅監査を通過。Main供給条件の事実と仮定、および32ケースのDC前後比較を追加しました。

Wing入力4.75V・11mA/個・125°C・最悪幅では、16mmは4.5669V、17mmは4.4813V。17mmには4.5V下限への不足が残ります。D-021改定・製造承認を行う変更ではありません。

検証：#138の保存10ケース再現、全DC解KCL残差<1e-7A、既存42570ファイル不変、追加のみ。報告書：docs/issue-141-wing-power-integrity.md。既存#137/#138成果物は不変。

Additional issues discovered: #138本文のGND端子7個表記は実inventoryの6接点と不一致。既存本文は変更せず本報告に記録。

Draftのまま提出。mergeは行いません。
