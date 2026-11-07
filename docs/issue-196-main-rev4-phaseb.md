# Issue #196 Phase B — Main Rev.4 配線・製造データ・再見積準備

**Main Rev.4 の全面配線と製造パッケージを作成した。** 最終40ネットの独立4指標はすべて0、native DRCの違反・未接続も0。全130 viaの全パッド銅間隔は最小 **0.145mm**。200mm GHハーネスを明示した127mA/Wingモデルでは最遠点 **4.797985V**、共通・両分岐は50mΩ以下となった。D-033は採択前の草案であり、再見積はPMOへ引き継ぐ。

指示書 `.issue196-runtime/instructions-196-phaseB.md` を全文読了した。同じ作業コピー `.issue196-runtime/git`、ブランチ `issue-196-main-rev4`（PR #197）で実施。起点はPhase A-2コミット `d07b7ea`。スクラッチ・TMPDIR・XDGは `.issue196-runtime/`、既設ランタイムは読み取り使用した。pushはPMOが行う。

以下 E は [Phase B証跡ディレクトリ](../hardware/kicad/qualification/issue-196-main-rev4-phaseb/README.md) を指す。

## native設計と配線

最終PCB/projectは E/inspection/final/main.kicad_pcb / main.kicad_pro、回路図とnative XML netlistは E/schematic/。基板SHA256は `b361a5a010a3ae2b08e5858735d46a5662112af4241ef55bab50d1ba3187b123`。

Phase A-2 `geometry-plan.json` の全59電気部品のXY・回転、三角形外形、3穴をそのまま実装した。J1/R1/R2/U2を除去し、C3実footprintのJ4を追加。J4は1=VBUS、2=USB_DM_ESD、3=USB_DP_ESD、4=GNDの1:1、R3/R4の27ΩとD-024の他のpin-netを保持。回路図は配線出力から逆生成せず、#175の論理契約に明示的な4削除・1追加を加えて作成し、全226論理pinをPCBとXMLへ独立照合した。232物理銅パッドとの差は重複番号ランド・機械NC等による。E/design-check.json参照。

旧Rev.3の配線は全廃し、KiCadRoutingToolsで全面自動配線（auto01）、電源pin未接続3件を追加自動配線（auto02）した。auto01は0.13mm間隔、auto02以降の信号逃げはD-019の0.10mmを使用、同ネットvia–pad目標は0.13mmを指定した。条件緩和によって0.10mmを下回る配線はない。ルータのexit 0を合格根拠にしていない。

J2.7/WING_ENにルータが作ったパッド内viaが1個残ったため、同ネットをrip-upして再配線した。全パッドから0.125mm離した局所via移設探索では成立しなかったため、J2.7に0.13mm bufferのnative via専用禁止域を追加した。auto03の固定周辺銅での再配線に続き、auto04で周辺ネットの自動rip-upを許可して成立。コネクタを誤ってBGAと扱う除外域をJ2/J3について無効化した。最終viaは全数パッド外にある。試行ログ・入力・出力をE/runs/、E/processes/に保存した。

初期抽出ではPGNDが遠方のviaまで細線でつながり、共通抵抗が約187mΩで不合格だった。U6近傍 **(97.075,103.15)mm** にGND viaを追加し、既存GNDへstub接続した。V5V2/HALL_5V/VBUS/GNDの554 segmentを、他ネット・穴予約・外形から実際に許される幅へ自動拡幅した（最大2mm、0.025mm刻み、間隔0.10005mm・端0.20005mmを計算上確保）。部品移動なし、銅箔の削除なし。E/runs/power01/changes.jsonに全変更を記録した。

最終は **1135 segment、130 via、4層1.2mm、信号最小幅0.10mm、via0.60/0.30mm**。In1.CuはGND plane専用、信号track0。3穴の全銅層予約はφ5.0004mmを外接する多角形、実銅箔・ベタ・padも独立検査済み。PCB外接 **75.785364×65.632051mm**、実面積2486.974443mm²。62 footprint（59電気部品＋3穴）。

## 最終の独立4指標

| 指標 | 結果 |
| --- | ---: |
| 必須未接続 | 0 |
| 異ネット接触（NCパッド含む） | 0 |
| 物的違反 | 0 |
| 説明不能な転送差分 | 0 |

E/inspection/final/assessment.json、connectivity.json、transfer-diff.json。40ネットについて全pad/track/viaの層と実fillの外周・穴を使う実銅箔union-findで確認。native DRCは違反0・未接続0で、印刷警告の除外にも依存していない。転送照合はfill cacheだけを除き、部品・pin-net・外形・zone規則等の全ASTを入力と照合する。全配線の新規作成・拡幅は明示的な許可差分。追加via禁止域は入力側にも記録し、Duplicateが発行した参照側UUIDの整合修正もE/input-revisions.jsonに残した。

元データのステンシル開口は多くが基板側の図形である。配線用基板を作る際に外形とともにいったん除去した後、保持部品の元パッドを含む図形を207個、新しい部品の剛体変換で復元した。廃止部品の30図形は除去。斜辺GHの長方形は回転を正しく保つpolygonへ変換した。25個のnative paste-padも保持。E/paste-transfer.json、製造CAM照合参照。ステンシル追加前後の**全非paste ASTが完全一致**することをE/copper-equivalence.jsonで証明し、電源抽出を最終hashへ結び付けた。追加後にもDRC・独立グラフ・via・paste・回路検査を実施した。

## 電源再検証 — 200mm前提

#165/#175のモデルを更新した。正側は実segment幅・via・padの抵抗網、GNDは実plane/thermal/track/pad/barrelのDC sheet FEM。35µm銅・20µm barrelを仮定、125°C、track幅−20%、PGND=U6.10、各GHの6 GND接点を使用した。USB入力境界は旧J1から**Main J4**へ変更。E/power-extraction-final.json、ground-extraction-final.json、resistance-summary.json参照。

| 経路 | 正側 mΩ | GND mΩ | 往復 mΩ |
| --- | ---: | ---: | ---: |
| J4入力→U6（50mΩ目標とは別） | 3.010 | 41.901 | 44.910 |
| Main共通 | 31.965 | 5.149 | **37.114** |
| J2分岐 | 1.594 | 1.877 | **3.471** |
| J3分岐 | 25.804 | 2.423 | **28.227** |

共通・両分岐とも≤50mΩ。GND meshは最大三角形面積0.03/0.0075mm²で確認、幅−20%の共通GND成分の差は約3.3%（Main共通往復の約0.5%）。解析矩形、相反性、重ね合わせ、KCLを検証し最大KCL残差1.91nA。最初の細meshで接点hubの数値桁落ちによる1µA基準超過を検出したため、long-double残差による反復改善を追加し、基準を緩めず解消した。製造銅厚や電流分担の保証値ではない。

### ハーネス導体の実経路

採用長を**各導体200mm**として、往路1本と6本の各帰路すべてにその長さを与えた。Phase A-2の17mm折れ線156.341mmに43.659mmの曲げ・Z経路・長さ余裕を含む電気導体長であり、113.018mmのコネクタ間直線へ短縮しない。実装上の曲げ半径・高さの認定は別。

#165の導体条件（銅抵抗率20°Cで1.7241×10⁻⁸Ωm、断面0.0804mm²＝AWG28相当、温度係数0.00393/K）を継承する。これは**完成ハーネスが満たすべき調達条件**であり、不明な線径を測定済みと扱わない。

```text
Rwire(T) = ρ20 × 0.200m / (0.0804×10⁻⁶m²) × [1+0.00393(T−20)]
Rharness = (Rwire + 2×Rcontact) × (1+1/6)
125°C: Rwire=60.585818mΩ/線、Rcontact=50mΩ/接点
Rharness=187.350120mΩ（往復）、127mAで降下23.793465mV
```

最悪17mm Wing、125°C・幅−20%、127mA/Wing、両Wing同時給電：

```text
Vfar = 5.2×0.98 − 0.050
       − 2×0.127×(Rcommon + 0.25Ω U5 Ron)
       − 0.127×(Rbranch + Rharness) − 0.147710145V Wing内降下
J3: 4.797984555V ≥ 4.60V（余裕197.985mV）
```

16/17mm、20/125°C、幅100/80%、127/231.0081/278mA、6/1帰線、両枝の全96条件はE/power-sensitivity.csv。1帰線集中の設計負荷感度も最悪4.780989Vだが、断線運転の認定ではない。設計負荷とストレス負荷を混同しない。Wing内147.710145mVは#165/#175が使う#141の分布負荷抽出を継承しており、今後のWing Rev.2全面配線には新抽出が必要。

UDB C3のPTC・SH候補100mm・接点は**5.2Vの上流損失**であり、200mm GH損失に混ぜない。上流を0.25/0.5/1.0Ω、効率75–95%、Main別負荷110mAの仮予約で掃引した。USB4.75V・効率80%なら、上流0.5ΩでU6入力4.485480V／USB485.438mA、1.0Ωでは4.217871V／509.258mAとなり500mAを超える。完成C3/SHの抵抗、効率下限、Main実負荷、USB許可制御は未実測で、全組立条件の電流保証は主張しない。E/power-budget.json参照。

## via全数検査

#183と同じnative effective copper shape測定で、**全130 via × 全232銅パッド**を共通銅層について検査。同ネット・TPを免除せず、via annulus外周からpad銅までの最短距離を評価した。NPTH3個はpad銅から除外し、穴予約を別検査。E/inspection/final/audit/via-pad/に全数JSON/CSV・pad形状、E/via-distribution.jsonに分布を保存した。

最小 **0.145000mm**、中央値0.234731mm、95 percentile 0.925000mm、最大1.908845mm。0.10mm未満0、目標0.125mm未満0、中心/drill/annulus重なり0。via銅円・drill円と両面pasteの重なりも0。

| 各viaの最近傍pad間隔 mm（下限含む・上限含まない） | 個数 |
| --- | ---: |
| 0.100–0.125 | 0 |
| 0.125–0.150 | 1 |
| 0.150–0.200 | 22 |
| 0.200–0.300 | 63 |
| 0.300–0.500 | 24 |
| 0.500–1.000 | 13 |
| 1.000以上 | 7 |

## 製造データと再見積

E/manufacturing/にGerber 4銅層・両mask/silk・外形、PTH130 via／NPTH3穴のExcellon、両面paste、BOM/CPL、fabrication-only ZIP、CAM画像を作成した。実装55箇所、TP4個・穴3個はBOM/CPLから除外。CPL原点は外接左下（KiCad 62.107317799,137.9）、上面native角度。GH斜辺・J4のpin1は業者previewでも確認する。

Gerbonaraの独立CAM照合は、全銅層の全track/via/pad、実GND fill（対称差0）、穴予約、外形、drill、mask、paste polygon（対称差0）、BOM/CPLとZIP内容を通過。非直交矩形のGerbonara bboxに符号付き三角関数の誤りを検出し、デコードされた矩形primitiveから絶対値付きcos/sinでbboxを独立再計算した。drillは0.001mm出力量子化を明示して照合。CAM contact sheetを目視し、三角形GNDと3穴予約、斜辺GH、北側J4、部品pasteを確認した。E/cam-check.json参照。

J4は **SM04B-SRSS-TB(LF)(SN) / C160404** を特定して記入した（[LCSC一次部品情報](https://www.lcsc.com/product-detail/C160404.html)）。C25は訂正済みSamsung CL05B104KO5NNNC / C1525を継承。コード未確定はC26–C28とR17で、MPNを保持し要調達確認とした。R3/R4の27Ωは保持。業者の自動代替を正式BOM改訂と扱わない。

再見積に必要な場所・外接寸法・実装数・BOM注意点・CPL変換・UDB別勘定を **[quote-handoff.md](../hardware/kicad/qualification/issue-196-main-rev4-phaseb/manufacturing/quote-handoff.md)** に集約した。外接面積はRev.3のほぼ倍なので、旧$122.29を新価格へ流用しない。業者へのアップロード、見積取得、発注は行っていない。

## D-033草案と未決事項

[decisions.mdのD-033](decisions.md#d-033---main-rev4-triangular-baseline-and-separated-udb-draft)へ、三角形・UDB分離・3穴・200mm GH×2・**D-017の100mm長をRev.4ではsupersede**する草案を追加した。D-024の電気骨格・D-019は継承、旧矩形/4穴/オンボードUSB方針はRev.4用に置き換える。旧成果物・過去の資格は上書きしない。[project-status.md](project-status.md)の改訂表と履歴にRev.4行を追加した。

残る事項はPMOの草案採択・再見積、業者DFM/stackup/銅厚/通常tenting受入れ、未確定BOM調達、C3/SH/GHの完成抵抗と1:1 pin順、GH上面嵌合高さ・200mm配索・曲げ半径、ケース南辺/Wing角逃げ・UDB固定、USB信号品質、スイッチング/ADCノイズ・起動/過渡・実負荷/効率/USB電流制御の実機確認。silkはnative footprintの現状を出力し、部品参照名の全面印刷整備を完了したとはしない。これらは製造GOや動作保証の別ゲートであり、今回のDRC・抵抗モデル合格と混同しない。

検証の入口は E/verify.py、結果はE/verification.json。成果物を同ブランチにコミットし、pushはPMOへ委ねる。

**Phase B の実施・成果物コミットまで完了。ここで停止する。**
