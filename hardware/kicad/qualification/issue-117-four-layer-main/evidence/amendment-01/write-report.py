"""Write the report from actual inspection JSON; preserve the Wing section verbatim."""
from helpers import *
d=json.loads((A/'assessment.json').read_text());cells=d['stage1'];old=(A/'report-before-amendment.md').read_text()
wing=old[old.index('## Wing：'):old.index('## D-012 改定の判断材料')]
reuse=json.loads((A/'main-reuse-and-runtime-revalidation.json').read_text());gate=d['stage0']
head=f'''# Issue #117 — 4層 Main 本試験と Wing 予備見通し（修正指示01）

**{d['status']}：smoke は両候補とも独立4指標0で合格した。Main は固定条件のまま各1回実行し、再充填後の独立 KiCad DRC で fab_router {cells['fab']['unconnected_count']}件、KRT {cells['krt']['unconnected_count']}件の未配線が残った。** 4層・幅/clearance 0.20mm・via 0.60/0.30mmの条件で、今回の両セルはMain完成を示せなかった。配置不可能性や4層一般の不成立を証明する結果ではない。

対象は [Issue #117](https://github.com/ihsinoky/he-piantor-42/issues/117)、継続提出先は [Draft PR #118](https://github.com/ihsinoky/he-piantor-42/pull/118)、ブランチ `issue-117-four-layer-main`。mergeしない。`docs/decisions.md` は変更していない。

以下 `E/` は [証跡](../hardware/kicad/qualification/issue-117-four-layer-main/evidence/)、`A/` はその [`amendment-01/`](../hardware/kicad/qualification/issue-117-four-layer-main/evidence/amendment-01/) を指す。**最新結果は `A/assessment.json`・`A/verification.json`**。`E/assessment.json` 等の前回run 2記録は当時の停止履歴として保持している。元指示全文は `E/instructions.md`、優先する修正指示全文は `A/instructions.md`、改稿前の報告全文は `A/report-before-amendment.md`。

## Stage 0：停止履歴、再利用と等価性

前回run 2は、固定smokeが非空ネット `N` しか持たず、「ネット不変」と「GNDゾーン」を両立できないため配線前に停止した。その判断・生証跡を維持する。修正指示01に従い、smokeのみIn1プレーンを既存ネット `N` に割り当て、ネット追加・改名は行わない。**このsmoke固有の逸脱はMainへ適用しない。MainはGNDプレーンのままである。** smokeの確認範囲は層役割の受理とheadless出力・KiCad読戻しの経路であり、MainのGND配線能力の証明ではない。

### 固定入力・Main再利用

| 固定2層入力 | SHA256 |
| --- | --- |
| Main PCB | `46676e57e9618940a33c5e298244e97aaec61498a87aa7c58a264e444fc71e20` |
| smoke PCB | `3f70465774f577ffe803f88de017004d164f045e6415ade22766a461a2454bec` |
| Project | `a5bc2aea160cc9a8b3035f77f0167c26a1de7ffdb749740c94fb7a9e9a3c87d5` |

Mainの4層入力を作り直していない。前回commit `7917d82` の `E/inputs/main/` 全ファイルをgit blobとbyte比較し、前回manifestのSHA256とも一致した。Main配線直前および最終監査でも再確認した。`A/main-reuse-and-runtime-revalidation.json` に全比較行がある。

| 再利用Main生成物 | SHA256 |
| --- | --- |
| 4層native PCB | `{reuse['files']['inputs/main/main.kicad_pcb']['sha256']}` |
| 4層corrected DSN | `{reuse['files']['inputs/main/corrected.dsn']['sha256']}` |
| Project（元とbyte同一） | `{reuse['files']['inputs/main/main.kicad_pro']['sha256']}` |

Mainは49 footprints / 199物理ランド / 37非空ネット / 元3トラックを保持する。F.Cu=signal、In1.Cu=power（GND全面ゾーン）、In2.Cu=signal、B.Cu=signal。板厚1.2mm。評価用stackup仮定は銅箔0.035mm×4、誘電体0.18/0.70/0.18mm、FR4、epsilon_r=4.5、loss_tangent=0.02、mask厚は合計から除外。メーカー確定値ではない。Mainのthermal gap/spoke/zone clearance/min thicknessは各0.20mmのまま。

前回のnative全AST照合、snapshot、DSNの層役割と全ネット読戻し、内層PTH/NPTH拡張を個別確認したうえでの2層基準への全AST投影一致を再利用した。元の外形・配置・全pad・net/NC・既存配線と層・その他要素は保持される。証跡は `E/native-equivalence.json`、`E/dsn-equivalence.json`、`E/preparation-readback.json`。DSNの既知のSMD例外50µmは既存検証済み復旧器で200µmへ戻したものをそのまま使用する。

fab_routerは#103と同一commit `69cf598db98c136bff16bbe02bccdded95674b18`、KRT v0.23.8は#113/#115と同一commit `c64c0db25e6cf23afa6769ee05665c7ea22b3ff2`。全ソースと独立検査runtimeのhashを再照合し差分0。KRT binary SHA256は `4411ccf3f074f519d8d69be29ac58b46ca7c4c2fe4f4be889d253d40996c2c0f`。ツールソースは編集していない。

### smoke準備と合格

固定smokeは4 footprints / 5物理ランド / 非空ネット `N` のみ / 元1トラック。`A/prepare-smoke*.py` は元2層PCBのlayers/setupに4層を加え、KiCadが生成・充填したNゾーンノードだけを移植する。既存要素は変更しない。native AST Counterではlayers/setup/zone以外の追加削除0、setup差はstackupだけ、プロジェクトはbyte一致。DSNは4層役割・N plane・全ネットを確認し、内層/planeを検査用メモリ上だけで除いた全ASTが#115の検証済み2層DSNと順序まで一致した。2層投影をルーターへ渡していない。

最初のsmokeは両候補各1回実行した。fab_routerはKiCad再充填後の4指標0。KRTは未配線0だが `starved_thermal` 1件（U2.1のIn1ゾーン接続）で不合格だった。`A/inputs/smoke/`・`A/runs/smoke/`・`A/inspection/smoke/` に全結果を保存した。SES転送の元線分UUID再採番は形状/ネット/幅/層を変えない説明可能な差として記録し、#87と同じ中心線被覆検査（2nm）を用いる。初版検査器のUUID判定・import問題も `A/inspection-development-notes.json` と保存版に残した。

追加したsmokeゾーンのpad接続方式だけをthermalから**solid**へ修正し、再度等価性を通した（`A/equivalence-gate-02.json`）。幅・clearance・via寸法、ルーター設定、元の配置・pad・net・配線は変えていない。固有のゾーン設定はMainに移さず、Main入力のbyte一致を維持する。これはStage 0のsmoke入力修正であり、Stage 1の結果を見た再設定・再実行ではない。smokeには各1回の制限はなく、両候補とも計2回、Mainは各1回のみ。

最終smokeは `A/inputs/smoke-02/`、出力は `A/runs/smoke-02/`、独立検査は `A/inspection/smoke-02/`。

| 最終smoke検査 | fab_router | KRT v0.23.8 |
| --- | ---: | ---: |
| 必須未接続 / 異ネット接触 / 物的違反 / 説明不能な転送変更 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| 独立KiCad未配線 / DRC違反 | 0 / 0 | 0 / 0 |
| In1信号トラック | 0 | 0 |
| headless・出力生成・KiCad読戻し・ゾーン再充填 | 合格 | 合格 |

fab_routerの実DSN読取りはIn1=`plane`、planeNet=`N`、全netGroupのusable sheets=`[0,2,3]`。KRTの禁止指定は `--layers F.Cu In1.Cu In2.Cu B.Cu --layer-costs 1 -1 1 1`。実出力でもIn1のトラック0、Nゾーンを保持した。直接のプレーン接続pad/viaは `plane-connectivity.json` のKiCad接続APIで別に読戻す。

KRTは `--escalation off --track-width 0.20 --clearance 0.20 --via-size 0.60 --via-drill 0.30` を明示。既定/明示の全実効設定と差分は `E/configuration/` と `A/configuration/`、明示smokeのGridRouteConfigは前回Mainの明示configと完全一致。差分はescalation、層コスト、寸法の明示値由来フラグ等として保存し、内部tierへ寸法決定を委ねない。fab_routerは#103の公開 `routeDsn` とAPI既定を維持し、全体budgetのみ1800000msを指定。幅/clearance 200µm・via600:300µmはDSNに明示し、パーサと保存出力で確認する。

**最終smokeゲート確定は `{gate['utc']}`**。再開09:22:54 UTCから30分以内。両Mainの開始時刻はこれより後である。

## Stage 1：Main固定条件の各1回

以下は元プロジェクトを採点用に使用し、保存出力を独立KiCad 9.0.9で再充填してから得た実測。未完成でもDRC JSON・全未配線ネット/端点・生差分を保存した。ルーター自己申告と独立値を区別する。

| 項目 | セルA fab_router | セルB KRT v0.23.8 |
| --- | --- | --- |
'''
rows=[('Main配線回数','1','1'),('独立KiCad未配線数 / ネット数',*[f"{cells[r]['unconnected_count']} / {cells[r]['unconnected_network_count']}" for r in ['fab','krt']]),('必須未接続 / 異ネット接触 / 物的違反 / 説明不能な転送変更',*[' / '.join('null' if v is None else str(v) for v in cells[r]['independent_metrics'].values()) for r in ['fab','krt']]),('幅mm : 本数',*[str(cells[r]['width_distribution']) for r in ['fab','krt']]),('via外径/drill mm : 個数',*[str(cells[r]['via_distribution']) for r in ['fab','krt']]),('層別トラック本数',*[str(cells[r]['tracks_per_layer']) for r in ['fab','krt']]),('経過秒',*[f"{cells[r]['elapsed_seconds']:.3f}" for r in ['fab','krt']]),('開始UTC',*[cells[r]['start_utc'] for r in ['fab','krt']]),('終了UTC',*[cells[r]['end_utc'] for r in ['fab','krt']]),('停止理由',*[cells[r]['stop_reason'] for r in ['fab','krt']]),('exit / timeout',*[f"{cells[r]['exit_code']} / {cells[r]['timed_out']}" for r in ['fab','krt']])]
body=''.join('| '+ ' | '.join(map(str,row))+' |\n' for row in rows)
body+='\n**未配線が残る両セルの4指標は、指定どおり全てnull。** 未配線実数や生DRCの0件を指標0へ代入せず、合格と扱わない。\n\n'
for router in ['fab','krt']:
 c=cells[router];z=c['plane_connections']['zones'][0]
 body+=f"### {router}の実測詳細\n\n未配線ネット別件数は `{c['unconnected_counts_by_net']}`。全端点の部品/パッドまたはtrack、座標、UUIDを `A/inspection/main/{router}/unconnected-net-endpoints.json` と `drc.json` に保存した。\n\n"
 body+=f"DRC種別の生件数は `{c['DRC_type_counts']}`、非印刷の生指摘は{c['raw_material_DRC_count']}件。非配線要素と元配線の説明不能な生差分は{c['unexplained_change_raw_count']}件。既存F.Pasteの正規化は同一KiCad saverで基準側も保存して照合し、ゾーン再充填のcache差分だけを除外する。実際の元線分は中心線被覆で保持を確認する。\n\n"
 body+=f"再充填後GND/In1プレーン面積は{z['filled_area_mm2']:.6f}mm²、直接接続は{len(z['directly_connected_pads'])} pads / {len(z['directly_connected_tracks_or_vias'])} tracks-or-vias。これは直接隣接の列挙であり、全GND端点の完成を示さない。各接続のUUID/ネットは `plane-connectivity.json`、GND未配線端点はDRCに残す。In1信号トラックは0本。\n\n"
 body+=f"raw PCB SHA256は `{c['raw_output_sha256']}`、独立再充填後PCB SHA256は `{c['refilled_output_sha256']}`。\n\n"
 if router=='fab':body+=f"公開APIの自己検査countsは `{c['router_claim_counts']}`。fab側の出力project差分はKiCad saverによる `/meta/filename` のout名への変更のみで、ルール下限の変更は0件。独立KiCadの未配線値とは測定主体が異なり、置換しない。SES・読戻し・有効settings・pass/connectionログも全て保存した。\n\n"
 else:body+="出力 `.kicad_pro` の全差分は、`board.design_settings.rules.min_via_drill` の未定義→0.3mm追加と、`kicad_routing_tools` の由来メタデータ追加の2箇所。既存min_track_width/min_clearance等とnetclass値の下限緩和は0件。追加書き戻しはあるが、本Issueの禁止する緩和方向の変更ではない。#115の『書き戻しそのもの禁止』という判定と混同しない。全差分は `transfer-diff.json`、raw出力projectを保存した。未配線残存のため本セルは不合格である。\n\n"
end='''## D-012 改定の判断材料

**PMO確認済み価格事実：** 48×44mm、1.2mm、HASL、5枚で2層 **$4.00**／4層 **$8.00**、送料別。発注数量は5・10・15…の刻みで6枚は選べない。これは指定Main条件の価格であり、Wing/PCBA/送料や将来見積もりへ外挿しない。

4層化を本命とするPO方針に対し、固定配置・現行0.20mmの3信号層＋GNDプレーンを両候補が受理し、スモークの一連の出力経路が通ることは実証できた。しかし、今回の各1回では両セルにMain未配線が残り、**現行条件でMain完成という改定根拠は得ていない**。追加条件の探索・Main再実行はしていない。ルーターの候補・既定戦略に依存する結果であり、4層による完成可能性全体や配置不可能性を断定しない。

改定する場合はD-012、D-017、DFMの層基準を整合させ、メーカー確定1.2mm stackup、Mainの3信号層＋GND plane、Wingにも4層を原則適用するか2層実証を認めるかをHuman Gateで明確にする必要がある。Wingの層数をMainだけで決める根拠はない。D-015どおり左右Wingは**同一設計定義から生成した別々の製造データセットで可、リバーシブルPCBAは必須ではない**。

残るリスク・未決定事項は、MainのRP2040周辺等の局所escapeとGND到達、via-in-pad/印刷/既存USB NPTH等の製造事項、メーカーstackup、Wing未設計geometry・回路・最終部品/ピッチ、analog settling/noise・磁気干渉の実測。smokeのsolid/Nプレーンは契約を確認する限定fixtureであり、Mainのthermal/GNDの成立を代替しない。採否・追加投資・要求変更はPOのHuman Gateとする。

## 監査と提出

再開開始は2026-11-04 **09:22:54 UTC**、smoke期限 **09:52:54 UTC**、全体期限 **11:22:54 UTC**。`A/start.json` に保存し、smokeゲートは期限内に通過した。Main各1回・設定変更/再実行0回・インフラ再起動0回。各プロセスのargv/headless環境/開始終了/elapsed/exitは `E/processes/amend01-*/`、入力hashと順序・基点ファイル不変・変更範囲・最新指標・JSON/Python構文は `A/verification.json`、成果物hashは `A/manifest.json`、提出は `A/submission.json` とする。

ブランチの前回commit `7917d82` に追加commitし、同じDraft PR #118を更新する。作業用gitは `/tmp/issue-117-main/git`、元リポジトリの `.git` は変更していない。変更範囲は本報告と本Issue証跡ディレクトリのみであり、既存要求/決定/他Issue成果物は変更しない。Wing節は前回run 2から全文維持し、今回の配線・再調査は0回である。
'''
(R/'docs/issue-117-four-layer-main-and-wing-outlook.md').write_text(head+body+wing+end)
(E.parent/'README.md').write_text('''# Issue #117 — four-layer Main and Wing outlook

Current report: [Main results and Wing outlook](../../../../docs/issue-117-four-layer-main-and-wing-outlook.md).

The latest amendment-01 results are in `evidence/amendment-01/assessment.json`,
`smoke-gate.json`, `verification.json`, and `submission.json`. Both smoke gates
passed. Each Main router was run exactly once, without changed settings or reruns.
See the report and independent refilled KiCad DRC for the measured open connections.

The original `evidence/assessment.json`, `equivalence-gate.json`, `verification.json`
and preparation scripts retain the prior run 2 Stage 0 stop as historical evidence.
They are superseded by amendment-01, whose instruction assigns the smoke plane to
its existing sole net N. The Main GND-plane input is reused byte-for-byte.

Both initial thermal smoke outputs and the corrected solid-zone smoke outputs
are preserved. The latter passed all four independent metrics. Main inputs were
never rebuilt. The previous report is `amendment-01/report-before-amendment.md`.

Wing analysis is retained verbatim from run 2; no Wing routing or new investigation
was performed, and no `hardware/layout/**` inputs were consumed for that analysis.
''')
print('Report written from actual results; Wing section retained verbatim.')
