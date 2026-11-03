# Issue #97 — fastroute 限定反証テスト

**反証成立（固定条件で不合格）。** 公式 fastroute v0.1.14 は Main を190.034秒で自然終了し、report に未配線 **1件**が残った。最終 SES の幅を別途実測すると **0.20mm 未満の path が71本、最小0.10mm** だった。未配線盤面で optimizer が実行される機構変更は確認できたが、今回のデフォルト条件を Main 完成の合格候補にはできない。幅条件を満たさないため、38→1を固定0.20mm条件での性能改善とは認定しない。

以下 `E/` は [新規証跡ディレクトリ](../hardware/kicad/qualification/issue-97-fastroute-falsification/evidence/) を表す。[Issue #97](https://github.com/ihsinoky/he-piantor-42/issues/97)、指示書全文は `E/issue97.json`、`E/instructions.md`。既存ファイルへの変更はなく、成果物は本書と指定証跡ディレクトリへの追加だけである。merge はしていない。

## 入力・公式配布物・固定条件

Main と smoke は #87 resume-01 の `main-restore/corrected.dsn`、`smoke-restore/corrected.dsn` を byte 同一コピーで使用した。実行前後に照合済み。

| 対象 | SHA256 |
| --- | --- |
| Main DSN | `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2` |
| smoke DSN | `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9` |
| Linux x64 配布 tar.gz | `079a109f76d84836e7d7a54519e75759dcab9baacc9c58b4224b027b852e49c6` |
| 展開した fastroute 実行ファイル | `a4efebd6bfbb6614c9bac0535441dd65983d1a8e2cb3e00ebcf3ce90f2757d9f` |
| 最終 Main SES | `584d5b50e12f2b34f4b71f736d4e193c84e408ec2a6e4a122f4c16235200a2b4` |

取得時の公式 latest API は非 draft・非 prerelease の **v0.1.14**。[公式リリース](https://github.com/parisxmas/fastroute/releases/tag/v0.1.14) の [Linux x64 プリビルド](https://github.com/parisxmas/fastroute/releases/download/v0.1.14/fastroute-0.1.14-linux-x64.tar.gz) を取得し、API asset digest と公式 `SHA256SUMS.txt` の双方に一致。`--version` は `fastroute 0.1.14`。tag の commit は `19c3b75322da6a0dc2f87a616fc0afe34a98f07e`。取得 URL・hash は `E/installation.json`、API応答・版・help・公式 checksum は `E/{release.json,release-tag.json,version.txt,help.txt,SHA256SUMS-official.txt}`。ソースビルドなし。バイナリ・配布アーカイブは成果物に含めない。公式ソース4ファイルは読取りによる仕様確認だけで、`E/official/` に保存した。

入力は配置固定、49部品・37ネット・197端子、2層。DSN の幅・clearance は200umを維持し、配置・層数・ルール・入力を変更していない。**出力側の幅縮小が固定条件違反**であり、入力条件の緩和を許可したものではない。

## Stage 0 と Stage 1

両 stage とも専用ディレクトリで、次の引数だけを使用した。

```text
fastroute -de corrected.dsn -do out.ses --report=report.json --max-time=1800
```

完全 argv、cwd、UTC開始終了、終了コード、経過時間、入力・実行ファイル・stdout/stderr・SES/report の hash は `E/processes/{smoke,main}/record.json`。`DISPLAY` と `WAYLAND_DISPLAY` を除去した headless 実行。LANG/LC_ALL=C.UTF-8、TZ=UTC。拡張機能はデフォルト有効、`--parity` / `--no-enhancements`、追加の router 設定は使っていない。外側安全上限1920秒は発火せず、内側1800秒上限にも到達していない。runner は既存 stage ディレクトリがあれば停止する。

**Stage 0：合格。** 21:50:38.233–21:50:38.249 UTC、プロセス経過0.008秒、exit 0、SES 984 bytes、report 未配線0・違反0。KiCad 9.0.9で元の smoke 基板コピーへ import できた。既存 #87 `check-import.py` による実銅箔グラフ・非配線同一性・KiCad DRCで4指標すべて0、SES幅も全2 pathsが0.20mm（`E/smoke-independent.json`、`E/smoke-ses-inspection.json`）。

最初の追加検査は検査環境に `Probe` ライブラリがない4警告で停止した。元基板のフットプリントから検査用ライブラリを作る既存手順を適用し、**保存済み出力のDRCと独立検査のみ**を再実施した。初回結果も `E/processes/smoke-{drc,independent}/` に保持し、警告解消後は `smoke-*-with-library/` に保持。ルーターの再実行や基板修正はない。Main開始前に import・独立検査の合格を `E/smoke-gate.json` に記録した。

**Stage 1：不合格。** 21:54:59.546–21:58:09.588 UTC、190.034秒、exit 0、stdout空、stderrに通常ログ、SES 64654 bytes。起動は1回だけ。最終 report は未配線1・clearance violations 0。残接続は GND の `J1.13@2 → R2.2`、airline長3.6363mmである。これは router の測定値であり独立 KiCad 未接続件数とは区別する。

## 固有の着眼点

### 1. 幅・clearance と report の意味

[最終SESの静的実測](../hardware/kicad/qualification/issue-97-fastroute-falsification/evidence/main-ses-inspection.json) は `(resolution um 10)` を10000座標単位/mmとして解釈した。406 serialized paths の幅分布は次のとおり。

| 幅 mm | path 数 |
| --- | ---: |
| 0.20 | 335 |
| 0.15 | 69 |
| 0.12 | 1 |
| 0.10 | 1 |

0.20mm未満は **71 paths**。これは SES path の数で、独立検査の material violations 件数ではない。該当 path のネット・幅・座標は同JSONの `narrow_paths` に全件保存。読取りスクリプトは `E/inspect-ses.py`。デフォルトの `automatic_neckdown=true` を変更しておらず、縮小出力が実在する。ただし各 path がどの内部操作で縮小されたかまでは追跡していない。

report の `violations=0` は `clearance_violations=[]` と整合するが、**0.20mm下限を満たすことを意味しない**。今回、別測定のSES幅が明確に下限を割る。未配線が残ったため、指示書のゲートに従い Main import・独立材料検査・KiCad DRCは行わず、実銅箔 clearance の合格も主張しない。幅の失敗だけで判定は確定し、下限設定の追加や再配線による補正はしない。

### 2. multi-start と最良結果の保存

最初の autorouter は20 passes、最良6未配線で停滞停止。デフォルト multi-start 内の並列 variant はそれぞれ最終 **1 / 5 / 4** 未配線となり、variant 1を選択した。これは同一プロセス内のデフォルト機能で、外部からの再起動や条件探索ではない。

選択後の optimizer と最終 report は1未配線を保持した。最後の checkpoint と最終SES書込みをログで確認。SESの **406 paths / 66 vias** は report の traces / vias と一致し、中心線長1095.071760mmは report の1095.0717mmと約0.000060mm差（表示精度の範囲）。最良1件を最終出力に引き継いだというログ・report・保存形状統計は整合する。ただし、Main の独立接続検査をしていないため、SES実銅箔の未接続1件を独立に証明したという意味ではない。

### 3. optimizer・終了コード・例外

116.251秒時点で **incomplete connections: 1** の盤面に対して optimizer が開始され、3 passesを完了した。optimizer score は180.48→225.11→247.69→251.86へ改善し、3 pass目の改善率1.6854%がデフォルト閾値2.50%未満となり停止。optimizer所要73.67秒、未配線は1のまま。#95の「未完配線なのでoptimizer全体skip」は今回覆されたが、完全配線には到達せず、幅条件も不成立である。

exit 0はSES/reportの書出し完了を示す観測であって、要求合格とは一致しない。ログで WARN / ERROR / panic / exception / backtrace 診断はいずれも0。内部で捕捉されてログに出ない失敗の不存在は主張しない。配線失敗・blocked診断はINFOとして残り、例外とは数えない。詳細は `E/{summary.json,stage-events.json,main-pass-history.csv}`。

### 4. Freerouting v2.5.0との比較

旧証跡は読取りのみで参照し、record内の全artifact hashを再照合した（`E/baseline-verification.json`）。比較元は `E/freerouting-comparison-source.json`。

| 指標 | #93 Run 1 | #95 Run 2 | 今回 fastroute |
| --- | ---: | ---: | --- |
| 最良／出力時のrouter未配線 | 58 / 58 | 38 / 38 | 1 / 1 |
| autorouter passes | 18 | 18 | 初回20、並列variants計64、合計84完了イベント |
| fanout | 無効 | 12 passes | 初回7 passes、各variantにもfanout |
| optimizer | 無効 | 有効指定だが未配線38でskip | 未配線1でも実行、3 passes |
| プロセス経過秒 | 112.004 | 159.863 | 190.034 |
| routing例外診断 | 0 | 0 | 0（観測ログのpanic/exception診断） |
| 終了コード | 0 | 0 | 0 |

variantのpassログには並列実行元のラベルがないため、個別pass履歴を推測して割り当てない。初回20と並列計64は区別してCSV保存した。Javaとのスレッド数・fanout・optimizer・neckdown等の実効条件は異なる。**同一DSNに対する指定セルの観測比較であり、同一材料条件や同一実効設定での速度・品質優劣を証明するものではない。**

## 判定・提出範囲・時間

[assessment.json](../hardware/kicad/qualification/issue-97-fastroute-falsification/evidence/assessment.json) の判定は `FALSIFIED / FIXED_CONDITION_FAIL`。Mainの独立4指標は未配線残存のためすべて **null**。

| 独立指標 | Main |
| --- | --- |
| required unconnected | null |
| wrong-net contacts | null |
| material violations | null |
| unexplained transfer changes | null |

Main SES importの可否は未測定。スモークの4指標0をMainに転用せず、router違反0や静的幅測定を独立4指標の0にも転用しない。PMOへの技術推奨は、**この単一デフォルト条件をMain完成の合格候補にしない**こと。機構変更の実動作は確認したが、追加時間・設定探索・再実行は行わない。本結果は固定配置の完成不可能性やfastroute一般の否定ではない。

作業元は現在の `he-piantor-42`、開始HEADは `3d0ec606cefaa55cd11448879750d56f86d64b2f`（取得時remote mainと一致）。元 `.git` が環境の読み取り専用mountのため、管理情報を `/tmp/issue-97-fastroute/git` へ複製し、同じ作業ディレクトリを `--work-tree` に指定して **issue-97-fastroute-falsification** ブランチを作成した。元 `.git` は変更していない。

検査用KiCadは #87と同じ公式9.0.9パッケージをhash照合して展開した（`E/kicad-package-hashes.json`）。導入中の一時領域不足を解消するため検査用依存物だけ一時的に作業ディレクトリの `.issue97-runtime/` に置いた。これは成果物・commit対象から除外し提出前に削除した。導入経緯は `E/inspection-setup/`。

保守的開始21:48:00 UTC、2時間期限23:48:00 UTC。指示書の日付は2026-11-04だが、実環境のUTC時計は2026-11-03であり、証跡は実時計を使用した。導入・実行・検査・記録・commit/push・Draft PR作成をすべて時間箱に含む。提出直前時刻と経過時間は `E/submission.json`、PR作成・CI確認までの最終時刻はDraft PR本文に記録する。

検証は `E/verify.py` によるartifact/input hash、厳密なargv、スモークゲート、Main null方針、追加のみの変更範囲、バイナリ不包含の確認。`E/manifest.json` に文書を含む証跡hashを保存する。生成時の空白を含むraw DSN/SES・公式ソースはそのまま保持し、文書・追加スクリプト・集計ファイルのwhitespace検査と区別した。製品基板修正、入力修正、追加router起動、ソースビルド、方式採用、製造出力、mainへの直接push、mergeは実施していない。
