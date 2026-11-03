# Issue #101 — freeRouting.org C++版 v2.0.1 限定反証テスト

**Stage 0 で不合格。Main は実行していない。** 公式ソースを変更せずビルドできたが、指定スモーク DSN に対する単一の `freeRouting --autoroute corrected.dsn` は **SIGSEGV（Python subprocess の終了コード -11）**で終了した。経過時間は **0.064540秒**。stdout・stderr はともに空で、`corrected.ses` は生成されなかった。指示書の「失敗したら Main に進まない」に従って停止し、ルーターの再実行・設定探索は行っていない。

対象は [Issue #101](https://github.com/ihsinoky/he-piantor-42/issues/101)。以下 `E/` は [今回の証跡](../hardware/kicad/qualification/issue-101-freerouting-cpp-falsification/evidence/) を表す。指示書全文は `E/instructions.md`、Issue 本文は `E/issue101.json`、機械判定は `E/assessment.json`。

## 公式配布物とビルド

GitHub の Java Freerouting とは別系統の **freeRouting.org C++版 2.0.1** を対象とした。[公式 Building from Source](https://freerouting.org/freerouting/building-from-source) が指定する [公式 tarball](https://freerouting.org/freerouting/changelog/freeRouting-2.0.1.tar.gz) を直接取得した。ソースの公開 Git リポジトリ・非公式ミラーは使用していない。

| 対象 | SHA256 |
| --- | --- |
| freeRouting-2.0.1.tar.gz | `81332ab624736a2f9f71ec14cf3b24610c98dceeeb816f5635d4479307f2ad1a` |
| ビルド済み実行ファイル（提出物には含めない） | `8d87ac8eb9784ae6b133ab174af3f977ac88ffdbe945736d45eda7938e67ecb6` |
| smoke DSN | `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9` |
| Main DSN（入力照合のみ、未実行） | `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2` |

取得元・hash は `E/installation.json`、HTTP 応答ヘッダーは `E/official/download.headers`。公式説明ページも `E/official/*.html` に保存した。`E/source-manifest.json` は tarball 全ソースファイルの hash 一覧で、ビルド後にも元のファイルが変更されていないことを照合した。

環境は Ubuntu 24.04、GCC 13.3.0、GNU make、Qt **6.4.2**。既存のコンパイラと make を使用し、Qt の開発・実行パッケージは Ubuntu Azure mirror から取得して、一時 `.issue101-runtime/qt/` に `dpkg-deb -x` で展開した。システムへのパッケージインストールは行っていない。パッケージ名・版・hash は `E/qt-download-azure.log`、`E/qt-package-hashes.json`、`E/qt-runtime-package-hashes.json`。当初の apt UID 切替エラーとデフォルト mirror の待機もログに残し、隔離した Azure source list と `APT::Sandbox::User=root` で取得を完了した。

展開した `freeRouting/` 内で、公式手順どおり次を実行した。

```text
qmake6 -v
qmake6
make -j2
```

`qt.conf` で展開先へ Qt の探索パスを向け、`LD_LIBRARY_PATH` で同じ Qt 実行ライブラリを指定した。初回 make は全 C++ コンパイルを完了したが、最後のリンクで展開先の `libGLX.so.0` とリンカー検索パスが不足して停止した。Ubuntu の `libglx0`・`libgl1` を明示取得・展開し、`LIBRARY_PATH` を同じライブラリディレクトリに設定して **make のリンクを再開**したところ成功した。ソースや `.pro` は変更していない。初回失敗は `E/make.log`、再開成功は `E/make-resume.log`、全 argv・UTC 時刻・終了コードは `E/build-record.json`。再現手順は `E/build-procedure.txt`、`E/build.py`、`E/resume-build.py`、`E/setup-runtime.py`。

ビルドは22:29:01–22:44:24 UTCに完了。`-h` の表示は `FreeRouting version 2.0.1`（`E/help.txt`）。バイナリと offscreen plugin の `ldd` で依存ライブラリの未解決はなかった（`E/binary-ldd.txt`、`E/qt-offscreen-ldd.txt`）。これはクラッシュ原因の特定や正常動作の証明ではない。

## Stage 0：SES 不生成のためゲート不通過

指定の #87 resume-01 `smoke-restore/corrected.dsn` を byte 同一コピーし、実行前後に hash を照合した。Main 入力も指定 hash と一致することだけを確認した（`E/input-hashes.json`）。配置、2層、幅・クリアランス0.20mmの入力条件は変更していない。

正確なルーター引数は次のとおり。実行ファイルは `.issue101-runtime/freeRouting/bin/freeRouting`、cwd は `E/processes/smoke/`。

```text
freeRouting --autoroute corrected.dsn
```

`--angle`、`--no-postroute`、デバッグ設定等は追加していない。45°・optimizer 有効の既定値は公式説明と保存したソースで確認した。実際にどの処理段階まで到達したかは、空のログからは確認できない。

DISPLAY・WAYLAND_DISPLAY を除去し、Qt の画面 backend のみ `QT_QPA_PLATFORM=offscreen` とした。Qt plugin・共有ライブラリのパスと、空の隔離 XDG ディレクトリを指定した。これはルーター設定の変更ではない。完全な環境・argv・cwd・入出力 hash は `E/processes/smoke/record.json` に保存した。

実行は **2026-11-03 22:44:29.165522–22:44:29.246820 UTC**、プロセス経過0.064540秒、終了コード -11。外側の時間制限は発火していない。入力2,116 bytesは不変、stdout 0 bytes、stderr 0 bytes、SES なし。`E/run-router.py` は stage ディレクトリの再利用を拒否し、Main 前にスモークゲートと独立4指標0を要求する。

KiCad 9.0.9・Python 検査依存物の一時環境は準備・起動確認まで済ませた（`E/inspection-setup.json`、`E/kicad-runtime-package-hashes.json`、`E/geometry-install.log`）。ただし **import 対象の SES が存在しないため、KiCad import・DRC・実銅箔独立検査・SES 全path幅実測はいずれも実施できなかった**。スモークの4指標すべて0というゲートは成立しない。準備した `run-checks.py` 等を、実行済み証跡とは扱わない。

| スモークの観測・独立指標 | 値 |
| --- | --- |
| router 未接続数 | null（未測定） |
| required unconnected | null |
| wrong-net contacts | null |
| material violations | null |
| unexplained transfer changes | null |

今回の null は **SES 不生成により測定不能**という意味であり、未配線残存を実測したという意味ではない。未接続数を推測で0や正の値に置き換えない。特に、DSN 読込・SES 書出の受け渡しに説明不能な変化がないことは確認できていない。原因の切り分けを目的とする別条件での再実行・デバッガ実行は行わず、SIGSEGV の根本原因は未特定とする。

## Stage 1 と比較

`E/smoke-gate.json` の `main_allowed=false` に従い、**Main 起動回数は0**。Main の未配線数・SES 幅・KiCad import 可否は未測定、独立4指標はすべて null。未完了 Main でも SES を書けるか、未接続数を数えられるかという固有の着眼点は、Main 未実行のため結論を出せない。

| 候補 | Main 未配線 | 最終 SES 幅条件 | 今回の到達点 |
| --- | ---: | --- | --- |
| Freerouting v2.5.0 Run 2（[#95](issue-95-freerouting-v250-run2.md)） | 38 | この比較では判定対象外 | 未完配線で optimizer skip |
| fastroute（[#99](issue-99-fastroute-width-floor.md)） | 37 | 全231 paths が0.20mm、下限未満0本 | 幅適合、未配線残存 |
| freeRouting.org C++ 2.0.1（#101） | null | SES なし、未測定 | スモーク SIGSEGV、Main 未実行 |

比較元の集計は `E/baseline-95/`、`E/baseline-99/` に保存した。今回の結果を38件・37件との配線性能差には換算しない。

## 判定と提出範囲

判定は **STAGE0_FAIL / 固定条件で不合格**。ビルド不能・ビルド時間切れではなく、ビルド後の指定 headless スモークで SES を生成できなかったことが失敗理由である。この単一条件を Main 完成の合格候補には認定できない。一方、この観測だけから他環境での一般的な動作不能、特定のソース不具合、Main の配線不可能性までは主張しない。

最新 origin/main `a50c824db1e86c6be90e44abbea9bb03b858a338` から **issue-101-freerouting-cpp-falsification** を作成した。元 `.git` が読取り専用のため管理情報のみ `/tmp/issue-101-freerouting-cpp/git` に複製し、現在ディレクトリを work-tree として使用した。開始時のローカル main は古く、#97・#99 が未追跡で残っていたが、最新 main の全6,403ファイルと byte/hash 一致を確認した上で一時 index・branch を更新した。既存ファイルへの書換えはない（`E/baseline-verification.json`）。

成果物は本書と指定の新規証跡ディレクトリへの追加のみ。tarball・ビルド済みバイナリ・依存パッケージ本体は提出物に含めない。保守的開始 **2026-11-03 22:25:00 UTC**、全作業の期限 **2026-11-04 00:25:00 UTC**。指示書の日付と異なる実環境 UTC 時計を一貫して用いた。取得・ビルド・実行・記録・検証・commit/push・Draft PR 作成をこの2時間に含める。

`E/verify.py` は元ファイルと公式ソースの不変、厳密 argv、実行証跡 hash、Main ゲート、追加のみ、バイナリ不包含、時間箱を確認する。結果は `E/verification.json`、成果物 hash 一覧は `E/manifest.json`、提出直前時刻は `E/submission.json`。Draft PR として提出し、main への直接 push・merge は行わない。
