# 無線Wing基板 見積ハンドオフ — Issue #299 / Stage 3

**DRAFT / NOT FOR ORDER.** 見積は PMO が行う。この作業では業者へアップロード・見積・注文していない。

- 製造パッケージ：`hardware/kicad/qualification/issue-299-wwing/manufacturing/`（Gerber一式＋ドリルは `gerber/<バリアント>/` と `wwing-<バリアント>-gerber.zip`、`BOM-jlcpcb.csv`、`CPL-jlcpcb-gerber-frame-<バリアント>.csv`、`FABRICATION.md`）。native PCB/回路図は同ツリーの `<バリアント>/wwing-<バリアント>.kicad_pcb` / `.kicad_sch` / `.kicad_pro`。基板 SHA-256（2026-11-21 検証、Codex 再レビューの M1 表と一致）：
  - 16L `5a7003167b50b147ed0ecb7b6972c53f840556ffd3efd520e64d4cd6fffd711c`
  - 16R `d7ec349e6b2aa4eeb2a711b8dc85ed4ffe28185cf1cb297ab62cabbacd69de44`（Fly notch 後、2026-11-21）
  - 17L `a6aa72a1df2848aa6ecd7e14645887bf59784d07af18a04ed75234b652907a03`
  - 17R `5e62589c6cbb51521ebb6b6077e94833c63d644bc5db12aeb9bc8b934743572a`（Fly notch 後、2026-11-21）
- 基板は4バリアントとも **2層・1.2mm**（16mm系 外形 117.3×118.43mm、17mm系 123.3×122.43mm、Issue #296 角トリム後）。最小幅/間隔 0.10/0.10mm、電源配線 0.30mm、via 0.60/0.30mm、銅箔 1oz。仕上げは PMO/業者が確定する。
- via 数は 231/253/232/255（16L/16R/17L/17R）、NPTH は各基板 46個（φ1.7 ×42＋φ2.2 ×4）。via–pad（異ネット）最小間隔は **0.100/0.1016/0.100/0.1052mm**（全て 0.10mm 下限以上）。異ネット via の pad 重なりなし → **POFV 不要**・通常 tenting を見積候補とし、業者 DFM を確認する。同ネットの via-on-pad 接合（GND ステッチ）あり（意図した接合）。
- **DFM 注意項目（開示）**：異ネット間隔が 0.10mm 規格を下回る graze が2バリアントにある。16R は10組・最悪 **0.082886mm**、17L は9組・最悪 **0.090410mm**（いずれも route2 のグリッド丸め級、REPORT に座標付きで記録）。16L/17R はなし。採用ゲートで PO 判断項目として扱い、発注準備時に業者 DFM で確認する。
- BOM は4バリアント共通で **実装49箇所／4 MPNグループ**。TMAG5253BA3IQDMRR ×21 = **C22401868**（文字どおりの型番で発注すること。BA1/BA2/BA4 等の感度違いと自動置換しない）、TMUX1208PWR ×3 = C494728、100nF ×24 = C45000、FH12-14S-0.5SH(55) ×1 = C5378715。TP 15点・NPTH は BOM/CPL から除外。手付け部品なし。
- 実装は **裏面（B.Cu 面）のみ**（反転実装の設計どおり）。CPL は **Gerber 座標系**（Mid X = KiCad X、Mid Y = −KiCad Y、Layer bottom、回転は KiCad 角度そのまま）。X2SON-4 の pin1（VCC）向きと FH12 の向きを業者 preview で照合する。
- TMAG5253BA3 在庫の再観測（2026-11-21、公開 web のみ）：LCSC は **InStock**（$0.4214）。JLCPCB の数値在庫は公開経路では取得できず（jlcsearch 索引は在庫数値なし）、最後の数値観測は **2,981個**（2026-11-19 見積画面）と 1,126個（Stage 1、同日）。4バリアント1セットで **84個**、全20枚ランで **420個**（10倍 = 4,200個）が必要で、最後の数値観測では10倍ルールを下回る pacing 項目のまま。見積時に JLCPCB 側で数値在庫を再確認すること。TMUX1208PWR は LCSC InStock（$0.3008）、FH12 は LCSC InStock（$0.5203、最後の数値 3,907個・2026-11-17）。
- Gate 5 の遠端 VCC 値はモデル出力であり測定保証ではない（`../REPORT.md` の Stage-3 errata にソルバの注意点あり）。
- 旧 Wing Rev.6（有線）の価格・条件を本基板に流用しない。センサー評価実測と X2SON 実装歩留まり確認（D-049 条件）は製造 GO とは別の PO 判断。
