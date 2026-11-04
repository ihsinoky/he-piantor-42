# Issue #113 — KiCad Routing Tools の限定反証テスト

**固定条件の達成は不合格（FIXED_CONDITION_FAIL）。** Stage 0 は独立4指標0で合格後、Main を公式デフォルト CLI で1回実行した。保存された Main 基板への独立 KiCad DRC は**未配線5件**、全636トラックの静的実測は **0.20mm × 365本 / 0.127mm × 271本**。0.20mm 下限を満たさない。Main の独立4指標は指示どおり **すべて null** とする。

**手順上の制限もある。** 実行前に #87 の独立照合器で配置・各パッドのネット/形状/層・ルール・既存配線を検証したが、ネイティブ基板のフットプリント自体の表裏および未使用ネットを含む全ネット定義の明示照合は、Main 起動後の補足となった。補足検査は両入力とも一致したが、全項目を実行前に明示検査したことにはならない。**厳密な事前等価性ゲートの手順適合は未認定**とし、完全な手順適合試験として扱わない。この不足を訂正する追加配線実行は行っていない。

対象は [Issue #113](https://github.com/ihsinoky/he-piantor-42/issues/113)。以下 `E/` は
[証跡ディレクトリ](../hardware/kicad/qualification/issue-113-kicad-routing-tools-falsification/evidence/) を指す。
指示書全文は `E/instructions.md`、Issue 本文は `E/issue113.json`。PO 承認済みの、この候補1件に限る KiCad ネイティブ経路例外であり、DSN/SES 原則の変更や採用ではない。

## 入力の特定・固定と等価性

Main は #87 `stage-ab.py` が `eda-004g/resume-02/evidence/processes/initial-author-pcb-explicit-public-library-io/` の基板・プロジェクトを byte 同一コピーし、`export-main.py` で DSN を生成したものを採用した。#87 配下の `spacing-drc/main.kicad_pcb` は故障注入品であり、採用していない。#87 `evidence/reuse-hashes.json` と同報告書が元基板の SHA256 を記録しており、今回の固定コピーと一致する。#87 配下に正常な Main 元基板の重複保存がないため、#87 が参照・固定した実際の生成元へ遡った。生成・修正して等価に仕立てた基板ではない。

スモークは #87 `evidence/processes/smoke-read-before/main.kicad_pcb` を採用した。`export-smoke.py` が保存した DSN 出力直前の基板であり、SES import 後の基板は使用していない。両者の `.kicad_pro` も固定し、基板側に含まれない設計ルールを引き継いだ。入出力の元ファイルは変更していない。

| 固定ファイル | SHA256 |
| --- | --- |
| Main PCB | `46676e57e9618940a33c5e298244e97aaec61498a87aa7c58a264e444fc71e20` |
| smoke PCB | `3f70465774f577ffe803f88de017004d164f045e6415ade22766a461a2454bec` |
| 両入力の元プロジェクト | `a5bc2aea160cc9a8b3035f77f0167c26a1de7ffdb749740c94fb7a9e9a3c87d5` |
| Main corrected.dsn | `75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2` |
| smoke corrected.dsn | `7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9` |

`E/input-provenance.json` に全コピー元と hash、`E/inputs/` に固定 PCB・プロジェクト・DSN を保持する。新しい KiCad 公開 API 読込スナップショットは #87 の保存値と全項目で一致した。元の KiCad プロジェクトを読み込み、最小幅・クリアランスと Default netclass 幅・クリアランスがいずれも0.20mm、銅箔2層であることを実測した。

| 項目 | smoke | Main |
| --- | ---: | ---: |
| フットプリント | 4 | 49 |
| 導電パッド / NPTH | 4 / 1 | 197 / 2 |
| 全物理ランド（NPTH含む） | 5 | 199 |
| 非空ネット | 1 | 37 |
| 元トラック / via | 1 / 0 | 3 / 0 |
| signal layers | F.Cu / B.Cu | F.Cu / B.Cu |

事前検査は #87 `resume-01/check-dsn.py` を無改変で再使用した。個別フットプリントの位置・回転・PN、各導電パッドの位置・形状・層・ネット/NC・端子在庫、外形全辺、元線分の端点・幅・層・ネット、global/netclass の0.20mm rule、#87 の固定された public router 読戻しを照合して PASS_WITH_SCOPE を得た。`E/{smoke,main}-dsn-equivalence.json` に個別行、`E/processes/*-dsn-equivalence/` に argv と結果がある。事前の `E/equivalence-gate.json` は **05:18:12.213 UTC**。ただし、その pass 値の範囲はこの照合器の検査項目に限り、冒頭の手順上の不足を覆さない。

表現差は以下のとおり。DSN は um 単位・resolution 10/um、KiCad は mm。DSN の Y 符号反転を戻し、既存 oracle の **0.000002mm（2nm）** 許容値で個別銅箔形状を比較した。これは間隔の緩和ではない。DSN が同形状を image alias で共有する場合も個別 PN と配置を照合する。ネットなし端子は DSN network に現れないが padstack に残る。NPTH は物理穴径+0.40mmの障害物として各層に表現される。PTH の穴・厚さ・印刷/マスク等、DSN 非表現情報は元のネイティブ基板に保持される。基板側の変更はしていない。

`E/check-native-inventory.py` の補足検査は両入力の native footprint layer と DSN front/back、空ネットを除く全ネイティブ net 定義と DSN network、signal layer 一覧を直接比較し、一致を確認した。実行時刻・個別参照・ネット一覧は `E/native-inventory-supplement.json`。これは実行後の補足であり、事前検査の不足は未認定のまま残す。

## 公式版・導入・デフォルト呼び出し

公式 [drandyhaas/KiCadRoutingTools](https://github.com/drandyhaas/KiCadRoutingTools/tree/c64c0db25e6cf23afa6769ee05665c7ea22b3ff2) の **v0.23.8 / commit `c64c0db25e6cf23afa6769ee05665c7ea22b3ff2`** を shallow clone。MIT ライセンスを `E/official/LICENSE` に保持した。README・必要な公式ソースと全ソース hash は `E/official/`・`E/source-manifest.json` にある。導入・実行後も tracked source に差分がないことを確認した。

公式 README の **Route Nets（400–410行）** は、全ネットを明示出力へ配線する次の基本形を提示する。`--help` も保存し、両 stage を同じ argv 形で実行した。配線オプションは追加していない。

```text
python3 py_router/route.py in.kicad_pcb out.kicad_pcb
```

実際の Python は一時 venv 内の Python 3.12.3。ルーター cwd・絶対入出力パス・環境・開始終了 UTC・終了コード・外側1800秒上限は各 `E/processes/{smoke,main}-route/record.json` にある。DISPLAY と WAYLAND_DISPLAY を除去した headless 実行である。KICAD_CLI は固定 KiCad 9.0.9 の場所のみを指定し、設定探索や KRT の機能スイッチは指定していない。

ソース `route.py` の既定値解決は、幅・via径/穴径・clearance を隣接 `.kicad_pro` の Default netclass から読む。層の省略時は基板の全銅箔層、ネット省略時は `*`。ログでも **幅0.20 / clearance0.20 / via0.60:0.30mm / F.Cu,B.Cu** が確認できる。MPS 順序と F=1.0/B=3.0 の層コストも既定のまま。

ただし `routing_defaults.py` は **FAB_TIER=auto / ESCALATION=fab** で、失敗ネットを元基板の下限より細く/狭くする救済を許し、出力プロジェクトの DRC 下限を実績値へ書き戻す。`fab_tiers.py` がその挙動を明記する。これを固定条件の緩和として受け入れていない。公式デフォルトの出力が元の条件を満たすかを検査し、下限未満を失敗とした。`--escalation off` や fab override への切替は別設定の探索になるため実行していない。README の配置・fanout・plane pour の前処理チェーンも手動実行していない。内部の rescue/sub-run はこの1回のプロセスの既定処理である。

公式 `build_router.py --tag v0.23.8` で release の Linux x86_64 prebuilt を取得した。GitHub asset digest と実ファイル SHA256 の一致は `E/binary-provenance.json`。Rust crate は公式 `Cargo.toml` 上0.23.7、repo VERSION は0.23.8で、Python-only patch の版規約と整合する。別版への置換ではない。

依存導入の最初の試行は `/tmp` 512MiB 上限で容量不足になったため、所有する一時 runtime を `.issue113-runtime/` へ移し、同じ requirements の導入を完了した。失敗ログも保持する。これは配線前の導入修復である。検査用 KiCad・Shapely・sexpdata・NumPy は既存 `.issue105-runtime/` を読取り利用し、バイナリ・ライブラリ hash、元 deb hash、実読込版/パスを `E/inspection-runtime-hashes.json` 等に記録した。システムへのインストールはない。ルーター本体・依存物・cache は成果物に含めない。

## Stage 0 と独立検査

スモーク1回は **05:20:55.231–05:21:01.211 UTC、5.980秒、exit0**。保存基板は全2トラックが0.20mm、via0。非配線 AST は同一、元1トラックも UUID を含む元レコードのまま保持し、1トラックだけ追加された。KiCad DRC の違反/未接続0、#87 の独立実銅箔グラフと既存 check-import による照合も合格した。

| スモーク独立指標 | 値 |
| --- | ---: |
| required unconnected | 0 |
| wrong-net contacts | 0 |
| material violations | 0 |
| unexplained transfer changes | 0 |

`E/smoke-gate.json` は **05:21:09.558 UTC**、Main 起動05:21:34.906 UTCより前である。runner は既存 stage ディレクトリへの再実行を拒否し、Main の前に gate を確認する。

KRT の出力 `.kicad_pro` には `min_via_drill=0.3` と由来メタデータの追加がある。既存の下限を緩和する変更ではなく、本件の PCB 差分指標とは分けて全件列挙した。独立検査は**保存出力 PCB の byte 同一コピーと元の固定プロジェクト**を組み合わせ、KRT の設定書戻しに合否を依存させていない。Probe footprint library は元 footprint から検査ディレクトリに用意しただけで、PCB は変更していない。

## Main：未配線・幅不適合・差分

Main1回は **05:21:34.906–05:23:36.903 UTC、121.997秒、exit0、外側timeoutなし**。最終保存 PCB は636トラック/87via、銅箔2層である。

元ルールで独立 KiCad DRC を実行し、**unconnected_items=5**。ネットは **QSPI_SD2 / V1V1 / WING_EN / XIN / XOUT**。各端点・UUID は `E/inspection/main/drc-with-library.json` に保持する。自己チェッカの値から転記した件数ではない。

| Main 独立4指標 | 値 |
| --- | --- |
| required unconnected | null |
| wrong-net contacts | null |
| material violations | null |
| unexplained transfer changes | null |

未配線が残るため4指標を null とする。一方、指示された出力 PCB への幅検査・差分検査・独立 DRC の生値は保持する。幅の全件実測は **0.20mm 365本 / 0.127mm 271本、最小0.127mm**。KRT が一時救済でログ出力した0.10mmを最終保存幅と混同しない。`E/main-width-inspection.json` に全636トラックと87viaの値がある。

独立 DRC の非印刷指摘は **479件**：via_diameter28 / track_width199 / drill_out_of_range28 / clearance198 / hole_clearance1 / annular_width24 / via_dangling1。このうち via_dangling は warning。既知の印刷指摘61件（text_height44 / silk_overlap12 / silk_over_copper5）は別扱いで保持し、抑制していない。静的幅の271本と DRC の幅指摘199件は集計単位が異なるため同一視しない。これらの生の指摘数を、null 方針の material 指標の代わりに「479」と代入しない。wrong-net contact の独立グラフ合格も主張しない。

最初の Main DRC では、歴史的な `/workspaces/...` の footprint library パスが存在せず49件の lib_footprint_issues があった。元の固定 Qualification.pretty を現在の絶対パスで登録し、**DRCだけ**再実行した。初回 raw は `drc.json`、最終 raw は `drc-with-library.json`。後者のlibrary警告は0である。元ライブラリ・PCB・プロジェクト・ルールを変更せず、再配線もしていない。

`E/main-board-diff.json` は全トップレベル AST の Counter 比較と全非配線 snapshot 比較による。

- footprint 移動/回転/削除、外形、ネット定義、silk・zone等を含む **PCB 非配線要素の追加/削除0、snapshot 非配線変更0**。
- **元3トラックの削除/変更0**。元レコードを保持し、633トラックと87viaを追加した。
- 出力プロジェクトの変更は別に全件保存。min_clearance・min_track_width と Default clearance は0.20→0.127mm、min_hole_clearanceは0.20→0.178553mm、min_via_diameterは0.60→0.25mm、min_through_hole_diameterは0.30→0.15mm、min_via_annular_widthは0.10→0.05mm、min_via_drill=0.15mm追加、KRT由来メタデータ追加。**これらは説明のある自動変更でも固定ルール適合とは認めない。**

`E/runs/main/out.kicad_pro` は raw のまま保存した。独立 DRC 用に元プロジェクトを別ディレクトリへコピーしたのは、出力を合格に修正する操作ではなく、元条件で採点するためである。raw PCB と検査 PCB の hash は一致する。

| 出力 PCB | SHA256 |
| --- | --- |
| smoke | `762df50b4513f276e2dbcc7a0bbb3d56554f9b86447981f76bfd77b266163cf5` |
| Main | `fb3babb75d8dbf9a10fbc8502d8759ca47f602c485323d1014a27faa89ce2f3b` |

KRT 内蔵検査・JSON_SUMMARY・improvement gate は**自己診断 telemetry**としてログに保持しただけで合否には使っていない。exit0 や内蔵 gate の accept は、未配線ゼロや固定条件での合格を意味しない。自己報告の via88と実保存87の差も、独立実測で補う。内部再配線等の正確な段階帰属を推測しない。

## 比較・判定の範囲

| 候補 | Main 未配線 | 保存出力の幅条件 | 到達点 |
| --- | ---: | --- | --- |
| Freerouting v2.5.0 Run 2（[#95](issue-95-freerouting-v250-run2.md)） | 38（router） | 本比較では未判定 | 未配線残存、optimizer skip |
| fastroute（[#99](issue-99-fastroute-width-floor.md)） | 37（router） | 全231 paths 0.20mm | 未配線残存 |
| fab_router（[#103](issue-103-fab-router-falsification.md)） | 16（自己接続検査） | 全276 paths 0.20mm | stagnant、未配線残存 |
| KRT（#113、基本 CLI デフォルト） | 5（独立 KiCad DRC） | 636 tracks中271本が0.127mm | 未配線・幅・元ルールに不適合、事前ゲート手順も未認定 |

元入力と合格基準は共通だが、KRT の既定実装は実際には元の寸法下限を緩めた出力を生成した。さらに手順上の不足、DSN/SESとnative直接出力の経路差、件数の検査主体差があるため、5対38/37/16から優劣を付けない。これは **0.20mmを守った KRT の未配線5件という結果ではない**。固定条件を満たす別設定の試行、配置完成不可能性、KRT一般の能力、adoption・製造承認を推定しない。

## 提出・時間箱・次の判断

最新 origin/main **`ce2d3803bec50d1c06546e44ca0736ef97d7de6d`** の7044ファイルが現在の作業ディレクトリと byte 同一であることを確認し、指定ブランチ **issue-113-kicad-routing-tools-falsification** をそこから作成した。元 `.git` が読取り専用のため管理情報だけ `/tmp/issue-113-krt/git` にコピーし、現在ディレクトリを work-tree として操作した。コピー時の ownership 保存警告後もファイル一致を検証している。元 `.git` を変更していないため、通常のローカル git の HEAD 表示は main のままである。提出用 HEAD・remote branch は上記指定ブランチである。

追加は本書と指定証跡ディレクトリだけで、既存ファイル・過去の証跡・product source・依存定義・CI を変更していない。既存の runtime や他 Issue の作業は保持した。高水準履歴への追記が必要なら PMO/PO が別途判断する提案に留める。

保守的開始 **2026-11-04 05:16:00 UTC**、期限 **07:16:00 UTC**。導入・等価性確認・実行・独立検査・記録・commit/push・Draft PR をすべて時間箱に含める。`E/verification.json` に入力不変・既定argv・実行順・元ルールでの検査・全baseファイル不変・追加のみ・バイナリ不包含・時刻、`E/submission.json` に提出前時刻、`E/manifest.json` に成果物hashを保存する。

本件は失敗結果および手順制限の報告として Draft PR で提出する。merge は行わない。追加実験は未承認であり、PMO はこの結果と手順不足を評価し、PO が報告の受入れと今後の投資を判断する。製品開発・printing/glyph・USB NPTH DFM・製造Gateは従来どおり未解決である。
