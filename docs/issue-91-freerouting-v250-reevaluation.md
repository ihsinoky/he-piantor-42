# Issue #91 — Freerouting v2.5.0 限定再評価

2026-11-03。**評価未完了：公式 native CLI が最初の pass 完了前に致命エラーで停止し、(A)(B)(C) はすべて判定不能。** Run 1 は1回実施、Run 2 は条件不成立で未実施。PMOには、この配布物を現時点の実行可能な継続候補とせず、JAR版による再評価の要否を別途判断することを推奨する。v2.5.0のアルゴリズム一般が未改善という判定ではない。

本評価の合格は、Main配線の技術合格、方式採用、製造可能、Human Gate通過を意味しない。方式採用・製品要求変更・mergeはPOの決定事項である。

## 開始条件・入力

[Issue #91](https://github.com/ihsinoky/he-piantor-42/issues/91) の全文とコメントを開始時に取得（[保存](../hardware/kicad/qualification/issue-91-freerouting-v250/evidence/issue91.json)）。開始時のHEAD・remote main・[PR #90](https://github.com/ihsinoky/he-piantor-42/pull/90) merge commitはすべて `0b78c9e138ef89c913337fe613badb4f5eee0aa4`。既存cloneの.gitは書込み可能で、指定ブランチを直接作成した。

以下、`E/` は [今回の証拠ディレクトリ](../hardware/kicad/qualification/issue-91-freerouting-v250/evidence/)、`P/` は [#87 resume-01 の既存証拠](../hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/) を指す。

- 入力は `P/processes/main-restore/corrected.dsn` のbyte同一コピー。開始時・実行直前・終了後ともSHA256は `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2`。
- `P/main-dsn-parity.json` は `PASS_WITH_SCOPE`、各padのrouter読戻し検証済み、実効間隔matrix・netclass幅0.20 mmの記録を確認。元の1.2 mm厚、穴、NC、印刷等のDSN非表現情報は元KiCad側に保持され、SES後検査がなお必要という限定も維持する。
- `P/processes/main-independent-diff/stdout` はルール1値だけのbyte局所変更、その他node不変。restore record、corrected-reader parity record、既存submission-integrityの同一hash、およびmain-initial-routeのコマンドを照合し、Issue指定の旧入力として同定した。
- 旧raw stdout/stderrは旧recordのSHA256と一致。旧証拠は無変更（[開始記録](../hardware/kicad/qualification/issue-91-freerouting-v250/evidence/start.json)、[整合性記録](../hardware/kicad/qualification/issue-91-freerouting-v250/evidence/integrity.json)）。

## 配布物・コマンド対応・実効値の限界

[公式v2.5.0リリース](https://github.com/freerouting/freerouting/releases/tag/v2.5.0) の [freerouting-cli-2.5.0-linux-x64.tar.gz](https://github.com/freerouting/freerouting/releases/download/v2.5.0/freerouting-cli-2.5.0-linux-x64.tar.gz) を `~/workspace/tools/freerouting-2.5.0/` に取得。SHA256は `64a957a9ef2a2fbde6ab2001bb32800f5ba34f9fd15575e363512934b870d63a` で公式release APIのdigestと一致。展開済み実行ファイルのhashも [distribution.json](../hardware/kicad/qualification/issue-91-freerouting-v250/evidence/official/distribution.json) に保存した。自前ビルド・改造なし。tarは所有者復元不可を報告したが、実行ファイルの展開・起動は成功した。

バナーは `Freerouting CLI v2.5.0 (build-date: 2026-10-05)`。`--version` は未対応で、入力なしエラーになるがバナーを出力する。[version.txt](../hardware/kicad/qualification/issue-91-freerouting-v250/evidence/official/version.txt) と [help.txt](../hardware/kicad/qualification/issue-91-freerouting-v250/evidence/official/help.txt) を保存。両probeはDSNを渡さず、配線実行ではない。probe時刻表示はUTC+09、Run 1はTZ=UTCで、runnerのUTC記録を時刻の基準とする。

Run 1は旧記録の短縮・長形式router引数をすべて保持した。[完全なargv・環境・開始終了・hash](../hardware/kicad/qualification/issue-91-freerouting-v250/evidence/processes/run-1/record.json) と [実行runner](../hardware/kicad/qualification/issue-91-freerouting-v250/evidence/run-router.py) を保存。差分はnative実行ファイルへの置換、入力／出力／user-dataの保存先、診断用 `--router.result_json=...` の追加。Java起動部・`-D...`・`-Xmx2g` はJAR専用なのでnativeには渡さない。headlessはnative入口で強制され、DISPLAYも除去。LANG/LC_ALL=C.UTF-8、FREEROUTING__環境変数なし、専用user-data、telemetry無効を指定した。

| 旧指定 | v2.5.0の対応・今回の確認範囲 |
| --- | --- |
| `-mp 100` | `router.autorouter.max_passes=100` への互換パス。非推奨警告とCLI適用ログあり。実停止未検証 |
| `-mt 0` | GlobalSettingsではoptimizer.maxThreads=0。一方CliSettingsではrouter.max_threads=0へ写像。今回のログにも1→0の適用がある |
| `--router.max_threads=1` | 指定は保持したが上記競合あり。autoroute pass自体は公開ソース上single-threaded。最終統合値のruntime captureなし |
| `-is sequential` | GlobalSettingsでoptimizer.itemSelectionStrategy=SEQUENTIAL。CliSettingsには短縮mapがなく、最終job値の保証なし |
| neckdown=false、optimizer=false、fanout=false | 同名長形式を保持、CLI適用ログあり。配線段階の実効値は未検証 |
| job_timeout=00:20:00 | 同名長形式を保持、適用ログあり。致命エラーで先に停止したためtimeout動作未検証 |

根拠は `E/official/` のv2.5.0 tag固定 `GlobalSettings.java.txt`、`CliSettings.java.txt`、`CliRunner.java.txt`、`AutorouteBatchLoop.java.txt` 等。`user-data/freerouting.json` は起動時のdefault保存であり実効設定の証明に使わない。ログの最終mergeにはAPI Settings priority 70も含まれる。さらにDSN幅・間隔について `DSN=200.0 → board=2000 (0.05 mm)` と出ており、今回の実効0.20 mmを保証する読戻しは得られていない。表示換算だけの問題か実値の問題かは未確定で、入力を補正し直していない。

したがって**同一引数を試したRun 1の起動失敗記録であり、同一実効条件での完走比較を達成したとは扱わない**。この失敗後の設定変更・再実行は行わない。

## 結果と段階ゲート

| 指標 | v2.1.0 保存結果 | v2.5.0 Run 1 | Run 2 |
| --- | --- | --- | --- |
| 指定／最終完了pass | 100／512（超過） | 100／null、完了ログ0本 | 未実施 |
| 内部例外 | maze catch ERROR 371件 | uncaught UnsupportedFeatureError 1件。maze ERRORは0件だが探索到達の証拠なし | — |
| 未配線推移 | pass 1:88、25:60、50:60、100:53、200:41、201:35、300:38、400:42、500:40、512:36 | サンプルなし（最良・最終ともnull） | — |
| 最良／最終pass値 | 35（201）／36（512）。終了時は履歴最良35を保存 | null／null | — |
| 経過秒 | 1203.752413 | 27.353819（致命エラー検知後のworker停止まで） | — |
| 終了コード | 0 | 143、workerのSIGTERM。自然終了コードはnull | — |
| SES | 保存済み、物理未検証 | 生成なし | — |

[集計JSON](../hardware/kicad/qualification/issue-91-freerouting-v250/evidence/summary.json)、[旧512pass全推移](../hardware/kicad/qualification/issue-91-freerouting-v250/evidence/baseline-pass-history.csv)、[再集計スクリプト](../hardware/kicad/qualification/issue-91-freerouting-v250/evidence/summarize.py)。旧例外内訳は [#89報告](issue-89-freerouting-main-analysis.md) のNPE 367件・配列境界4件（詳細付与の有無を含む）を引き継ぐ。

Run 1は10:52:22.885045 UTC開始。10:52:23.282763720 UTCのjob開始ログ後、stderrに `SerializationConstructorAccessor class not found for declaringClass: app.freerouting.board.model.items.ObstacleArea`。`BoardSnapshotManager.serialize → getHash → BasicBoard.getHash → AutorouteBatchLoop.run:65` のSTARTEDイベント用hash計算で未捕捉ErrorとなりThread-1が終了した。公開ソースでもこのhash取得は初期未配線計測と配線loopより前にある。

[raw stdout](../hardware/kicad/qualification/issue-91-freerouting-v250/evidence/processes/run-1/stdout)、[raw stderr／全stack](../hardware/kicad/qualification/issue-91-freerouting-v250/evidence/processes/run-1/stderr)、[詳細log](../hardware/kicad/qualification/issue-91-freerouting-v250/evidence/processes/run-1/user-data/freerouting.log) を保存。プロセス自体は残ったため、回復しない失敗として10:52:50 UTCにSIGTERMで早期停止し、10:52:50.239174 UTC終了。20分timeoutによる自然停止を観測した結果ではない。[worker-stop.json](../hardware/kicad/qualification/issue-91-freerouting-v250/evidence/processes/run-1/worker-stop.json) に理由を記録。SESとresult.jsonは未生成なので保存hashも存在しない。架空の出力は作成していない。

- **(A) 内部例外：判定不能。** 新しいnative固有の致命エラーは確認したが、旧maze例外の解消は測れない。「371→0で解消」と数えない。
- **(B) passes制御：判定不能。** 100適用ログはあるが最終pass番号がなく、100終了・101非実行を検証できない。
- **(C) 改善傾向・完成見通し：判定不能。** 未配線推移とSESがなく、完成可能性を評価できない。

[Run 2 gate](../hardware/kicad/qualification/issue-91-freerouting-v250/evidence/run-2-gate.json) はfalse。(1)(2)解消の証拠がなく、未配線残存数も未測定のため追加実行しない。未配線0の証拠もSESもないのでSES取込み・DRC・独立検査は実施しない。Mainの独立4指標は **required未接続=null、wrong-net接触=null、対象材料違反=null、説明不能な受渡し変化=null**。nullはゼロ／合格を意味しない。

## PMO向け推奨・作業範囲

現配布native CLIにはこの入力で実行阻害があり、継続候補への昇格を裏付けられない。#89のv2.1.0に対する追加投資停止推奨を覆す証拠もない。次に限定評価を設けるなら、**同じv2.5.0公式JARとTemurin JRE 21以上を用い、同じhash入力でnative serialization障害を回避できるか**を最初の問いとすることを提案する。その際、短縮引数とnested設定の競合を先に対応表で解決し、最終job設定・0.20 mm実効ルールの読戻しを保存してから対照配線を行う必要がある。別途承認するIssueで回数・時間箱を定義する提案であり、本Issue内でJARへの差替え試行はしていない。router改造・設定探索は推奨範囲に含めない。

開始を保守的に2026-11-03 10:50:00 UTC（初回時刻観測10:50:32）とした。全体期限12:50、router打切り12:30。10:52:50に失敗実行を停止し報告へ移行。PO回答待ち・除外時間なし。配布取得、probe、source照合、報告、提出、CI観測を連続経過に含める。最終の提出時刻・所要時間・CI状況はDraft PR本文に記録する。

実施：Issue全文／最新main確認、入力hash／旧parity確認、公式配布物取得とhash／版照合、Run 1を1回、失敗の記録、旧ログ集計、段階ゲート判定、本書と証拠保存、指定ブランチでcommit/push・Draft PR提出・CI確認。

未実施：Run 2、JARへの切替実行、設定変更による再実行、SES取込み・DRC・独立4指標の計測、配置／入力／材料／層数変更、router改造・fork・自前ビルド、他版／他backend実験、製品設計、製造出力、方式採用、merge。Issue #87/#89の既存証拠・失敗記録・hashは変更しない。任意のDashboardや過去文書も変更しない。
