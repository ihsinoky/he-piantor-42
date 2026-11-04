# Issue #124 — Main BOM具体化・Economic PCBA見積もり（5枚）

[Issue #124](https://github.com/ihsinoky/he-piantor-42/issues/124) の調査結果。**49行すべてを抽出し、確定42行（購入部品38行＋基板テストパッド4行）、PO判断ギャップ7行、確定部品の価格未取得0行。取得分部品代は5枚 $23.3810。** ギャップ7行の金額は空欄のまま残した。

**5枚の条件付き計算額は $90.5410（表示 $90.54）、1枚 $18.1082（表示 $18.11）。** 基板 $8.00、取得部品代、Economic PCBA料金、9種Extendedのフィーダー、leadless 10個のX線検査、USB固定脚の手はんだ工程を仮定した計算である。**ギャップ7行の部品代・調達余剰・送料税金などを含む発注総額は未確定であり、この金額を全BOM込みの価格と扱わない。** 金額はUSDのまま、為替換算なし。

機械可読版は [main-bom.csv](../hardware/kicad/qualification/issue-124-main-bom-pcba/main-bom.csv)。各行の出典、公開価格URL、UTC取得日時、数量帯、選定理由・候補はCSVの `source` / `notes` に記録した。[抽出証跡](../hardware/kicad/qualification/issue-124-main-bom-pcba/extraction-evidence.json) と [公開価格証跡](../hardware/kicad/qualification/issue-124-main-bom-pcba/price-evidence.json) を添付する。

## 抽出元・権威・完全性

固定したリポジトリコミットは **`c3450394fb0aee3ab1b3e10f116e21c1ebfeee2c`**（作業開始時 `origin/main` / PR #122 merge後）。以下の全ファイルのSHA256を抽出証跡に記録した。

| 役割 | リポジトリ内のパス |
| --- | --- |
| 49フットプリントの直接抽出元（#121の再充填済み4層基板） | `hardware/kicad/qualification/issue-121-full-auto-conditions/evidence/inspection/main-cell1/krt/main.kicad_pcb` |
| 独立照合した回路図 | `hardware/kicad/qualification/eda-004g/resume-02/evidence/processes/initial-author-schematic/main.kicad_sch` |
| 回路図から生成済みのネットリスト | `hardware/kicad/qualification/eda-004g/resume-02/evidence/processes/initial-netlist/main.xml` |
| native refと元のSourceID・パッケージの対応 | `hardware/kicad/qualification/eda-004g/resume-02/main-contract-v2.json` |
| 電気構成・値・パッケージの元ソース | `hardware/tscircuit/src/qualification/revm1-routing-proof.tsx` の `RepresentativeMain`、strategy 3 |
| USBの固定脚・NPTHを含む元の形状 | `hardware/tscircuit/src/qualification/native-support-footprints.tsx` |

基板の `footprint` 直下の Reference / Value / footprint IDをS式から抽出。回路図の実インスタンスとネットリストをリファレンスで結合し、**49参照の集合、49値、49 footprint IDがすべて一致**した。値の食い違い0行。回路図の `#FLG01` / `#FLG02` は仮想PWR_FLAGで基板部品ではないため除外した。取り違え防止のため、旧 `hardware/sensor-test/bom.csv` の参照番号を転記せず、下表に現基板refとSourceIDの両方を示す。

[抽出スクリプト](../hardware/kicad/qualification/issue-124-main-bom-pcba/extract-design.py) はリポジトリルートから `python3 hardware/kicad/qualification/issue-124-main-bom-pcba/extract-design.py` で実行できる（標準ライブラリのみ、設計ファイルを変更せずJSONを標準出力する）。

対象は既存の**代表配線検証用Main**。元ソース自身が `NON-PRODUCT` としている。#121はこの配置・部品を保存した配線検証であり、製造承認済みMainの新規設計・BOM承認に読み替えない。[#121報告](issue-121-full-auto-conditions.md) の非配線AST不変の記録を追跡した。LED、BOOT/RESET実装スイッチ、Hallセンサ、mux、Wing、ハーネスはこの49行に存在せず、旧基板BOMから補っていない。製品要求との不足は別途設計レビュー対象。

### 「片面・全SMD・199ランド」の実データとの差異

全49フットプリントの配置レイヤは `F.Cu`。一方、`attr smd` だけではパッド種別を表さない。実際のpadノードは次の通りだった。

| padノード | 1枚 | 内容 |
| --- | ---: | --- |
| `smd` | 193 | うちTP1–TP4が4個の裸銅箔パッド |
| `thru_hole` | 4 | J1のシェル固定脚。GND接続、長穴 |
| `np_thru_hole` | 2 | J1の位置決め穴。はんだ接合ではない |
| 全padノード | **199** | 導電ランド197＋NPTH2 |

したがって、**49フットプリント ≠ 購入・搭載49部品**。購入部品は45個/枚（うち7個/枚は未選定）、5枚225個、TP4箇所/枚は購入不要。はんだ工程の幾何上の候補は193箇所/枚（199−NPTH2−裸TP4）、そのうちSMD189、PTH4である。NCパッドや露出パッドの実際の課金接合数はBOM/CPL/工程確認で変わり得る。

J1を「スルーホールゼロ」に合わせて書き換えていない。基板生成スクリプトはすべてのフットプリントに `FP_SMD` を与えつつ、J1の4脚には明示的に `PAD_ATTRIB_PTH` を生成している。これは値不一致ではなく、**PMO前提と物理データの製造ギャップ**。選定済みJ1の型番は確定として残し、USB NPTHとシェル実装工程はPO/製造者確認待ちとした。

## 部品対応付けの根拠・状態の定義

- **確定**：既存の具体型番を現MainのSourceIDへ対応付けた行、またはIssueの優先順位に従い値・サイズ・必要精度が一致する具体受動部品へ対応付けた行。ここでの「確定」は本調査のBOM対応付けを意味し、製造リリースや在庫確保の承認ではない。
- **ギャップ**：POによる仕様/選定判断が必要。CSVの `part_number` / `lcsc` / 金額は空欄。候補MPN・LCSCは `notes` と後述の表だけに置く。候補価格を確定小計へ混ぜない。
- **未取得**：部品対応付けは確定したが公開単価を取得できない場合の排他的な行状態。今回は0行。ギャップ7行は選定未了であり、価格取得失敗7行とは数えない。
- TP1–TP4は元ソースで `footprintVariant="pad"`、直径1.2mmのテストパッド。購入MPN/LCSCは **N/A**、購入数0、部品代0。LCSC番号を創作しない。これは欠落や価格未取得ではなく部品非該当の確定4行。

| 選定済み部分 | 出典 |
| --- | --- |
| U1 RP2040 / C2040、J1 TYPE-C-31-M-12 / C165948、U2 USBLC6-2SC6 / C7519、U3 W25Q16JVUXIQ / C2843335、Y1 ABM8-272-T3 / C20625731、U4 AP2112K-3.3TRG1 / C51118、U5 TPS22919DCKR / C2149796 | [component-sources.md](../hardware/jitx/component-sources.md)、[M1電気ソース](../hardware/tscircuit/src/evaluation/m1-four-key.tsx)。Mainソースで同一MPNを確認。U5はさらに [D-009](decisions.md#d-009---hall-analog-power-rail) の暫定baseline |
| J2 BM14B-GHS-TBT(LF)(SN) / C265384 | [G0B freeze proposal](../hardware/rev-m1/g0b-freeze-proposal.md) のJST GH案・LCSC対応、[D-017](decisions.md#d-017---revm1-mainwing-architecture-and-interface-freeze)、Mainの `JstGh14` |
| 受動部品 | Mainソースの値/サイズ、旧 [sensor-test/bom.csv](../hardware/sensor-test/bom.csv) の1%抵抗・C0G/X7R baselineを参照し、[DFM policy](../hardware/rev-m1/dfm-policy.md) に従いBasic優先。公開ページの `componentLibraryType=base` をBasic、`expand` をExtendedとして記録 |

R3/R4用C25190は公開ページで **Extended**。27Ω・0603・1%を満たす具体型番として対応付けたが、Basicとは記載しない。値やサイズを変えてフィーダー費を削減しない。Basic優先は電気性能を犠牲にしない方針であり、未選定7行もX5Rへ無断置換しない。

## 全49行のBOMと部品代

各購入行は基板1枚で1個、`qty_for_5=5`。単価帯は同一LCSCの5枚合算必要数量で選ぶ（例：C1525は10個/枚→50個、C25804は4個/枚→20個）。各refの小計は単価×5であり、合算型番小計を行ごとに重複計上しない。全価格の取得は2026-11-04 UTC（秒単位はCSV/価格証跡）、価格源は各C番号リンクのJLCPCB公開ページ。

| ref / SourceID | value | footprint / package | 具体MPN / LCSC | 区分 | 単価USD | 5枚必要数 | 小計USD | 状態 |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| C1 / C_XIN | 15pF | `Qualification:C1` / 0402 | 0402CG150J500NT / [C1548](https://jlcpcb.com/partdetail/C1548) | Basic | 0.0026 | 5 | 0.0130 | 確定 |
| C2 / C_XOUT | 15pF | `Qualification:C2` / 0402 | 0402CG150J500NT / [C1548](https://jlcpcb.com/partdetail/C1548) | Basic | 0.0026 | 5 | 0.0130 | 確定 |
| C3 / C_MCU_HF1 | 100nF | `Qualification:C3` / 0402 | CL05B104KO5NNNC / [C1525](https://jlcpcb.com/partdetail/C1525) | Basic | 0.0031 | 5 | 0.0155 | 確定 |
| C4 / C_MCU_HF2 | 100nF | `Qualification:C4` / 0402 | CL05B104KO5NNNC / [C1525](https://jlcpcb.com/partdetail/C1525) | Basic | 0.0031 | 5 | 0.0155 | 確定 |
| C5 / C_MCU_HF3 | 100nF | `Qualification:C5` / 0402 | CL05B104KO5NNNC / [C1525](https://jlcpcb.com/partdetail/C1525) | Basic | 0.0031 | 5 | 0.0155 | 確定 |
| C6 / C_MCU_HF4 | 100nF | `Qualification:C6` / 0402 | CL05B104KO5NNNC / [C1525](https://jlcpcb.com/partdetail/C1525) | Basic | 0.0031 | 5 | 0.0155 | 確定 |
| C7 / C_MCU_HF5 | 100nF | `Qualification:C7` / 0402 | CL05B104KO5NNNC / [C1525](https://jlcpcb.com/partdetail/C1525) | Basic | 0.0031 | 5 | 0.0155 | 確定 |
| C8 / C_MCU_HF6 | 100nF | `Qualification:C8` / 0402 | CL05B104KO5NNNC / [C1525](https://jlcpcb.com/partdetail/C1525) | Basic | 0.0031 | 5 | 0.0155 | 確定 |
| C9 / C_MCU_HF7 | 100nF | `Qualification:C9` / 0402 | CL05B104KO5NNNC / [C1525](https://jlcpcb.com/partdetail/C1525) | Basic | 0.0031 | 5 | 0.0155 | 確定 |
| C10 / C_MCU_HF8 | 100nF | `Qualification:C10` / 0402 | CL05B104KO5NNNC / [C1525](https://jlcpcb.com/partdetail/C1525) | Basic | 0.0031 | 5 | 0.0155 | 確定 |
| C11 / C_MCU_HF9 | 100nF | `Qualification:C11` / 0402 | CL05B104KO5NNNC / [C1525](https://jlcpcb.com/partdetail/C1525) | Basic | 0.0031 | 5 | 0.0155 | 確定 |
| C12 / C_VREG_IN | 1uF | `Qualification:C12` / 0402 | 候補は後述（未選定） | — | — | 5 | — | ギャップ |
| C13 / C_VREG_OUT | 1uF | `Qualification:C13` / 0402 | 候補は後述（未選定） | — | — | 5 | — | ギャップ |
| C14 / C_MCU_BULK | 10uF | `Qualification:C14` / 0805 | 候補は後述（未選定） | — | — | 5 | — | ギャップ |
| C15 / C_FLASH | 100nF | `Qualification:C15` / 0402 | CL05B104KO5NNNC / [C1525](https://jlcpcb.com/partdetail/C1525) | Basic | 0.0031 | 5 | 0.0155 | 確定 |
| C16 / C_LDO_IN | 1uF | `Qualification:C16` / 0603 | 候補は後述（未選定） | — | — | 5 | — | ギャップ |
| C17 / C_LDO_OUT | 1uF | `Qualification:C17` / 0603 | 候補は後述（未選定） | — | — | 5 | — | ギャップ |
| C18 / C_LOAD_IN | 1uF | `Qualification:C18` / 0603 | 候補は後述（未選定） | — | — | 5 | — | ギャップ |
| C19 / C_LOAD_OUT | 1uF | `Qualification:C19` / 0603 | 候補は後述（未選定） | — | — | 5 | — | ギャップ |
| C20 / C_ADC_A | 1nF | `Qualification:C20` / 0402 | 0402B102K500NT / [C1523](https://jlcpcb.com/partdetail/C1523) | Basic | 0.0038 | 5 | 0.0190 | 確定 |
| C21 / C_ADC_B | 1nF | `Qualification:C21` / 0402 | 0402B102K500NT / [C1523](https://jlcpcb.com/partdetail/C1523) | Basic | 0.0038 | 5 | 0.0190 | 確定 |
| C22 / C_ADC_C | 1nF | `Qualification:C22` / 0402 | 0402B102K500NT / [C1523](https://jlcpcb.com/partdetail/C1523) | Basic | 0.0038 | 5 | 0.0190 | 確定 |
| J1 / J_USB | TYPE-C-31-M-12 | `Qualification:J1` / usbFootprint | TYPE-C-31-M-12 / [C165948](https://jlcpcb.com/partdetail/C165948) | Extended | 0.1873 | 5 | 0.9365 | 確定 |
| J2 / J_WING | BM14B-GHS-TBT(LF)(SN) | `Qualification:J2` / JstGh14 | BM14B-GHS-TBT(LF)(SN) / [C265384](https://jlcpcb.com/partdetail/C265384) | Extended | 0.6069 | 5 | 3.0345 | 確定 |
| R1 / R_CC1 | 5.1k | `Qualification:R1` / 0603 | 0603WAF5101T5E / [C23186](https://jlcpcb.com/partdetail/C23186) | Basic | 0.0015 | 5 | 0.0075 | 確定 |
| R2 / R_CC2 | 5.1k | `Qualification:R2` / 0603 | 0603WAF5101T5E / [C23186](https://jlcpcb.com/partdetail/C23186) | Basic | 0.0015 | 5 | 0.0075 | 確定 |
| R3 / R_USB_DP | 27 | `Qualification:R3` / 0603 | 0603WAF270JT5E / [C25190](https://jlcpcb.com/partdetail/C25190) | Extended | 0.0016 | 5 | 0.0080 | 確定 |
| R4 / R_USB_DM | 27 | `Qualification:R4` / 0603 | 0603WAF270JT5E / [C25190](https://jlcpcb.com/partdetail/C25190) | Extended | 0.0016 | 5 | 0.0080 | 確定 |
| R5 / R_QSPI_SS | 1k | `Qualification:R5` / 0603 | 0603WAF1001T5E / [C21190](https://jlcpcb.com/partdetail/C21190) | Basic | 0.0017 | 5 | 0.0085 | 確定 |
| R6 / R_WING_PD | 100k | `Qualification:R6` / 0603 | 0603WAF1003T5E / [C25803](https://jlcpcb.com/partdetail/C25803) | Basic | 0.0029 | 5 | 0.0145 | 確定 |
| R7 / R_HALL_PD | 100k | `Qualification:R7` / 0603 | 0603WAF1003T5E / [C25803](https://jlcpcb.com/partdetail/C25803) | Basic | 0.0029 | 5 | 0.0145 | 確定 |
| R8 / R_RUN | 10k | `Qualification:R8` / 0603 | 0603WAF1002T5E / [C25804](https://jlcpcb.com/partdetail/C25804) | Basic | 0.0024 | 5 | 0.0120 | 確定 |
| R9 / R_XOUT | 1k | `Qualification:R9` / 0603 | 0603WAF1001T5E / [C21190](https://jlcpcb.com/partdetail/C21190) | Basic | 0.0017 | 5 | 0.0085 | 確定 |
| R10 / R_ADC_A_TOP | 6.8k | `Qualification:R10` / 0603 | 0603WAF6801T5E / [C23212](https://jlcpcb.com/partdetail/C23212) | Basic | 0.0023 | 5 | 0.0115 | 確定 |
| R11 / R_ADC_A_BOTTOM | 10k | `Qualification:R11` / 0603 | 0603WAF1002T5E / [C25804](https://jlcpcb.com/partdetail/C25804) | Basic | 0.0024 | 5 | 0.0120 | 確定 |
| R12 / R_ADC_B_TOP | 6.8k | `Qualification:R12` / 0603 | 0603WAF6801T5E / [C23212](https://jlcpcb.com/partdetail/C23212) | Basic | 0.0023 | 5 | 0.0115 | 確定 |
| R13 / R_ADC_B_BOTTOM | 10k | `Qualification:R13` / 0603 | 0603WAF1002T5E / [C25804](https://jlcpcb.com/partdetail/C25804) | Basic | 0.0024 | 5 | 0.0120 | 確定 |
| R14 / R_ADC_C_TOP | 6.8k | `Qualification:R14` / 0603 | 0603WAF6801T5E / [C23212](https://jlcpcb.com/partdetail/C23212) | Basic | 0.0023 | 5 | 0.0115 | 確定 |
| R15 / R_ADC_C_BOTTOM | 10k | `Qualification:R15` / 0603 | 0603WAF1002T5E / [C25804](https://jlcpcb.com/partdetail/C25804) | Basic | 0.0024 | 5 | 0.0120 | 確定 |
| TP1 / TP_SWDIO | TestPoint | `Qualification:TP1` / testpoint:circle:1.2mm | 基板パッド / N/A | 購入なし | 0.0000 | 0 | 0.0000 | 確定 |
| TP2 / TP_SWCLK | TestPoint | `Qualification:TP2` / testpoint:circle:1.2mm | 基板パッド / N/A | 購入なし | 0.0000 | 0 | 0.0000 | 確定 |
| TP3 / TP_RUN | TestPoint | `Qualification:TP3` / testpoint:circle:1.2mm | 基板パッド / N/A | 購入なし | 0.0000 | 0 | 0.0000 | 確定 |
| TP4 / TP_QSPI_SS_FLASH | TestPoint | `Qualification:TP4` / testpoint:circle:1.2mm | 基板パッド / N/A | 購入なし | 0.0000 | 0 | 0.0000 | 確定 |
| U1 / U_MCU | RP2040 | `Qualification:U1` / rp2040Footprint | RP2040 / [C2040](https://jlcpcb.com/partdetail/C2040) | Extended | 1.0890 | 5 | 5.4450 | 確定 |
| U2 / U_ESD | USBLC6-2SC6 | `Qualification:U2` / sot23_6 | USBLC6-2SC6 / [C7519](https://jlcpcb.com/partdetail/C7519) | Extended | 0.1800 | 5 | 0.9000 | 確定 |
| U3 / U_FLASH | W25Q16JVUXIQ | `Qualification:U3` / flashFootprint | W25Q16JVUXIQ / [C2843335](https://jlcpcb.com/partdetail/C2843335) | Extended | 1.5761 | 5 | 7.8805 | 確定 |
| U4 / U_LDO | AP2112K-3.3TRG1 | `Qualification:U4` / sot23_5 | AP2112K-3.3TRG1 / [C51118](https://jlcpcb.com/partdetail/C51118) | Extended | 0.1787 | 5 | 0.8935 | 確定 |
| U5 / U_LOAD | TPS22919DCKR | `Qualification:U5` / sot363 | TPS22919DCKR / [C2149796](https://jlcpcb.com/partdetail/C2149796) | Extended | 0.1226 | 5 | 0.6130 | 確定 |
| Y1 / Y1 | ABM8-272-T3 | `Qualification:Y1` / crystalFootprint | ABM8-272-T3 / [C20625731](https://jlcpcb.com/partdetail/C20625731) | Extended | 0.6561 | 5 | 3.2805 | 確定 |

確定購入38行＝190個/5枚の部品代は **$23.3810**（1枚 $4.6762）。確定の裸TP4行は0個/0ドル。ギャップ7行＝35個/5枚の部品代は含まない。

### PO判断が必要なBOMギャップ（7行、3グループ）

現Mainの回路図/PCB/ソースは容量・サイズを持つが誘電体や具体型番を持たない。旧M1 BOMには各電源用容量についてX7Rを指定している。この履歴をX5Rへ緩和する権限を推定せず、以下を未選定とした。**回路図とPCBの値の食い違いはない。** Basic候補の存在はX7R仕様変更の根拠ではない。

| ref | 既存baseline / 現Mainサイズ | 公開ページで確認した候補（未選定） | POが解決する事項 |
| --- | --- | --- | --- |
| C12, C13 | 1µF X7R / 0402 | Samsung CL05A105KA5NQNC / [C52923](https://jlcpcb.com/partdetail/C52923)、25V、±10%、**X5R**、Basic | X7Rを維持して別候補を選ぶか、温度/DCバイアス/実効容量を確認してX5Rを認めるか |
| C14 | 10µF X7R / 0805 | Samsung CL21A106KAYNNNE / [C15850](https://jlcpcb.com/partdetail/C15850)、25V、±10%、**X5R**、Basic | bulkの実効容量・誘電体の確定 |
| C16, C17, C18, C19 | 1µF X7R / 0603 | Samsung CL10A105KB8NNNC / [C15849](https://jlcpcb.com/partdetail/C15849)、50V、±10%、**X5R**、Basic | LDO入出力、Hall load入出力の各レール条件での選定 |

候補ページには価格もあるが、選定されていないためCSV価格欄も取得分小計も空欄扱い。BOMギャップに加え、J1固定脚の実装方法/USB NPTH、検証用データを製品Mainへ採用する範囲が製造上の未解決事項として残る。

## 公開価格の取得方法と限界

JLCPCBの公開 `https://jlcpcb.com/partdetail/C番号` を認証なしでHTTP GET。表示本文が価格表を省略する場合でも、同じ公開HTMLの `self.__next_f.push([1,...])` に返る構造化データに数量帯別 `startNumber` / `endNumber` / `productPrice` があった。断片をJSONデコードして連結し、**対象 `componentCode` に一致するオブジェクトだけ**を抽出、同一帯を重複除去。HTMLのJSON-LD `Product.offers.priceCurrency=USD` と照合した。類似商品や検索スニペットの「from」価格は採用しない。価格証跡には取得時刻、元HTMLのSHA256、具体MPN/分類/仕様、全数量帯と適用数量を保存した（公開画像の一時署名URLなどは保存しない）。

確定購入38行には数量が入る価格帯が取得できた。LCSC直接HTTP取得には403もあったが、JLCPCB公開価格が利用できたため、価格が全面的にブロックされた停止条件には該当しない。単価の数値を推測した行はない。

これは**設計上の必要数による消費部品代**。当該公開ページから実注文のMOQ・attrition・low-quantity minimum charge、リアルタイムの割当可能在庫は取得していない。ページのおすすめ商品にある `stockCount` を対象部品在庫と誤読していない。掲載あり/価格ありを即納保証に読み替えず、必要数が注文できるかは本人アカウントの見積もりで確認する。最低請求数や余剰があれば $23.3810 に追加される。リザーブ購入のMOQとPCBA注文の必要数も区別する。

## Economic PCBA料金と適用計算

料金の一次出典は [JLCPCB PCB Assembly Cost](https://jlcpcb.com/help/article/pcb-assembly-price)（ページ更新2026-10-22、取得2026-11-04T11:27:45Z）。[FAQ](https://jlcpcb.com/help/article/pcb-assembly-faqs) にはsetup $8 / stencil $1.50 / SMT $0.0017の別値が残っているため、計算は専用料金表に統一した。最終金額は注文画面で確定する。

| 公開Economic料金 | 本件での扱い |
| --- | --- |
| setup $8.18 / order、stencil $1.53 | 片面1デザインで各1回 |
| SMT $0.0016 / joint（1–100,000 joints） | 199×5=995の指定参考計算、および実pad種別を分けた計算を下記に示す |
| Extended feeder $3.07 / type | 確定部分は9種→$27.63。Basicは追加なし。Preferred免除やキャンペーンは適用しない |
| X-ray：1–10 componentsなら $1.64 / component | U1 QFNとU3 USONの各5個、合計10個なら$16.40の予算。実課金対象は見積もりで確認 |
| manual $0.0164 / joint、hand-solder labor $3.58 / order | J1 shell 4×5=20接合を手はんだにするケース：$0.328+$3.58=$3.908 |
| pre-reflow $0.016 / joint | shellの工程として指定された場合20×$0.016=$0.32。manualケースに二重加算しない。課金SMT接合数も再確認 |
| parts placement confirmation $0.45 | 任意選択のため主計算に含めない。選択時追加 |

[公開能力表](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) はEconomicで片面SMT/THT混載、4層、1.2mm、0402、0.4mm IC pitchを掲載する。本件寸法48×44mm・5枚は一般掲載範囲に入るが、標準stackup・色/表面処理・具体部品/USB工程などの適格性は注文画面での確認が必要。PTH脚が存在するだけでStandard移行と断定しない。

確定部分のExtended 9種は **C2040 / C165948 / C7519 / C2843335 / C20625731 / C51118 / C2149796 / C265384 / C25190**。R3/R4の同一型番は1種として課金し、5枚や2参照ごとにフィーダー費を掛けない。未選定7行が新たなExtended型番になればさらに種類数分が増える。

X線検査は公開料金説明がQFN等の隠れ接合を対象とする一方、個別ページの `xrayFlag=false` も返るため、ゼロと断定しない。ここでは両leadless型番を対象に置いた条件付き予算とした。U1だけ5個が対象なら$8.20となり、主計算から$8.20減る。メーカー検査設定/見積もりが優先する。

### 指定の49フットプリント・199padを料金式へ適用

配置数を単価に掛ける方式ではなく、公開料金は**接合数**に依存する。指定199を全部SMT接合と置いた単純参考計算は `199×5×$0.0016=$1.592`、setup/stencilと合わせ **$11.302**。これに取得部品代$23.381、基板$8、確定9種フィーダー$27.63、X線10個$16.40を加えると **$86.713（1枚$17.3426）** になる。ただしNPTHと裸TPまで課金接合に数えた参考値であり、実データに基づく完成見積もりではない。

pad種別に従う手はんだケースでは **SMD189×5=945 joints → $1.512**（式中の945は個数）。PTHは20接合としてmanualの$3.908を別計上する。すべてのPTHが追加費用なしでリフロー扱いになれば `(189+4)×5×$0.0016=$1.544`、同じ他費用で$86.665となるが、その工程を採用済みとはしていない。NC/露出パッドの扱い・pre-reflow指定を含め、課金接合数はメーカー側BOM/CPL照合で確定する。

### 5枚の内訳（条件付き・未選定7行を除く）

| 費目 | 5枚 USD | 前提 |
| --- | ---: | --- |
| 基板本体 | 8.0000 | 指示書でPMO確認済み：4層48×44mm、1.2mm、5枚、2026-11-04。送料別。Workerによる再見積もり値ではない |
| 確定購入38行の部品 | 23.3810 | 190個、純必要数。未選定35個は除外 |
| setup | 8.1800 | Economic、片面、1デザイン |
| stencil | 1.5300 | 1回 |
| SMT | 1.5120 | 189×5接合×0.0016 |
| Extended feeder | 27.6300 | 確定9種×3.07 |
| X-ray予算 | 16.4000 | 2型番×5個×1.64の仮定 |
| USB shell manual + labor予算 | 3.9080 | 20接合×0.0164+3.58の仮定 |
| **実装費・検査費計** | **59.1600** | setup〜manualを合算 |
| **取得部品代＋条件付き費用の合計** | **90.5410** | **5枚 $90.54、1枚 $18.11（丸め前18.1082）** |

**未取得/未確定分を含める式**：`5枚総額 = 90.5410 + C_gap + Δ調達 + Δ実装/工程 + 送料・税等`。`C_gap` は7行35個の確定後部品代、`Δ調達` はMOQ/attrition/最低請求・価格変動分、`Δ実装/工程` は未選定Extended型番・X線対象・シェル工程等が上の仮定から変わる差額。上限を裏付ける価格がないため、全BOM総額の有限な上限や「この金額以下で発注可能」とは主張しない。1枚総額はこの式全体を5で割る。

含めていないもの：送料・税/関税、Wingとハーネス、筐体、プログラミング/機能試験、製造DFMによる追加工程。単一Main設計なので異種パネル費なし、面積21.12cm²なので大型基板費の条件にも達しない。Standard専用の$0.48/board minimum、fixtureやhandling費をEconomicへ流用しない。クーポン/Preferred免除/数量超過の値引きは見込んでいない。#121に残るvia-in-pad/paste/印刷やUSB NPTHレビューが工程変更を要求すれば、基板$8の適用条件も再確認する。

## 正確な注文見積もりまでの残ステップ

1. POが7行の誘電体・電圧・実効容量と具体MPN/LCSCを決定し、候補を確定行へ昇格する。既存代表配線用Mainをどこまで製品Mainとして採用するかも確認する。
2. J1の4 PTH shell脚と2 NPTH、既知via-in-pad等のDFMをレビューし、リフロー/pre-reflow/manualの工程とEconomic適格性を確認する。基板/footprintを本Issueで変更しない。
3. 承認対象のGerber・drill・BOM・CPLを生成/検査する。裸TP4行と仮想PWR_FLAGは購入/配置BOMへ入れない。現CSVは調査用49行台帳であり、そのまま注文投入するBOMではない。ref、回転、極性、EP、USB/JST shell/hold-down対応を確認する。
4. **ユーザー本人のJLCPCBアカウント**でGerber/BOM/CPLをアップロードし、5枚すべての実装、4層/1.2mm/色/仕上げ/stackupを指定。各C番号の在庫・Economic対応・分類・最低請求数・attrition、フィーダー数、接合数、X線費、USB工程、送料税を表示した最終見積もりを保存する。Workerはログイン・発注を行っていない。
5. PMOが成果物と不足事項をレビューし、POがPRのマージを判断する。本IssueはDraft PRまで、製造発注やマージは行わない。

## 作業・検証記録

指示書を最初に読み、`gh issue view 124 --repo ihsinoky/he-piantor-42` で本文を取得。元 `.git` の所有権保持コピーは環境が拒否したが、ファイルコピーは完了しており、コピー先を検証後 `/tmp/issue-124-bom/git` でfetchし、`origin/main`から `issue-124-main-bom-pcba` を作成した。既存未追跡の `.issue*-runtime/` は成果物に含めない。

抽出集合/回路図・ネットリスト値・footprint ID・合計pad数、CSV49行の一意性/列/状態/数量/Decimal小計、公開価格コード/数量帯/USD、既存追跡ファイル差分なしを検証した。設計・配線・既存文書を変更していないため、DRCやルータの再実行は行っていない。タイムボックス3時間内の追加ファイルだけをDraft PRとして提出し、マージしない。
