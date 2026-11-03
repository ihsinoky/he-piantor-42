# Issue #99 — fastroute 幅下限200µm強制の単一条件再テスト

**固定条件で不合格。** 公式 fastroute v0.1.14 に `--router.min_trace_width_um=200` だけを追加した Main は28.184秒で自然終了し、router report に**未配線37件**が残った。最終 SES の全231 pathsは0.20mmで、下限未満は**0本**。幅下限は保存結果において成立したが、完全配線には到達しなかった。未配線が残ったため Main の独立4指標はすべて **null** とする。

対象は [Issue #99](https://github.com/ihsinoky/he-piantor-42/issues/99)。以下 `E/` は [今回の証跡](../hardware/kicad/qualification/issue-99-fastroute-width-floor/evidence/) を指す。指示書全文は `E/instructions.md`、Issue本文は `E/issue99.json`。比較元は [#97 の Draft PR #98](https://github.com/ihsinoky/he-piantor-42/pull/98)、commit `bc0d108f3cdc6d4c7c9f3d11b9ccba86d91208c2`。ローカルの既存#97成果物をこのcommitのGit blobと全件照合した（`E/baseline-verification.json`）。比較に使った集計・Main record/report・SES幅実測は `E/baseline-97/` にも収録した。

## 唯一の設定差分と一次情報

両 stage の正確な引数は次のとおり。実行ファイルの絶対パスは `/tmp/issue-99-fastroute/fastroute-0.1.14-linux-x64/fastroute`。

```text
fastroute -de corrected.dsn -do out.ses --report=report.json --max-time=1800 --router.min_trace_width_um=200
```

**automatic_neckdown は既定の true を維持し、無効化していない。** 実バイナリの `--help` はこの設定を “never neck traces below W um” と説明する（`E/help.txt`）。[公式 v0.1.14 control.rs](https://github.com/parisxmas/fastroute/blob/v0.1.14/crates/fr-engine/src/autoroute/control.rs) の113–119行は正の neckdown 半幅を指定最小半幅以上へ clamp し、348–361行はµmを基板単位に変換し半幅を切り上げる。`inserter.rs` の223・288行、`maze.rs` の350・878行はその clamp を使用する。`reflect.rs` の164・223行で snake_case CLI名から `minTraceWidthUm` の数値設定への対応も確認した。これらの一次情報から追加無効化を必要とする根拠は見つからず、指定の1設定のみで実行した。

読取り用の公式ソースを `E/official/`、判断を `E/configuration-decision.json` に保存。ソース取得は仕様確認だけで、ビルドはしていない。設定値の完全なreadbackはreportに含まれないため、help、CLI対応ソース、完全argv、実行ログ、最終SES全path実測を合わせて証拠とする。ログは版・thread limits・拡張multi-start・optimizerの実行を示すが、設定値200の明示ログとは扱わない。

`--parity` / `--no-enhancements` は使用せず、拡張・multi-start・fanout・optimizer・thread数はデフォルト。ログ上autorouterとoptimizerは各3 threads。入力・配置・層数・ルールは変更していない。外部からの実行はスモーク1回、Main1回だけで、内部multi-startは既定機能である。再実行・条件探索はしていない。

## 公式配布物と入力同一性

#97で取得済みの公式 Linux x64 プリビルドを再利用し、今回取得した [公式 v0.1.14 SHA256SUMS](https://github.com/parisxmas/fastroute/releases/download/v0.1.14/SHA256SUMS.txt) とリリースAPIのasset digestにも再照合した（`E/installation.json`、`E/release-current.json`、`E/SHA256SUMS-current.txt`）。`--version` は `fastroute 0.1.14`。ソースtagのcommitは `19c3b75322da6a0dc2f87a616fc0afe34a98f07e`。

| 対象 | SHA256 |
| --- | --- |
| 公式Linux x64 tar.gz | `079a109f76d84836e7d7a54519e75759dcab9baacc9c58b4224b027b852e49c6` |
| 実行ファイル | `a4efebd6bfbb6614c9bac0535441dd65983d1a8e2cb3e00ebcf3ce90f2757d9f` |
| smoke DSN | `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9` |
| Main DSN | `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2` |
| 最終Main SES | `4e23af52e0a956f95d69ece26736ee66a18ad33229e3aad5c7bd4f27a5ad7b34` |

入力は指定された#87 resume-01の `smoke-restore/corrected.dsn` と `main-restore/corrected.dsn` をbyte同一コピーし、実行前後にhash照合。Mainは49部品・37ネット・197端子、2層、幅・clearanceは0.20mm。完全argv、cwd、UTC時刻、環境、終了コード、経過時間、全入出力hashは `E/processes/{smoke,main}/record.json` に保存した。DISPLAYとWAYLAND_DISPLAYを除去してheadless実行。外側安全上限1920秒と内側1800秒上限はいずれも発火していない。バイナリと配布アーカイブは提出物に含めない。

## Stage 0：合格してからMainを開始

スモークは22:16:57.478–22:16:57.504 UTC、プロセス経過0.017秒、exit 0。SES 984 bytes、router未配線0。静的実測で全2 pathsが0.20mm（`E/smoke-ses-inspection.json`）。

KiCad 9.0.9で元のスモーク基板コピーにSESをimportし、保存後のsnapshot・KiCad DRC・既存#87 `check-import.py` の実銅箔グラフと非配線同一性を検査。**required unconnected / wrong-net contacts / material violations / unexplained transfer changes はすべて0**（`E/smoke-independent.json`）。#97で必要だったProbe検査ライブラリは今回も元基板のfootprintから先に作成し、基板自体は修正していない。検査プロセスもすべてexit 0である。

検査用KiCadパッケージ・依存debのhashは#97と一致（`E/kicad-package-hashes.json`）。展開とPython依存導入は一時 `.issue99-runtime/` のみで行い、システムへのインストールはしていない。セットアップ記録は `E/inspection-setup/`、実行環境は `E/kicad-env.json`、既存oracleのhashは `E/oracle-hashes.json`。検査用依存物は提出前に削除し、commit対象外とした。

ゲート記録 `E/smoke-gate.json` は22:18:19.325 UTC、Main開始22:18:26.280 UTCより前。runnerは既存stageディレクトリがあれば停止し、Main前にゲートと独立4指標0、幅検査を確認する。

## Stage 1：幅を守ったが未配線37件

Mainは22:18:26.280–22:18:54.476 UTC、28.184秒、exit 0、SES 35627 bytes。reportの未配線件数37は `unrouted` 配列37件と一致し、残接続の端子・ネット・長さはそのまま `E/processes/main/report.json` に保持した。router clearance violationsは0である。

`E/inspect-ses.py` は#97と同じ静的実測方式で、SESの `(resolution um 10)` を10000単位/mmと解釈し、全serialized pathを走査した。幅分布は **0.20mm × 231 paths** のみ、最小0.20mm、下限未満0本。層別はF.Cu 221 / B.Cu 10、viaは17。reportの231 traces / 17 viasと一致し、中心線長586.035791mmとreport 586.0358mmも表示精度内で一致した。幅下限が最終出力で有効だったことは確認できる。

未配線残存のため、MainのKiCad import・独立材料検査・DRCは行っていない。import可否は未測定であり、スモークの成功をMainへ転用しない。routerのviolations=0は独立検査値ではなく、静的SES幅検査も接続性や実銅箔clearanceの合格を証明しない。

| Mainの独立指標 | 値 |
| --- | --- |
| required unconnected | null |
| wrong-net contacts | null |
| material violations | null |
| unexplained transfer changes | null |

## #97との比較

| 観測項目 | #97（幅指定なし） | #99（幅下限200µm） |
| --- | ---: | ---: |
| 出力時router未配線 | 1 | 37 |
| SES幅分布 mm（paths） | 0.20:335 / 0.15:69 / 0.12:1 / 0.10:1 | 0.20:231 |
| 0.20mm未満paths / 最小幅 | 71 / 0.10mm | 0 / 0.20mm |
| 初回autorouter完了passes | 20 | 18 |
| 並列variant完了passイベント計 | 64 | 58 |
| autorouter完了passイベント総数 | 84 | 76 |
| multi-start variant 1 / 2 / 3未配線 | 1 / 5 / 4 | 40 / 38 / 39 |
| multi-start後に保持した盤面 | variant 1（1未配線） | 初回（37未配線） |
| 初回fanout passes | 7 | 8 |
| optimizer開始時の未配線 | 1 | 37 |
| optimizer完了passes | 3 | 1 |
| optimizer score | 180.48 → 251.86 | 843.91 → 862.94 |
| optimizer所要秒 | 73.67 | 4.07 |
| プロセス経過秒 | 190.034 | 28.184 |
| WARN / ERROR / panic・exception・backtrace診断 | 0 / 0 / 0 | 0 / 0 / 0 |
| 終了コード | 0 | 0 |

初回はpass 4で37未配線に到達し、停滞規則により18 passesで停止。既定multi-startの3 variantsはいずれも初回より悪く、最終出力は初回の37未配線を保持した。並列pass行にはvariant識別子がないため、個別pass履歴は推測で割り当てず、`E/main-pass-history.csv` で初回と並列計を区別した。variant別の最終結果は明示ログを用いた。

optimizerは未配線37でも24.060秒時点で開始し、1 passを完了。改善率2.2556%が既定2.50%未満となって停止し、未配線は37を保持。1800秒を使い切った停止ではない。詳細は `E/summary.json` と `E/stage-events.json`。例外数は観測ログの診断件数であり、ログに出ない内部捕捉失敗の不存在は主張しない。

**今回の観測では幅下限未満71→0本と引き換えに、未配線が1→37件（+36）へ増えた。** このトレードオフを記録し、固定0.20mm条件で#97の未配線1件を再現したとは認定しない。単一試行・既定並列処理の比較なので数値差の決定論的な因果や普遍的性能差を証明するものでもない。

## 判定・提出範囲・時間箱

`E/assessment.json` の判定は `FIXED_CONDITION_FAIL`。固定条件下でこの単一指定条件をMain完成の合格候補にはできない。配置の完成不可能性やfastroute一般の否定には拡張しない。追加配線実行や設定探索は行わない。

作業元は現在の `he-piantor-42`、main / origin/mainは開始時 `3d0ec606cefaa55cd11448879750d56f86d64b2f`。元 `.git` は読取り専用のため管理情報のみ `/tmp/issue-99-fastroute/git` に複製し、現在ディレクトリをwork-treeとして、取得済みorigin/mainから **issue-99-fastroute-width-floor** を作成した。#97ブランチから派生していない。既存#97ファイルは未追跡のまま保持し、今回のcommitには含めない。変更は本書と指定の新規証跡ディレクトリへの追加のみ。

保守的開始2026-11-03 22:15:00 UTC、期限2026-11-04 00:15:00 UTC。指示書の日付と異なる実環境UTC時計を一貫して使用した。導入・実行・独立検査・記録・commit/push・Draft PR作成を時間箱に含める。提出前の時刻は `E/submission.json`、PR作成後の確認時刻はDraft PR本文へ記録する。

`E/verify.py` で厳密argv、入出力hash、元入力と既存参照の不変、スモークゲート順序、Mainのnull方針、追加のみ、バイナリ不包含、時間箱を確認した（`E/verification.json`）。`E/manifest.json` は本書と証跡のhash一覧。生のDSN/SES・公式ソースの空白は保持し、追加スクリプト・文書・集計の空白検査と区別する。成果物はDraft PRとして提出し、mergeは行わない。
