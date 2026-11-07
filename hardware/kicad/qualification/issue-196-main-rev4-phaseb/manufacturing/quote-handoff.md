# Main Rev.4 再見積ハンドオフ — Issue #196 / PR #197

再見積は PMO が行う。この作業では業者へアップロード・見積・注文していない。

- 製造ZIP：`hardware/kicad/qualification/issue-196-main-rev4-phaseb/manufacturing/main-rev4-fabrication-review.zip`。4銅層・両面mask/silk・外形のGerber 9枚＋PTH/NPTH drill 2個（11ファイル）。paste、BOM/CPL、CAM画像は別添。
- native PCB/project：同証跡ディレクトリの `inspection/final/main.kicad_pcb` / `.kicad_pro`。回路図：`schematic/main.kicad_sch`。
- 基板は**三角形、外接75.785364×65.632051mm**、実面積2486.974443mm²。見積入力は実面積から矩形換算せず外接寸法を使う。4層・1.2mm、D-019の最小幅/間隔0.10/0.10mm、via0.60/0.30mm、In1 GND。仕上げ・銅厚・積層はPMO/業者が確定する。
- via130個、φ2.2 NPTH 3個、Main上の部品PTH/slotなし。全via–全pad銅間隔最小0.145mm、viaの両面paste重なり0。POFVなし・通常tentingを見積候補とし、業者DFMを確認する。
- `BOM.csv` / `CPL.csv` は**実装55箇所**。TP1–TP4と穴は除外。全59電気部品の台帳は `../main-bom.csv`。CPLは上面、X=KiCadX−62.107317799、Y=137.9−KiCadY、native角度。特に斜辺J2/J3と180°のJ4のpin1/部品回転を業者previewで照合する。
- J4：JST **SM04B-SRSS-TB(LF)(SN)**、LCSC **C160404**。根拠：[LCSC部品ページ](https://www.lcsc.com/product-detail/C160404.html)。同名のSR/SZ・代替品と自動置換しない。C3の実footprintと同型番を採用。JLCPCBの利用工程・在庫・実装受入れはPMOが確認する。
- C25はPhase A-2入力の訂正済み台帳どおりSamsung CL05B104KO5NNNC / **C1525**。R3/R4（27Ω）は保持。C26–C28 / R17などコード空欄は元MPNを保持した要調達確認項目で、勝手に代替しない。見積時代替と基板BOMの正式変更を区別する。
- MainからJ1 USB-C、R1/R2 CC、U2 ESDを除去。PO在庫UDB C3とSH 4芯1:1ハーネス候補100mmをMain BOMへ二重計上しない。別途GH14 1:1 **200mm×2本**を計上する。100mm GH契約は本Rev.4には適用しない。
- 電源合格はGH導体断面0.0804mm²（AWG28相当）以上、各接触50mΩ以下、6帰線等分のモデル条件。完成200mmハーネスの導通・抵抗、SH/C3 PTCを含む上流電圧/電流予算、最大嵌合高さ・曲げ半径は組立確認が必要。未知の細線ハーネスへ計算値を流用しない。
- 旧Rev.3の$122.29をRev.4の価格としない。外接面積はほぼ倍、実装数減・JST追加・延長ハーネス・在庫C3を含めて再見積する。PCB製造適合の検算と製造GO/実機認定は別。
