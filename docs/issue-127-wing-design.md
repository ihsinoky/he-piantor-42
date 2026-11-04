# Issue #127 Stage 2 — Evaluation Wing 設計入力

2026-11-04 / baseline `22d25dd` / Draft、製造・配線承認前。
[Stage 1](issue-127-wing-parts-placement-review.md) は先に `6c6aed6` でコミットした。
推奨は Wing にセンサ・3 MUX・ローカル容量・GH14を維持する案。
D-017の凍結変更を要さないためStage 2を実施した。

## 到達範囲と成果物

**16.0 / 17.0 mmの3×3 Wingと、ピッチ可変の代表21キー候補の配置・外形・
ピン単位ネット・BOMを作成した。** G0Bの3×3＋12 Hall-only負荷の構成も
別バリアントとして用意し、21スイッチの代表配置と区別した。
2層配線評価は後続Issue。本データはその入力で、Gerber/配線済みPCBではない。

| 定義 / JITXクラス | ピッチ | 外形 | Hall / MUX / 100 nF / GH14 / TP |
| --- | --- | --- | --- |
| `pitch9` / `Pitch16`, `Pitch17` | 16 / 17 mm | **64×80 mm** | 9 / 3 / 12 / 1 / 15 |
| `representative21` / `Representative16`, `Representative17` | 16 / 17 mm、可変定義あり | **98×98 mm** | 21 / 3 / 24 / 1 / 15 |
| `load21` / `Load16`, `Load17` | 16 / 17 mm | **98×98 mm** | 21 / 3 / 24 / 1 / 15 |

- 設計の正: [`wing/definition.py`](../hardware/jitx/wing/definition.py)。
  `define_wing(pitch, kind)` は有限の16–17 mmを受理し、CLI既定出力は今回対象の両端のみ。
- native JITX: [`evaluation_wing.py`](../hardware/jitx/he_piantor_42_jitx/evaluation_wing.py)。
  既存の`Circuit` / `Net` / `Board` / `Design` / `.at()`パターン、既存Hall/MUXモデルを使用。
  新GH14モデルは既存の承認済みproject-owned `JstGh14.tsx`を転記した。
  arbitrary pitchはinstantiation開始前に `make_wing_design(name, pitch, kind)` でクラスを定義する。
- [`wing/generated/`](../hardware/jitx/wing/generated/) の6ディレクトリに各
  `definition.json`, `placements.csv`, `nets.csv`, `bom.csv`, `placement.svg`。
  JSON/CSVは下流ツールから読める設計入力、SVGは配置レビュー用の概略図。
- `definition.json`には外形頂点、4個の取付NPTH候補、機構keepout寸法、
  100 mm 1:1ケーブル条件、センサのMUX/address/role、全物理ピンnet/NCが含まれる。
  CSVにはリファレンスとMPN、mm座標、角度、面、ネット端点がある。

## 共通寸法とピッチ差分

全て基板中心原点、+Y上、mm、top実装、角度0°。基板厚1.2 mm、2層。
`WingSubstrate`は既存qualificationの公称材料モデルを再利用し、最大寸法のみ100 mmに設定。
MainのD-019スタック/0.10 mmルールを流用しない。仮の配線幅/間隔0.15 mm、
via 0.65/0.30 mm等は既存qualification scaffoldingであり、Wing製造条件の承認ではない。

3×3は列A/B/Cの中心Xが`(-p, 0, p)`、行0/1/2のYが`(p+10, 10, 10-p)`。
中心範囲は32×32 / 34×34 mm、1ピッチセルの外接は48×48 / 51×51 mm。
基板外形・MUX中心`(-18,-22),(0,-22),(18,-22)`・GH原点`(0,-33)`・
取付穴・制御TPは共通。センサ、直近容量、raw TPのみピッチに追従する。
Hall用容量はセンサ原点から`(+3.5,0)`、MUX用は`(+5,+1)`。
ピッチによって部品/ネットが変わらないことを検証した。

取付候補は各辺から3 mm内側に4個のφ2.2 mm NPTH、周囲φ5 mmを予約。
**native JITXのBoardは矩形のみ**で、NPTH/keepoutはJSON側の設計定義にある。
下流のnative PCB化ではこれらの穴/禁止領域を必ず実装し、取り込み後に再検証する。
配線後に穴を追加する運用は不可。スイッチ用PCB穴は仮定しておらず、
センサ基板の上に別の非磁性固定/ストローク治具を置く案。治具寸法は未確定。

GHの原点は信号ランド列の中心。pin1は+X端、14信号ランドは
`x=8.125−1.25×(pin−1), y=0`、0.6×1.7 mm。
機械補強ランドは`x=±9.975,y=−3.35`、1×2.8 mm、電気的NC。
ピン1表示とケーブル回路番号の対応は下流基板化で必須。
ヘッダ本体20.75×4.25 mm、配置検証用ランド包絡は20.95 mm幅。
ケーブル/ラッチ用に原点からX±13、Y−7〜+1 mmの平面投影を予約する。
全6基板でこの予約領域が100 mm以内に入る。これはtop-entryの上方引出しを
仮定した予約であり、曲げ半径・高さ・ラッチ操作・実ハーネスの機構保証ではない。
[JST資料](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf)と承認済みnativeモデルを根拠にした。

## 代表21キー候補とfull-loadの区別

既存[G0B §5](../hardware/rev-m1/g0b-freeze-proposal.md)に最終21キーの座標はない。
[Issue #117の見通し](issue-117-four-layer-main-and-wing-outlook.md)の6列×3行＋thumb3は
未採用の推定モデルで、17 mmでは1ピッチセル幅だけで102 mmとなる。
その配置の採用を仮定せず、指示書で許可された**新しい候補**を提示する。

代表候補は5列×4行20キー＋中央下のthumb1キー、stagger/回転なし。
X=`−2p,−p,0,p,2p`、Y=`2p,p,0,−p`、thumb=`(0,−2p)`。
ピッチセル外接は80×80 / 85×85 mmで、98×98 mm内に余白を持つ。
GHは`(−29,−36)`、MUXは`(18,−35),(29,−35),(40,−35)`で、
thumbの左右に空けた領域を使う。4穴とコネクタ予約領域を含む。
実キーキャップ外形・操作性・磁石軸/センサ感磁点・治具干渉は未検証。
**PiANTORの最終18＋3親指配列や左右の完成Wingとしての採用を意味しない。**
100×100条件を満たす電気/寸法評価候補の採否はPOに求める。

代表候補のrow-major順（thumbは最後）にA/B/Cへラウンドロビンで配り、
各MUXに7入力を割り当てる。全21点にスイッチを置く候補なので、
G0Bの磁気3×3比較に勝手に代用しない。

別の`load21`は`pitch9`と**同一の3×3座標/列MUX割当**に、各列Xで
Y=`−15,−20,−25,−30` mmのHall-only負荷4個を加える（計12）。
追加サイトにはスイッチ/磁石を置かない。MUXは`(30,−12),(30,−24),(30,−36)`、
GHは`(−29,−39)`。磁気領域の最下行と最初の負荷サイト中心距離は
16 mm版で9 mm、17 mm版で8 mmにすぎず、磁気的分離は**未証明**。
G0Bで認められた別基板構成として、通常のピッチ比較は独立`pitch9`で行い、
`load21`はfull-load電気評価に使う。磁石を近づける場合は追加負荷への影響を測定する。
full-loadを代表21キー形状の磁気/操作性検証と同一視しない。

## BOMと電気接続

| リファレンス | 型番 / 値 | pitch9 | representative21 / load21 |
| --- | --- | ---: | ---: |
| `U_H{A,B,C}{0..2 / 0..6}` | DRV5055A3QDBZR、SOT-23 | 9 | 21 |
| `U_MUX_{A,B,C}` | TMUX1208PWR、TSSOP-16 | 3 | 3 |
| `C_H…`, `C_MUX_…` | GRM188R71C104KA01D、100 nF / 16 V / X7R / ±10%、0603 | 12 | 24 |
| `J_WING` | BM14B-GHS-TBT(LF)(SN) | 1 | 1 |
| `TP_W_*`, `TP_H_*` | PCB_PAD_1.2MM、基板銅箔（購入部品ではない） | 15 | 15 |

容量は既存0402モデルを変更せずWing専用0603モデルを追加した。
[村田製作所の製品仕様](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM188R71C104KA01-01.pdf)
を根拠とする候補MPNで、実効容量・在庫・手はんだ工程は別途確認。
9キーは名目1.2 µF、21キーは2.4 µFのローカル容量。bulkは追加していない。
ハーネス（GHR-14V-S×2、SSHL-002T-P0.2×28、100 mm 14導体1:1）は
基板BOMとは別の既存共用アセンブリで、今回Main側部品を追加しない。

14 pinはG0Bの全割当をそのまま保持。6 GND接点は独立端子を同一GNDネットに接続。
MUXはHALL_5V給電、共有A0/A1/A2/WING_EN、DをA/B/C各出力へ。
Hall VCC=pin1、OUT=pin2、GND=pin3。MUXの物理pin3(NC)は未接続、
address0..6をS1..S7に接続し、address7に対応する**S8=物理pin9**をNCとする。
G0Bの「unused S7」はゼロ起点のaddress7を指すものとして区別する。
3×3ではaddress0..2のみ、残りS4..S8は全てNC。空き入力をGNDへ短絡しない。
Main側のADC分圧/フィルタとenable pull-downは変更しない。

TPは遠端HALL_5V/GND、A0/A1/A2/EN、各MUX出力＋隣接GND、
中心/直交隣接/対角rawの計15。治具を外して接触できる配置案であり、
実治具を取り付けたときのプローブ到達性・負荷は後続確認。

## 検証と限界

固定lockで `jitx==4.4.3`、`jitxlib-standard==4.4.0`、`ruff==0.16.10` を復元。

```sh
cd hardware/jitx
uv sync --locked --group dev
uv run python -m wing.export --check
uv run python -m unittest discover -s tests -p test_evaluation_wing.py -v
uv run ruff check wing he_piantor_42_jitx/evaluation_wing.py \
  he_piantor_42_jitx/components/connectors/jst_bm14b_ghs_tbt.py tests/test_evaluation_wing.py
uv run jitx design build he_piantor_42_jitx.evaluation_wing.Pitch16 \
  he_piantor_42_jitx.evaluation_wing.Pitch17 \
  he_piantor_42_jitx.evaluation_wing.Representative16 \
  he_piantor_42_jitx.evaluation_wing.Representative17 \
  he_piantor_42_jitx.evaluation_wing.Load16 \
  he_piantor_42_jitx.evaluation_wing.Load17 --dry --no-dependency-check
```

結果: 6バリアントのdry build成功、3テストメソッド（6構成を反復）成功。
実際のJITX部品/ポートで凍結ピン割当、給電、MUX→Hall、未使用入力NCを確認。
実ランド形状を座標変換して、他部品のパッド重複0、銅箔の外形から0.5 mm内側への
包含、全取付穴φ5予約との非干渉を確認した。JSON/CSV/SVGの再生成一致も確認。
これはパッド重複と設計入力の検査で、配線DRC/returnの連続性/製造性の証明ではない。

通常のnon-dry buildは `no runtime reachable in this project` で停止した。
本環境ではJITX runtime未起動のため、runtimeでのbuild/export結果はない。
dry buildは回路/配置の変換確認までで、Gerber/CAM/製造出力を含まない。

局所MUX escape、GHの0.65 mmランド間隙、共有アドレスと21 rawの交差、
2層GND returnの分断、GH補強ランド下の逃げを後続配線評価で検証する。
平均密度だけで2層成立を判定しない。パッド重複はなく明白な配置破綻は
検出していないが、手はんだ時のこて到達、sensor横容量とスイッチ機構、
非磁性取付具、keycap端部、磁石高さ、プローブ/ケーブル干渉は未確定。

## PO判断と次の作業

1. Stage 1の現行責務維持案をレビュー。Main寄せを優先する場合はD-017再審議を別途行う。
2. 代表21キーの5×4＋1を**評価候補**として使うか判断。最終18＋3配列が必要なら
   100 mm条件と両立する別のstagger/thumb配置を指定してから設計を更新する。
3. 確定ピッチは後の実測/G2判断。今回16/17両方を提供し、製品ピッチは選定していない。
4. 後続でNPTH/keepoutをnative PCBに反映し、機構/治具・footprint/手はんだレビュー、
   2層配線/独立DRC、その後にfull-load・ハーネス・磁気/アナログ実測を行う。

Main設計と既存決定文書は変更していない。`hardware/layout/**`は消費していない。
Draft PRまで。マージ・発注・製造承認は本Issueでは行わない。
