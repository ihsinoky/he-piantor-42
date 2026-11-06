# Issue #167 — Main 2 Wing Stage 2 再開：D-027、実装候補と資格確認の停止

**PO承認の入力再定義をD-027へ記録し、案Cの回路・基板候補を作成した。独立検査は全44ネットで実施したが、全体配線1回＋局所修正1回の上限内に合格せず停止した。Issueは未完了、製造GOではない。** 最終試行の実測4指標は **未接続3／異ネット接触0／物的違反2／説明不能な転送変更24**。4指標0の資格は取得していない。入力再定義そのものを停止理由にしていない。

発注・課金・mergeは行っていない。既存の [Draft PR #168](https://github.com/ihsinoky/he-piantor-42/pull/168) を同じ `issue-167-main-dual-wing-stage2` で更新する。本報告のEは [再開証跡フォルダ](../hardware/kicad/qualification/issue-167-main-dual-wing-stage2/resume/) を指す。

## 1. 再開範囲と保全

`.issue167-runtime/instructions-167-resume.md` と `instructions-167.md` を全文読み、Issue #167およびDraft PR #168を取得した。再開headは `0a1f355510e3f2fcadfdc68e7ae97ea90122eb6b`。通常の `.git` は古いmainを指し読取り専用なので、前回と同じ `.issue167-runtime/git` を継続使用した。新しいブランチへの付替え、mainのcheckout、mergeはしていない。

D-024／D-025／D-026、#160／#163の取り込み、旧入力予算は引き継ぐ。[前回報告全文](../hardware/kicad/qualification/issue-167-main-dual-wing-stage2/resume/previous-run-report.md) と旧status／publication／manifestをEへ保存した。前回の入力4.75V不成立という証明は過去要件に対する証跡として残す。旧検証passを今回の合格へ流用しない。

開始時計は **2026-11-06 07:22:18 UTC**、4時間の期限は **11:22:18 UTC**（E/start.json）。停止は時間切れではなく、事前に固定した配線試行上限への到達による。残時間を追加試行へ転用しない。一時Git、XDG、ツール用tmpは `.issue167-runtime/`、既存のKiCad／KRT依存環境は読取り使用した。

## 2. D-027とUSBコネクタ位置の入力

[D-027](decisions.md#d-027---main-usb-input-requirement-at-the-board-connector) を追記した。既存決定本文は変更していない。

[USB 2.0仕様](https://www.usb.org/document-library/usb-20-specification) §7.2.1.4／§7.2.2は、構成後の高電力機能について給電点の下限とケーブル降下を区別する。USBコネクタでローカルGNDを基準にする入力範囲を、次のとおり **4.50–5.25V** と定める。

```text
給電点下限 4.75V − VBUSケーブル降下125mV − GNDケーブル降下125mV
= デバイス側コネクタでの実効下限4.50V
```

これはコネクタから変換器までの基板損失を含まない。そこは実配線から別に引く。列挙用の低電力条件、§7.2.2 Figure 7-47のバス給電hub経由の低電圧経路と、500mAが許可された構成後の給電を混同しない。USB-C形状や5.1kΩのCC抵抗だけから500mA超の許可は導かない。

構成許可前・未列挙・reset・suspendでは変換器、U5、両MUXをoffとする必要がある。今回の回路候補ではU6.ENとU5.ONを既存 `HALL_PWR_EN`／R7のdefault-offへ接続した。既存sensor-test firmwareはこの許可管理を実装済みとはいえず、変更していない。USB descriptorと構成／suspend処理の実装・実証は未完了である。

## 3. 回路・基板候補

起点は#155の `inspection/final/main.kicad_pcb`、SHA256 **`fdc1a7748f94714e395eb50f3e08c43afa24192ee76eb3d1804a8cba28690222`**。

| 項目 | 作成した候補／確認 |
| --- | --- |
| 外形 | X76–124／Y70–122、48×52mm |
| 既存配置 | 全53 footprintの座標・角度を保全。J1/J2、4穴、全層Ø5mm予約を保持 |
| J3 | (105,73)、0°、GH14同一ピン契約。補強ランドは機械NC |
| MUX_EN1 | U1.8／GPIO6 → J3.7、R16=100kΩ外部プルダウン。旧NCを回路源から除去 |
| 変換器 | U6=可変版TPS63070RNMR、PS/SYNC=GNDで強制PWM、VSEL／未使用FB2=GND |
| 帰還 | R17=55kΩ／R18=10kΩ、初期0.1%・25ppm/Kを要求。公称0.8×(1+55/10)=5.2V |
| L/C | L1=1.5µH XFL4020-152MEC候補、入力22µF×2、出力22µF×3、VAUX 100nF |
| default-off | U6.ENと既存U5.ONは共通HALL_PWR_EN。U5入力をVBUSからV5V2へ変更 |
| 2分岐 | U5出力近傍から両GHへ分岐。意図した太い電源経路をseed化し、信号はD-019のまま |
| 成果物 | 66 footprints、うち電気部品62／機械穴4。論理245 pins／44 nets |

[TIデータシート](https://www.ti.com/lit/ds/symlink/tps63070.pdf) の可変版ピン割当とRNM0015Aランド例からU6候補を作成した。[Coilcraft XFL4020-152](https://www.coilcraft.com/en-us/products/power/high-voltage-inductors/xfl/xfl4020/xfl4020-152/) は1.5µH±20%、25°C DCR最大15.8mΩ。量産向けランド／mask／paste照合は完了していない。C23/C24/C26–C28は **22µF・16V・X7R・0805の要求値を置いた段階**で、実効容量・DCバイアス・ESRを満たす具体的MPNは未確定。これを最終BOMとは呼ばない。精密抵抗のMPNも未確定である。複製元由来のSourceID属性が新部品に残り、後段の製造追跡用には整理が必要となる。

E/circuit-source.pyは既存の凍結済み回路契約に変更・追加を明示し、PCBからネットを逆生成せずにnative schematicを作成する。KiCad CLIでその [回路図](../hardware/kicad/qualification/issue-167-main-dual-wing-stage2/resume/schematic/main.kicad_sch) をnetlistへexportし、独立に全245論理pinsをPCB padと照合した。E/circuit-check-global.json／local.jsonの差は0。これは**論理接続指定の一致**であり、物理的な導通合格ではない。

## 4. D-019再配線と独立資格確認

4層／1.2mm、信号幅・間隙0.10mm、via0.60/0.30mm、In1.CuはGND専用、escalation offを保持した。E/routing-scope.jsonで**全体1回1800秒＋原因を限定した局所1回900秒**に固定した。初期配置・seed銅箔の手動修正は3回を上限とし、修正後にも残ったJ1近傍の0.086mm間隙違反は、該当するV5V2の2 segmentsだけを全体配線の対象へ渡した（E/global-seed-ripup.json）。0.086mmを許容条件へ変更していない。API互換修正でnative保存に至らなかった起動は配線試行に数えず、ログはすべて保存した。

KRTのresolverを配線直前に読取り、幅・間隙・via・層コスト `[1,-1,1,1]` とoffを確認した。#131に保存されたKRT全2055 source hashesと実使用runtimeを照合し、変更0件。ルータのexit code 0だけでは合格としない。

| 独立実測項目 | 全体1回目 | 局所最終1回 |
| --- | ---: | ---: |
| 必須未接続 | **3** | **3** |
| 異ネット接触 | 0 | 0 |
| 物的違反 | 0 | **2** |
| 説明不能な転送変更 | **1** | **24** |
| 全ネット確認 | 44 | 44 |
| 資格判定 | **不合格** | **不合格** |

独立手順は、入力側projectを使用したKiCad再fill／DRC、native読取りsnapshot、実銅箔の44-net union-find、nonroute AST差分、保持すべき各segmentの中心線coverage／via一致からなる。GNDは実fillのouter／hole polygonsを含め、同名ネットという理由で導通を合成しない。

全体結果はV1V1が2成分、V3V3が3成分。V5V2の保持via1件も欠落した。局所修正では、未接続2電源ネットとルータ診断が挙げた `XOUT`／`QSPI_SD0` の4ネットだけをripping対象とし、欠落viaとC26への局所接続を入力へ戻した。最終結果でも **V1V1が3成分、V3V3が2成分** で、合計未接続3件。さらに `QSPI_SCLK`／`QSPI_SD2` の保持対象20 segments＋4 viasが欠落した。nonroute AST追加／削除は0である。dangling viaはV3V3 (106.4,92.3) とV5V2 (90,78.5) の2件。幅・via・In1 GND条件の検査は両回とも合格した。

E/inspection/*/assessment.jsonは従来の判定法を保持し、KiCadに未接続がある場合の「資格指標」をnullにする。上表はE/status.jsonにまとめた**直接観測値**であり、nullを0へ置換していない。raw DRC、connectivity、transfer-diffをすべて残した。印刷上の既存61件（text-height44／silk-overlap12／silk-over-copper5）は物的指標と分離し、その記録を消していない。

**試行上限に達したため、追加の手配線・別順序試行・新ツール試行はしない。** 全体・局所の両候補を証跡として保持し、「最終合格板」というパスへ移していない。

## 5. 電源の再評価：計算と未保証の境界

### 5.1 5.2V精度と動特性

強制PWMのFB精度±1%、帰還抵抗の初期±0.1%と25ppm/K×100K、FB leakage最大100nAを独立に端点計算すると **5.112095–5.288737V**。要求DC範囲5.096–5.304V内に入る計算である。入力4.50–5.25Vから基板損失を差し引いても、ICの入力動作範囲に対して余裕はある。

しかし部品MPN・実効容量・ループ応答・起動波形を確定しておらず、**片側50mVのリップル／過渡予算は未検証**。計算上の帰還精度だけでレール全体が入力範囲全域で保証されたとはしない。上限5.354Vを守る起動overshoot、逆給電、ノイズ／ADC settlingも未実証である。

### 5.2 他負荷の最大値見積りと500mA

E/power-budget.jsonとE/connector-current-sensitivity.csvに保存した。Main他負荷の**設計上の最大割当見積りは110mA**。

| 他負荷 | 最大割当見積り | 根拠と限界 |
| --- | ---: | --- |
| RP2040（内部linear VREG、USB／ADC／ロジックを含む） | 80mA | [公式datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf) Table637のPopcorn最大平均DVDD16.6＋IOVDD35.5、USB用2mAを併記し、さらに25.9mAを予約。48MHzの測定例から133MHz全workloadの保証maxは導けず、割当上限は未実証 |
| W25Q16JV flash | 25mA | read／program／eraseの計画包絡。実動作・PVT・I/O駆動を含むシステム確認は未完了 |
| LDO Iq、CC／USB／ESD、pullup/down等 | 5mA | Iq80µA級に対する余裕を含む工学的予約。個別最大の完全積上げ・全state検証は未完了 |

125°C抵抗率／幅−20%の正側VBUS実配線モデルは **121.486mΩ**。GNDを追加50mΩと仮定し、他負荷も同一抵抗へ流す保守的な集中モデルで定電力の二次式を解く。入力コネクタ4.50V、127mA/Wing、レール高側5.354Vでは次のとおり。

| 効率の仮定 | 変換器入力 | 変換器入力電流 | Main他負荷込み | 500mAとの差 |
| --- | ---: | ---: | ---: | ---: |
| 80% | 4.415111V | 385.017mA | 495.017mA | 4.983mA |
| 90% | 4.422546V | 341.662mA | 451.662mA | 48.338mA |

**80%は保証下限ではない。** 他負荷110mAも未実証の割当で、GND抵抗も仮定である。したがって「設計負荷でUSB500mA内に入る保証を取得した」とはしない。設計／ストレス、入力3点、効率5点、GND感度3点、レール3点の405ケースを、KVLと電力式で相互検算した。11mA包絡はストレスのみとし、500mAを超えるケースを合格へ読み替えない。

### 5.3 実抵抗と最遠点

E/extract-power.pyは#141中心線抵抗モデルを、**各segmentの実線幅**に対応するよう局所的に拡張した。変更した関数本文、入力hash、KCL残差をE/power-extraction-local.jsonへ保存する。35µm箔／20µm barrel、パッド拡がり等の近似モデルであり、製造最小値・実測上限ではない。GND planeの抵抗は抽出していない。

| 正側のみ、125°C／幅−20% | 抽出モデル値 |
| --- | ---: |
| J1 VBUS → U6 VIN | 121.486mΩ |
| U6 V5V2 → U5 IN | 54.013mΩ |
| U5 OUT → 2枝の共通部 | 6.661mΩ |
| J2枝（共通部を除く） | 23.848mΩ |
| J3枝（共通部を除く） | 25.282mΩ |

レールからの共通正側だけで **60.674mΩ** となり、共通往復50mΩ目標をモデル上超える。太い幹線だけでなく、小ピンのescapeと接続部を含めた改善が必要である。

既存17mm Wingの147.710145mV、代表100mmハーネス／接点19.305mV（ともに127mA時）、U5 Ron感度0.25Ωを保持した条件付き計算では、Main追加GND降下0／25／50mVに対し、127mA最遠点は **4.796863／4.771863／4.746863V**。これは5.2V下限・動特性を別途満たした場合の感度であり、4.60Vの設計保証ではない。11mA包絡の結果もE/power-budget.jsonに分離した。GND抽出・実効率下限・最大負荷・動特性・正常な電源ネットの成立を省略していない。

## 6. POFVと製造・見積の扱い

未資格の局所候補を**診断目的で**全via再走査した。E/pofv-reclassification.json／pofv-sites.csvは実候補のhashを持ち、総108 vias／候補26件（mounted-center21、mounted-drill-edge2、mounted-annulus-only2、bare-testpad1）。D-022のepoxy-fill／copper-cap方針と、J1の12 SMD contacts＋4 PTH shell legsを同一Economic PCBAで実装する要求を保持する。製造業者の受入れや追加料金合意は取得していない。

**製造データの再生成と確定BOM／CPL・PCBA見積はゲート未通過のため保留。** 旧#155 CAM／見積を48×52mmの新板へ転用していない。D-024の「適用ゲート後に製造データ・BOM／CPL／見積を更新」に従う。E/pcba-update-status.jsonには外形・4層／1.2mm・追加13 refs・予定58実装部品（旧45）・新POFV件数と、見積不能の条件を明記した。金額を推測して確定見積とせず、発注／カート／課金操作はしていない。

## 7. 検証・公開・再開に必要な判断

E/verification.jsonは、記録の算術・保全・試行数・source hashes・native論理一致・不合格の正確な表示を検査した結果である。**証跡整合passとPCB資格failを分ける。** 実行方法と成果物の地図はE/README.md、現在状態はE/status.json、公開本文はE/draft-pr-body.md、commit／push／PR更新結果はE/publication.jsonを参照する。

再開には、今回の失敗を踏まえた**新たな有限の配線範囲・試行枠**の判断が必要となる。候補の次の問題を同時に解消する必要がある。

- V1V1／V3V3の実未接続と、局所処理がQSPI_SCLK／QSPI_SD2を変更した転送問題。旧板資格やルータexit codeで代替しない。
- レール共通部の正側60.674mΩ、未抽出のGND、変換器入力線の損失。50mΩ目標を変更しない。
- C／精密Rの具体的選定・ランド／mask／paste確認、効率・Main最大負荷・50mV動特性・USB許可制御の根拠。
- その後の全44ネット独立4指標0、製造CAM、確定BOM／CPL、POFV／Economic工程、現行PCBA見積。

機構(b)を維持し、J3近傍の筐体支持とGH実物操作／挿抜力はM1の後段検証として残す。機構実物未確認を今回の停止理由にはしていない。mergeは行わない。

生のプロセス出力とKRT生PCBにはツール由来の空白警告が残る。hash付き生データを保持し、正規化済み検査板・著作コード・報告書と分離した。E/staged-whitespace.jsonに対象を記録する。
