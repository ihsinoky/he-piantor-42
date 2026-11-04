# Issue #131 — Wing 自動配線の実現条件探索

**16mm の最初の合格条件は KRT・2層・幅／クリアランス0.10mm。独立4指標すべて0、幅監査通過。** 同条件の17mmも合格した。 16mm・2層0.127mmは未配線1件。16mmの合格時点で探索を止め、4層の2セルは実行していない。

対象は [Issue #131](https://github.com/ihsinoky/he-piantor-42/issues/131)。指示書全文は [`E/instructions.md`](../hardware/kicad/qualification/issue-131-wing-condition-search/evidence/instructions.md)、Issue本文は `E/issue131.json`。以下の `E/` は `hardware/kicad/qualification/issue-131-wing-condition-search/evidence/`。

## Stage 0：pads 禁止だけを解除

基準は main `e0374fe` と #129 修正ラウンドのゲート通過入力。既存ファイルは変更せず、新規証跡へ3基板を複製した。JSON/CSV・Wingソース・`docs/decisions.md` は不変。各入力PCBの4箇所を `(pads not_allowed)` → `(pads allowed)` とした以外、PCBの全文は #129 入力と一致する。tracks／vias／copper pour／footprints の禁止、256辺のφ5mm keepout、φ2.2mm NPTH、配置・ネット・外形・板厚1.2mmを保持した。プロジェクトも #129 とbyte一致。`fp-lib-table` の参照先だけ新規証跡内の同一ライブラリへ移した。

#129 の `check-equivalence.py` を複製し、禁止対象の期待値を `not z.GetDoNotAllowPads()` とした。他の検査項目・数値・許容差・assertion はbyte一致であり、構築スクリプトをimportしない独立public readerで検査した。ゲートは今回1回、2026-11-04T20:44:42.552120+00:00 に3基板すべて通過。その後同じhashを `stage0-frozen-hashes.json` に再固定した。変更の厳密比較は `stage0-change-audit.json`。

| 改訂入力 | PCB SHA256 |
| --- | --- |
| pitch9-16mm | `fcc1333efc3f1200cb160c459166d0d118ff82f1675005368338593ee623b11a` |
| representative21-16mm | `d23e9e35dbf89304aa521955687f35404ddcc5d97ee01bf579b9eaa82353dad1` |
| representative21-17mm | `0d98eec014a23f6e06b34bb3641532dcc6c6d65ea9ac936d905264cd985c69cc` |

改訂入力の追加DRCは3基板とも違反0件。未配線はpitch9で92件、代表両ピッチで各152件（配線前）。#129のNPTHに由来する `items_not_allowed` 各4件は解消した。`input-drc-*.json` と `input-drc-summary.json` に実測を保存した。

## Stage 1：指定順の単一run

KRT v0.23.8、commit `c64c0db25e6cf23afa6769ee05665c7ea22b3ff2` を #129 と同一のまま使用。全2055ソースファイルとgrid_router binaryのhash一致を `runtime-revalidation.json` に確認した。binary SHA256 は `4411ccf3f074f519d8d69be29ac58b46ca7c4c2fe4f4be889d253d40996c2c0f`。KRT本体を変更していない。

各セルは Stage 0 の改訂入力から派生させ、プロジェクトのglobalとDefault netclassの幅／クリアランスだけをセル値へ設定。PCBはStage 0とbyte一致する。ビア0.60/0.30mm、板厚1.2mm、穴・外形のクリアランス0.20mmを維持した。セルごとの条件・固定hash・生成物は `cell-inputs/<cell>/`、起動設定・実効readback・出力は `runs/<cell>/`。

CLIは `--escalation off --track-width <セル幅> --clearance <セル幅> --via-size 0.6 --via-drill 0.3`。readbackは公式resolverのnet選択直前にtraceで停止する読取り専用処理で、配線を開始しない。全runで実効幅／クリアランス・ビア寸法・F.Cu/B.Cu・escalation offを確認した。内部tierに寸法を委ねず、途中の条件調整・再試行・手配線はない。各配線の上限は1800秒。

4指標の順は required unconnected / wrong-net contacts / material violations / unexplained transfer changes。未配線ありの4指標はすべてnull。

| セル | 独立DRC未配線 | 独立4指標 | 幅監査 | 判定 |
| --- | ---: | --- | --- | --- |
| KRT-16-2L-0127 | 1 | null / null / null / null | 855 tracks / min 0.127mm・通過 | 不合格 |
| KRT-16-2L-0100 | 0 | 0 / 0 / 0 / 0 | 765 tracks / min 0.1mm・通過 | 合格 |
| KRT-16-4L-0127 | — | null / null / null / null | 未実施 | 16mm合格で打ち止め |
| KRT-16-4L-0100 | — | null / null / null / null | 未実施 | 16mm合格で打ち止め |
| KRT-17-2L-0100 | 0 | 0 / 0 / 0 / 0 | 727 tracks / min 0.1mm・通過 | 合格 |

2層0.127mmの残り1件は `U_MUX_A.14 GND` とGNDトラックの間。物的DRC違反は0件だが、未配線があるため不合格。2層0.10mmの16mmは全30ネットを独立に接続確認できた。この条件が指定順で最初の合格であり、4層入力の構築・配線は行っていない。

## 独立検査と監査

`inspect-cell.py` は #129 の検査ハーネスを踏襲し、各セルの固定入力プロジェクトで保存出力をDRCした。KRT出力プロジェクトは別に全差分を監査し、最小幅・全ネットクラスが入力と一致することを確認。追記はKRTの `fab_floor_origin` 記録のみで、ルールの書き換えではない。全トラック実幅にセルのピン留め幅未満はない。全ビアの実測径／ドリルも0.60/0.30mmである。

未配線0のセルでのみ #87 の実銅箔graph (`snapshot_graph`) により必須パッド間の連結と異ネット接触を実測した。#129と同じ境界箱の保守的事前除外（いずれかの軸で厳密に2nm超離れた組だけを除外）を使い、形状・穴の減算・接触／距離述語・union-find・判定基準は変更していない。実行した関数ソースとoracle hashは各 `graph-method.json`。rule areaは銅箔ではなく、非配線オブジェクトの厳密AST差分とDRCで保持を確認した。全セルの非配線オブジェクト差分・非配線snapshot差分は0。

独立検査出力は `inspection/<cell>/` の `assessment.json` / `drc.json` / `copper-graph.json`（未配線0のみ）/ `transfer-diff.json` / `width-audit.json` / `physical-audit.json`。実行のstdout・stderr・開始終了・exit code・timeout枠は `processes/`、セルの集約は `runs/<cell>/report.json` と `assessment.json`。

今回の結果は指定入力・各1回の実現条件確認であり、再現性の統計評価や製造承認ではない。配置・機構・アナログ性能・実機評価は行っていない。基板費用や正式設計ルールの採否は今回の成果から別途判断できる。

## 提出・環境

作業ブランチは `issue-131-wing-condition-search`。通常の `.git` が読取り専用のため、管理情報を `.issue131-runtime/git` に複製し、同じ作業ツリーに対してGitを実行した。KRTは新ランタイムに複製、KiCad/geometry/venvは `.issue129-runtime/` を読取り専用で再利用した。変更可能なキャッシュ・一時ファイルは `.issue131-runtime/` に限定し、ランタイム本体は提出しない。

保守的開始は実UTC `2026-11-04 20:43:54`、期限は `2026-11-05 00:43:54`。ユーザー環境の日付は11月5日だが、実ホスト時計が11月4日を返すため、実行記録は実UTCに統一した。`verification.json` は基準mainの全ファイルbyte不変、固定入力hash、探索順と単一run、実効設定、全JSON/Python構文、再利用元の読取り専用維持を検証する。全証跡hashは `manifest.json`。

著作した報告書・Python・JSONのwhitespace検査は通過。全体のdiff-checkはKRT生出力PCBのタブのみの空行1506件（出力3基板と検査用の同一コピー計6ファイル）を検出する。出力のbyte保存を優先して整形していない。詳細は `whitespace-audit.json`。

公開結果は `publication.json` を参照。コミット済みの指定ブランチからDraft PR作成を試み、mergeは行わない。

提出仕上げはランタイム再起動後に再開した。配線セル・等価性ゲート・独立検査は再実行せず、保存済みの結果と実行記録を照合した。提出監査の実行時刻は `verification.json` の `submission_audit_utc` に分離し、元runの時刻は保持した。`manifest.json` はリポジトリルート相対パスのSHA256一覧で、この報告書・提出監査・公開記録も含む。manifest自身のみ循環を避けるため対象外。
