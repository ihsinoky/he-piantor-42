# Issue #107 — Topola の限定反証テスト

**判定：FIXED_CONDITION_FAIL。Stage 0 のスモークで未配線1件が残ったため、Main は実行しない。** デフォルトの `topola corrected.dsn -o out.ses` は0.042432秒で自然終了し、SES 生成・KiCad import に成功した。しかし出力は入力に存在した0.20mmの線分1本だけで、新しい接続を作らなかった。独立検査は未接続の assertion で失敗した。4指標は指示どおりすべて **null**。

対象は [Issue #107](https://github.com/ihsinoky/he-piantor-42/issues/107)。以下 `E/` は [証跡](../hardware/kicad/qualification/issue-107-topola-falsification/evidence/) を指す。指示書全文は `E/instructions.md`、Issue 本文は `E/issue107.json`。ルーター実行は **smoke 1回、Main 0回**。`.cmd`、追加配線オプション、設定探索、再実行、ソース修正は行っていない。

## 公式取得・ビルド

公式 [Codeberg の固定コミット](https://codeberg.org/topola/topola/src/commit/666e06cfd7ba1f1e5daf700288acb9e0a4f84ceb) **`666e06cfd7ba1f1e5daf700288acb9e0a4f84ceb`**（既定ブランチ develop）を使用。CLI・本体ソースの SPDX は MIT。README は work-in-progress interactive topological router と説明する。一次資料・ライセンスは `E/official/`、公式 API 応答・取得 URL・archive SHA256 は `E/codeberg-*.json` と `E/acquisition.json` に保存した。GitHub ミラーは使用していない。

Codeberg の Git 通信が停滞したため、公式 Codeberg のコミット指定アーカイブを取得した。Git 依存 petgraph も公式アーカイブと commit API から Git オブジェクトを復元し、**元コミット `1bae625ec5f0373ebe859e027af56dcb11a3ac85` と SHA が完全一致**することを assertion で確認した。Cargo キャッシュにこの shallow commit を入れ、Git URL を同一コミットのローカルリポジトリへ向けて取得を回復した。依存の置換版やソースパッチは使用していない。`E/reconstruct-petgraph.py`・`petgraph-reconstruction.json`・`installation.json` に手順と環境を保存した。

実行したビルドコマンドは指定どおり：

```text
cargo install --locked --path crates/topola-cli
```

Rust **1.99.1**、Cargo **1.99.1**、Topola **topola-cli 0.1.0**。最終ビルド exit 0、release profile 2m09s（Cargo 表示）。バイナリ SHA256 は `dc2cee1668023a88d2f14335940115660684a4a9fbdbf6d64b6fb8a61057a2c0`。バイナリ自体・ソースアーカイブ・依存キャッシュは成果物に含めない。

**公式ソースに Cargo.lock は存在しない。** `--locked` を維持したまま Cargo は警告を出し、その時点の依存を解決してビルドした。従って全依存が upstream lockfile で固定されたビルドとは扱わない。完全なコンパイルログは `E/build-final.log`、導入失敗と取得回復は `E/build.log`・`build-retry.log`・`rust-install*.log`。Rust の初回 /tmp ダウンロード展開は EOF で失敗し、容量のある workspace にランタイムを移して再導入した。ビルド再試行は配線再実行ではない。

## 固定入力・実行条件

#87 resume-01 の入力を実行前に SHA256 照合し、スモークのコピーは実行後も同一と確認した。配置、2 signal layers、配線幅・clearance 0.20mm を変更していない。`E/input-hashes.json` に参照元と hash を保存。

| 入力 | SHA256 |
| --- | --- |
| Main（照合のみ・実行なし） | `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2` |
| smoke | `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9` |

両 stage 用のハーネス `E/run-router.py` は argv を `topola corrected.dsn -o out.ses` に固定。DISPLAY / WAYLAND_DISPLAY を除去、stdin は DEVNULL、PTY なし。外側安全上限は **1800秒**、期限到達時にプロセスグループを停止して記録する。既存 stage ディレクトリの再使用を拒否し、Main 前にスモーク合格ゲートを要求する。今回は短時間の自然終了であり、timeout や対話待ちを観測していない。

## Stage 0：SES・KiCad・独立検査

実行 **2026-11-04T01:12:31.864533Z–01:12:31.906953Z**、exit **0**、経過 **0.042431747秒**、外側 timeout **false**。stdout / stderr はともに空で、Topola 自身の未配線件数や停止理由の出力はない。完全 argv・cwd・全入出力 hash は `E/processes/smoke/record.json`。

SES は329 bytes、SHA256 `c63256d74101330a681400b1ba472618f78608c12745f75ae687130feca83826`。`(resolution um 1)` を1000単位/mmとして全 path を静的測定した（#97以降と同方式）。

| SES 実測 | 値 |
| --- | --- |
| path 数・層 | 1、F.Cu |
| 幅分布 mm | {"0.2": 1} |
| 0.20mm未満 path | 0 |
| 中心線長 | 2.0mm |
| via | 0 |

唯一の path は `(path F.Cu 200 10000 -10000 10000 -12000)`。入力の既存配線と同じ線分である。KiCad 保存後の snapshot でも元基板と銅箔が一致し、追加配線は0本。**幅下限はこの保存 SES で成立したが、新規に自動生成した配線が DSN 規則を守るという実証にはならない。** CLI ソースには既定 `routed_band_width: 100.0` があるものの、今回100µmの新規配線は出力されなかったため、その影響は未測定。

KiCad **9.0.9** で元スモーク基板のコピーに保存 SES を import・保存し、既存 read-pcb、KiCad DRC、#87 の無改変 `check-import.py` を順に実行。import・snapshot・DRC のプロセスは exit 0。独立 oracle は **exit 1 / `AssertionError: KiCad unconnected remains`** で停止した。これは検査環境の導入エラーではなく、未配線を検出した期待どおりの拒否である。

**未配線1件**は、保存 SES を import した基板の KiCad DRC JSON `unconnected_items` の要素数。U2.1（16,10mm）と U1.1（10,10mm）の欠落接続である。Topola の自己申告、端点不足数、未接続ネット数ではない。`E/processes/smoke-import/drc.json` に端点・UUIDを保存した。補助の既存銅箔グラフも net N が2つの島に分かれることを示す。

| 独立4指標 | Stage 0 | Stage 1 |
| --- | --- | --- |
| required unconnected | null | null |
| wrong-net contacts | null | null |
| material violations | null | null |
| unexplained transfer changes | null | null |

Stage 0 は未配線残存のため全指標 null。診断用の raw DRC は violations 0、非配線意味・snapshot の非配線要素・元の銅箔は同一だったが、これらを4指標の合格に読み替えない。`E/measure-smoke.py` は未改変 oracle の失敗後に読み取り測定だけを追加し、raw 診断と null の合否指標を `E/smoke-independent.json` に分けて保存した。検査用 runtime は #105 から再利用し、oracle hash は `E/oracle-hashes.json` に記録した。

**Stage 1 はゲート不合格により未実行。** Main の未配線数、所要時間、SES 幅、KiCad import 可否はすべて未測定。`E/smoke-gate.json` は main_allowed=false。1800秒の Main 打切りを観測したものでもない。

CLI の `Invoker::replay` は内部 `execute` の Result を処理せず、CLI はその後 SES を保存する実装である（固定ソース `E/official/src/autorouter/invoker.rs`）。従って exit 0 を完全配線の根拠にはできない。今回の内部失敗原因・コマンドの途中状態は計測しておらず、根本原因は特定しない。

## 既存 Main 結果との比較

| 評価 | 対象 | 最終未配線 | プロセス秒数 | 備考 |
| --- | --- | --- | --- | --- |
| Freerouting v2.5.0 Run 2 / #95 | Main | 38 | 159.863043 | fanout有効、未配線残存で optimizer skip |
| fastroute / #99 | Main | 37 | 28.184144 | 幅下限200µm指定 |
| fab_router / #103 | Main | 16 | 298.698 | API既定相当 |
| Topola / #107 | smoke | 1 | 0.042432 | 入力の既存銅箔のみ、Stage 0 不合格 |
| Topola / #107 | Main | 未測定 | 未測定 | ゲートにより未実行 |

比較元は [#95](issue-95-freerouting-v250-run2.md)、[#99](issue-99-fastroute-width-floor.md)、[#103](issue-103-fab-router-falsification.md)。対応する集計は `E/comparison.json`。Topola のスモーク1件と他の Main の件数・速度は直接比較できない。今回の事実は、指定の既定条件ではスモーク接続を完成できなかったことであり、Topola 全般の能力、別コマンドでの挙動、固定配置の完成不可能性は結論しない。

## 提出と検証

作業ブランチ **issue-107-topola-falsification**、最新 main の base **`d17f59cae40e21adec453194e219530fb9ae91dc`**。作業開始時に既存6,749ファイルを最新 main の Git blob と全件照合した。元 `.git` が読取り専用のため管理情報だけ `/tmp/issue-107-topola/git` に複製し、現在のディレクトリを work-tree に使用。read-tree で index を合わせ、既存ファイルを書き換えずブランチを作成した。

本書と指定証跡ディレクトリの追加だけを提出する。取得・ビルド用 `.issue107-runtime/` と先行タスクの `.issue105-runtime/` は提出対象外。既存ファイルの再照合、追加のみ、バイナリ不在、ゲートと件数の整合を `E/verify.py`・`verification.json` で確認。証跡 hash は `E/manifest.json`。

全体開始 **2026-11-04T01:03:12Z**、2時間期限 **03:03:12Z**。取得・ビルド・スモーク・独立検査・記録・Draft PR 作成を時間箱内で行う。提出直前時刻・経過は `E/submission.json`、PR 作成後の時刻は PR 本文に記録する。**Draft PR を作成し、merge はしない。**
