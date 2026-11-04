# Issue #117 — 4層 Main 本試験と Wing 予備見通し（修正指示01）

**FIXED_CONDITION_FAIL：smoke は両候補とも独立4指標0で合格した。Main は固定条件のまま各1回実行し、再充填後の独立 KiCad DRC で fab_router 26件、KRT 28件の未配線が残った。** 4層・幅/clearance 0.20mm・via 0.60/0.30mmの条件で、今回の両セルはMain完成を示せなかった。配置不可能性や4層一般の不成立を証明する結果ではない。

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
| 4層native PCB | `33f079d07bfb2dad9a76dce0667a1fd1371c94406df16f36ae17fe559d74af01` |
| 4層corrected DSN | `661d00c7d99adc270314a1a4940e64838999b948471f4d36a17aa9eac4d5e7f2` |
| Project（元とbyte同一） | `a5bc2aea160cc9a8b3035f77f0167c26a1de7ffdb749740c94fb7a9e9a3c87d5` |

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

**最終smokeゲート確定は `2026-11-04T09:29:19.054667+00:00`**。再開09:22:54 UTCから30分以内。両Mainの開始時刻はこれより後である。

## Stage 1：Main固定条件の各1回

以下は元プロジェクトを採点用に使用し、保存出力を独立KiCad 9.0.9で再充填してから得た実測。未完成でもDRC JSON・全未配線ネット/端点・生差分を保存した。ルーター自己申告と独立値を区別する。

| 項目 | セルA fab_router | セルB KRT v0.23.8 |
| --- | --- | --- |
| Main配線回数 | 1 | 1 |
| 独立KiCad未配線数 / ネット数 | 26 / 21 | 28 / 24 |
| 必須未接続 / 異ネット接触 / 物的違反 / 説明不能な転送変更 | null / null / null / null | null / null / null / null |
| 幅mm : 本数 | {'0.2': 255} | {'0.2': 496} |
| via外径/drill mm : 個数 | {'0.6/0.3': 106} | {'0.6/0.3': 42} |
| 層別トラック本数 | {'F.Cu': 199, 'In2.Cu': 41, 'B.Cu': 15} | {'F.Cu': 454, 'In2.Cu': 42} |
| 経過秒 | 287.649 | 104.724 |
| 開始UTC | 2026-11-04T09:29:19.127808+00:00 | 2026-11-04T09:29:20.271956+00:00 |
| 終了UTC | 2026-11-04T09:34:06.776242+00:00 | 2026-11-04T09:31:04.996209+00:00 |
| 停止理由 | stagnant | Fixed CLI completed its routing, rescue, reconciliation and re-grade; exit 0 with open nets |
| exit / timeout | 0 / False | 0 / False |

**未配線が残る両セルの4指標は、指定どおり全てnull。** 未配線実数や生DRCの0件を指標0へ代入せず、合格と扱わない。

### fabの実測詳細

未配線ネット別件数は `{'ADC_B': 1, 'GND': 3, 'HALL_5V': 1, 'HALL_PWR_EN': 1, 'MUX_A0': 1, 'MUX_A1': 1, 'MUX_A2': 1, 'QSPI_SCLK': 1, 'QSPI_SD1': 1, 'QSPI_SD2': 1, 'QSPI_SD3': 1, 'SWDIO': 1, 'USB_DM': 1, 'USB_DM_CONN': 2, 'USB_DP': 1, 'V1V1': 1, 'V3V3': 3, 'VBUS': 1, 'WING_EN': 1, 'XIN': 1, 'XOUT_XTAL': 1}`。全端点の部品/パッドまたはtrack、座標、UUIDを `A/inspection/main/fab/unconnected-net-endpoints.json` と `drc.json` に保存した。

DRC種別の生件数は `{'silk_overlap': 12, 'silk_over_copper': 5, 'text_height': 44, 'hole_to_hole': 1, 'track_dangling': 16}`、非印刷の生指摘は17件。非配線要素と元配線の説明不能な生差分は0件。既存F.Pasteの正規化は同一KiCad saverで基準側も保存して照合し、ゾーン再充填のcache差分だけを除外する。実際の元線分は中心線被覆で保持を確認する。

再充填後GND/In1プレーン面積は2014.048951mm²、直接接続は4 pads / 42 tracks-or-vias。これは直接隣接の列挙であり、全GND端点の完成を示さない。各接続のUUID/ネットは `plane-connectivity.json`、GND未配線端点はDRCに残す。In1信号トラックは0本。

raw PCB SHA256は `21624b6cde758b9b6199aa6e748faeb806bf67cb9788214c6a4f1d907fc957c6`、独立再充填後PCB SHA256は `8b5b229722dc6ef242210b5c061983e504d9806735796756cdfc0e3caf6be631`。

公開APIの自己検査countsは `{'violations': 0, 'incompletes': 19}`。fab側の出力project差分はKiCad saverによる `/meta/filename` のout名への変更のみで、ルール下限の変更は0件。独立KiCadの未配線値とは測定主体が異なり、置換しない。SES・読戻し・有効settings・pass/connectionログも全て保存した。

### krtの実測詳細

未配線ネット別件数は `{'ADC_A': 1, 'ADC_B': 1, 'ADC_C': 1, 'GND': 1, 'HALL_PWR_EN': 1, 'MUX_A0': 1, 'MUX_A1': 1, 'MUX_A2': 1, 'QSPI_SCLK': 1, 'QSPI_SD0': 1, 'QSPI_SD1': 1, 'QSPI_SD2': 1, 'QSPI_SD3': 1, 'RUN': 1, 'SWCLK': 1, 'SWDIO': 1, 'USB_DM': 1, 'USB_DP': 1, 'USB_DP_CONN': 1, 'V1V1': 3, 'V3V3': 3, 'WING_EN': 1, 'XIN': 1, 'XOUT': 1}`。全端点の部品/パッドまたはtrack、座標、UUIDを `A/inspection/main/krt/unconnected-net-endpoints.json` と `drc.json` に保存した。

DRC種別の生件数は `{'silk_overlap': 12, 'silk_over_copper': 5, 'text_height': 44, 'via_dangling': 9}`、非印刷の生指摘は9件。非配線要素と元配線の説明不能な生差分は0件。既存F.Pasteの正規化は同一KiCad saverで基準側も保存して照合し、ゾーン再充填のcache差分だけを除外する。実際の元線分は中心線被覆で保持を確認する。

再充填後GND/In1プレーン面積は2044.392986mm²、直接接続は4 pads / 17 tracks-or-vias。これは直接隣接の列挙であり、全GND端点の完成を示さない。各接続のUUID/ネットは `plane-connectivity.json`、GND未配線端点はDRCに残す。In1信号トラックは0本。

raw PCB SHA256は `72c3f81318e7a268324396898209c8544692c8cf8512ab295f7e4ada2fd2f24c`、独立再充填後PCB SHA256は `89d38a80750d29ba41aa64ff123db8a908a79d2ccc2b6eec261677e86547d2b4`。

出力 `.kicad_pro` の全差分は、`board.design_settings.rules.min_via_drill` の未定義→0.3mm追加と、`kicad_routing_tools` の由来メタデータ追加の2箇所。既存min_track_width/min_clearance等とnetclass値の下限緩和は0件。追加書き戻しはあるが、本Issueの禁止する緩和方向の変更ではない。#115の『書き戻しそのもの禁止』という判定と混同しない。全差分は `transfer-diff.json`、raw出力projectを保存した。未配線残存のため本セルは不合格である。

## Wing：配線なしの予備見通し

以下は資料上の事実と仮定に基づく推定であり、Wing の PCB 実測・配線結果ではない。調査した設計定義は `hardware/rev-m1/{architecture,main-wing-interface,evaluation-plan,dfm-policy,g0b-freeze-proposal}.md`、`docs/decisions.md` の D-012/D-015/D-017、`docs/hall-acquisition.md`。hash と計算値は `E/wing-outlook.json`。**`hardware/layout/**` のファイルは開かず、検索・計算の入力にも使用していない。**

### 21キーの寸法と100×100mm

**事実：** D-015/D-017 は各 Wing 21キーと3種類のピッチを指定するが、21キーの XY 座標・stagger・thumb 回転・外形は未確定。`hardware/rev-m1/g0b-freeze-proposal.md` §5 は、ピッチ比較用の **3×3スイッチ領域**と、別領域の追加12個の Hall 負荷（必要なら第4 Wing）を区別している。21センサの full-load 基板を21スイッチの完成 Wing と同一視しない。

**推定モデル：** 6列×3行の18キー＋同じ幅内の4行目にthumb 3キー、stagger/回転なし。中心範囲は5p×3p、端のキーに1ピッチ分の合計余白を仮定した「ピッチセル外接矩形」は6p×4p。さらに全周2mm追加する場合も併記する。キー占有幅を実寸で確定したモデルではなく、配置案の採用でもない。

| ピッチ p | 中心範囲 5p×3p | ピッチセル外接 6p×4p | 全周2mm追加 | 100mm幅との関係 |
| --- | --- | --- | --- | --- |
| 17.0mm | 85×51mm | 102×68mm | 106×72mm | この仮定では超過 |
| 16.5mm | 82.5×49.5mm | 99×66mm | 103×70mm | 余白なしで幅残り1mm、全周2mmでは超過 |
| 16.0mm | 80×48mm | 96×64mm | 100×68mm | この仮定では境界一致、機構/コネクタ余裕は未検証 |

一般式は `W=5p+w_outer+2m`。100mm以内には `w_outer+2m ≤ 15 / 17.5 / 20mm` が必要（17 / 16.5 / 16mm順）。外側の必要包絡寸法と基板外形余白を設計してから評価する。7列×3行ならピッチセル外接は119×51 / 115.5×49.5 / 112×48mmとなり、いずれも幅超過。配置形式だけで結論が変わるため「16mmなら必ず入る」「17mmは全配置で不可能」とは言えない。

3×3の評価領域だけなら同じピッチセル仮定で51 / 49.5 / 48mm角だが、追加12センサの磁気的分離、3 mux、コネクタ、治具まで含む外形ではない。G0B §2 記録の JST GH 本体20.75×4.25mmも、ケーブル曲げ・保持・取付穴とともに別途配置が必要。100×100mmは `evaluation-plan.md` / `dfm-policy.md` 上の最適化目標であり、磁気性能や操作性より優先しない。

### ネットと密度

**事実（D-017、interface、G0B §3/6、hall-acquisition §4）：** 各 Wing は Hall21個、TMUX1208×3、各muxで7入力使用・S7未接続。共有アドレス3本、Wing毎 enable1本、analog出力3本、HALL_5Vと共通GNDを持つ。14接点のうち6本のreturnは別ネットではなく共通GND。Wing に3V3やHALL_PWR_ENを追加する契約ではない。ADC分圧/filterはMain側であり、Wing は各Hall/muxの局所decouplingを持つ。

**推定：** 21本の局所Hall出力＋3本のmux出力＋3アドレス＋1enable＋2電源/returnで約 **30ネット**（追加test回路・部品により変わる）。コネクタは9種類のネット／14接点。3 mux の各7入力を近傍にまとめれば、21本を全基板幅に引き回す必要はない。アドレスとenableは各3 muxへ分岐する。

**Main実測との比較：** 固定Mainは48×44mm＝2112mm²、199ランド、37非空ネット、約0.0942ランド/mm²（本Issueのnative棚卸し）。仮にWingを3端子Hall×21、16端子mux×3、14接点コネクタ、各Hall/muxに2端子decoupler×24とする概算では、コア125＋decoupling48＝173電気ランド。端子数・decoupling個数は未実装モデルの仮定で、実BOMではない。上の6p×4p面積では約0.0249 / 0.0265 / 0.0282ランド/mm²で、Mainより平均約3.3～3.8倍疎になる。ただしスイッチ穴・磁石・取付keepout・thumb分離・コネクタ金具・testpointを数えておらず、使用可能な配線面積や局所escape難度を示す値ではない。

### 2層0.20mm／4層の見通しと未決定入力

**楽観の根拠（推定）：** 16～17mmのセンサ間隔に対しHall出力は局所7本単位、MainのRP2040/USB/QSPI/crystalの集中escapeを持たない。muxを対応するHall群に寄せ、裏面に連続returnを確保できれば、2層0.20mmで成立する余地がある。平均面積密度の概算もこれを支持するが、合格の証明ではない。

**悲観の根拠（推定）：** SMD片面が基本なのでmux周囲に7入力・出力・制御・電源/returnが集中する。仮にmuxパッドピッチ0.65mm、パッド幅0.30mmなら隙間0.35mmに対し、0.20mm線と両側0.20mm clearanceに必要な0.60mmを満たさず、パッド間の1本通過はできない。この数値は承認済みfootprintの実測ではなくescape感度例。スイッチ固定穴、Hallと磁石の位置拘束、コネクタreturn、配線によるGND分断も平均密度では見えない。127mA/WingというD-017の計画電流、analog settling/noise、磁気干渉の実測は別途必要。

**4層が効きそうな場所（推定）：** In1 GND planeでreturnと電源/制御交差を分離し、In2でmux入力の交差・connector fanout・thumb接続の逃げを増やす。一方でパッド直近のescape間隔、via0.60mmの占有、磁石・穴keepoutは4層でも残る。幅/間隔の緩和は局所escapeに効く可能性があるが、製造基準と別の承認・検証を要し、本Issueでは緩和条件を試していない。2層/4層の完成可否はいずれも未判定。

本格配線テストに必要なのは、D-015に沿う project-owned または承認済みの21キー座標生成定義、左右/stagger/thumb/ピッチ別の外形・固定穴・機構keepout、最終Hall/mux/connectorのpin mapと検証済みfootprint、各muxへの7入力割当とS7 NC、decoupling/testpointを含む回路・ネットリスト、配置・層基準・zone/return方針、固定native/DSN入力と期待接続表である。評価3×3＋12負荷と完成21キーWingの対象区別、コネクタ・100mmハーネス・治具の干渉確認、GND再充填を含む独立採点も必要。既存資料の「実装未着手」と最終Hall/production pitch未決定を、仮の配線データで埋めてはいない。

## D-012 改定の判断材料

**PMO確認済み価格事実：** 48×44mm、1.2mm、HASL、5枚で2層 **$4.00**／4層 **$8.00**、送料別。発注数量は5・10・15…の刻みで6枚は選べない。これは指定Main条件の価格であり、Wing/PCBA/送料や将来見積もりへ外挿しない。

4層化を本命とするPO方針に対し、固定配置・現行0.20mmの3信号層＋GNDプレーンを両候補が受理し、スモークの一連の出力経路が通ることは実証できた。しかし、今回の各1回では両セルにMain未配線が残り、**現行条件でMain完成という改定根拠は得ていない**。追加条件の探索・Main再実行はしていない。ルーターの候補・既定戦略に依存する結果であり、4層による完成可能性全体や配置不可能性を断定しない。

改定する場合はD-012、D-017、DFMの層基準を整合させ、メーカー確定1.2mm stackup、Mainの3信号層＋GND plane、Wingにも4層を原則適用するか2層実証を認めるかをHuman Gateで明確にする必要がある。Wingの層数をMainだけで決める根拠はない。D-015どおり左右Wingは**同一設計定義から生成した別々の製造データセットで可、リバーシブルPCBAは必須ではない**。

残るリスク・未決定事項は、MainのRP2040周辺等の局所escapeとGND到達、via-in-pad/印刷/既存USB NPTH等の製造事項、メーカーstackup、Wing未設計geometry・回路・最終部品/ピッチ、analog settling/noise・磁気干渉の実測。smokeのsolid/Nプレーンは契約を確認する限定fixtureであり、Mainのthermal/GNDの成立を代替しない。採否・追加投資・要求変更はPOのHuman Gateとする。

## 監査と提出

再開開始は2026-11-04 **09:22:54 UTC**、smoke期限 **09:52:54 UTC**、全体期限 **11:22:54 UTC**。`A/start.json` に保存し、smokeゲートは期限内に通過した。Main各1回・設定変更/再実行0回・インフラ再起動0回。各プロセスのargv/headless環境/開始終了/elapsed/exitは `E/processes/amend01-*/`、入力hashと順序・基点ファイル不変・変更範囲・最新指標・JSON/Python構文は `A/verification.json`、成果物hashは `A/manifest.json`、提出は `A/submission.json` とする。

ブランチの前回commit `7917d82` に追加commitし、同じDraft PR #118を更新する。作業用gitは `/tmp/issue-117-main/git`、元リポジトリの `.git` は変更していない。変更範囲は本報告と本Issue証跡ディレクトリのみであり、既存要求/決定/他Issue成果物は変更しない。Wing節は前回run 2から全文維持し、今回の配線・再調査は0回である。
