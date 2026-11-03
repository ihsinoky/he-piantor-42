# Issue #93 — Freerouting v2.5.0 公式JAR限定再評価

2026-11-03。**smoke成功、Run 1は18passesで停滞停止し最良・最終58未配線。内部例外は観測範囲で解消、pass制御は一部解消、完成見通しは未解消。条件不成立のRun 2は実施せず、PMOには現時点で継続候補へ昇格させないことを推奨する。**本評価の合格はMain配線の技術合格、方式採用、製造可能、Human Gate通過を意味しない。方式採用・製品要求変更・mergeはPOの決定事項。

## 開始条件・証拠

[Issue #93](https://github.com/ihsinoky/he-piantor-42/issues/93) 全文・コメントを開始時に確認し、[issue93.json](../hardware/kicad/qualification/issue-93-freerouting-v250-jar/evidence/issue93.json) に保存。`git fetch origin` 後のmainは `0b78c9e138ef89c913337fe613badb4f5eee0aa4`。[PR #92](https://github.com/ihsinoky/he-piantor-42/pull/92) はOPEN・mergedAt=null。本ブランチはorigin/mainから作成し、#92のcommitを含めない。#91は同PRブランチから読取りだけ行った。

以下、`E/` は [本評価の新規証拠](../hardware/kicad/qualification/issue-93-freerouting-v250-jar/evidence/)、`P/` は [#87 resume-01の保存証拠](../hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/) を表す。既存の#87/#89/#91の証拠・記録は変更しない。

- Mainは `P/processes/main-restore/corrected.dsn` のbyte同一コピー。開始時のSHA256は `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2`、Issue固定値と一致。
- smokeは `P/processes/smoke-restore/corrected.dsn`。SHA256 `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9` は既存 `smoke-restore/record.json` と一致。
- 開始・入力照合は `E/start.json`、実行直前・直後のhash、完全argv・UTC時刻・環境・stdout/stderr/SES/設定のhashは各 `E/processes/*/record.json`。実行したファイルは `E/run-router.py`。

## 配布物・健全性ゲート

[公式リリース](https://github.com/freerouting/freerouting/releases/tag/v2.5.0) から取得した [freerouting-2.5.0.jar](https://github.com/freerouting/freerouting/releases/download/v2.5.0/freerouting-2.5.0.jar) のSHA256は `f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7`。release APIのasset digestと一致。

実行用は [Temurin 25.0.5+8 JRE Linux x64](https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.5%2B8/OpenJDK25U-jre_x64_linux_hotspot_25.0.5_8.tar.gz)。SHA256 `6fac98f0c8202efc3135a9e9e42aa61963ec42d1c5cbb40caf231e7b14a24ef6` をAdoptium APIのchecksumと公式 `.sha256.txt` の両方に照合した。JRE・JARとも `~/workspace/tools/issue-93/` 配下。公式API応答、取得URL、hashと一致判定、`java -version` は `E/official/` に保存。

最初にTemurin 21.0.13+9 JREも取得・hash照合した（SHA256 `a535a1df9c6284d9618872984e026ae0352d1f7e9e0605425c0e6114f47351dd`）。ただしJARのmanifestとclassを**実行前に静的検査**するとmajor version 69（Java 25）だったため、21はrouterに使用せず25を取得した。JRE 21以上という許可範囲内であり、smokeのやり直しではない。manifestのBuild-Revisionは `b647a2f824cfbc54bc4dcaee71b03b7cd945eb76`。router改造・fork・自前ビルド・native実行はない。

smokeは1回のみ、11:03:08.923–11:03:13.063 UTC、4.139454秒、exit 0。例外0、stderr空、SES 976 bytes生成。初期1未配線→pass 1で0→pass 2で0、job COMPLETED。`E/smoke-gate.json` にMain実行許可を記録した。smoke結果をMainの物理合格と扱わない。

## コマンド・保存設定の対応と比較の限界

Run 1は `P/processes/main-initial-route/record.json` の引数を保持したJAR起動。`-Djava.awt.headless=true -Duser.language=en -Duser.country=US -Xmx2g`、専用tmp/user-data、`--gui.enabled=false --api_server.enabled=false -da --profile.allow_telemetry=false --router.automatic_neckdown=false --router.max_threads=1 --router.optimizer.enabled=false --router.fanout.enabled=false --router.job_timeout=00:20:00 -mp 100 -mt 0 -is sequential`。差分はJRE/JAR版・保存先パスとTZ=UTCの明示のみ。DISPLAYおよびFREEROUTING__環境変数は除去。telemetryはCLI指定に加えて詳細logの `Analytics are disabled` を確認。

実行後の `user-data/freerouting.json` をそのまま保存する。ただし新版logには **CLI適用前にdefaultを保存した** とあり、このファイルをruntime実効値の完全なdumpとは扱えない。旧 `effective-start-settings.json` もtransientの停止値を記録しないという#89の限界を維持する。

| 項目 | v2.1.0保存値／指定 | v2.5.0保存JSON・実行証拠 |
| --- | --- | --- |
| 版・headless | version=2.1.0、gui.enabled=false | JSON version=2.5.0、gui.enabled=trueは起動前default。実際はheadless指定、GUIなし、配線job開始 |
| pass上限 | router.max_passes=100、`-mp 100` | JSON router.autorouter={}。CLI適用logは100、旧名→autorouter.max_passesへの互換警告。実停止は結果表で判定 |
| timeout | job_timeout=00:20:00 | JSON項目なし、CLI適用logは00:20:00。外側runnerは1260秒安全上限 |
| neckdown | automatic_neckdown=false | JSON項目なし、CLI適用logはfalse。最終job値の直接dumpはない |
| autorouter threads | router.max_threads=1 | JSON項目なし。CLIでは1の後に `-mt 0` がmax_threads=0を適用。実行logはautorouter pass single-threaded |
| optimizer threads | optimizer.max_threads=0、`-mt 0` | JSON optimizer={}。新版短縮CLIはrouter.max_threadsへ写像し旧版と意味が異なる。実行logはoptimizer.max_threads=3。Run 1ではoptimizer無効のため配線pass並列化を意味しない |
| optimizer | `--router.optimizer.enabled=false`、旧JSONではenabled項目なし | JSON optimizer={}。CLI適用false、実行stageの有無は詳細logで確認 |
| fanout | fanout.enabled=false | JSON fanout={}。CLI適用false、runtime pre-pass判定 `settings.fanout.enabled=false` |
| item selection | `-is sequential`、旧保存JSONに項目なし | GlobalSettings側はSEQUENTIALへ写像するがCliSettings側に-is写像なし。最終値は判定不能。Run 1ではoptimizer無効 |
| telemetry | allow_telemetry=false、disable_analytics=true | JSONはtrue/falseのdefault。CLI無効化指定および `Analytics are disabled` logで確認 |
| board固有設定 | 旧trace_pull_tight_accuracy=500、scoring等を保存 | 新JSONは疎な{}。DSN由来5項目、CLI6項目、API Settings priority 70由来45項目をmergeしたlogあり。全scoring値の同一性は保証しない |

根拠はtag相当commit固定の `E/official/{GlobalSettings,CliSettings,SettingsMerger,RouterSettings,RoutingJobScheduler,AutorouteBatchLoop}.java.txt` および `sources.json`。API Settingsはschedulerがjob値を再mergeする内部名であり、外部APIを使用した意味ではない。設定不一致は再実行で補正しない。

DSN読込みlogは `DSN=200.0 → board=2000 (0.05 mm)` と表示する。入力には `(resolution um 10)`、`(unit um)` があり、旧parityは0.20 mmを確認済みだが、新版に対して同じ読戻し検査は未実施。表示換算の問題か実値の差かは本評価で確定せず、同一材料条件の物理合格を主張しない。以上により、**指定した同一コマンド条件での観測比較であり、全項目の同一実効値を証明した対照試験ではない**。

## 結果・判定・段階ゲート


| 指標 | v2.1.0保存結果 | v2.5.0 JAR Run 1 | Run 2 |
| --- | --- | --- | --- |
| 指定／完了pass | 100／512（超過） | 100／18（停滞停止、100境界は未到達） | 条件不成立・未実施 |
| 内部例外 | maze catch 371件：NPE 367、配列境界4 | maze 0、その他routing ERROR 0、stderr空 | — |
| 未配線推移 | 1:88、25:60、50:60、100:53、200:41、201:35、300:38、400:42、500:40、512:36 | 初期128、1:58、2:104、3:103、4:102、5:103、6:102、7:103、8:58、9:103、10:103、11:102、12:58、13:103、14:103、15:102、16:58、17:103、18:103 | — |
| 最良／最終pass／復元後最終 | 35（pass 201）／36（512）／35 | 58（初到達pass 1）／103（18）／58 | — |
| プロセス経過秒 | 1203.752413 | 112.004141 | — |
| 終了コード | 0 | 0、自然終了、外側timeoutなし | — |
| SES | 保存済み・Main物理未検証 | 26168 bytes、保存のみ・未取込み | — |

[再集計スクリプト](../hardware/kicad/qualification/issue-93-freerouting-v250-jar/evidence/summarize.py)、[集計JSON](../hardware/kicad/qualification/issue-93-freerouting-v250-jar/evidence/summary.json)、[全18pass CSV](../hardware/kicad/qualification/issue-93-freerouting-v250-jar/evidence/run-1-pass-history.csv)、[旧512pass CSV](../hardware/kicad/qualification/issue-93-freerouting-v250-jar/evidence/baseline-v210-pass-history.csv)。旧raw stdout/stderrは旧recordのhashとも照合する。旧371件はmaze catchの定義であり、全routing ERRORではない。今回の再集計ではそれとは別に `Error during autoroute_item` のNPEが3件あり、旧stdout全ERRORは374件（NPE計370、配列境界4）。既存報告・rawは変更せず、母数を区別する。stdout/stderrに重複する旧例外は二重計上しない。

Run 1は11:03:19.989 UTC開始、11:05:11.993 UTC終了。配線stageは108.17秒。詳細logに初期128未配線、fanout false、autorouter single-threadedを確認し、optimizer stageは実行されていない。pass 8/12/16では旧盤面の復元後の値58が完了INFOに出る（詳細logのpass統計は復元前の値を含む）。従ってCSVはINFO完了行の観測値として扱う。終端logは「best score 405.13がpass 8から0.5超改善せず、18passesで停止」、続いて103未配線の盤面を最良58へ復元し、最終stage報告58・job COMPLETED・SES保存を示す。COMPLETEDやexit 0は全接続を意味しない。

- **(A) 内部例外：解消（今回の18pass観測範囲）。** maze NPE/配列境界0、その他routing ERROR 0、未捕捉例外0。#91のnative serialization障害もなくSES生成まで進んだ。旧512passと同じ長さの無例外保証や一般的な欠陥修復の証明ではない。詳細logのversion checkにだけネットワーク制限によるProtocolExceptionが1診断あるが、捕捉されて配線を継続しておりrouting例外とは区別する。
- **(B) passes制御：一部解消。** 観測した実行では指定100を超過せず、18で自然停止した。旧版の512超過と異なる挙動は確認したが、停止理由は停滞であり**100完了・101非実行という境界動作は検証できていない**。固定ソースには `currentPass > autorouter.maxPasses` の停止条件があるが、それだけで実行上の解消と認定しない。
- **(C) 改善傾向・完成見通し：未解消。** 初期128→最良58への進展はあるが、pass 1後に最良更新がなく、残り58で停滞停止。旧最良35より完成に近づいた証拠もない。ただし同一実効値の保証に限界があるため、アルゴリズム一般の性能回帰や固定配置の完成不可能とは断定しない。

[Run 2 gate](../hardware/kicad/qualification/issue-93-freerouting-v250-jar/evidence/run-2-gate.json) はfalse。(A)の観測改善と未配線残存だけでは足りず、(B)を解消とする実測がないため、厳密な条件付き実行は行わない。時間残があっても100到達を狙う再実行・設定探索はしない。Main router実行は合計1回。

未配線0に到達していないので、SES取込み・DRC・独立4指標の測定は実施しない。**required未接続=null、wrong-net接触=null、対象材料違反=null、説明不能な受渡し変化=null**。router表示の0 violationsは独立4指標の0／合格ではない。判断は [assessment.json](../hardware/kicad/qualification/issue-93-freerouting-v250-jar/evidence/assessment.json) にも保存した。

## PMO向け技術推奨・実施範囲・時間

**現時点では、v2.5.0 JARをMain完成へ向けた継続候補に昇格させないことを推奨する。** JARによって配線アルゴリズムの観測と例外なしの完走は可能になった一方、58未配線の停滞と実効設定の対応限界が残る。時間・pass数の追加や設定探索による完成を支持する証拠は得ていない。将来の追加評価をPMOが提案する場合も、先に最終job設定・実効材料ルールの読戻し方法と100停止の検証方法を確定した別の承認範囲が必要。本Issueから追加router実行を許可する提案ではない。方式採用・製品要求変更・mergeは判断しない。

開始は保守的に2026-11-03 11:00:00 UTC（初回時計観測11:00:53）。120分期限13:00、router打切り12:40。smokeとRun 1は11:05:11.993までに終了し、時間切れ打切りは発生していない。全時間に取得・準備・smoke・待機・集計・報告・commit/push・PR作成・CI確認を含め、待ち時間の除外なし。最終提出時刻と総所要時間はDraft PR本文、および提出直前記録 `E/submission.json` に記載する。

実施：開始main／PR #92状態・Issue全文確認、入力hash照合、公式JAR／Temurin JRE取得と公式digest照合、実行前class互換性検査、smoke 1回、Run 1を1回、保存JSON／logの設定対応表、旧raw再集計と対照、(A)(B)(C)および段階ゲート判定、証拠・本文保存、指定ブランチcommit/push・Draft PR提出・CI確認。

未実施：条件不成立のRun 2、100停止の実測、最終job設定全値／材料実効値の直接読戻し、SES取込み・DRC・独立4指標。入力改変・配置変更・材料緩和・層数変更・router改造／fork／自前ビルド・native再試行・他版／別backend実験・製造出力・製品設計・方式採用・mergeは行っていない。#87/#89/#91の旧証拠・記録、PR #92、任意のDashboard等は変更しない。
