# Issue #117 — 4層 Main の事前ゲートと Wing 予備見通し

**STAGE_0_STOP：指定された smoke のネット不変と GND ゾーンを両立できず、配線前に中断した。** 固定 smoke は非空ネットが `N` の1個だけで `GND` が存在しない。ネットを追加・改名せずに「ネット GND の全面ゾーン」を構築できないため、smoke 配線は両候補0回、Stage 1 の Main 配線も両候補0回である。4層で Main が完成するかは **未判定**。ルーターの失敗や配置不可能性を示す結果ではない。

対象は [Issue #117](https://github.com/ihsinoky/he-piantor-42/issues/117)。以下 `E/` は [証跡ディレクトリ](../hardware/kicad/qualification/issue-117-four-layer-main/evidence/) を指す。指示書全文は `E/instructions.md`、機械可読の結論は `E/assessment.json` と `E/equivalence-gate.json`。この報告は要求変更・製造承認ではなく、`docs/decisions.md` は変更していない。

## Stage 0：固定入力と等価性

#115 の保存入力を byte 同一コピーし、次の SHA256 を照合した。提出ブランチの基点は `e87f8bc5d4855201276ce53d9f54d19bea9536e3`。基点7349ファイルの全 byte 一致を確認し、元の読取り専用 `.git` を変更せず `/tmp/issue-117-main/git` でブランチを作成した。成果物は本書と指定証跡ディレクトリだけの追加である。

| 固定入力 | SHA256 |
| --- | --- |
| Main PCB | `46676e57e9618940a33c5e298244e97aaec61498a87aa7c58a264e444fc71e20` |
| smoke PCB | `3f70465774f577ffe803f88de017004d164f045e6415ade22766a461a2454bec` |
| 両入力のプロジェクト | `a5bc2aea160cc9a8b3035f77f0167c26a1de7ffdb749740c94fb7a9e9a3c87d5` |

`E/preflight.json` は #103 の fab_router ソース1534ファイル、#113 の KRT ソース2055ファイル、独立 KiCad 検査 runtime 26ファイルの hash 一致を記録する。fab_router は `69cf598db98c136bff16bbe02bccdded95674b18`、KRT v0.23.8 は `c64c0db25e6cf23afa6769ee05665c7ea22b3ff2`。KRT binary の SHA256 は `4411ccf3f074f519d8d69be29ac58b46ca7c4c2fe4f4be889d253d40996c2c0f`。ツールソースの修正、別版導入、配線の条件探索はない。

### 生成した入力と差分

`E/prepare-four-layer.py` と `E/inputs/{main,smoke}/` に手順・元ファイル・生成物を保存した。層は F.Cu signal / In1.Cu power（GND専用）/ In2.Cu signal / B.Cu signal。板厚は1.2mm。スタックアップの評価用仮定は銅箔各0.035mm ×4、誘電体0.18 / 0.70 / 0.18mm、FR4、比誘電率4.5、損失正接0.02、ソルダーマスク厚を合計から除外する。合計は1.20mm。メーカー確定スタックアップやインピーダンス保証ではない。

Main は **49 footprints / 199物理ランド / 37非空ネット / 元3トラック**を保持し、In1.Cu に GND の全面ゾーンを追加して KiCad 9.0.9 の `ZONE_FILLER` で充填した。外形のままクリップされる矩形ゾーン、clearance / 最小銅箔幅 / thermal gap / spoke は0.20mm。充填済み銅箔面積は約2064.18mm²（内部単位の生値も保存）。これは入力のゾーン面積であり、配線完了後の GND 接続を示す値ではない。

初回の native 保存で KiCad が既存 F.Paste 矩形の反転した始終点を正規化したため、厳密な AST 照合が停止した。`E/preparation-attempt-01/` と失敗ログを保持し、準備スクリプトを修正した。修正後は KiCad が生成・充填した **zone ノードだけ**を、元 PCB へ層・stackup を追加したテキストに移植する。これにより既存の描画表現も保持した。これは配線前の入力準備の修正であり、ルーター実行や結果を見た再配線ではない。

最終入力の全トップレベル AST Counter は、layers / setup / zone 以外の追加・削除が両基板とも0。setup は stackup 以外が完全一致。フットプリント内の全パッド、ネット定義、外形、元トラックと元層、UUID、印刷・ペースト・その他の既存要素を保持した。元 `.kicad_pro` は byte 同一である。

さらに #115 と同じ独立 `eda-004g/resume-02/read-pcb.py` で KiCad 読戻しを行い、既存 snapshot との差分は Main の layers=2→4 と zones=0→1、smoke の layers=2→4 だけだった。幅 / clearance 0.20mm、via 0.60/0.30mm、板厚1.2mmも読戻し一致。詳細は `E/native-equivalence.json` と `E/preparation-readback.json`。

### 再生成 DSN の読戻し

4層 native から KiCad の公開 `ExportSpecctraDSN` で `raw.dsn` を新規生成した。既知の KiCad exporter の SMD間例外値 `clearance 50 (type smd_smd)` は、#87/#115 の既存検証済み `restore-clearance.py` を無改変で呼び、**その数値トークンだけ200µmへ復旧**して `corrected.dsn` とした。幅・global/class clearance は200µm、via padstack は600:300µm、4層貫通を明示する。元ルールを緩和する操作ではない。raw・補正後・byte位置・hashを保存した。

`E/check-four-layer-dsn.py` は、4層の名前と signal/power の役割、Main の plane GND / In1.Cu、全 native 非空ネットと DSN network 集合を直接照合した。内層の PTH 形状・via 形状・NPTH 障害物は外層と同じ形状・座標の拡張であることを検証した上で、**追加内層・planeだけを検査用メモリ上で除外**し、via の層範囲名と B.Cu index を2層表現へ戻すと、基板ファイル名以外の **全 AST が #115 の検証済み corrected.dsn と順序まで完全一致**した。ルーターへ2層投影を渡してはいない。

この照合は #115 の native/DSN 個別照合済み基準に対する厳密な推移的照合であり、placement の位置・回転・front/back・PN、全パッド座標/形状、ネット、NC、外形、元トラック、ルールの一致を含む。内層形状を無条件に捨てた比較ではない。結果は `E/inputs/*/dsn-projection.json`、`E/dsn-equivalence.json`。

### smoke を止めた理由と層役割の確認範囲

固定 smoke は **4 footprints / 5物理ランド / 非空ネット `N` だけ / 元1トラック**。`GND` の追加はネット棚卸しを変え、`N` を `GND` に改名すると元トラックとパッドのネットも変わる。ネット0は未割当であり、GND の代用にできない。したがって `E/inputs/smoke/main.kicad_pcb` は4層 stackup を保持する **ゾーン未作成の不適合準備物**として保存し、有効な4層 smoke 入力とは認定していない。空の GND ゾーンや4信号層への読み替えは行っていない。

配線を呼ばない公開パーサ／設定解決だけを実行した。

- fab_router `readDsn` は In1.Cu を `plane` と読み、Main の planeNet を `GND` に対応づけた。全 netGroup の信号用 usable sheets は `[0,2,3]`（F/In2/B）。全層幅200µmも読戻した。smoke では GND planeNet 不在がそのまま現れる。`E/read-fab.ts` は配線APIを呼ばない。
- KRT は #115 の trace 停止方式で `batch_route` の config 構築後、net選択・配線処理の前に停止した。既定と明示指定の両 dump・全差分を `E/configuration/` に保持する。明示指定は `--escalation off --track-width 0.20 --clearance 0.20 --via-size 0.60 --via-drill 0.30 --layers F.Cu In1.Cu In2.Cu B.Cu --layer-costs 1 -1 1 1`。負値は固定版公式 CLI が規定する、via 通過を残したトラック配置禁止である。4層を bare CLI で信号配線させてはいない。

KRT の既定解決との実効差分は escalation、In1 の禁止コスト、および寸法をクラス由来から明示値由来にするフラグだけ。実効幅0.20 / clearance0.20 / via0.60/0.30は変わらない。これは **設定読戻しの結果**であり、実配線での層役割遵守・headless出力・SES転送・4指標合格を確認したものではない。

等価性ゲートの判定は **不成立**。条件の明示修正がないまま、スモークや本試験へ進むことはしない。再開には、同じ `N` ネットのプレーンでよいのか、smoke の改名・置換を認めるのか等について、指示元による固定条件の解消が必要である。

## Stage 1：両セル未実行

| 項目 | セルA fab_router | セルB KRT v0.23.8 |
| --- | --- | --- |
| smoke 配線回数 / Main 配線回数 | 0 / 0 | 0 / 0 |
| 停止理由 | Stage 0 の固定 smoke 条件が不成立 | 同左 |
| 必須未接続 / 異ネット接触 / 物的違反 / 説明不能な転送変更 | null / null / null / null | null / null / null / null |
| 未配線数・ネット/端点、幅/via分布、層別本数、プレーン接続、実行時間 | 未測定 | 未測定 |
| 出力プロジェクト下限書き戻し / 緩和 | 出力なし・対象外 | 出力なし・未検証 |

独立4指標は、未実行を0として扱わない。ゾーン再充填後の出力接続検査、出力 DRC 生値、実配線の停止理由は出力が存在せず取得できない。再充填済みの **入力** と出力の独立検査は区別する。インフラ障害による配線中断・再実行も0回。準備物から Main 完成や不完成を推定しない。

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

**PMO確認済み価格事実（今回の指示書）：** 48×44mm、1.2mm、HASL、数量5枚で **2層 $4.00／4層 $8.00、送料別**。差額は5枚で$4.00。発注数量は5・10・15…の刻みで、6枚は選べない。これは指定Main条件の事実であり、Wing・PCBA・送料や将来の実発注見積もりへ外挿しない。

POの「4層を本命とする」方針に対し、Mainの配置・ネット不変の4層入力作成とDSN表現保持は確認できた。両候補の設定読戻しにもプレーン専用化の表現がある。ただし **4層で現行0.20mmのままMain完成、という技術的根拠は今回得ていない**。Stage 0の固定smoke条件を解消してから、許可された各1回のMain試験に進む必要がある。今回の0回を合格や実行済みとして扱わない。

改定する場合は、D-012およびD-017/DFMの層基準を整合させ、Mainの3信号層＋GND plane、1.2mmの実メーカーstackup、Wingにも4層を原則適用するか2層実証を認めるかをHuman Gateで明確にする必要がある。WingをMainの結果だけで同じ層数に決める根拠はまだない。左右WingはD-015どおり **同一設計定義から生成した別々の製造データセットでよく、リバーシブルPCBAは必須ではない**。

残るリスクはsmokeの評価契約、実配線のプレーン遵守とGND到達、KRT出力プロジェクトの下限書き戻し、現行寸法での局所escape、Wingの未設計geometry/回路とanalog/magnetic実測、USB NPTH等の既存製造事項。価格差だけでそれらの合格を推定しない。採否・要求変更・追加試験はPO判断とし、このPRでは決定ログを更新しない。

## 検証と提出

`E/verification.json` に基点ファイル不変、追加範囲、固定hash、native/DSN読戻し、配線0回、独立指標null、Wing分析のみ、JSON/著作ファイル検査を保存する。各プロセスのargv・headless環境・開始/終了・elapsed・exitは `E/processes/`、成果物hashは `E/manifest.json`。途中の入力生成失敗を含め生ログを保持し、ツールbinaryや依存物を成果物へ含めない。

開始を保守的に **2026-11-04 09:05 UTC**、Stage 0目安期限10:35 UTC、全体期限12:05 UTCとした。条件不整合は期限前に検出した。smoke条件について確認を提示したが、明示修正の回答がない限り元の固定条件を維持する。Draft PRで提出し、mergeしない。提出時刻は `E/submission.json`。
