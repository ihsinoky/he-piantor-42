# 無線Matrix評価基板 見積ハンドオフ — Issue #288 / Draft PR #289

**DRAFT / NOT FOR ORDER.** 見積は PMO が行う。この作業では業者へアップロード・見積・注文していない。

- 製造パッケージ：`hardware/kicad/qualification/issue-288-wmatrix/manufacturing/`（Gerber一式＋PTH/NPTHドリル、`BOM-jlcpcb.csv`、`CPL-jlcpcb-gerber-frame.csv`、`FABRICATION.md`）。native PCB/回路図は同ツリーの `wmatrix.kicad_pcb` / `wmatrix.kicad_sch` / `wmatrix.kicad_pro`。基板 SHA-256：`5baf83c84f938b4acd787bd2694bd3b6434984dcc2c31410396b3081a113d6e7`。
- 基板は **128×80mm・2層・1.2mm**（外形は Matrix Rev.3 から不変）。最小幅/間隔 0.10/0.10mm、電源配線 0.30mm、via 0.60/0.30mm、銅箔 1oz。仕上げは PMO/業者が確定する。
- via 389個、φ2.2 NPTH 4個。via–pad（異ネット）最小間隔 **0.1002mm**（0.10mm 下限以上、0.125mm 目標未満の箇所14件は `../via-audit-s2/via-pad-diffnet.json` に座標付きで開示）。同ネットの via-on-pad 接合あり（意図した接合）。**POFV 不要**・通常 tenting を見積候補とし、業者 DFM を確認する。
- BOM は **実装54箇所／12 MPNグループ**。TMAG5253BA3IQDMRR ×18 = **C22401868**（文字どおりの型番で発注すること。BA2/BA4 等の感度違いと自動置換しない）。TMUX1208PWR ×3 = C494728。TP 25点・NPTH・U_XIAO・J_BATT は BOM/CPL から除外（後述）。
- CPL は **Gerber 座標系**（Mid X = KiCad X、Mid Y = −KiCad Y、上面、回転は KiCad 角度そのまま）。X2SON-4 の pin1（VCC）向きと USB-C の回転を業者 preview で照合する。
- **手付け部品（PCBA 対象外）**：Seeed XIAO nRF52840（U_XIAO、ソケット footprint のみ実装しモジュールは手差し）、電池コネクタ J_BATT（JST B2B-XH-A (LF)(SN)）— LCSC コードがパッケージ時点で検証できなかったため、未検証コードを BOM に載せず手付け扱いとした。見積時にコード確定できれば PCBA へ移してよい。
- 電源：USB-C（ベンチ給電）と NiMH パック入力は同一ノード VIN_SRC（同時接続禁止、基板シルクと REPORT に明記）。AP2112K-3.3 の専用 Hall レール HALL_3V3 はバースト最悪条件（18センサ全ON 90mA＋MUX＋分圧）でも電圧降下 **最悪 16.83mV**（配線幅 −20% ケース、予算 50mV）。根拠は `../rail-droop-s2.json`。
- TMAG5253BA3 在庫の再観測（2026-11-19、パッケージ時点）：LCSC/JLCPCB の数値在庫は取得経路から得られなかった（検索では製品ページに到達せず、tscircuit の JLCPCB ライブラリ索引 jlcsearch では該当品は価格表あり・在庫数値なし＝Global Sourcing 扱い）。最後の数値観測は Stage 1 の **1,126個**（2026-11-19）で、1枚あたり必要数18個の10倍（180個）を大きく上回る。見積時に JLCPCB 側で在庫を再確認すること。
- 旧 Matrix Rev.3/Rev.4 の価格・条件を本基板に流用しない。センサー評価実測と X2SON 実装歩留まり確認（D-049 条件）は製造 GO とは別の PO 判断。
