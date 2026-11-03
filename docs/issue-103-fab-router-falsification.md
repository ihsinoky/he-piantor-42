# Issue #103 — fab_router の限定反証テスト

**固定条件で不合格。** Main を単一設定・1回実行し、最終 SES に対応する自前接続検査で**未配線16件**が残った。最終 SES は全276 paths が0.20mmで、下限未満は0本。スモークは KiCad import・独立4指標すべて0・自前 checkDrc との一致を確認してから Main に進めた。Main は未配線残存のため独立4指標をすべて **null** とする。

対象は [Issue #103](https://github.com/ihsinoky/he-piantor-42/issues/103)。以下 `E/` は [証跡](../hardware/kicad/qualification/issue-103-fab-router-falsification/evidence/) を指す。指示書全文は `E/instructions.md`、Issue 本文は `E/issue103.json`。追加実行・設定探索はしていない。

## 対象・導入・再現条件

公式 [fabPlane/fab_router](https://github.com/fabPlane/fab_router/tree/69cf598db98c136bff16bbe02bccdded95674b18) を clone し、commit **`69cf598db98c136bff16bbe02bccdded95674b18`** を使用。デュアルライセンスの **GPL-3.0-only 側**として利用した（`E/official/LICENSE`、`COPYING`）。本体の `src/`・`spec/` は無改変。公式コード・仕様の参照箇所、全ソース hash、導入情報は `E/official/`・`source-manifest.json`・`source-provenance.json` に保存した。

Bun **1.4.4** は公式 Linux x64 ZIP を取得し、GitHub release asset digest と SHA256 `bf8ccbfb2b0b80159e0f9a6d15c55317add8077534dbc6130a3edb52fccb395c` を照合して展開した。`bun install` は成功（5 packages、TypeScript 5.9.3、@types/bun 1.4.2）。コマンド・所要時間・終了コード・stdout/stderr は `E/bun-installation.json`・`dependency-install.json`・`bun-install.log`。

初回 full clone は `/tmp` の512MB容量上限で失敗し、一時物を `.issue103-runtime/` に移して shallow clone した。最初の `bun install` は既定 cache が読取り専用のため EROFS となり、`BUN_INSTALL_CACHE_DIR` を一時領域に指定して再実施した。いずれも配線前の導入修復であり、配線の再試行ではない。依存パッケージ本体・clone 本体・実行バイナリは提出物に含めない。

自作の最小ドライバ `E/driver.ts`（GPL-3.0-only）は、無改変の公開 `routeDsn` API を1回呼び、SES・report・stats・diagnostics を保存する。続いて元 DSN を再読込し、**実際に保存した SES** を `applySes` して `checkDrc` を実行する。これは自己検査の serialization roundtrip であり、独立検査ではない。tscircuit / `routeSrj` は呼ばない。受け入れコーパス全体の runner は使っていない。

実行形は両 stage 共通で次のとおり。絶対パス・cwd・UTC・経過時間・終了コード・全入出力 hash は `E/processes/{smoke,main}/record.json` にある。

```text
/tmp/issue-103-fab-router/bun/bun-linux-x64/bun run E/driver.ts /tmp/issue-103-fab-router/fab_router STAGE/corrected.dsn STAGE
```

`DISPLAY`・`WAYLAND_DISPLAY` を除去して headless 実行。設定の追加は **`timeBudgetMs: 1800000`（timeoutSeconds 換算1800秒）だけ**。外側安全上限は1920秒。その他は公開 API の組込みデフォルトで、`useFileSettings` は未指定（false）、neck-down 下限 `neckWidthUm` も未指定で既定実装はネットクラス幅を維持する。両 stage の実効設定 readback は同一である。

```json
{
  "maxPasses": 100,
  "maxStagnantPasses": 3,
  "viaCost": 50,
  "planeViaCost": 5,
  "bendCost": 0,
  "preferredDirectionCost": 1.5,
  "startRipupCost": 100,
  "ripupEnabled": true,
  "fanoutEnabled": false,
  "routerEnabled": true,
  "optimizerEnabled": true,
  "strictDrc": false,
  "layers": {},
  "viasAllowed": true,
  "ignoreNetGroups": [],
  "seed": 1,
  "shoveEnabled": true,
  "orderByDifficulty": true,
  "detailedRouter": "off",
  "globalPlan": "off",
  "timeBudgetMs": 1800000,
  "angleMode": "45"
}
```

**既定では `detailedRouter: "off"`、`globalPlan: "off"`、fanout false、optimizer true、shove true** である。格子非依存詳細探索を搭載するという候補の説明から、今回それが有効だったとは推定しない。slow-tier の tiles profile などへの切替は設定探索になるため行っていない。今回の結果の範囲はこの API デフォルト相当条件である。

## 入力・固定条件

#87 resume-01 の `smoke-restore/corrected.dsn` と `main-restore/corrected.dsn` を byte 同一コピーし、実行前後に指定 SHA256 と照合した。入力・配置・ルールは変更していない。Main の parse summary は49部品・37ネット・197 pads・2 signal layers（F.Cu/B.Cu）、defaultWidth/defaultClearance・default/smd 間 spacing はいずれも200µm。詳細は各 `parse.json`。

| 入力・出力 | SHA256 |
| --- | --- |
| smoke DSN | `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9` |
| Main DSN | `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2` |
| smoke SES | `21fbea511c0d496440312037dc746801c4c54721f17bfb68e9d29c5a81244b19` |
| Main SES | `4f17a8505b4f0ff82050f014e83733154287d18d8e0447dbb6946a0a9e2a98bc` |

## Stage 0：独立検査と自己判定が一致

スモークは **2026-11-03T22:56:24.788689+00:00–2026-11-03T22:56:25.072167+00:00**、プロセス経過0.283秒、exit 0。SES 983 bytes、全2 paths が0.20mm、未配線0。自前 `checkDrc` は違反0・未接続0（`E/processes/smoke/check-drc-after.json`）。

KiCad **9.0.9** へ元基板のコピーに SES を import し、保存した基板の snapshot・KiCad DRC・既存 #87 `check-import.py` の実銅箔グラフ検査と非配線同一性検査を実行した。元のローカル銅箔を保持し、**required unconnected / wrong-net contacts / material violations / unexplained transfer changes はすべて0**。DRC の violations / unconnected_items も0。`E/smoke-independent.json` と `E/processes/smoke-*/` が実測証跡で、自前判定との一致はこの fixture の範囲で確認できた。

最初の import 起動は `libprotobuf.so.32` 不足で基板読込前に失敗した。失敗 record を `smoke-ses-import-runtime-failure/` に保存し、KiCad 9 用追加ライブラリを展開して**検査だけ**を再実行した。最終検査プロセスはすべて exit 0。Probe 検査ライブラリは元の footprint から作成し、基板は編集していない。KiCad のパッケージ hash・依存導入・検査環境・oracle hash は `E/kicad-package-hashes.json`・`setup-inspection.py`・`complete-inspection-runtime.py`・`kicad-env.json`・`oracle-hashes.json` に記録した。

スモーク合格ゲートは **2026-11-03T22:57:12.823385+00:00** に保存し、Main 起動 **2026-11-03T22:57:23.683684+00:00** より前である。`run-router.py` は stage の再利用を拒否し、Main 前に合格ゲート・独立4指標0・自前 checkDrc 0を要求する。

## Stage 1：最終残接続と正直な未完了報告

Main は **2026-11-03T22:57:23.683684+00:00–2026-11-03T23:02:22.383444+00:00**、プロセス経過 **298.698秒**、exit **0**。report は **15 passes、未配線127→16件、stoppedBy=`stagnant`、timedOut=false、aborted=false**。1800秒上限・外側1920秒上限の発火有無は record/report に記録している。

pass 終了時の残接続は **27 → 16 → 17 → 16 → 14 → 15 → 14 → 15 → 15 → 15 → 15 → 15 → 15 → 15 → 15**（`E/main-events.json`）。途中 pass 最少は14件、最終 pass hook は15件だが、最終保存結果は16件である。停止後の巻戻し・optimizer それぞれの直後を観測する hook はないため、この増加の原因を特定したとは扱わない。途中 pass と最終保存結果を区別する。最終 `incompleteAfter` は `statsAfter.connections.incomplete` と、保存 SES を再適用した `checkDrc.counts.incompletes` に一致した（`E/assessment.json` の `self_roundtrip_consistency`）。未接続の個別端点は `check-drc-after.json`、ネット別は `result.json` の `perNet` に残す。

`ok: true` と exit 0 は API 処理・SES 生成成功を示し、完全配線を意味しない。**report に残接続数と停止理由が明記される**ため、未完了を隠す出力ではなかった。driver も最終ログに `incompleteAfter`・`stoppedBy`・checkDrc 件数を明示する。report の `violationsAdded` は0、保存 SES の自前 checkDrc は違反0件・未接続16件である。

`E/inspect-ses.py` は #97/#99 と同じ静的実測方式で全 serialized path を走査した。`(resolution um 10)` は10000単位/mm、幅分布は **0.20mm × 276 paths**、最小0.20mm、下限未満0本。層別{'F.Cu': 187, 'B.Cu': 89}、via 115個、中心線長840.598807mm。`main-ses-inspection.json` に全件集計を保存した。これは幅の静的検査であり、実銅箔 clearance や接続の独立合格を意味しない。

| Main 独立指標 | 値 |
| --- | --- |
| required unconnected | null |
| wrong-net contacts | null |
| material violations | null |
| unexplained transfer changes | null |

未配線が残るため、指示書どおり4指標は null。Main の KiCad import・独立 DRC は行わず、import 可否も未測定とする。**自前 checkDrc の違反なしと Main 独立検査との一致は未確認**であり、スモークの一致を Main に転用しない。自前 `violationsAdded=0` も独立合格の代わりにはしない。今回 Main における自己判定の誤り・正しさを一般化する根拠はない。

## 比較・判定・提出範囲

| 候補 | Main 未配線 | 最終 SES の幅条件 | 停止・到達点 |
| --- | ---: | --- | --- |
| Freerouting v2.5.0 Run 2（[#95](issue-95-freerouting-v250-run2.md)） | 38 | 本比較では未判定 | 未配線残存で optimizer skip |
| fastroute（[#99](issue-99-fastroute-width-floor.md)） | 37 | 全231 paths が0.20mm | 幅適合、未配線残存 |
| fab_router（#103、API デフォルト相当） | 16 | 全276 paths が0.20mm | `stagnant`、未配線残存 |

比較元の集計を `E/baseline-95/`・`baseline-99/` に保存した。未配線数は各ルーターの報告・自己接続検査による数であり、Main の独立4指標による合格順位ではない。単一試行であり、方式一般の優劣や配置の完成不可能性を主張しない。

判定は **FIXED_CONDITION_FAIL**。幅条件は保存 SES で成立したが、未配線が残るためこの単一設定を Main 完成の合格候補にはできない。設定変更・再実行・ルーター本体修正は行わない。

最新 origin/main **`9f97ebe6626ebf0c38e030bb8c9a2b9c27fb462d`** の全6475ファイルを byte/hash 照合して、指定ブランチ **issue-103-fab-router-falsification** を作成した。元 `.git` は読取り専用のため管理情報だけ `/tmp/issue-103-fab-router/git` に複製し、現在のリポジトリを work-tree とした。既存ファイルの変更はなく、本書と指定証跡ディレクトリへの追加のみを提出する。

保守的開始 **2026-11-03 22:51:00 UTC**、期限 **2026-11-04 00:51:00 UTC**。指示書の日付と実環境時計の差は実 UTC を一貫して記録した。導入・ドライバ・実行・検査・記録・commit/push・Draft PR 作成すべてを2時間に含める。検証結果は `E/verification.json`、成果物 hash 一覧は `E/manifest.json`、提出直前時刻は `E/submission.json`。Draft PR として提出し、**merge は行わない**。
