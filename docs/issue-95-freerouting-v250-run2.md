# Issue #95 — Freerouting v2.5.0 Run 2

2026-11-03。**fanout有効で最良・最終は58→38未配線へ改善したが、18 autorouter passesで停滞停止した。optimizerは有効化されたものの、未配線残存のためrouter自身がスキップした。PMOには、現行の固定条件でMain完成を目指すFreerouting v2.5.0線を継続候補から閉じることを技術推奨する。** 方式採用・製品要求変更・mergeはPOの決定事項。本評価はMain配線の技術合格、製造可能、Human Gate通過を意味しない。

## 開始条件と同一性

[Issue #95](https://github.com/ihsinoky/he-piantor-42/issues/95) 全文・コメントを確認し、[issue95.json](../hardware/kicad/qualification/issue-95-freerouting-v250-run2/evidence/issue95.json) に保存。開始時の `git fetch origin` 後のmainは `0b78c9e138ef89c913337fe613badb4f5eee0aa4`。そこから専用ブランチ `issue-95-freerouting-v250-run2` を作成し、PR #92/#94のcommitを含めない。#93は [PR #94の固定commit](https://github.com/ihsinoky/he-piantor-42/blob/b2ed21437428ba975c0519734da6cb5ed57522bc/docs/issue-93-freerouting-v250-jar-reevaluation.md) と保存証拠を読取りだけで参照した。

以下 `E/` は [本評価の新規証拠ディレクトリ](../hardware/kicad/qualification/issue-95-freerouting-v250-run2/evidence/) を表す。開始時照合は `E/start.json`。

| 対象 | SHA256（開始時に一致確認） |
| --- | --- |
| #87 main-restore/corrected.dsn | `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2` |
| 公式 freerouting-2.5.0.jar | `f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7` |
| Temurin 25.0.5+8 JRE配布archive | `6fac98f0c8202efc3135a9e9e42aa61963ec42d1c5cbb40caf231e7b14a24ef6` |

取得済みの `~/workspace/tools/issue-93/` を再利用し、再取得なし。JREの実ファイルもarchive内の全regular filesと照合（`E/jre-installed-integrity.json`）。版情報は `E/java-version.txt`。入力はbyte同一コピーで、実行前後のhash一致も確認した。

## 実行条件と実効設定の限界

[実行したrunner](../hardware/kicad/qualification/issue-95-freerouting-v250-run2/evidence/run-router.py) は新規ディレクトリを一度だけ作り、既存なら停止する。実行コマンドは `python3 hardware/kicad/qualification/issue-95-freerouting-v250-run2/evidence/run-router.py`。完全argv・cwd・環境・UTC開始終了・終了コード・全実行artifactのhashは [record.json](../hardware/kicad/qualification/issue-95-freerouting-v250-run2/evidence/processes/run-2/record.json)。stdout/stderr、入力DSN、出力SES、未変更のuser-data JSON/logを同ディレクトリに保存した。

#93 Run 1のargvと保存先パスだけ正規化して比較し、差分が `--router.optimizer.enabled=false→true` と `--router.fanout.enabled=false→true` の2点であることを起動前assertで確認（`E/command-comparison.json`）。headless、`-Xmx2g`、`-mp 100`、`-mt 0`、`-is sequential`、`--router.max_threads=1`、`--router.automatic_neckdown=false`、`--router.job_timeout=00:20:00`、専用tmp/user-data、telemetry無効を保持。LANG/LC_ALL=C.UTF-8、TZ=UTC、DISPLAYとFREEROUTING__環境変数の除去も同一。smokeなし、router実行はこの1回のみ、外側安全上限1260秒。

[実効設定証拠](../hardware/kicad/qualification/issue-95-freerouting-v250-run2/evidence/effective-settings-evidence.json) と詳細logにCLI適用と `Analytics are disabled` を保存。JSONはCLI適用前defaultであり完全な実効job dumpではない。`-mt 0` は `router.max_threads=1` を0に上書きし、runtimeはautorouter single-threaded／optimizer.max_threads=3と表示する。`-is sequential` の最終job値、全scoring値は直接dumpされず、#93で指摘したCLI写像の限界が残る。DSN幅・clearanceの表示も `DSN=200.0 → board=2000 (0.05 mm)` で#93と同じ。実効材料値の独立読戻しは未実施で、同一物理条件の合格を主張しない。再実行で補正はしない。

## 3者対照

旧rawを再集計し、#93 rawは固定commitから読んでrecordのhashを照合。旧rawのhashも旧recordと一致した。集計器は `E/summarize.py`、結果は [summary.json](../hardware/kicad/qualification/issue-95-freerouting-v250-run2/evidence/summary.json)、全pass完了INFO観測値は `E/{baseline-v210,run-1,run-2}-pass-history.csv`。復元時の完了行と復元前統計は区別する。

| 指標 | v2.1.0保存結果 | #93 v2.5.0 Run 1 | #95 v2.5.0 Run 2 |
| --- | --- | --- | --- |
| fanout / optimizer指定 | 無効 / 無効 | 無効 / 無効 | 有効 / 有効（実際はskip） |
| 指定／完了autorouter passes | 100／512（超過） | 100／18 | 100／18（別にfanout 12） |
| 停止理由 | 正確なtrigger未確定。約1200秒のjob timeoutと整合（#89）。外側timeoutなし | best scoreがpass 8から0.5超改善せず停滞停止 | 同じ停滞条件。best score 610.26がpass 8から0.5超改善せず停止 |
| maze内部例外 | 371：NPE 367、配列境界4 | 0 | 0 |
| stdout routing ERROR全体 | 374：NPE 370、配列境界4（maze以外のNPE 3を含む） | 0、stderr空 | 0、stderr空 |
| 未配線推移（pass:値） | 1:88、25:60、50:60、100:53、200:41、201:35、300:38、400:42、500:40、512:36 | 初期128、1:58、2:104、3:103、4:102、5:103、6:102、7:103、8:58、9:103、10:103、11:102、12:58、13:103、14:103、15:102、16:58、17:103、18:103 | 初期128、fanout後baseline 48、1:38、2:97、3:99、4:81、5:99、6:99、7:85、8:38、9:98、10:100、11:100、12:38、13:97、14:98、15:98、16:38、17:97、18:98 |
| 最良／最終pass／復元後最終 | 35（pass 201）／36／35 | 58（pass 1）／103／58 | 38（pass 1）／98／38 |
| プロセス経過秒 | 1203.752413 | 112.004141 | 159.863043 |
| 終了コード・状態 | 0（最終job state未記録） | 0、COMPLETED | 0、COMPLETED（全接続を意味しない） |
| 出力SES | 保存のみ | 26168 bytes、未取込み | 45389 bytes、未取込み |

証拠のraw SES/logには生成時の行末空白があるため、そのまま保存しhashを維持する。文書・スクリプト・集計ファイルのwhitespace検査と、rawのhash検査を分けた。新旧stdout/stderrの重複stack traceは二重計上しない。Run 2の詳細logにはversion check由来の捕捉済み `java.net.ProtocolException` 診断が1件ある（L25）が、routing例外ではなく、その後のjobを継続した。DEBUGの挿入失敗・FAILED経路は観測されるが、NPEや配列境界例外には数えない。

## fanout・optimizerの実動作と効果

根拠は [詳細log](../hardware/kicad/qualification/issue-95-freerouting-v250-run2/evidence/processes/run-2/user-data/freerouting.log) と、行番号付き抽出 `E/stage-events.json`。

- **fanoutは実動作を確認。** 11:18:47.018開始（L62）、12 passes後、3連続pass進捗なしで停止（L216）。11:19:01.902完了、14.85秒、145/163 pins escaped（89.0%、L217）。passごとのfanouted数は重複し得るため累積pin数にはしない。fanout後のautorouter開始baselineは48未配線、pass 1で38となった。Run 1の58から20件（約34.5%）改善した。
- **optimizerは有効化のみ確認、実行されなかった。** CLI trueはL17。しかしL4992で `Skipping optimization stage: the board has 38 unrouted connection(s) (optimizer only runs on completely routed boards).` と明記。直前の `Before optimization` 統計はoptimizerの処理実行を示さない。従って「fanout前段とoptimizer段の両方の実動作を確認」という要求のうち、optimizer側は未達である。optimizerの品質改善効果は評価不能で、効果ゼロと一般化しない。未配線盤面を救済する段としては今回到達できなかった。
- Run 2は18pass完了後の98未配線盤面を最良38へ復元（L4960）、最終stage 38（L4990）。Run 1より約47.86秒（42.7%）長い。154.31秒というstage所要時間はfanoutを含むsession値で、純粋なautorouter単体時間とは扱わない。1回ずつの観測比較であり統計的な性能保証ではない。両フラグを同時変更した試験だがoptimizerはskipなので、進展はfanoutを含む配線経路で生じたと解釈する。

内部routing例外は今回18passesでも0。ただし旧512passesと同じ長さの無例外を保証しない。指定100は超過しなかったが、停滞停止のため100完了・101非実行の境界検証は引き続き未達。未配線の最良値はpass 1以降更新されず、旧最良35にも達しない。

## ゲート・PMO向け推奨

未配線0のゲートは不成立。SESは保存のみで、KiCad取込み・独立検査・DRCを行わない。**required未接続=null、wrong-net接触=null、対象材料違反=null、説明不能な受渡し変化=null**（`E/assessment.json`）。routerの0 violationsは独立4指標の0ではない。

**閉じる場合の結論：現行の固定DSN・配置・材料条件でMain完成へ向かうFreerouting v2.5.0の追加評価線を閉じることをPMOへ推奨する。** 最後の指定セルでも38未配線で停滞し、optimizerは完全配線になるまで動かないため、残接続を埋める根拠がない。fanoutの改善は認めるが、時間延長・設定探索・同条件再実行を次の一手として推奨しない。固定配置の完成不可能性やFreerouting一般の否定は主張しない。POの方式採用・製品要求変更・mergeの判断は本workerでは行わない。

## 時間・実施／未実施

作業開始は保守的に2026-11-03 11:18:00 UTC、90分期限12:48:00 UTC。routerは11:18:41.942–11:21:21.804 UTC（159.863秒）、自然終了、外側timeoutなし。準備・実行待ち・集計・報告・commit/push・Draft PR作成・CI確認をすべて時間箱に含む。提出直前の経過時間は `E/submission.json`、提出とCI確認までの最終時刻・総時間はDraft PR本文に記録する。

実施：開始main確認、Issue全文確認、入力/JAR/JRE照合、専用ブランチ、指定2点だけ変更したrouter 1回、ログによるstage確認（optimizer skipを明記）、保存証拠の再集計・3者対照、技術推奨、証拠のhash検査、文書・commit/push・Draft PR・CI確認。

未実施：smoke、2回目以降のrouter、設定探索、optimizer実行確認と効果測定、100pass境界検証、完全実効job dump・材料読戻し、SES取込みと独立4指標。入力改変・配置変更・材料緩和・層数変更・router改造/fork/自前build・native CLI・他版/別backend実験・製造出力・製品設計・方式採用・mergeは実施していない。既存#87/#89/#91/#93の証拠・記録とPR #92/#94は一切変更しない。
