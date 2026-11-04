# Issue #109 — AutoRoute の限定反証テスト

**判定：FIXED_CONDITION_FAIL。Stage 0 の KiCad DRC で未接続2件と元の銅箔の欠落を確認したため、Main は実行しない。** 指定の `autoroute corrected.dsn -o out.ses --check` は終了コード0、約0.00776秒で SES を生成し、内蔵 DRC は clean と報告した。しかし SES に path はなく、KiCad import 後は元の線分1本も失われた。合否用4指標はすべて **null**。

対象は [Issue #109](https://github.com/ihsinoky/he-piantor-42/issues/109)。以下 `E/` は [証跡ディレクトリ](../hardware/kicad/qualification/issue-109-autoroute-falsification/evidence/) を指す。指示書全文は `E/instructions.md`、Issue 本文は `E/issue109.json`。ルーター実行は **smoke 1回、Main 0回**。追加オプションによる調整、設定探索、配線再実行、ソース修正は行っていない。

## 取得・ビルド

公式 [pingpongshow/AutoRoute の固定コミット](https://github.com/pingpongshow/AutoRoute/tree/e4b3e4a4a443822eb5374762f76f074538e46df2) **`e4b3e4a4a443822eb5374762f76f074538e46df2`** を `git clone` で取得した。ライセンスは **MIT**。`E/source-provenance.json` に SHA・コミット日時・取得時の clean status、`E/clone.log` に取得ログ、`E/official/` に README・LICENSE・Cargo.toml・Cargo.lock と Rust ソースを保存した。検討メモの公開日からコミット日時を推定せず、取得した Git オブジェクトの日時を記録している。

指定どおり、公式ワークスペースのルートで次を実行した。

```text
cargo build --release
```

Rust **1.99.1**、Cargo **1.99.1**、CLI **autoroute 0.1.0**。ビルド exit **0**、Cargo 表示 **8m 46s**。GUI も含めた公式ワークスペース全体をビルドし、GUI の `f32` 推論に関する警告3件を保存した。警告修正はしていない。`E/build.log` が全出力、`E/build-record.json` と `E/installation.json` がコマンド・環境・バージョンの記録。既存 #107 の Rust toolchain を参照し、Cargo home は新規 runtime にコピーして使った。公式 Cargo.lock とソースに差分はない。

CLI バイナリの SHA256 は `7fcceae76996b1110ca2d1edd590e79d7756a45251293c856420341a2ff17219`。**バイナリ自体、取得用 Git、依存キャッシュ、ビルド用 runtime は成果物に含めない。**

## 固定入力・実行方法

#87 resume-01 の両 DSN を実行前に照合し、smoke の実行後も hash が同一であることを確認した。配置、2層、配線幅・clearance 0.20mm を変更していない。参照元は `E/input-hashes.json`。

| 入力 | SHA256 | 使用 |
| --- | --- | --- |
| smoke | `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9` | Stage 0で1回 |
| Main | `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2` | 照合のみ |

`E/run-router.py` は両 stage の argv を `autoroute corrected.dsn -o out.ses --check` に固定し、既存 stage ディレクトリの再使用を拒否する。DISPLAY / WAYLAND_DISPLAY を除去、stdin は DEVNULL、PTY なし。外側安全上限は1800秒で、今回は自然終了した。Main は `smoke-gate.json` の合格を必須とする。

既定値はソース上、iterations 40、via-cost 5000µm、optimize 1、refine 有効。これらを CLI で指定・変更していない。既存配線を無視するオプションも使用していない。

## Stage 0 の観測

実行 **2026-11-04T03:21:44.878727Z–03:21:44.886473Z**、経過 **0.007757342秒**、exit **0**、外側 timeout **false**。stdout は空。完全な argv・cwd・時刻・全入出力 hash は `E/processes/smoke/record.json`、自己報告は同 `stderr`。

```text
board: 2 layers, 7 pads, 1 nets (0 routable)
keeping existing routing on 1 nets (use --reroute-wired to route from scratch)
grid pitch: 212 um
refine: 0 vertices straightened in 0.00s
routed in 0.00s: 1 iterations, 0 vias, 0 failed nets, 0 conflicted nets
DRC: clean (5 tolerance um)
wrote out.ses
```

入力の唯一のネット N には、U1 の同番号2ランド間の既存0.20mm線分がある。既定パーサーは既存 wire/via を持つネット全体を `fixed` にする（`E/official/crates/dsn/src/parse.rs`）。ログでも固定ネット1、routable 0となった。SES の `network_out` は空で、新しい接続は出力されなかった。

| 保存 SES の静的実測 | 値 |
| --- | --- |
| bytes | 454 |
| SHA256 | `854264bd2867439d0fd492acfe08c91ab119308ec7e5c14322e8fdfe8bf1b7f7` |
| resolution / 単位 | um 10 / 10000単位毎mm |
| path / via | 0 / 0 |
| 幅分布 | 空 |
| 最小幅 | null（pathなし） |
| 0.20mm未満 path | 0（対象が0本） |

`E/inspect-ses.py` は #97以降と同じ、最終 SES の resolution から全 path 幅を実測する方式。**path が0本なので、0.20mm幅の配線生成能力や幅制約の実効性を確認した結果ではない。**

## KiCad import・独立検査

KiCad **9.0.9**、Shapely **2.2.0**、sexpdata **1.0.2**。#105/#107 の検査 runtime を参照し、今回の XDG 設定・cache は新規 runtime 内に作成した。`E/inspection-versions.json` にバージョン確認時の標準出力と警告を保存。バージョン確認では既定 home が読取り専用との警告が出たが、本検査では `E/kicad-env.json` の専用 XDG パスを使用した。

元スモーク基板のコピーへ保存 SES を import・保存し、既存 `read-pcb.py`、KiCad DRC、無改変 #87 resume-01 `check-import.py` を実行した。import・snapshot・DRC はすべて exit **0**。独立 oracle は exit **1**、**`original local copper changed`** の assertion で停止した。検査環境の導入失敗ではなく、元線分の欠落を検出した拒否である。oracle と共通銅箔検査の hash は `E/oracle-hashes.json`。

保存 SES の KiCad import 後、配線は **1本→0本**。U1 の (10,10)–(10,12)mm の元0.20mm線分について、中心線の欠落長は **2.0mm**。非配線要素の意味・snapshot は同一だったが、元の銅箔は保持されなかった。この挙動は今回保存した SES と KiCad 9.0.9 の組合せで観測したものである。

**未接続2件**は `E/processes/smoke-import/drc.json` の **`len(unconnected_items)`**。内訳は U1 の同番号2ランド間、U2.1–U1.1 間。元線分の欠落で前者も未接続になっている。端点座標・UUID は同 JSON に保存した。自己報告の failed nets、未接続ネット数、端点不足数とは別の数え方である。

`E/measure-result.py` は oracle 停止後の保存ファイルを読み取り測定し、`E/smoke-measurement.json` に診断を記録した。raw DRC の violations **0**、銅箔グラフの wrong-net 接触ペア **0**、N の島数 **3**。これらは不合格の診断情報であり、合否用指標の0に読み替えない。

| 合否用4指標 | Stage 0 | Stage 1 |
| --- | --- | --- |
| required unconnected | null | null |
| wrong-net contacts | null | null |
| material violations | null | null |
| unexplained transfer changes | null | null |

**Stage 1 はゲート不合格により未実行。** Main の未配線数・時間・SES幅・import可否はいずれも未測定。`E/smoke-gate.json` は `main_allowed=false`、`E/assessment.json` に判定と実行回数を保存した。

終了コード **2は観測していない**。指示の「2の場合は部分 SES を KiCad DRC で数える」に該当する実行はなかったが、今回の exit 0 の SES についても独立に数え、上記2件を記録した。不合格の4指標は null を維持する。

## 固有の着眼点

1. **グリッド・障害物**：実測ログは **212µm**。固定ソースの `RouterConfig::effective_pitch` は最小クラスの `(width + clearance) × 0.53` を80–500µmに clamp するため、200+200µmから212µmとなる。指示書の「0.40mm相当」は幅とclearanceの和であり、このコミットの実ピッチは0.40mmではなかった。入力規則を変更した結果ではない。新規 path がなく、細いパッドや障害物の回避能力は未測定。保存後銅箔の wrong-net 接触0も、その能力の実証にはならない。
2. **自己 DRC と独立検査**：内蔵 `--check` は幾何検査を5µm toleranceで clean とした。独立検査では未接続と元線分欠落を確認した。自己 DRC は接続完成や KiCad import 後の保存性を保証する検査ではなく、CLI の exit は `result.complete` に基づく。今回の exit 0 / clean は独立合格と一致しなかった。新規銅箔がないので、clearance の数値判定そのものが食い違ったとは結論しない。
3. **比較**：下表の既存 Main 結果を記録する。自己報告と KiCad 件数の定義、および Main と smoke の規模は異なる。

| 評価 | 対象 | 最終未配線 | 秒数 | 件数の出典 |
| --- | --- | --- | --- | --- |
| Freerouting v2.5.0 Run 2 / #95 | Main | 38 | 159.863043 | ルーター報告、Main importなし |
| fastroute / #99 | Main | 37 | 28.184144 | ルーター報告、幅下限200µm |
| fab_router / #103 | Main | 16 | 298.698 | API・stats・保存SES roundtrip自己検査 |
| AutoRoute / #109 | smoke | 2 | 0.007757342 | 保存SES import後のKiCad DRC |
| AutoRoute / #109 | Main | 未測定 | 未測定 | Stage 0不合格により未実行 |

比較元は [#95](issue-95-freerouting-v250-run2.md)、[#99](issue-99-fastroute-width-floor.md)、[#103](issue-103-fab-router-falsification.md)。元集計のコピーと hash は `E/comparison/`、`comparison-sources.json`、比較表の値は `E/comparison.json`。smoke の所要時間や件数から Main の性能順位を推定しない。

今回反証されたのは、**指定入力・指定の既定コマンドがスモークを完成し、元の銅箔を保ったまま KiCad に戻せること**。別条件での能力や、固定配置の完成不可能性は結論しない。

## 提出・検証

作業ブランチ **issue-109-autoroute-falsification**、開始時最新 main **`2321223e7ae7ccfdcee1b8391f642128aa57feb8`**。既存6,837ファイルを最新 main の blob と全件照合した。元 `.git` が読取り専用のため、公式 origin を `/tmp/issue-109-autoroute/git` に bare clone し、現在の作業ディレクトリを work-tree に指定して read-tree とブランチ作成を行った。既存作業ツリーのファイルは書き換えていない。

本書と指定証跡ディレクトリの**追加のみ**を提出する。先行タスクの runtime を含む既存16,438ファイルの hash を `E/preexisting-files.json` に保存し、提出前に内容不変を再照合する。`E/verify.py`・`verification.json` で main の全ファイル、実行回数・ゲート、入力とSES hash、null方針、追加のみ、ELFバイナリ不在を確認する。証跡 hash は `E/manifest.json`。

全体開始 **2026-11-04T03:11:47Z**、2時間期限 **05:11:47Z**。提出直前時刻と経過は `E/submission.json`、Draft PR 作成後の時刻は PR 本文に記録する。**Draft PR を作成し、merge は行わない。**
