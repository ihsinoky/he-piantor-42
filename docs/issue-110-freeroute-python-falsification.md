# Issue #110 — Python版 freeroute の限定反証テスト

**構成A / B とも FIXED_CONDITION_FAIL。** 指定スモークを各1回実行し、両方とも SES 生成・KiCad import は成功した。しかし全2 paths が **0.02mm**、KiCad DRC は **未接続3件・violations 4件（幅違反2、dangling 2）**。独立検査は元の銅箔の変化を検出して不合格となった。Stage 0 ゲートに従い、**Main は両構成とも0回**。未接続が残るため合否用4指標はすべて **null**。

対象は [Issue #110](https://github.com/ihsinoky/he-piantor-42/issues/110)。以下 `E/` は [今回の証跡](../hardware/kicad/qualification/issue-110-freeroute-python-falsification/evidence/) を指す。指示書全文は `E/instructions.md`、Issue 本文は `E/issue110.json`。構成別の全ログ・SES・検査結果は `E/A/`・`E/B/`。grid、引数調整、再実行、入力・ルーターの修正は行っていない。

## 固定導入とコマンド

Python **3.12.3** の隔離 venv へ `pip install freeroute==2026.7.14` で固定導入した。実コマンドの追加 `--report` は pip の取得証跡保存用で、ルーターオプションではない。インストールログ・pip JSON・導入環境を `E/install.log`・`pip-report.json`・`installation.json` に保存。

- 配布物：`freeroute-2026.7.14-py3-none-any.whl`
- SHA256：`a1b8b369a3e5df558dea15568876621f705e0c9510979caa92b3ff2c43ee4a93`
- pip install の download digest と、同版を pip download で取得した wheel の実ファイル SHA256 を照合した。配布物自体・venv は提出しない。
- ライセンス：GPL-3.0-or-later。配布物の `METADATA` に License-Expression と Alpha 宣言がある（`E/official/METADATA`）。版は同メタデータの2026.7.14で固定し、説明文中の0.1.0を採用しない。

実行した `--help` 全文は `E/help.txt`。位置引数 DSN、`--engine`、`--pack`、`--shove`、出力 `-do` が使用可能であることを確認し、指定順序のまま実行した。

```text
# A
freeroute corrected.dsn --engine exact --shove -do out.ses
# B
freeroute corrected.dsn --engine room --pack --shove -do out.ses
```

実行ファイルは `/tmp/issue-110-freeroute/venv/bin/freeroute`。完全argv・cwd・UTC時刻・終了コード・実時間・入出力 hash は `E/{A,B}/processes/smoke/record.json`。stdout / stderr は双方空。DISPLAY / WAYLAND_DISPLAY を除去し、stdin は DEVNULL、PTY なし。各 stage の外側上限1800秒は発火せず、自然終了した。その他は既定値のまま（exact の max-passes は CLI 実装上10）。

`E/run-router.py` は構成と argv を固定し、既存 stage ディレクトリの再使用を拒否する。Main の起動は当該構成の `smoke-gate.json` の合格を必須とする。各 gate は `main_allowed=false`。

## 入力と Stage 0

指定 #87 resume-01 の DSN を照合した。smoke はbyte同一コピーで実行し、終了後にも同一性を確認した。Main は照合のみ。配置・ルール・層数は変更していない。

| 入力 | SHA256 |
| --- | --- |
| smoke corrected.dsn | `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9` |
| Main corrected.dsn | `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2` |

| 観測 | A：exact + shove | B：room + pack + shove |
| --- | ---: | ---: |
| 開始 UTC / 2026-11-04 | 03:28:52.006176 | 03:29:05.493062 |
| 処理秒 | 0.114962805 | 0.114645088 |
| 終了コード | 0 | 0 |
| SES bytes | 1004 | 1004 |
| paths / vias | 2 / 0 | 2 / 0 |
| 全path幅 / 最小幅 mm | 0.02 / 0.02 | 0.02 / 0.02 |
| 0.20mm未満 paths | 2 | 2 |
| KiCad import exit | 0 | 0 |
| KiCad 未接続項目数 | 3 | 3 |
| raw DRC violations | 4 | 4 |
| 内訳 | track_width 2 / track_dangling 2 | track_width 2 / track_dangling 2 |
| raw DRC clearance 違反 | 0 | 0 |
| 独立 oracle exit | 1 | 1 |
| Main 実行回数 | 0 | 0 |

両 SES はbyte同一、SHA256 **`577e9d21227da42cfc558eae408b6661eb5c1ddd607a4dbc47e985acc1b96682`**。`E/{A,B}/inspect-ses.py` は #97以降の方式で、routes の `(resolution um 10)` を10000単位/mmと解釈し、全 path を列挙して測定した（`smoke-ses-inspection.json`）。`path F.Cu 200` は200 / 10000 = **0.02mm**。全中心線長は0.8mm。

KiCad **9.0.9** の実 import でも幅 **0.0200mm** を確認し、基板の下限 **0.2000mm** に対する `track_width` 違反が2件出た。静的解釈だけの疑義ではない。KiCad は例として SES 座標 (16000,-10000) を基板上 (1.6,1.0)mm に取り込み、元の端子 (16,10)mmから離れた銅箔となった。元の0.20mm線分 (10,10)–(10,12)mmは保持されず、欠落中心線長 **2.0mm**。非配線要素の意味およびsnapshotは同一だった。

## 独立検査と null 方針

元 KiCad スモーク基板・project のコピーに保存 SES を import し、保存後の read-pcb snapshot、KiCad DRC、無改変 #87 resume-01 `check-import.py` を実行した。import / snapshot / 検査用 footprint library 準備 / DRC はすべてexit 0。oracle は両方とも **`original local copper changed`** で停止した。これは導入不備ではなく、既存銅箔保持の検査での拒否である。

検査は既存 `.issue105-runtime` の KiCad・Shapely **2.2.0**・sexpdata **1.0.2** を参照し、今回専用 `/tmp` XDG ディレクトリを使用。バージョンは今回再測定した `E/inspection-versions.json`、環境は各構成の `kicad-env.json`、無改変 oracle のhashは `E/oracle-hashes.json`。元基板から Probe footprint library を用意しただけで基板は補正していない。ハーネスの由来と今回のパス変更は `E/script-provenance.json`。

oracle 停止後も保存ファイルへの読み取り診断を実行し、`smoke-measurement.json` に件数と元銅箔の欠落を記録した。**未接続3件は DRC JSON の `len(unconnected_items)`** であり、未接続ネット数や端点不足数とは異なる。内訳は元のU1同番号ランド間、U2–U1、端子から離れた新銅箔–U1。wrong-net 銅箔接触ペアは診断上0、required pad を含むNの島数は元2→返却後3（graphのdisconnected値）。返却後には別に端子を含まない孤立銅箔の島も1つある。U3はネットなし端子である。

| 合否用4指標 | A Stage 0 | B Stage 0 | A/B Stage 1 |
| --- | --- | --- | --- |
| required unconnected | null | null | null |
| wrong-net contacts | null | null | null |
| material violations | null | null | null |
| unexplained transfer changes | null | null | null |

未接続が残るため、診断上のwrong-net=0やDRC件数を合否用4指標に代入しない。Stage 1 はゲート不合格で未実行につき、未配線数・実時間・幅・import可否はすべて未測定。Stage 0の結果からMain性能を推定しない。

## exact の自己検証の主張

配布物の説明は exact について「違反を出すくらいならネットを落とす」と主張する。**今回の固定 DSN → 指定 CLI → 最終 SES → KiCad という出力保証は反証された。** exact の部分結果にも0.20mmを下回る幅があり、独立 KiCad DRC でも幅違反2件を検出した。未接続3件とは別の失敗である。clearance 違反は今回0件であり、clearance違反を実測したという結論にはしない。

読取り保存した配布ソース `E/official/pipeline.py` は内部座標を scale で割って出力用座標へ変換し、width を DSN rule の200としている。`writer.py` はそれを整数で書き、resolution には入力の um 10 をそのまま付けている。これは保存 SES の座標・幅がともに10分の1で取り込まれた観測と整合する。**内部 exact 幾何検査自体が同じ内部単位で誤判定したことまでは検証していない**。反証範囲は、自己検証後に配布 CLI が実際に出す最終成果物の無違反性である。コードやSESを補正しての追試は指示範囲外なので実施しない。

## 既存結果との比較

| 評価 | 対象 | 未配線 | ルーター処理秒 | 件数の出典 |
| --- | --- | ---: | ---: | --- |
| Freerouting v2.5.0 Run 2 / #95 | Main | 38 | 159.863043 | ルーター自己報告、Main importなし |
| fastroute / #99 | Main | 37 | 28.184144 | router report、幅下限200µm |
| fab_router / #103 | Main | 16 | 298.698 | API / stats / SES roundtrip自己検査 |
| freeroute A / #110 | smoke | 3 | 0.114962805 | 保存SESのKiCad DRC |
| freeroute B / #110 | smoke | 3 | 0.114645088 | 保存SESのKiCad DRC |
| freeroute A/B / #110 | Main | 未測定 | 未測定 | Stage 0不合格により未実行 |

比較元の集計コピーとhashは `E/comparison/`・`comparison-sources.json`。各数値の定義と基板規模が異なるため、処理速度や配線能力の順位にはしない。

## 提出と検証

作業元は現在の `he-piantor-42`、開始時最新 main **`2321223e7ae7ccfdcee1b8391f642128aa57feb8`**。元 `.git` は読み取り専用のため、公式 origin を `/tmp/issue-110-freeroute/git` に bare clone し、現在ディレクトリを work-tree として main の全blobとの一致を照合した後、read-tree と **issue-110-freeroute-python-falsification** ブランチ作成を行った。元の .git と既存ファイルを変更していない。

本書と指定証跡ディレクトリの追加だけを提出する。既存36,887ファイルの SHA256 は `E/preexisting-files.json`、main照合は `baseline-verification.json`。`E/verify.py` は既存ファイル不変、入力・SES hash、正確なargv、実行回数、ゲート、null方針、診断件数、追加のみ、バイナリ不包含を確認する。結果は `verification.json`、提出物hashは `manifest.json`。

全体開始 **2026-11-04T03:26:53Z**、2時間期限 **05:26:53Z**。提出直前時刻と経過を `E/submission.json` に記録し、Draft PR作成後の時刻をPR本文に残す。KiCad DRC 内の日付は環境の +09:00 表記だが、プロセス記録・時間箱はUTCで統一した。Draft PRとして提出し、mergeは行わない。
