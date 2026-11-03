# Issue #105 — fab_router 詳細ルーター有効の単一条件

**判定：FIXED_CONDITION_FAIL。Main の最終未配線は 21 件（#103 は16件）。** 詳細ルーター `tiles` を有効にした単一条件で、外部中断からの回復後に1回の完了実行を得た。保存 SES の全 267 paths が 0.20mm 以上、0.20mm 未満は 0 本。Main の独立4指標は未配線が残るためすべて **null**。自前 checkDrc と Main の独立検査との一致は **未確認**。

対象は [Issue #105](https://github.com/ihsinoky/he-piantor-42/issues/105)。以下 `E/` は [証跡](../hardware/kicad/qualification/issue-105-fab-router-detailed/evidence/) を指す。指示書全文 `E/instructions.md`、Issue 本文 `E/issue105.json`。Main の起動は中断試行1回と、その回復1回。完了実行は1回だけであり、追加条件・追加調整は実施していない。

## 一次情報からの条件特定

[fabPlane/fab_router の固定コミット](https://github.com/fabPlane/fab_router/tree/69cf598db98c136bff16bbe02bccdded95674b18) **`69cf598db98c136bff16bbe02bccdded95674b18`** を GPL-3.0-only 側で利用。本体 `src/`・`spec/` は無改変で、#103 の hash と全件一致した（`source-manifest.json`、`source-identity-vs-103.json`）。一次情報のコピーは `E/official/`。

- README は詳細ルーターを搭載し、global planning は既定 off の独立サブシステムと説明する。完全配線を保証するとはしておらず、密集基板の completion frontier を明記している。
- `spec/api/settings.md:42` は `detailedRouter` を `off`（fast）/ `tiles`（slow）と定義する。
- `tools/acceptance/run-case.ts:269–276` は開発元の slow/SRJ 向け詳細モードとして `detailedRouter = "tiles"` のみを補う。これは SRJ 用コードであり、DSN 全体に slow tier が自動適用されるとは解釈しない。
- `spec/acceptance/README.md` の名前付き参照プロファイルは default/p1/fanout/strict/novia。DSN 用の詳細完全配線プロファイルは定義されていない。参照用 default の60秒上限などは採用せず、#103 の非モード設定を保持する。
- `docs/DESIGN.md §9b` と `src/route/passes.ts:333–346` は tiles が line-search の後に corner-stitch channel search を行うことを示す。既に失敗した接続・後続 pass の ripup/contention 条件で詳細探索へ進む。`globalPlan` は前提ではない（同 §10.8、`passes.ts:1429`）。

従って採用条件は **`detailedRouter: "tiles"` だけ**。`globalPlan: "off"`、fanout false、seed 1、コスト、1800000ms 上限、useFileSettings 未指定を保持した。tscircuit / routeSrj / 受け入れコーパス runner は実行していない。`configuration-decision.json` に判断を保存した。

## Main 前の全項目 readback とハーネス

**2026-11-03T23:42:49.600104+00:00** に元 Main DSN を parse し、無改変 `src/pipeline/index.ts` の `resolveSettings` で全実効設定を取得した。`main-preflight/` と `settings-comparison-before-main.json` に保存。これは設定解決だけで、route / routeDsn は呼ばない。#103 の `report.effectiveSettings` と比較して変更は **off → tiles の1項目だけ**であることを assertion で確認した。未指定フィールドは `<unset>` と明記し、内部派生値を明示設定に置き換えない。実行時には driver が設定を再解決し、この事前 readback および結果 report と完全一致することを検査する。

| 設定（全宣言項目） | #103 | #105 | 差分 |
| --- | --- | --- | --- |
| `angleMode` | `"45"` | `"45"` | 同一 |
| `bendCost` | `0` | `0` | 同一 |
| `connectionBudgetMs` | `"<unset>"` | `"<unset>"` | 同一 |
| `copperToEdgeClearanceUm` | `"<unset>"` | `"<unset>"` | 同一 |
| `detailedBudgetMs` | `"<unset>"` | `"<unset>"` | 同一 |
| `detailedMaxTiles` | `"<unset>"` | `"<unset>"` | 同一 |
| `detailedNegotiation` | `"<unset>"` | `"<unset>"` | 同一 |
| `detailedRouter` | `"off"` | `"tiles"` | 変更 |
| `fanoutEnabled` | `false` | `false` | 同一 |
| `fanoutMaxItems` | `"<unset>"` | `"<unset>"` | 同一 |
| `fanoutMaxPasses` | `"<unset>"` | `"<unset>"` | 同一 |
| `globalBinUm` | `"<unset>"` | `"<unset>"` | 同一 |
| `globalHistoryRamp` | `"<unset>"` | `"<unset>"` | 同一 |
| `globalHistoryWeight` | `"<unset>"` | `"<unset>"` | 同一 |
| `globalLayerBias` | `"<unset>"` | `"<unset>"` | 同一 |
| `globalMaxIterations` | `"<unset>"` | `"<unset>"` | 同一 |
| `globalPlan` | `"off"` | `"off"` | 同一 |
| `globalPresentWeight` | `"<unset>"` | `"<unset>"` | 同一 |
| `holeClearanceUm` | `"<unset>"` | `"<unset>"` | 同一 |
| `ignoreNetGroups` | `[]` | `[]` | 同一 |
| `layers` | `{}` | `{}` | 同一 |
| `maxItems` | `"<unset>"` | `"<unset>"` | 同一 |
| `maxPasses` | `100` | `100` | 同一 |
| `maxStagnantPasses` | `3` | `3` | 同一 |
| `neckWidthUm` | `"<unset>"` | `"<unset>"` | 同一 |
| `optimizerEnabled` | `true` | `true` | 同一 |
| `optimizerMaxItems` | `"<unset>"` | `"<unset>"` | 同一 |
| `optimizerPasses` | `"<unset>"` | `"<unset>"` | 同一 |
| `orderByDifficulty` | `true` | `true` | 同一 |
| `planeViaCost` | `5` | `5` | 同一 |
| `preferredDirectionCost` | `1.5` | `1.5` | 同一 |
| `presentCongestionCost` | `"<unset>"` | `"<unset>"` | 同一 |
| `ripupEnabled` | `true` | `true` | 同一 |
| `routerEnabled` | `true` | `true` | 同一 |
| `seed` | `1` | `1` | 同一 |
| `shoveEnabled` | `true` | `true` | 同一 |
| `shoveMaxDepth` | `"<unset>"` | `"<unset>"` | 同一 |
| `shoveMaxMoved` | `"<unset>"` | `"<unset>"` | 同一 |
| `shoveWindowUm` | `"<unset>"` | `"<unset>"` | 同一 |
| `startRipupCost` | `100` | `100` | 同一 |
| `strictDrc` | `false` | `false` | 同一 |
| `timeBudgetMs` | `1800000` | `1800000` | 同一 |
| `useFileSettings` | `"<unset>"` | `"<unset>"` | 同一 |
| `viaCost` | `50` | `50` | 同一 |
| `viasAllowed` | `true` | `true` | 同一 |

Bun **1.4.4**、TypeScript 5.9.3、@types/bun 1.4.2 は #103 と同一。公式 Bun ZIP の SHA256 は `bf8ccbfb2b0b80159e0f9a6d15c55317add8077534dbc6130a3edb52fccb395c`。`installation.json`・`bun-install.log` に導入を記録した。

ドライバ基本形は #103 と同じ公開 `routeDsn` → SES 保存 → 元 DSN 再読込 → **保存 SES** applySes → checkDrc。追加したのは設定受け渡し・readback 専用モード・実効設定一致チェックである。変更後 `driver.ts` と旧版、`driver-diff.patch` を保存した。ルーター本体を改変していない。headless（DISPLAY/WAYLAND_DISPLAY 除去）、外側上限1920秒。`run-router.py` は既存 stage ディレクトリの再利用を拒否し、Main 前にスモーク合格と事前設定差分のゲートを検査する。

## 入力・固定条件

#87 resume-01 の corrected.dsn を byte 同一コピーした。実行前後の SHA256 は以下と一致し、配置固定、2 signal layers、幅/clearance 200µm を保持。Main parse は49部品・37ネット・197 pads、F.Cu/B.Cu。詳細は各 `parse.json`。

| 入力 | SHA256 |
| --- | --- |
| Main | `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2` |
| smoke | `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9` |

実行 argv・cwd・UTC・全入出力 hash は `E/processes/{smoke,main}/record.json` にある。

## Stage 0：スモーク合格

2026-11-03T23:42:49.692818+00:00–2026-11-03T23:42:49.808700+00:00、0.116秒、exit 0。SES 生成成功、全2 paths が0.20mm、未配線0。保存 SES 再適用後の自前 checkDrc は違反0・未接続0。

KiCad **9.0.9** で元基板のコピーに import して保存し、保存基板の snapshot・KiCad DRC・#87 の既存独立銅箔グラフ/非配線同一性検査を実行した。**required unconnected / wrong-net contacts / material violations / unexplained transfer changes はすべて0**。自前 checkDrc と一致した（`smoke-independent.json`）。検査プロセスは全て exit 0。

スモークゲート保存 **2026-11-03T23:44:47.423316+00:00** → Main 開始 **2026-11-03T23:49:11.383590+00:00** の順を検証した。検査ランタイムの初回 Python package 導入が /tmp 容量不足で停止したため、#105 の一時 geometry 環境を workspace に移し再導入してから独立検査した。この導入修復では配線を再実行していない。その他の導入時パス修復は `installation.json`、ライブラリ hash は `kicad-package-hashes.json`、oracle hash は `oracle-hashes.json`。

## 外部中断の保存と回復

前回の Main は **2026-11-03T23:44:47.507650+00:00** に起動し、ユーザーから報告されたランタイム再起動という外部要因で中断された。result.json・out.ses・完了 record.json は存在せず、ルーターが正常終了して返した結果ではない。途中ログは pass 6・未接続17件までを含むが、本テストの最終結果として採用しない。中断原因の帰属はユーザーのランタイム再起動報告に基づく。

元の processes/main/ 全ファイルを **processes/main-attempt-1-interrupted/** に移して byte/hash 同一で保存し、元 main-launch.json も同ディレクトリの launch-original.json に複製した。元 main-launch.json・スモーク証跡・条件特定・readback・既存スクリプトは変更していない。再開時の全証跡 hash と検証結果は recovery-preflight.json。

ユーザーの明示指示により、同一条件の回復 Main を **1回だけ** 実行した。これは設定探索ではなく、インフラ障害で未完了となった実行の回復である。起動回数は2回（外部中断1、回復1）、本テストの完了実行は1回。スモークおよび条件特定は再実行していない。Bun と clone は workspace に残っており /tmp の symlink を復旧しただけで、再導入や配線探索はない。ハーネス run-router-recovery.py の変更は launch 記録を main-recovery-launch.json に分ける1箇所だけで、driver.ts は元のままである。

## Stage 1：単一の完了 Main と #103 比較

| 実測 | #103 API既定相当 | #105 tiles |
| --- | --- | --- |
| 最終未配線 | 16 | 21 |
| passes | 15 | 10 |
| 停止理由 | stagnant | stagnant |
| timedOut / aborted | False / False | False / False |
| プロセス秒数 | 298.698 | 262.260 |
| SES 幅分布（mm） | {"0.2": 276} | {"0.2": 267} |
| 0.20mm未満 path | 0 | 0 |
| via 数 | 115 | 107 |
| SES path 数 | 276 | 267 |

全設定差分は「Main 前の全項目 readback」の表のとおり詳細モードだけ。pass ごとの残接続は以下（最終 SES と混同しない）。

- #103: 27 → 16 → 17 → 16 → 14 → 15 → 14 → 15 → 15 → 15 → 15 → 15 → 15 → 15 → 15
- #105: 27 → 15 → 16 → 17 → 16 → 17 → 17 → 18 → 16 → 17

Main は **2026-11-03T23:49:11.383590+00:00–2026-11-03T23:53:33.643709+00:00**、exit **0**、外側 timeout **False**。自前結果は `incompleteBefore=127` → `incompleteAfter=21`。保存 SES の SHA256 は `3786385549dd0dcb56169e3777368c6dc5b4c0a8ea378a313281898ce0575dd1`。幅は `(resolution um 10)` から10000単位/mmとして全 path を静的実測した。層別 {"F.Cu": 182, "B.Cu": 85}、中心線長 796.394308mm。これは幅の実測であり、実銅箔 clearance の独立合格ではない。

`report.incompleteAfter`・`statsAfter.connections.incomplete`・保存 SES 再適用後の `checkDrc.counts.incompletes` は一致した。自前 checkDrc は **{"violations": 0, "incompletes": 21}**、report violationsAdded は 0。個別端点は `check-drc-after.json`、ネット別未配線は `result.json` の perNet、pass と接続の全イベントは stdout と `main-events.json` に保存した。途中 pass から停止後の巻戻し/optimizer を経た最終保存結果への差の原因は、専用 hook で観測していないため特定しない。

API `ok: true` と exit 0 は処理と SES 生成の成功であり、完全配線を示さない。残接続数と停止理由は明記され、未完了を隠していない。

| Main 独立指標 | 値 |
| --- | --- |
| required unconnected | null |
| wrong-net contacts | null |
| material violations | null |
| unexplained transfer changes | null |

未配線が残るため指示書に従い Main の KiCad import・独立検査は実施せず、import 可否は未測定。**Main の自己判定と独立検査との一致は未確認**。スモークの一致を転用しない。詳細化後の最終未配線は #103 から +5 件であり、この事実をそのまま報告する。単一試行でルーター方式一般や配置の完成不可能性を結論しない。

## 提出・検証

ブランチ **issue-105-fab-router-detailed**、base **9f97ebe6626ebf0c38e030bb8c9a2b9c27fb462d**。main 最新の全 tracked files を byte/hash 照合した。元 `.git` が読取り専用なので管理情報だけ `/tmp/issue-105-fab-router/git` に複製し、現在のディレクトリを work-tree に使用。既存ファイルには変更せず、本書と指定証跡ディレクトリだけを追加。前タスクの未追跡成果物は提出対象に含めない。依存 package・clone・実行バイナリは含めない。

前回開始・期限は元の timebox.json に保存。今回の再開開始は **2026-11-03 23:48:06 UTC**、再開から2時間の期限は **2026-11-04 01:48:06 UTC**（recovery-preflight.json）。既存のスモーク・条件特定を引き継ぎ、回復・検査・記録・Draft PR 作成をこの期限内に行う。実環境 UTC を一貫して使用する。集計・文書生成・検証には `summarize-recovery.py`・`write-report-recovery.py`・`verify-recovery.py` を使用。旧版スクリプトは前回証跡として保存し、実行していない。検証は `verification.json`、成果物 hash は `manifest.json`、提出時刻は `submission.json`。Draft PR を作成し、**merge はしない**。
