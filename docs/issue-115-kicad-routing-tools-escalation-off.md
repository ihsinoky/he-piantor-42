# Issue #115 — KRT escalation 無効の単一条件試験

**FIXED_CONDITION_FAIL（固定条件では不合格）。** KRT v0.23.8 の変更を `--escalation off` のみに限定し、全項目の事前等価性ゲートとスモーク独立4指標0を確認後、Mainを1回実行した。元プロジェクトでの独立 KiCad DRC は **未配線28件・24ネット**。保存された **全554トラックは0.20mm**（下限未満0本）だが、未配線が残る。さらに出力プロジェクトへ **`rules.min_via_drill=0.3` が追加書き戻し**された。既存下限の緩和は0件だが、「書き戻しなし」も満たさない。

対象は [Issue #115](https://github.com/ihsinoky/he-piantor-42/issues/115)。以下 `E/` は [証跡](../hardware/kicad/qualification/issue-115-kicad-routing-tools-escalation-off/evidence/) を指す。指示書全文は `E/instructions.md`、Issue本文は `E/issue115.json`。本セルをKRTの最後の評価とし、追加探索・再配線は行っていない。候補限りのnative直接編集例外を継続する。

## 同一版・固定入力・追加だけの作業

公式 [KRT v0.23.8 の固定commit](https://github.com/drandyhaas/KiCadRoutingTools/tree/c64c0db25e6cf23afa6769ee05665c7ea22b3ff2) `c64c0db25e6cf23afa6769ee05665c7ea22b3ff2` を使用した。#113で公式 `build_router.py --tag v0.23.8` とrequirementsに従って導入した `.issue113-runtime/` を再利用し、別版への変更はない。公式binaryのSHA256は `4411ccf3f074f519d8d69be29ac58b46ca7c4c2fe4f4be889d253d40996c2c0f`。全ソース・検査runtime・binaryのbyte一致を再検証し、`E/runtime-revalidation.json` に記録した。導入由来資料は `E/reused-*`、必要な公式一次資料は `E/official/` に保存し、ツール本体・依存物は成果物に含めない。

#113の `evidence/inputs/{main,smoke}/` をそのままコピーし、次を照合した。基板を加工して条件へ合わせる操作はない。

| 固定対象 | SHA256 |
| --- | --- |
| Main PCB | `46676e57e9618940a33c5e298244e97aaec61498a87aa7c58a264e444fc71e20` |
| smoke PCB | `3f70465774f577ffe803f88de017004d164f045e6415ade22766a461a2454bec` |
| 元プロジェクト（両入力） | `a5bc2aea160cc9a8b3035f77f0167c26a1de7ffdb749740c94fb7a9e9a3c87d5` |

コピー元・全入力hashは `E/input-provenance.json`、固定PCB/プロジェクト/DSN/新規snapshotは `E/inputs/`。配置固定、幅・clearance 0.20mm、銅箔2層、via 0.60/0.30mmを継承する。

作業開始時の通常 `.git` は古いmainを示していた。前回の独立git管理情報を `/tmp/issue-115-krt/git` にコピーしてfetchし、最新 `origin/main=6e30438c854db4fe5c4d8a9a8dbeadcb385ff8e5` の **7199ファイルすべてが現在ディレクトリとbyte同一**であることを確認した。そのcommitから指定ブランチ `issue-115-kicad-routing-tools-escalation-off` を作成した。元 `.git` は読取り専用のため変更せず、現在のディレクトリをwork-treeとして使用する。通常gitのHEAD表示はmainのままだが、提出用gitのHEADとremote branchは指定ブランチである。変更は本書と指定証跡ディレクトリの新規追加だけである。

## 配線前の等価性ゲート

`E/prepare-inputs.py` は #87 の既存独立 `resume-01/check-dsn.py` を無改変で利用し、以下を両入力で照合した。

- 各フットプリントの位置・回転・PN、各導電パッドのネット/NC・形状・位置・層・在庫。
- NPTHを含む物理ランド、外形全辺、global/netclassの0.20mmルール、元トラックの端点・幅・ネット・層、過去のpublic router実効読み戻し。
- `E/check-native-inventory.py` による **native footprint layerとDSN front/back** の個別照合。
- 同検査による **未使用ネットを含む全非空native net定義とDSN network** の集合一致。空ネット0はネットなしを示すnative表現でありDSN network定義には含まれない。
- signal layersがF.Cu/B.Cuの2層であること、新しいnative snapshotが#113固定snapshotと全項目一致すること。

Mainは49 footprints / 199物理ランド / 37非空ネット / 元3トラック、smokeは4 footprints / 5物理ランド / 1非空ネット / 元1トラック。DSNのum単位・Y反転を戻し、既存照合器の2nm許容差を使う。これはルール緩和ではない。DSN非表現の穴・厚さ・印刷等はnative入力に保持される。詳細行は `E/{main,smoke}-dsn-equivalence.json` と `E/native-inventory.json`。

**全項目完遂のゲートは06:04:25.475923 UTC**（`E/equivalence-gate.json`）。smoke/Mainの配線起動はいずれもこの後であり、#113で事後補足となった項目を含め今回はすべて事前に完遂した。

## 単一条件と実効設定の読み戻し

公式READMEのRoute Nets（400–410行）は基本CLI、325/873行は `--escalation` とその実装元を示す。実際のhelpは `E/processes/route-help/stdout` の518行以降に **`--escalation {off,board,fab}`、既定fab**、offの意味を記載する。公式 `routing_defaults.py` の `FAB_TIER='auto' / ESCALATION='fab'`、`fab_tiers.py` のpolicy定義・`may_narrow()`・`escalation_rungs()` と照合した。offは失敗時の縮小を拒否し、descent用rungsを空にする。wide power/impedanceのpad entryに最長2mmの例外があることも一次資料に明記されている。本試験ではpower/impedance追加指定はせず、保存出力の全幅を別途実測した。offは出力プロジェクト書き戻し機能そのものを無効にするスイッチではない。

公式READMEを固定commitのraw URLから再取得し、ローカル公式コピーとのhash一致も確認した。公式ソースは変更していない。

実行形は両stageで次だけである。

```text
python3 py_router/route.py in.kicad_pcb out.kicad_pcb --escalation off
```

**読み戻し差分の確定は06:05:55.488646 UTCで、smoke/Main起動前**。`E/read-effective.py` が公式 `route.py` を実行し、公式のCLI解決・基板/netclass読込・GridRouteConfig構築が終わった3231行のnet選択直前でtrace停止する。配線処理・出力保存へ進まない。CLI全111項目、batch_routeの全109引数（既定値を含む）、GridRouteConfigの全107フィールド、routing_defaults全108定数、環境ノブ全93項目、fab tierと内部escalation policyを読み戻した。

#113には全設定dumpがなかったため、**同じ固定入力・同じ版・同じruntimeで#113のbare CLIを設定解決まで再現**したbaselineとoffを比較する。過去実行時のdumpを取得できたと偽っていない。`E/configuration/{main,smoke}-{default,off}.json` と `diff.json` に全値を保持する。

| 差分箇所（両stage共通） | baseline | 今回 |
| --- | --- | --- |
| CLI namespace.escalation | fab | off |
| 内部escalation policy名 | fab | off |

**差分は同じescalation無効化の2表現のみ**。内部board floorsも含め他の解決値は一致し、連動する別パラメータ差分はなかった。fab tierはauto、幅/clearance0.20、via0.60/0.30、F.Cu/B.Cu、層コストF=1/B=3、順序等は既定のまま。`--no-fix-drc-settings`・fab override・寸法指定等の追加スイッチは使っていない。offに伴う実行経路の変化を相殺していない。

最初の読み戻しはJSON serializerがfrozensetに対応せず停止した。停止箇所は同じ配線前のtrace点で、公式ソースや条件は変えていない。serializerだけを修正して読み戻しを完了した。失敗ログも残す。実際の配線はsmoke1回/Main1回だけである。

## Stage 0 → Stage 1と独立検査

runnerは既存stageディレクトリへの再実行を拒否し、Mainではsmoke gateと設定差分の確定を要求する。DISPLAY/WAYLAND_DISPLAYを除去したheadless実行で、Python/独立KiCad 9.0.9/環境/argv/時刻/exit/1800秒外側上限は `E/processes/*/record.json` に保存した。

スモークは独立4指標すべて0、全2トラック0.20mm、via0。元1トラックをUUIDを含め保持し、1トラックだけ追加。**smoke gateは06:06:07.857928 UTC**、Main起動 **06:06:18.182996 UTC** より前に確定した。smoke出力のmin_via_drill追加は下記に列挙する。Stage 0の進行条件は指定された独立4指標0で判定した。

Mainは **06:06:18.182996–06:07:21.491950 UTC、63.309秒、exit0**。1回だけ実行し、timeout・設定探索・手動前処理・追加配線なし。KRT内蔵JSONのacceptやexit0を合格根拠にせず、**保存出力PCBのbyte同一コピー＋元の固定プロジェクト**で採点した。

独立検査は#113と同じnative snapshot・全トップレベルAST Counter差分・KiCad DRC。smokeの接続/shortは#87の実銅箔graphと既存check-importでも検証した。Mainは元のQualification.prettyを最初から正しい絶対パスで登録し、library起因のDRC指摘は0。ルールやPCBの修正はない。

| 独立4指標 | smoke | Main |
| --- | ---: | --- |
| required unconnected | 0 | null |
| wrong-net contacts | 0 | null |
| material violations | 0 | null |
| unexplained transfer changes | 0 | null |

Mainに未配線が残るため、指定どおり4指標は**すべてnull**。実測未配線28件と生の検査値は別に報告する。wrong-net等の合格を推定しない。

Mainの保存出力は **554 tracks / 39 vias / 2層**。全554トラックの幅は **0.20mm、最小0.20mm、0.20mm未満0本**。全線分・viaの実測行は `E/main-width-inspection.json` にある。自己報告のvia38と保存実測39を混同しない。

独立DRCは未配線28件のほか **via_dangling 9件（warning）**。既知の印刷指摘61件（text_height44 / silk_overlap12 / silk_over_copper5）もrawに保持する。#113の元ルール非印刷479件に対し今回は9件だが、これをnullのmaterial指標へ代入しない。寸法由来のDRC指摘はこの出力ではない。

全AST/snapshot差分では、**PCB非配線要素の追加/削除0、非配線snapshot差分0、元3トラックの変更/削除0**。551トラックと39viaが追加された。これらは生の差分検査結果であり、未配線時の独立4指標nullを置き換えない。

## 出力プロジェクトの全差分と判定

smoke/Mainともにプロジェクトの全差分は同じ次の2箇所だけだった（`E/{smoke,main}-board-diff.json`）。raw出力 `.kicad_pro` は `E/runs/` に保持する。

1. `board.design_settings.rules.min_via_drill` を未定義から **0.3mmへ追加**。
2. `kicad_routing_tools` を追加。内容は `repo_rules.min_via_drill=0.3`、`fab_floor_origin={min_hole_clearance:0.2, min_through_hole_diameter:0.3, min_track_width:0.2, min_via_annular_width:0.1, min_via_diameter:0.6}`、`records_rev=1`。

min_track_width/min_clearance等の既存値変更・緩和は0件で、Default netclassも維持された。しかし **min_via_drillの追加も下限書き戻し**である。指示の「書き戻しがあれば失敗」に従い失敗理由へ含める。`--no-fix-drc-settings` で打ち消す試行は実施しない。未配線残存だけでも不合格は確定している。

| 保存出力 | SHA256 |
| --- | --- |
| smoke PCB | `321576d8610a28a739057290908e812930ed2c686eb17afac2ea5d6ae939eb3a` |
| Main PCB | `13c843919d906e2e2bea2775cd31ec479155b3d6b77e5b9743de6c7b04781926` |

## #113および従来候補との比較

未配線はDRC missing-connectionの**28件・24ネット**。V1V1とV3V3が各3件、残る22ネットが各1件。

- #113と共通の5ネット：**QSPI_SD2 / V1V1 / WING_EN / XIN / XOUT**。解消したネット0。V1V1は1→3件。
- 新たに残った19ネット：**ADC_A / ADC_B / ADC_C / GND / HALL_PWR_EN / MUX_A0 / MUX_A1 / MUX_A2 / QSPI_SCLK / QSPI_SD0 / QSPI_SD1 / QSPI_SD3 / RUN / SWCLK / SWDIO / USB_DM / USB_DP / USB_DP_CONN / V3V3**。

したがって#113の未配線ネット集合を今回の集合が厳密に包含し、5→28件（+23件）、5→24ネット（+19ネット）。各端点・UUIDは `E/inspection/main/drc.json`、機械可読比較は `E/assessment.json`。

| 候補 | Main未配線 | 幅・到達点 |
| --- | ---: | --- |
| Freerouting #95 | 38（router） | optimizer skip、残存 |
| fastroute #99 | 37（router） | 全231 paths 0.20mm、残存 |
| fab_router #103 | 16（自己接続検査） | 全276 paths 0.20mm、stagnant |
| KRT #113 / escalation fab | 5（独立DRC） | 全636 tracks中271本0.127mm、元下限緩和、事前ゲート手順未認定 |
| **KRT #115 / escalation off** | **28（独立DRC）** | **全554 tracks 0.20mm、事前ゲート完遂、min_via_drill追加書き戻し** |

#113の5件は0.20mmを守った結果ではない。今回は幅を守る出力を得たが未配線ゼロを達成せず、固定条件でKRTの成立を示せなかった。従来候補とは検査主体やnative/DSN経路が異なるため、この表から一般的優劣・配置不可能性・製造承認を推定しない。本追加セルをもってKRT評価を終了する。

## 検証・提出

`E/verification.json` は全baseファイル不変・追加のみ・入力hash・設定差分確定→smoke→独立gate→Mainの順序・両stage各1回・元ルールによる検査・成果物にツールbinaryなしを検証する。`E/authored-file-checks.json` はJSON読込と著作ファイルのwhitespace検査を記録する。全体diff-checkで検出される空白はraw Main出力PCBとそのbyte同一検査コピーだけであり、証跡のbyte同一性を保つため整形していない。`E/manifest.json` は証跡hash、`E/submission.json` は提出時刻と時間箱を保持する。

保守的開始 **2026-11-04 06:01:00 UTC**、期限 **08:01:00 UTC**。調査・ゲート・実行・独立検査・記録・commit/push・Draft PR作成を含め2時間内に提出する。Draft PRで報告し、mergeしない。以後の採否・投資判断はPOに委ねる。
