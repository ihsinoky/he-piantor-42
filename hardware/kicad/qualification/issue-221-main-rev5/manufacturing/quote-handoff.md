# Main Rev.5 再見積ハンドオフ — Issue #221

提出用データは生成・検証済み。D-035は**提案**であり、発注対象の正式切替・製造GOはPOゲート。
見積依頼・業者アップロード・カート投入・注文・支払いはしていない。

- 製造ZIP：[main-rev5-fabrication-review.zip](main-rev5-fabrication-review.zip)。
  4銅層・両面mask/silk・外形のGerber9枚＋PTH/NPTH drill2個、合計11ファイル。
  ステンシルは `paste/` 別添。BOM/CPL・CAM画像・本書はZIPに混ぜない。
- native PCB/projectは `../inspection/final/main.kicad_pcb` / `.kicad_pro`、回路図は `../schematic/main.kicad_sch`。
  Rev.4の古いZIPと混用しない。各生成元hashとCAM読戻しは `../export-provenance.json` / `../cam-check.json`。
- 三角形の外形・3穴はRev.4から不変。保存済みGerberの外接寸法は **75.785365×65.632051mm**、
  実面積約2486.974443mm²。寸法は線中心で算出し、見積では外接寸法を使用する。
  4層・1.2mm、最小幅/間隔0.10/0.10mm、via0.60/0.30mm、In1 GND。
  銅厚・積層・仕上げ・DFM受入れはPMO/業者が確定する。
- via130、φ2.2 NPTH3、部品PTH/slotなし。全30,160 via–pad組の銅外縁間隔最小0.145mm。
  viaと両面pasteの重なり0。POFVなし・通常tentingを候補とし、業者DFMで確認する。
- [BOM.csv](BOM.csv) / [CPL.csv](CPL.csv) は実装55箇所。TP1–TP4・穴を除外。
  全59電気部品の台帳は `../main-bom.csv`。発注用座標候補は
  [CPL-jlcpcb-gerber-frame.csv](CPL-jlcpcb-gerber-frame.csv) と[フレーム注記](CPL-jlcpcb-gerber-frame-NOTES.md)。
  CPL.csvはX=KiCadX−62.107317799、Y=137.9−KiCadY。GerberフレームはX=KiCadX、Y=−KiCadY。
- **J4のみ Molex 781710004 / LCSC C588524**。JLCPCB掲載はExtended、SMT Assembly、Economic/Standard。
  正式なMolex指定品を使い、互換品への自動置換はしない。在庫・工程・モデル受入れはPMO確認。
  上面180°、原点(100,90)、pin1中心(101.8,91.875)mm。J2/J3を含めpin1・回転を業者previewで照合する。
  VBUS/GNDは0.60mm幅でランドから出し、本体外のY=92.65mmで1.10mmへ拡幅。F.Cu非推奨領域への侵入0。
  Molex図面781710000-SD Aの信号ランド0.60×0.85mm、pitch1.20mm、補強0.70×0.80mm。
  図面の参考条件はPCB1.0mm・stencil0.1mm・開口100%。本基板は承認済み1.2mmを保持し、ステンシル条件は業者確認。
- C25=C1525、R3/R4=27Ωを継承。C26–C28/R17などLCSC空欄は元MPNを保つ要調達確認項目。
  見積時の代替提案と設計BOMの正式変更を区別する。
- PO在庫は **Geon × Wolf Fly DBと同梱EZmate↔EZmate 170mmケーブル**。旧C3/SHハーネスを手配対象にしない。
  [POの追加確認](https://github.com/ihsinoky/he-piantor-42/issues/221#issuecomment-6750942420)どおり、付属ケーブルで直接接続し、EZmateケーブルの別途調達は不要。
  FlyをMain BOMへ二重計上せず、別途GH14 1:1 200mm×2本を計上する。
  挿抜10回級の内部接続用途。基板外への機構・嵌合高さ・曲げ半径は組立確認が必要。
- 電源モデル：125℃・実配線幅−20%で入力VBUS4.788mΩ、GND43.898mΩ、往復48.686mΩ。
  Rev.4比+3.776mΩ（500mA時+1.888mV）。下流共通37.109mΩ、J2分岐3.473mΩ、J3分岐28.230mΩ。
  GH各導体200mm/0.0804mm²以上・各接触50mΩ・6帰線・各Wing127mAの条件で最遠点4.797986Vを維持。
  35µm銅/20µmめっき/積層は抽出仮定であり、完成品の実測保証ではない。
  Flyヒューズ/ケーブル/接点の完成上流抵抗・効率・USB許容電流は要確認。
  効率75%の感度条件はRev.4から引き続き500mA予算を超えるため、上流を無条件合格にしない。

## 初回通電前の必須チェック（PMO判断）

[PMOコメント](https://github.com/ihsinoky/he-piantor-42/issues/221#issuecomment-6750886847)に従う。
**Mainへまだ接続せず**、Fly DB単体をUSB電源につなぎ、同梱ケーブル先端の
端子1（VBUS）と端子4（GND）の間で **+5Vの極性**を実測する。
GND基準で端子1=5V／端子4=0Vを確認・記録してから電源を切り、Mainへ接続する。
線色を根拠にせず、端子番号と観察面を写真/測定記録に残す。異常なら接続・通電しない。
初回接続後にUSB認識を確認し、D+/D−取り違えが実証された場合のみRev.5.1で是正する。
本作業では実物測定を実施していない。これらは組立時の未実施ゲートであり、完了したとは扱わない。

旧Rev.3/Rev.4の価格を本Rev.5へ流用しない。部品変更・実装工程・GHハーネス・在庫Flyを含めPMOが再見積する。
