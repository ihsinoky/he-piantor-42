# Issue #223 — Main Rev.5 L1 代替評価

評価日: 2026-11-10（日本時間）。在庫取得は **2026-11-09 21:56:00–04 UTC / 11-10 06:56:00–04 JST**。
対象基準コミット: `dceb01c`（Main Rev.5 merge済み）、作業ブランチ: `l1-substitute-eval`。

**結論: Coilcraft XGL4020-152MEC / LCSC C7417180 を第1位の代替として推奨する。**
同一1.5µH±20%、同一端子形状・最大外形・高さ、低いDCRで、JLCPCB公開調達データの
在庫フィールド588個／販売可能数フィールド576個はいずれも必要5個を上回る。
正式な代替承認・調達方法・実装受入れはPOゲート。BOMの自動置換を認める記録ではない。
現行 C3033018 は3個のままで、在庫回復は確認できなかった。

## 1. 要件と設計源

正本は [Issue #223](https://github.com/ihsinoky/he-piantor-42/issues/223) と
作業指示 `.issue223-runtime/INSTRUCTIONS.md`。Issue本文のDraft PR要件は、今回の
ユーザー指示「push・PR作成をしない」に従い実施せず、ローカルコミットまでとする。

| 項目 | 要求／現行値 | repo内の根拠・解釈 |
| --- | --- | --- |
| L1／接続 | 1.5µH XFL4020-152MEC、SW1–SW2間 | [Rev.5 schematic](../schematic/main.kicad_sch)、[export netlist](../schematic/main.net.xml) のL1。PCBから回路を逆推定していない |
| U6／制御 | TPS63070RNMR、PS/SYNC(pin1)=GND、強制PWM | 同netlist、[#167 §3](../../../../../docs/issue-167-main-dual-wing-stage2.md)。TI [S1] §7.5/8.4でPWMを確認 |
| レール／負荷 | 5.2V、DC±2%、片側50mV動的予算、127mA×2=254mA連続 | [D-026](../../../../../docs/decisions.md#d-026---main-two-wing-implementation-design-first-mechanics-and-regulated-52-v)、[#165](../../../../../docs/issue-165-dual-wing-power-study.md)、[Rev.5 budget](../power-budget.json)。11mA/sensor包絡はstressのみ |
| 入力境界 | D-027がD-026の「変換器入力4.75V」を更新。Rev.5はUSB4.75VからFly/PTC/EZmate等とMain配線損失を差引く | [D-027](../../../../../docs/decisions.md#d-027---main-usb-input-requirement-at-the-board-connector)、[Rev.5計算](../power-budget.py)。4.75VをL1入力に直接置かない |
| L許容差・実効L | 現行1.5µH±20%。同じ公称／許容差を優先。TI実効L推奨範囲0.7–2.8µH | [#167 §3](../../../../../docs/issue-167-main-dual-wing-stage2.md)、[S1] §7.3、[S2] |
| 設計ピーク／Isat | repoにL1ピークの確定値はない。本評価で既存負荷・入力抵抗モデルとTI式から定常ピーク **0.635917A**、20%余裕込み **0.763101A** を導出 | §3、[calculation.json](calculation.json)。変換器全体の電流保証や起動／故障時ピークと混同しない |
| DCR予算 | repoに独立したL1 DCR上限予算はない。現行25°C typ14.4／max15.8mΩを**劣化させない比較基準**とする | #167 §3／[S2]。D-026の共通・分岐各50mΩは下流配線ループで、SW1–SW2のL1 DCR予算ではない |
| ランド | `Rev4:L1`をRev.5が継承。pad中心x=±1.55mm、各1.30×3.60mm、内側gap1.80mm、外側span4.40mm、F.Cu/Mask/Paste | [実基板](../inspection/final/main.kicad_pcb)のL1=(101.5,101.5)mm、0°を直接読取り。`Rev4`という名前から旧基板を使ったわけではない |
| 外形／高さ／シールド | 現行4.0±0.3mm角、2.10mm max、シールド。代替も同じ包絡を維持 | [S2] p3。repoに独立した筐体高さ保証はなく、現行品の包絡を基準にする |
| 調達 | JLCPCB実装掲載、評価時在庫≥5、正式承認はPO | Issue #223。公開在庫は予約・見積確約ではない |

## 2. 要求値 vs 候補値と順位

メーカー値は25°C。Isatは**同じL低下率ごと**に比較する。Irmsは20°C／40°C温度上昇の
参考値で、任意の基板・周囲温度で保証される絶対最大電流ではない。[S2–S4]

| 比較項目 | 現行基準 C3033018 | **1位 C7417180** | 2位（除外）C3221841 | 3位（除外）C5355380 |
| --- | --- | --- | --- | --- |
| MPN | XFL4020-152MEC | **XGL4020-152MEC** | Bourns SRP4020FA-1R5M | XFL4020-102MEC |
| L／許容差 | 1.5µH±20% | **1.5µH±20%** | 1.5µH±20% | 1.0µH±20%（現行1.2–1.8µH範囲を継承しない） |
| DCR typ／max | 14.4／15.8mΩ | **13.0／14.3mΩ** | 14.4／15.8mΩ | 10.8／11.9mΩ |
| Isat 10%／20%／30%低下 | 4.1／4.4／4.6A | **3.2／5.3／7.5A** | 4.1／4.5／7.5A | 4.5／5.1／5.4A |
| Isat(10%)÷設計ピーク | 6.45倍 | **5.03倍** | 6.45倍 | 6.11倍（異なるLでピーク0.736968A） |
| Irms 20°C／40°C上昇 | 6.7／9.1A | **8.0／11.1A** | 6.7／9.1A | 8.0／11.0A |
| シールド／コア | 有／composite | **有／composite** | 有／metal alloy powder | 有／composite |
| 外形／高さmax | 4.0±0.3mm角／2.10mm | **同左** | 4.1±0.2mm角／2.10mm | 現行と同じ |
| 同一ランド適合 | 現行 | **同一端子図・同一推奨ランド、メーカーdrop-in指定。§4参照** | 推奨ランドは異なる。採用せず、変更検討もしない | 現行と同一機械図。ただしL値変更 |
| JLCPCB区分 | Extended | **Extended** | Extended | Extended |
| 実装掲載 | SMT／Economic・Standard | **SMT／Economic・Standard** | SMT／Economic・Standard | SMT／Economic・Standard |
| 公開`overseasStockCount` | **3** | **588** | **0** | **11,407** |
| 公開`canPresaleNumber` | **0** | **576** | **0** | **10,969** |
| USD単価、1–9個tier | $3.5250 | **$5.4502** | $1.5425（在庫なし参考） | $2.5697 |
| `preMinPurchaseNum` | 3 | **2** | 6 | 4 |
| 判定理由 | 必要5個に不足 | **唯一の推奨。電気／機械／公開調達数を満たす** | 在庫0で失格。実装可否の最終判定に進めない | 同一1.5µH要求を維持する代替としては失格。TIに1µH例はあるが動特性の再評価が必要 |

調達値は [stock-snapshot.json](stock-snapshot.json) と[S5–S8]。
上表の`preMinPurchaseNum`は公開フィールド名のまま記録する。発注UIでの数量制約を
実注文で検証していない。通貨USD、部品単価のみで、Extended実装費・税・送料等を含まない。
C7417180は5個なら部品代$27.2510、現行の同tier仮定$17.6250に対し **+$9.6260/5個**。
10個以上の価格を5個へ流用しない。

**在庫の証拠範囲:** JLCPCB公開ページをGETし、サーバーが返すRSCの対象コードの
`componentInfo`と価格recordsを抽出した。検索結果の古いLCSC在庫1個という記述は採用しない。
`overseasStockCount`は自社実装倉庫の確保済み数と同義とは断定せず、
`canPresaleNumber`も併記する。C7417180は両方≥5、現行は両方<5である。
公開ページは実装対応を掲載しているが、納期・部品予約・アカウント別利用可否・Economicでの
当該見積への受入れは未確認。`assemblyComponentFlag=false`も原データ通り保存し、
このフィールド単体を「実装不可」と解釈しない。PO/PMOが調達時に再確認する。

## 3. ピーク電流とDCRの定量評価

`python3 calculate.py`で元netlist・実PCB・電源モデルを読取り、[calculation.json](calculation.json)を再生成できる。
元ファイルのSHA-256も同JSONに保存する。

Rev.5の上流感度中で最も厳しいUSB4.75V、上流予約1Ω＋基板往復0.048686448Ω、
Main他負荷110mA、効率75%を用いる。これは**保証された入力・効率下限ではない**。
既存sweepのVout=5.304VではVIN=4.184469671V。本評価は動的上側予算まで含めた
Vout=5.354VとしてKVLを再計算し、VIN=**4.179708282V**を使う。
この条件はUSB500mAを超える既存stress感度であり、採用品によりUSB予算が解決したとはしない。

TI [S1] §9.2.2.2式(7)(8)で、`D=1−VIN/VOUT`、
`Iavg=Iout/[η(1−D)]`、`ΔIpp=VIN·D/(f·L)`、`Ipeak=Iavg+ΔIpp/2`。
fは§7.5の最小2.1MHzを使用。Lは1.5µH×0.8（許容差）×0.9（DC biasの10%低下予約）
=**1.08µH**。設計点はD=0.219330、Iavg=0.433815A、ΔIpp=0.404204A、
**Ipeak=0.635917A、Irms=√(Iavg²+ΔIpp²/12)=0.449234A**。
TI推奨20%余裕込みIsat要求0.763101Aに対し、C7417180の10%低下Isat=3.2Aは4.19倍。
設計ピーク自体に対して5.03倍、Irms(20°C上昇)はモデルIrmsの17.81倍。

XGLは10%低下Isatでは現行4.1Aより低い。20%低下では5.3A>4.4A、30%低下では
7.5A>4.6Aであり、単に「全Isatが改善」とは書かない。Lmax=1.8µHのTI式(9)による
RHPZは同条件で約**1.136MHz**（推奨400kHz超）。これは定常boost近似で、
buck-boost遷移・起動・短絡・温度ディレーティングやループ安定性の実測保証ではない。
10%低下のbias予約と25°C catalogue Isatによるスクリーニングであり、125°CのIsatを
25°C値で保証していない。L1をICの3.6A（typ）平均入力電流制限そのものと取り違えない。

銅損は`PL=Irms²·DCR`。25→125°Cは銅の近似`R(T)=R25·[1+0.00393(T−25)]`を使う。
125°Cは既存抵抗感度との比較温度であり製品ambient保証ではない。

| DCR最大値での比較 | 25°C | 125°C近似 |
| --- | ---: | ---: |
| 現行DCR | 15.8000mΩ | 22.0094mΩ |
| C7417180 DCR | 14.3000mΩ | 19.9199mΩ |
| DCR差 | **−1.5000mΩ (−9.49%)** | **−2.0895mΩ** |
| 現行L1銅損 | 3.188610mW | 4.441734mW |
| C7417180 L1銅損 | 2.885894mW | 4.020050mW |
| 銅損差 | **−0.302716mW** | **−0.421684mW** |
| 出力損失換算抵抗差 `ΔPL/Iout²` | **−4.692110mΩ** | **−6.536109mΩ** |
| 仮に全体効率90%を基準とし、上記銅損差だけ反映した効率 | **90.018034% (+0.018034 percentage points)** | **90.025124% (+0.025124 percentage points)** |

効率換算は`ηnew=Pout/(Pout/0.90+ΔPL)`、Pout=5.354×0.254=1.359916W。
75%感度で求めた同一電流波形を固定してDCR差を抽出した例であり、90%効率を実証した値ではない。
**DCRが9.49%低下しても、変換器全体の効率が9.49%改善するわけではない。**
typ比較なら14.4→13.0mΩ（−1.4mΩ）であり、typとmaxを交差比較しない。

L1はU6のSW1–SW2にあり、[既存電源モデル](../power-budget.py)の
`rail_common_loop`、U5 Ron0.25Ω、分岐ループへ直列に足す部品ではない。
上表の出力換算抵抗は**変換損失を比較するための等価値**で、下流50mΩ予算やセンサー電圧を
直接補正する値ではない。既存の効率仮定にL1損失が含まれるため、追加計上すると二重計上になる。
基板往復48.686448mΩ／共通37.109mΩ等の配線抵抗は変わらない。

Bourns候補のDCR差は0、同じ電流近似なら銅損・DCR由来効率差も0。
1µH候補は同じbias/tolerance条件でΔIpp=0.606306A、ピーク0.736968A、Irms=0.467792A、
25°Cの実波形で銅損2.604072mW（現行より−0.584538mW）。リップルは50%増え、
**DCR差だけの計算（−0.787062mW）を総損失差として採用しない**。安価でも今回は推奨しない。
コア損・周波数依存ESR・スイッチ損・ADCノイズをDCRだけで定量保証することはできない。

## 4. 同一フットプリントでの載せ替え

Coilcraft [S2]製品ページがXGL4020をXFL4020のdrop-inとして示し、1.5µH同士を対応付ける。
[S2] Doc745-3 (2026-03-10) と[S3] Doc1529-3 (2026-02-19)の図面を目視照合した。
両方とも本体4.0±0.3mm角、高さmax2.10mm、端子幅0.82±0.05mm、端子内gap1.57±0.25mm、
端子の長手3.25mm typ、推奨ランド幅0.98mm×長さ3.40mm、中心間2.37mmで一致する。

**既存PCBの1.30×3.60mm／中心間3.10mmはメーカー推奨ランドそのものではない。**
本評価は既存品と候補の共通機械図を既存PCBへ当てて、載せ替えで新しいランド差分が
発生しないことを確認したもの。名目の右端子x=0.785–1.605mmに対し、既存右padは
x=0.900–2.200mmで重なり0.705mm、gap／幅公差端点を組み合わせた最小重なり0.530mm。
長手3.25mm typはpad長3.60mm内に収まり、外形包絡は現行と同じ。
配置誤差、はんだ量、stencil、濡れ／接合強度はこの幾何計算だけで保証しない。
mask/paste開口も既存データを保持し、量産ランド受入れは従来からの実装確認項目として残す。
非極性部品だが短リード／高dv/dt方向のメーカー表示と業者モデルの回転はpreviewで照合する。

Bourns [S4]は推奨ランド幅1.4mm、長手3.4mm、外側span3.8mmで、同一推奨ランドとは呼べない。
在庫0で既に失格のため、採用用のランド変更・基板改版へ進めていない。
今回XGLの同一外形・端子候補が残るため「フットプリント変更候補しか残らない場合」の停止条件は
発動しない。基板・フットプリント・回路図・BOMは一切変更しない。

## 5. 結論と残るゲート

1. **C7417180をPO承認候補として推奨**。同一1.5µH、既存ランドに対する機械互換、
   DCRを悪化させず、定常電流余裕と公開調達数を満たす。Extended同士だが単価は+$1.9252/個。
2. **C3221841は在庫0で失格**。補充されてもランド受入れを再評価するまで推奨しない。
3. **C5355380はL値変更のため今回の代替として失格**。同一機械形状・豊富な在庫・低DCRだけで
   1.5µH設計を変更しない。

PO/PMOが正式承認時にC7417180の最新在庫・必要5個＋業者要求予備数・納期・実装工程・費用と
業者モデル／回転を再確認する。公開フィールドは予約ではなく、アカウント内の見積を取得していない。
基板原型に残るランド／stencil確認、実機の温度・起動・過渡50mV・5.2V精度・ADCノイズ・
USB許可電流・完成上流抵抗／効率は未検証のまま。代替推奨は電源系全体の製造GOを意味しない。

## 6. 一次資料と再現手順

- **S1** [TI TPS63070 Rev.B](https://www.ti.com/lit/ds/symlink/tps63070.pdf): §7.3、7.5、9.2.2.2、式(7)–(9)、Table5。
- **S2** [Coilcraft XFL4020-152製品ページ](https://www.coilcraft.com/en-us/products/power/high-voltage-inductors/xfl/xfl4020/xfl4020-152/) および [XFL4020 datasheet](https://www.coilcraft.com/getmedia/50632d43-da1b-4cdb-8ab4-3029cab51df3/xfl4020.pdf)。
- **S3** [Coilcraft XGL4020-152製品ページ](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xgl/xgl4020/xgl4020-152/) および [XGL4020 datasheet](https://www.coilcraft.com/getmedia/76c9c081-4945-4c85-9129-9356e1ad6734/xgl4020.pdf)。
- **S4** [Bourns SRP4020FA datasheet](https://www.bourns.com/docs/product-datasheets/srp4020fa.pdf): p1電気特性・機械図・推奨ランド。
- **S5** [JLCPCB C3033018](https://jlcpcb.com/partdetail/Coilcraft-XFL4020152MEC/C3033018)。
- **S6** [JLCPCB C7417180](https://jlcpcb.com/partdetail/Coilcraft-XGL4020152MEC/C7417180)。
- **S7** [JLCPCB C3221841](https://jlcpcb.com/partdetail/BOURNS-SRP4020FA1R5M/C3221841)。
- **S8** [JLCPCB C5355380](https://jlcpcb.com/partdetail/Coilcraft-XFL4020102MEC/C5355380)。

このディレクトリで`python3 calculate.py`（ネットワーク不要）。設計源hash、net接続、実ランド寸法、
KVLの残差とIsat余裕を検査する。在庫再取得は`python3 capture-stock.py /tmp/issue223-stock-recheck.json`。
元の時点証跡を上書きせず比較する。これは公開GETのみでカート・アカウント・注文操作をしない。
取得証跡にHTTP Date、取得UTC、HTML SHA-256、対象コード別の許可フィールドと全価格tierを保存。
署名付き画像URLや他顧客メタデータを保存しない。参照PDFのhashは[sources.json](sources.json)。
