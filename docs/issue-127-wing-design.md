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
| `representative21` / `Representative16` | 16 mm | **110×100 mm（100×100不適合）** | 21 / 3 / 24 / 1 / 15 |
| `representative21` / `Representative17` | 17 mm | **116.5×104.75 mm（100×100不適合）** | 21 / 3 / 24 / 1 / 15 |
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
全6構成でこの予約領域が各基板の外形内に入る。代表21キー基板自体は100 mmを超える。これはtop-entryの上方引出しを
仮定した予約であり、曲げ半径・高さ・ラッチ操作・実ハーネスの機構保証ではない。
[JST資料](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf)と承認済みnativeモデルを根拠にした。

## 代表21キー候補とfull-loadの区別

**2026-11-04 フォローアップで旧5×4＋thumb1（98×98 mm）を superseded とし、
Piantor の片側3行×6列＋親指3キーに置き換えた。旧候補の生成物は現行ファイルで置換した。**
現行の座標出所・寸法実測・不適合は末尾のフォローアップ節を参照。
代表配置のソース順（3行row-major、最後にthumb3）をA/B/Cへラウンドロビンで配り、
各MUXに7入力を割り当てる。21 rawのネット・BOM・凍結GH14接続は変更しない。
G0Bの磁気3×3比較への代用はしない。

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

初回候補の検証結果（今回の差分の検証は末尾）: 6バリアントのdry build成功、3テストメソッド（6構成を反復）成功。
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
2. Piantor代表21キーは両ピッチで100×100 mmに不適合。Piantor配置を維持して寸法要件を
   見直すか、配置側の変更を明示的に許可するかをPOが判断する。勝手な圧縮は行わない。
3. 確定ピッチは後の実測/G2判断。今回16/17両方を提供し、製品ピッチは選定していない。
4. 後続でNPTH/keepoutをnative PCBに反映し、機構/治具・footprint/手はんだレビュー、
   2層配線/独立DRC、その後にfull-load・ハーネス・磁気/アナログ実測を行う。

Main設計と既存決定文書は変更していない。初回候補では`hardware/layout/**`を消費していなかった。
今回の明示的なPiantor基礎データ指定に基づく取り込みの範囲は以下に記録する。
Draft PRまで。マージ・発注・製造承認は本Issueでは行わない。


## フォローアップ — Piantor 配置への置換（2026-11-04）

### 座標の出所と変換

基礎は既存の[幾何記録](layout-geometry.md)、[D-001](decisions.md#d-001---one-piece-geometry)、
および `hardware/layout/layout_source.json` に記録された具体的なキー中心座標。
取り込み元はコミット `6a835825a686ef8cba63d8e52bbc9f0700e1ecde`、
ファイルblob `3c62900c0d60a69a761b05930ec06844373c169d`。
左側21点を一切補間せず [`piantor_left21.json`](../hardware/jitx/wing/piantor_left21.json) に転記した。
上流はQMK `d9f6dd215f2c4d295c6ad85b1f602125c2d81db1` の
`keyboards/cantor/keyboard.json`、`LAYOUT_split_3x6_3`。
元記録はPiantor相当パス `keyboards/beekeeb/piantor/keyboard.json` とblobも保持している。
今回はrepo内の記録を使用し、上流の最新版やPCBとの再照合は行っていない。
QMK由来の21座標はGPL-2.0-onlyのまま出所とライセンスを同梱し、project-ownedとして再許諾しない。

D-015および初回指示には `hardware/layout/**` 消費禁止があるが、今回のPO指示は
repo既存のPiantorキー中心を正とすることを明示しているため、**この評価用代表Wingに限り**
既存座標を出所付きで取り込んだ。決定文書は変更せず、製品採用のsource approvalは未解決のまま。
生成処理はWing内のスナップショットのみを読み、`hardware/layout/**`への実行時依存はない。

ソースの列スタッガは各行 `(0.25,0.25,0.125,0,0.125,0.25)` uに行番号を加算。
親指3点は `(3.5,3.25), (4.5,3.5), (5.5,3.75)` u。
ピッチをpとして `X=(source_x−2.75)p`, `Y=(1.875−source_y)p+9` mm。
これは単位変換・Y軸の反転・平行移動のみで、列間隔も親指クラスタも圧縮していない。
D-001の±30°は一体型左右フィールド間の姿勢であり、片側Wingでは適用しない。
既存幾何記録も列スタッガと一体型回転・gapを独立パラメータとしている。
全センサの `source_key_id`, `source_x_u`, `source_y_u` をdefinitionへ記録した。

### 外形の実測と100×100 mm要件

生成した `definition.json` の外形4頂点の `max−min` を測定した設計値（実物測定ではない）。
採用外形は1ピッチセルの外接に各辺3 mm、下辺側に電装用18 mmを加えた矩形。
セルは既存と同じ設計仮定で、実スイッチ/キーキャップCADの保証寸法ではない。
この外形選択は評価入力であり、最小可能外形や製造承認を主張しない。

| ピッチ | キー中心の外接 | 1ピッチセル外接 | 生成外形の実測 W×H | 100×100適合 | W/H超過 |
| --- | --- | --- | --- | --- | --- |
| 16.0 mm | 88×60 mm | 104×76 mm | **110×100 mm** | **満たさない** | **10 / 0 mm** |
| 17.0 mm | 93.5×63.75 mm | 110.5×80.75 mm | **116.5×104.75 mm** | **満たさない** | **16.5 / 4.75 mm** |

100 mmに収めるための圧縮・スタッガ変更・親指位置変更はしていない。
1ピッチセルを保持する前提では電装帯や基板余白を削るだけでも幅が超過する。
PO判断は、(a) Piantor配置を維持して100×100要件を見直す、または
(b)100×100を維持するため配置/セル/機構前提の変更を別途明示承認する、のいずれか。
製品ピッチの選定も別判断であり、16 mmだけを合格扱いしない。
`WingFabRules`の100 mm制限は維持しているため代表21キーはその制約にも不適合。
この差分を製造可能・配線済み・fab検証合格と解釈しない。

MUXは下端から10 mmのサービス帯にX=`0,14,28` mmで配置、GHは左端から18 mm・下端から10 mm。
制御TPは上端から3 mm。取付穴は既存と同じ端から3 mm/φ2.2/φ5予約で外形に追従する。
下流ではNPTH/keepout反映と機構・手はんだ・2層配線評価が必要。
`load21`は代表形状から独立した3×3＋12 Hall-onlyの電気負荷用なので、定義と生成物を維持した。
`pitch9`の定義/全生成物、Stage 1文書、Main設計、既存決定文書は変更していない。

### 今回の検証

固定lockのJITX 4.4.3 / jitxlib-standard 4.4.0で4テストメソッド成功（17.4秒）。
6構成のnative接続・NC・部品数に加え、Piantor全21点の全ペアで相対X/Yを確認。
両ピッチで実ランドの部品間重複0、外形から0.5 mm内側への包含、取付穴φ5予約との非干渉、
ケーブルアクセス領域の包含を確認した。代表21キーの寸法不適合はテストでも明示的に確認し、
従来の「全構成100 mm以内」という判定を残していない。

`Representative16` / `Representative17`のnative JITX dry build成功。
dry buildは100 mm fab制約を満たす証拠ではない。runtime build、配線、DRC、製造出力は未検証。
`python3 -m wing.export --check`で全6構成の再生成一致、Ruff check/formatと
`git diff --check`成功。代表両ピッチのplacement/nets/bom/definition/svgは再生成済みで、
電気接続・MPN・リファレンスを保持したためnets.csvとbom.csvは既存とバイト一致する。

取り込んだ21点は元コミットの左側キー配列と完全一致することを別途照合した。
`git diff --exit-code`で `pitch9` / `load21` の全生成物、Stage 1文書、
Main設計、`hardware/rev-m1`、`hardware/layout`、既存決定文書の差分なしを確認。
外形表は生成JSONの頂点から直接計算し、宣言済みwidth/height値のみを転載したものではない。
再測定例（`hardware/jitx`で実行）:

```sh
python3 - <<'PYMEASURE'
import json
from pathlib import Path
for pitch in (16, 17):
    d = json.loads(Path(f"wing/generated/representative21-{pitch}mm/definition.json").read_text())
    xs, ys = zip(*d["outline_mm"])
    w, h = max(xs)-min(xs), max(ys)-min(ys)
    print(pitch, w, h, "fits:", w <= 100 and h <= 100,
          "excess:", max(0, w-100), max(0, h-100))
PYMEASURE
```
