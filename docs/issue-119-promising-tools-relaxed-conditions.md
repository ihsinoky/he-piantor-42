# Issue #119 — 有望ツール × 4層・0.127mm（標準ビア）

**FIXED_CONDITION_FAIL。独立 KiCad DRC の未配線は A=19、B=1、C=27、D=31件。完成セルはなかった。** KRT・4層は #117 の28件から1件まで減ったが、U1 の V3V3 接続が残る。Freerouting は0.127mm入力に対して0.0952mm線分を30本出力し、寸法条件にも不合格。D-012／正式設計ルールを変更する根拠としての完成実証には達していない。

[Issue #119](https://github.com/ihsinoky/he-piantor-42/issues/119) の固定4セルを各1回実行した。新規ブランチ `issue-119-promising-tools-relaxed`、追加のみ、Draft PR提出、mergeしない。以下 E は [証跡ディレクトリ](../hardware/kicad/qualification/issue-119-promising-tools-relaxed/evidence/) を指す。指示書全文は E/instructions.md、Issue本文は E/issue119.json。

## 固定入力・Stage 0

#117 の証跡は、未mergeの `issue-117-four-layer-main` の commit `f7be53ff26390e89e0911a9f0fb05eee80b540b9` から `git show commit:path` で直接取得した。mainや作業ディレクトリの未追跡コピーを4層入力の出典にしていない。E/source-117-provenance.json は取得対象全ファイルのhashを保持し、E/source-117/ に元入力・修正済みsmoke・既存の等価性証明・比較用DRCを保存する。

| 取得時照合対象 | SHA256（一致） |
| --- | --- |
| #115固定2層 Main PCB | `46676e57e9618940a33c5e298244e97aaec61498a87aa7c58a264e444fc71e20` |
| #117 4層native Main PCB | `33f079d07bfb2dad9a76dce0667a1fd1371c94406df16f36ae17fe559d74af01` |
| #117 4層corrected Main DSN | `661d00c7d99adc270314a1a4940e64838999b948471f4d36a17aa9eac4d5e7f2` |

2層のMain/smokeは #115 ブランチのgit blobともbyte比較済み（E/source-115-provenance.json）。0.127mm入力は E/inputs/{main4,smoke4,main2,smoke2}/。元データを original.* として保持し、各ルール変更後のhashを E/equivalence-gate.json に固定した。

変更はルール値だけである。DSNの全width/clearanceルールを200→127µmへ明示変更し、逆変更した全文のbyte一致と全AST一致を確認した。wire/path、via padstack、部品、ネット、層役割等は変更していない。native PCBはzone clearance/min_thickness/thermal_gap/thermal_bridge_widthの0.20→0.127mmだけを変更し、逆変更後の全AST一致を確認した。既存銅箔3本（smokeは1本）は元の0.20mmを保持する。プロジェクトはmin_track_width/min_clearanceとDefault netclassのtrack/differential幅・clearance/gapを0.127mmにした。ビア0.60/0.30mm、穴・端面・annular条件、その他設定は保持した。E/prepare-inputs.py とproject全差分に証明を保存した。

4層は F.Cu=signal、In1.Cu=power/GND、In2.Cu=signal、B.Cu=signal の #117 構成を保持する。4層smokeは #117 修正済み `smoke-02` の既存ネットNプレーン・solid接続をそのまま用い、ネット追加はない。このsmoke固有設定はMainのGND/thermal設定へ移していない。

等価性ゲート確定 `2026-11-04T10:04:36.543155+00:00` → 対応条件smokeの4指標0確認 `2026-11-04T10:05:48.976581+00:00` → 全Main開始 `2026-11-04T10:06:09Z`。Stage 0 は保守的開始09:58 UTCから約8分で完了した。4層fab/KRT/Freeroutingと2層fabのsmokeを各1回実行し、全て **必須未接続／異ネット接触／物的違反／説明不能な転送変更 = 0 / 0 / 0 / 0**、独立KiCad DRCも未配線0・違反0だった。元の0.20mm配線と追加0.127mm配線の保持を読戻している。

## ツールと固定構成

fab_routerは #103/#117 と同じ commit `69cf598db98c136bff16bbe02bccdded95674b18`、公開 `routeDsn` とAPI既定、全体budget 1800000msのみ明示。KRT v0.23.8は commit `c64c0db25e6cf23afa6769ee05665c7ea22b3ff2`、binary SHA256 `4411ccf3f074f519d8d69be29ac58b46ca7c4c2fe4f4be889d253d40996c2c0f`。既存manifestとの全ソース／検査runtime hash照合は差分0（E/runtime-revalidation.json）。本体を編集していない。

KRTは `--escalation off --track-width 0.127 --clearance 0.127 --via-size 0.60 --via-drill 0.30 --layers F.Cu In1.Cu In2.Cu B.Cu --layer-costs 1 -1 1 1`。smoke/Main双方で無改変CLIの設定解決直後・配線開始前に停止するtrace読戻しを実施し、GridRouteConfigとescalation offを確認した。既定との差分を E/configuration/ に保存した。内部tierに寸法を委ねていない。

Freeroutingは公式v2.5.0 JAR（SHA256 `f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7`）、Temurin 25.0.5+8。#95 Run 2のargvとパスを除き完全一致を検証した（E/configuration/freerouting-vs-95.json）。fanout/optimizer=true、automatic_neckdown=false、headless、-Xmx2g、100pass上限、-mt 0、-is sequential、job timeout20分、専用user-data/tmp、telemetry offを維持した。CLIの `router.max_threads=1` は後続の `-mt 0` に上書きされ、実ログはautorouter single-threaded／optimizer.max_threads=3である。

Freeroutingの実効設定・stage読戻しは E/runs/main4/free/effective-settings-readback.json の行番号付きログ抜粋。fanoutは実動作し、18pass後の停滞停止から最良27件へ復元し、optimizerは未配線27件のためskipした。保存freerouting.jsonはCLI前の既定値であり、全実効job dumpではない。-isの最終値や全scoring値は直接dumpされず、startupの「DSN=127 → 0.03175mm」という表示も実寸の証拠として採用しない。保存SESを独立KiCadへ取込み、実寸分布を下表に示す。

## 全4セルの実測

独立KiCad 9.0.9でSES転送またはnative出力の読戻し、元の0.127mmプロジェクトを使ったzone再充填、全severity DRC、全非配線AST比較、元配線の中心線被覆（2nm）を全セルで実行した。未完成でもDRC生JSONを保存した。

| 項目 | A fab×4層 | B KRT×4層 | C Freerouting×4層 | D fab×2層 |
| --- | --- | --- | --- | --- |
| 独立未配線数 | 19 | 1 | 27 | 31 |
| 4指標（順序は下記） | null / null / null / null | null / null / null / null | null / null / null / null | null / null / null / null |
| 自己申告未配線 | 11接続 | 1 open pad pair / V3V3失敗1ネット | 27接続 | 17接続 |
| 幅mm:本数 | {"0.127": 296, "0.2": 3} | {"0.127": 554, "0.2": 3} | {"0.0952": 30, "0.127": 487, "0.2": 3} | {"0.127": 364, "0.2": 3} |
| ビア外径/drill mm:個数 | {"0.6/0.3": 122} | {"0.6/0.3": 80} | {"0.6/0.3": 38} | {"0.6/0.3": 118} |
| 層別トラック本数 | {"B.Cu": 21, "F.Cu": 225, "In1.Cu": 0, "In2.Cu": 53} | {"B.Cu": 40, "F.Cu": 462, "In1.Cu": 0, "In2.Cu": 55} | {"B.Cu": 17, "F.Cu": 466, "In1.Cu": 0, "In2.Cu": 37} | {"B.Cu": 100, "F.Cu": 267} |
| 配線プロセス経過秒 | 237.104 | 114.561 | 153.799 | 325.832 |
| 停止理由 | stagnant（7 passes） | CLI正常終了・最終再採点でもopen | 18 passes停滞・最良復元・optimizer skip | stagnant（12 passes） |
| exit / 外側timeout | 0 / false | 0 / false | 0 / false | 0 / false |
| 生DRC（印刷61件を除く） | {"track_dangling": 23} | {} | {"track_width": 30} | {"hole_to_hole": 2, "track_dangling": 33} |
| 説明不能な銅箔/非配線転送差分の生件数 | 0 | 0 | 0 | 0 |

4指標の順序は **必須未接続／異ネット接触／物的違反／説明不能な転送変更**。今回は全セルで未配線が残るため、規定どおり全値null。生DRCのshort 0や転送差分0を合格指標0へ代入しない。印刷指摘は全セル共通でsilk_overlap12 / silk_over_copper5 / text_height44。DRC warningもrawに保持し、物的指摘を黙って除外していない。

**Bの層利用：** F.Cu462 / In1.Cu0 / In2.Cu55 / B.Cu40本。#117のKRTは454 / 0 / 42 / 0本だった。今回B.Cuへ40本が生成されたことは実測事実だが、それだけを改善の原因と断定しない。全4層出力でIn1信号トラック0を確認し、GNDゾーンも再充填した。

**Cの寸法不適合：** 487本は0.127mm、30本は0.0952mm、既存3本は0.20mm。全ビアは0.60/0.30mmを保持した。DSNルールとCLIは固定済みだが、ツール出力に下限未満の線分が生じた。30本をKiCadがtrack_width errorとして指摘する。automatic_neckdown=falseの適用はログで確認できるものの、この幅縮小の内部原因は本測定では確定していない。smoke合格はMainでのルール遵守保証ではない。設定変更・補正・再実行はしない。

**自己申告と独立値：** fabはA 11→独立19、D 17→独立31で不一致。Main完成の判定に自己検査violations=0を用いない。KRTはJSON_SUMMARY_MIN/JSON_REGRADEで36ネット成功、V3V3失敗、open pair1、未接続pad deficit2、escalations0を報告し、独立DRCでもV3V3の欠線1件を確認した。Cは自己27と独立27が一致するが、自己violations0は幅違反30件の独立結果と一致しない。

**出力プロジェクト書戻し：** A/C/Dの差分は `/meta/filename` のmain→outだけ。Bはmin_via_drill未定義→0.3mmとkicad_routing_tools由来メタデータを追加した。min_track_width/min_clearanceやnetclassの下限緩和はない。書戻しの存在自体は記録し、#115の「書戻しなら失敗」という別条件と混同しない。全差分は各 inspection/.../transfer-diff.json、raw .kicad_proは runs/ に保存した。

## 残接続とU1集中

全ネット／端点のdescription、座標、UUIDは inspection/{main4,main2}/{tool}/unconnected-net-endpoints.json とdrc.json。ネット別件数は次の実測値。

- A：`{"GND": 3, "HALL_5V": 3, "HALL_PWR_EN": 1, "MUX_A0": 1, "MUX_A1": 1, "MUX_A2": 1, "QSPI_SD0": 1, "QSPI_SD1": 1, "SWCLK": 2, "SWDIO": 1, "USB_DP": 1, "V1V1": 1, "XOUT_XTAL": 2}`
- B：`{"V3V3": 1}`
- C：`{"ADC_A": 1, "ADC_C": 1, "CC2": 1, "GND": 13, "HALL_5V": 2, "QSPI_SS_FLASH": 1, "V3V3": 6, "WING_EN": 1, "XIN": 1}`
- D：`{"GND": 5, "HALL_5V": 3, "HALL_PWR_EN": 1, "MUX_A0": 1, "MUX_A1": 1, "MUX_A2": 1, "MUX_OUT_B": 1, "QSPI_SD0": 1, "QSPI_SD1": 2, "QSPI_SD2": 2, "QSPI_SD3": 1, "QSPI_SS_FLASH": 1, "QSPI_SS_MCU": 3, "SWCLK": 1, "SWDIO": 1, "USB_DP": 4, "V1V1": 1, "XOUT": 1}`

| 独立DRCの分布 | #117 4層0.20mm | 今回4層0.127mm |
| --- | --- | --- |
| fab 未配線総数 / U1 pad明示端点を含む行 | 26 / 14 | 19 / 9 |
| KRT 未配線総数 / U1 pad明示端点を含む行 | 28 / 27 | 1 / 0 |

このU1件数はDRC端点のliteralな「Pad ... of U1」を数えたもので、track端点の先の部品を含めない。Dは31件中12行、Cは27件中3行がU1 pad明示端点を持つ。**KRTの0行を「U1問題が解消」とは解釈できない。** Bの残りV3V3はtrack間DRCなので、保存出力をKiCad接続APIで別に追跡した。片側の島には **U1.48/U1.49** のみ、他側の電源島にはU1.1/.10/.22/.33/.42/.43/.44、U4.5、decoupling等が属する（E/inspection/main4/krt/residual-connected-pad-components.json）。残課題はなおU1近傍の電源接続である。最近傍による推測ではなく、GetConnectedPads/GetConnectedTracksをたどった実測である。

CはGND13件・V3V3 6件に集中する。AはGND/HALL_5V各3、SWCLK/XOUT_XTAL各2などへ残る。U1の明示pad端点が減っても、電源分岐・stub間欠線や物的違反が残るため、端点の表現変化だけを完成と扱わない。

## 既存結果との比較と次の判断材料

値の添字相当 `(D)` は独立KiCad DRC、`(R)` はrouter自己申告。未試行は「—」とし、異なる検査主体の数値を同一精度のランキングにしない。

| ツール | 2層0.20mm | 4層0.20mm | 2層0.127mm | 4層0.127mm |
| --- | --- | --- | --- | --- |
| fab_router API既定系 | 16(R), #103 | 26(D), #117 | **31(D) / 17(R), D** | **19(D) / 11(R), A** |
| KRT escalation off | 28(D), #115 | 28(D), #117 | — | **1(D), B** |
| Freerouting v2.5.0 fanout/optimizer on | 38(R), #95 | — | — | **27(D/R), C・幅違反あり** |

出典：[fab #103](issue-103-fab-router-falsification.md)、[KRT #115](issue-115-kicad-routing-tools-escalation-off.md)、[Freerouting #95](issue-95-freerouting-v250-run2.md)、[#117固定branch報告](https://github.com/ihsinoky/he-piantor-42/blob/f7be53ff26390e89e0911a9f0fb05eee80b540b9/docs/issue-117-four-layer-main-and-wing-outlook.md)。#117の比較DRCはE/source-117/に同branchから保存した。#113のKRT 5件はescalationによる混合幅・下限書戻し込みであり、「2層0.127mm固定」セルには転用しない。

**実測に基づく判断材料：** 同じ独立DRCでは4層fabは26→19（7件減）、4層KRTは28→1（27件減）。今回fabの4層A=19は2層D=31より12件少ない。この差は4層＋GNDプレーンを含む構成全体の差であり、追加層だけの因果効果や再現性を証明する統計ではない。2層fabの0.20mm旧16件は自己値なので、独立31件と直接引き算しない。同じ自己値で見ても16→17であり、幅を細くすれば常に改善するという結果ではない。

**推定・PO向け論点：** 自動完成を示したセルはないため、D-012や正式設計ルールの変更・製造承認を本測定から確定しない。KRT×4層×0.127mmは標準ビアと物的DRCの条件を保ちながら残接続を局所化した最も近い観測結果であり、次の意思決定ではU1.48/.49のV3V3島を含む出力の設計レビューが具体的な材料になる。手直し・再試行は本Issueでは実施していない。Freeroutingの未配線減少は幅不適合を伴うので、同じ製造条件で成立した改善とは扱えない。配置の完成不可能性やツール一般の優劣をこの各1回の測定から断定しない。

価格に関する「0.127mm追加料金なし／4層化5枚+$4」はPO指示書の前提であり、このIssueではメーカー見積を再取得していない。現物製造やD-012の正式変更を行った事実はない。

## 監査・提出

全Main配線は `2026-11-04T10:06:09Z` 開始、最終Dは `2026-11-04T10:11:35Z` 終了。smoke/Mainの再実行0、結果を見た設定変更0。E/main-freeze.json はMain前の設定・スクリプト・ゲートhash、E/processes/ は全argv/cwd/環境/UTC/経過秒/終了コード/timeout、E/verification.json は入力不変・ゲート順序・固定4回・保存DRC・スクリプト不変・追加のみを検証する。E/manifest.json は全証跡hashを保持する。

保守的開始09:58 UTC、Stage 0期限10:58 UTC、全体期限12:58 UTC（3時間）。提出時刻・経過時間とDraft PR番号は E/submission.json に記録する。作業gitは `/tmp/issue-119-main/git` を使い、元.gitを変更しない。既存ファイル・正式設計・他Issueの証跡を変更しない。raw PCB/SES/logの空白はbyte証拠として保持し、著作ファイルの構文／JSON／whitespace検査と区別する。
