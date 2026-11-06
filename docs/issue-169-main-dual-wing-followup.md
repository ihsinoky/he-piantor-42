# Issue #169 — Main 2 Wing Stage 2 フォローアップ：有限2回の結果と停止

**Issueは未完了、製造GOではない。** 追加配置・seed見直しによって、1回目は独立4指標すべて0／全44ネットを達成した。共通正側抵抗も#167の60.674mΩから **33.295mΩ** に改善した。しかし出力コンデンサの実効容量余裕を増す1210品へ更新した2回目は、独立直接観測 **未接続2／異ネット接触2／物的違反4／保持配線転送差分7** で不合格。全体2回の枠を使い切って停止した。1回目の配線合格を、部品更新後の基板の合格に転用しない。

**実行不備も停止に含む。** 2回目の準備DRCはC26とSW2の衝突を検出したが、呼出しシェルのコマンド列が前段assert失敗で終了せず、当時のroute.pyにも独立preflightガードがなかったため、その入力で2回目を実行した。これは作業者の回避可能な実行ミスであり、D-019下で設計が不可能である証拠ではない。試行を帳消しにせず、2回目として全数計上する。生ログと当時のrunnerを保全し、将来のガードを修正した。追加配線・局所rip-upで埋め合わせない。

発注・課金・mergeは行っていない。新決定は行わず、D-019／D-022／D-024〜D-027を変更していない。以下Eは[今回の証跡](../hardware/kicad/qualification/issue-169-main-dual-wing-followup/)を指す。

## 1. 起点・ブランチ・時間枠

指定 `.issue169-runtime/instructions-169.md` を全文読み、[Issue #169](https://github.com/ihsinoky/he-piantor-42/issues/169)と[Draft PR #168](https://github.com/ihsinoky/he-piantor-42/pull/168)を取得した。起点はPR #168 head **`ac74ef964e2c64a5dfde1f67af8f440e539b317d`**、ブランチ `issue-167-main-dual-wing-stage2`。同headから **`issue-169-main-dual-wing-followup`** を作成した。

通常 `.git` は古いmainを指し書込み制限があるため、#167のGitメタデータを `.issue169-runtime/git` に複製した。作業ツリーは指定どおり現在の `he-piantor-42`。Git操作は `git --git-dir=.issue169-runtime/git --work-tree=. …`。既存の追跡ファイル・`docs/decisions.md`は変更していない。関連外の未追跡成果物もコミットしない。

開始 **2026-11-06 07:55:12 UTC**、期限 **11:55:12 UTC**（4時間、E/start.json）。停止理由は配線試行枠の消費であり、残時間による追加試行は行わない。新規ランタイム・Git・XDG・ツールのTMPDIRは `.issue169-runtime/`。KiCadとKRT依存環境は既設を読取り使用した。

## 2. 配置と電源seed

案Cの48×52mm、X76–124／Y70–122、J3=(105,73)・0°を維持。**既存53 footprintの座標・角度は両候補とも全数維持**した。既存部品の移動はない。4 NPTHと全層Ø5mm銅箔予約も独立に確認した。

#155の完成済みU1電源ネット **V1V1／V3V3と全QSPIネット** を、ネット全体のsegment／viaとして種配線へ保持した。#167の局所候補から保持欠落を引き継いでいない。既存USB shellの0.20mm bonds3本も保持した。その他は新しい全体配線対象とした。

V5V2幹線をIn2.Cu **2.4mm** へ拡幅し、U5側に並列viaを追加。J1のPTH/NPTHと取付穴予約を避ける経路へ修正した。HALL_5VはB.Cuの3mm幹線・U5近傍2枝を維持しつつ、元V3V3/QSPI viaとの衝突を避けた。意図的に太くした電源だけの変更で、信号の最小幅・間隙は0.10mmのまま。

| 追加部品 | seed-a | seed-b |
| --- | --- | --- |
| C26 | (91.8,77.5)、0805 | (91.8,77.5)、1210 |
| C27 | (93,80)、0805 | (93.5,81)、1210 |
| C28 | (96.2,80)、0805 | (98,81)、1210 |
| U6／L1／C23／C24／C25／R16〜R19 | #167位置を維持 | seed-a位置を維持 |
| 電源escape | U6側0.25mm | U6側0.40mmへ変更 |
| ルータ順序／探索方向 | mps／既定 | inside_out／backward |

seed-bは**seed-aの配線前入力**から準備した。1回目の配線後結果の局所rip-upではない。拡大したC26.1とSW2 seedが衝突する不備は2回目の入力・結果に残り、隠していない。準備4回＋seed-b2回の幾何検査、生入力、失敗したAPI呼出しもEに保存した。

## 3. 部品選定とBOM

[TI TPS63070 datasheet](https://www.ti.com/lit/ds/symlink/tps63070.pdf) §7.3、§8.4.5、§9.2.2と、E/sources内のメーカー仕様・特性表を照合した。PS/SYNC=GNDは§8.4.5の強制PWM指定と一致する。曲線説明の表記だけから極性を変更していない。

| refs | 選定MPN | 判断 |
| --- | --- | --- |
| C23/C24 | GRM21BC81C226ME44L | 22µF±20%、16V、X6S、0805。入力側2個。X6Sの部品温度上限105°Cを明記 |
| C26–C28 | **C3225X7R1C226K250AC** | 22µF±10%、16V、X7R、1210。出力側3個。seed-bへ実寸ランドを反映 |
| C25 | GRM155R71E104KE14D | 100nF±10%、25V、X7R、0402、VAUX |
| R17 | **TNPW060354K9BEEA** | 54.9kΩ、初期±0.1%、25ppm/K、0603 |
| R18 | **TNPW060310K0BEEA** | 10kΩ、初期±0.1%、25ppm/K、0603 |
| U6／L1 | TPS63070RNMR／XFL4020-152MEC | 可変版、強制PWM／1.5µH。#167の選定を保持 |

55.0kΩの未確定指定を、実在の54.9kΩ精密品へ具体化した。公称は **5.192V**。FB±1%、抵抗初期±0.1%と25ppm/K×100K、FB leakage100nAを端点計算した **5.104240–5.280590V** は、5.2V±2%の5.096–5.304V内に入る。長期ドリフトを保証した計算ではない。

0805 Murata品のメーカー典型DCバイアス曲線は5.35V近傍で容量が半分以下へ低下する。1回目の配線合格だけで出力フィルタを確定せず、2回目は容量保持率の高いTDK 1210品へ変更した。[TDK製品情報](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C3225X7R1C226K250AC)とメーカー特性表では5.35V近傍の容量保持を保守的に85%と読取り、許容差0.9、温度0.85、AC/経時余裕0.9を乗じ、出力3個を **38.62485µF** とする選定スクリーニングを保存した。2.4MHz付近のESRは1個約2–10mΩという典型曲線の読取りである。入力2個は保持0.4、許容差0.8、温度0.78、余裕0.9で9.88416µFを評価し、TIの入力4.7µF最小値との余裕を確認した。

**これらはメーカーの保証最小容量／保証最大ESRではない。** 古い典型特性表のmirrorと、取得できたメーカー仕様書、403となった取得結果を区別して保存した。125°Cは銅抵抗感度であり、X6S入力Cを含む製品全体の125°C環境保証ではない。50mVの動特性・起動overshoot・逆給電・ADC settlingは未実証。部品選定のスクリーニングを電源系の製造認定と呼ばない。

E/main-bom.csvは**seed-bの選定台帳62行（実装58＋裸TP4）**。R16/R19は既存R6の100k品、J3は既存J2の同一GH品。seed-aのBOM/CPL58行は別のレビュー資料へ保存した。R17と出力TDK品のJLC調達対応、在庫／attrition／最低請求／Economic対応は未確定である。

## 4. D-019全体配線と独立資格確認

**4層／1.2mm／信号幅・間隙0.10mm／via0.60/0.30mm／In1.Cu GND専用／escalation off** を保持。全体最大2回、各2400秒、局所配線0回を事前のE/routing-scope.jsonに固定した。両回ともルータ直前のresolver状態を読み取った。KRT全2055 source hashesと実使用binaryも既存証跡と照合し、変更0件。

| 直接観測4指標 | seed-a 全体1回目 | seed-a paste整備後 | seed-b 全体2回目 |
| --- | ---: | ---: | ---: |
| 必須未接続 | 0 | 0 | **2** |
| 異ネット接触 | 0 | 0 | **2** |
| 物的違反 | 0 | 0 | **4** |
| 説明不能な保持配線転送変更 | 0 | 0 | **7** |
| 確認ネット数 | 44 | 44 | 44 |
| 独立配線資格 | 合格 | 合格 | **不合格** |

入力projectでのnative再fill／KiCad DRC、native snapshot、実銅箔の全44-net union-find、nonroute AST差分、各保持segmentの中心線coverage／via一致を独立実施。GNDは実fillのouter/hole polygonsを含め、同名ネットという理由で導通を合成しない。各候補で回路源→native回路図export→**245論理pins**とPCB padを独立照合した。

seed-aの追加C/R/J3には、複製元の**基板全体F.Paste図形**が伴わない問題を発見した。元部品の開口36個を翻訳複製し、入力と出力へ同一ASTを適用した。**銅箔変更・配線追加・rip-upは0**。E/paste-correction.jsonを残し、修正後も全44ネット・4指標0を再確認した。`inspection/final/`はこの**seed-aのpaste整備板**であり、seed-bの最終合格板という意味ではない。

seed-bのXINはY1.1／C1.1／U1.20が3成分、未接続2。C26.1[V5V2]とSW2 seed2本が接触し、異ネット接触2、DRC shorting_items2＋solder_mask_bridge2。保持すべきHALL_5Vの7 segmentsに中心線／幅coverage差分が生じた。via欠落・nonroute AST追加削除は0。V1V1／V3V3／QSPIの保持ネットは両回とも接続が成立し、局所rip-upで破壊していない。

未接続があると資格指標をnullにする既存assessment法は維持した。上表はconnectivity／DRC／transfer-diffの直接観測値で、nullを0にしていない。両回とも幅・via・In1 GND条件は合格。継承した印刷DRC61件（text_height44／silk_overlap12／silk_over_copper5）は物的指標から分け、生ログを残した。

## 5. 正側とGNDの実形状抵抗抽出

E/power-extraction-*.json、ground-extraction-*.json、resistance-summary.jsonにPCB hashとモデル条件を保存した。正側は#141中心線モデルを各segmentの実幅へ拡張。GNDは実fill・穴・thermal spokes、実GND tracks/padsとbarrelsを三角形DC sheet FEMへ変換した。

**最終採用モデルの基準はU6.10 PGND、USB側はJ1.1/12のGND contacts。** shellを独立の電流源にせず、U6の制御GNDピン全部を理想短絡して改善したことにしない。初期の複数IC-GND均等モデルは `*-equal-IC-contacts.json` として診断履歴に分離した。GH側は6 return contactsへ均等に電流を注入する仮定で、実ハーネス不均衡は未評価。

| モデル値、125°C／配線幅−20%（mΩ） | USB入力 正側 / GND | レール共通 正側 / GND / 往復 | J2枝 往復 | J3枝 往復 |
| --- | ---: | ---: | ---: | ---: |
| seed-a | 121.979 / 11.409 | 33.295 / 9.916 / **43.211** | 24.833 | 26.095 |
| seed-b | 109.625 / 10.302 | 32.123 / 8.782 / **40.904** | 24.203 | 23.623 |

両候補とも共通・枝の50mΩ目標を**モデル上**満たした。特に共通正側は#167の60.674mΩから33.295／32.123mΩへ改善した。ただしseed-bは短絡しているため、ネットを分けた抵抗値は診断であり動作中の電圧予測として成立しない。

メッシュ最大面積0.03／0.0075mm²で収束傾向を照合し、10×5mm銅板の解析解、相反則、重ね合わせ、KCL残差を検査した（E/ground-model-verification.json）。境界簡略化2µm、sheet35µm、barrel20µm、層高さ0/0.2/1.0/1.2mm、pad/landing接触近似を明記した。GND配線の幅−20%は適用したが、filled plane／thermal形状はnativeのまま。plane/spoke etch、保証銅厚／plating／stackup、接点電流分担が未確定なので、数値を製造最大抵抗として使わない。

## 6. 電源予算の更新と未保証項目

4.50–5.25VはD-027どおりUSBコネクタ位置で定義し、抽出した正側＋GND入力損失を別に引いた。Main他負荷110mAは#167の割当（RP2040 80／flash25／その他5mA）を継承し、保証最大とは呼ばない。効率75–95%の仮定、設計127mA/Wingとストレス231.0081／278mA/Wing、入力3点・レール3点を計270ケース保存した。

| 入力4.50V、効率80%仮定、127mA/Wing、入力電流は高側レール5.354V | 変換器入力 | USB合計（他負荷110mA込み） | 条件付き最遠点 J2 / J3 |
| --- | ---: | ---: | ---: |
| seed-a | 4.434191V | 493.361mA | 4.801355 / 4.801195V |
| seed-b | 4.440902V | 492.781mA | 4.802021 / 4.802095V |

最遠点列は、レール下限5.096V・下向き50mV、Main抽出往復、U5 Ron0.25Ω、#141/#167の100mmハーネス19.305mVと17mm Wing147.710145mVを組み合わせた**別の出力下側条件**である。電流列と同じレール電圧で同時に生じる値ではない。計算上は4.60Vを上回るが、実効率下限・他負荷・動特性・正常な基板の成立を未確認のまま保証へ昇格しない。reset／未構成／suspendでU6/U5/両MUXをoffにするUSB許可firmwareも未実証である。

## 7. CAM／POFV／PCBA見積

seed-aのpaste整備後の独立配線合格を基に、**レビュー目的の**4銅層Gerber、mask/silk/outline、PTH/NPTH drill、F/B paste、BOM/CPLをE/manufacturing-seed-a-reviewへ再生成した。source hash、元project使用、出力前後board不変を照合。Gerbonaraで全銅層のtracks／pads／110 vias、実In1 plane polygons、4 plated slots／6 NPTH、mask、元図形と追加pad paste、CPL座標変換を照合し、fabrication-review ZIPを検査した。CPLは(76,122)起点でX右／Y上、Gerber/drillは絶対原点。回転・極性と製造受入れは後段確認である。

このCAMは**0805出力Cのseed-a専用**。現在の1210選定BOMと組み合わせて発注しない。**seed-bの最終CAM・確定PCBA見積は生成・確定していない。** D-024の資格ゲート未通過のため保留し、旧見積やseed-a CAMを最終候補へ流用していない。

| POFV再走査 | 全vias | 候補 | 内訳 |
| --- | ---: | ---: | --- |
| seed-a paste整備板 | 110 | 28 | mounted-center21、drill-edge4、annulus-only2、bare-TP1 |
| seed-b 不合格板の診断 | 127 | 40 | mounted-center29、drill-edge7、annulus-only2、bare-TP2 |

D-022のepoxy fill／copper capと、J1の12 SMD contacts＋4 PTH shell legsを**同一Economic PCBA**で実装する要求を保持する。POFV全via台帳と候補座標CSVを更新したが、製造者の対象範囲／mask/paste／plating／追加料金の受入れは取得していない。PCBA見積は金額を推測して確定扱いせず、E/pcba-update-status.jsonに資格・調達・工程・見積の不足を明記した。ゲート失敗後の見積のために発注／カート／課金／サポート送信は行わない。

## 8. POへ上げる条件変更の要否と公開

**今回の結果からD-019緩和が必要とは結論しない。** seed-aは同条件で4指標0を達成している。seed-bには準備不備と実行制御ミスがあるため、それを層数／間隙／escalationの限界の証拠にしない。次の有限枠を認めるか、1210配置・C26/SW2・XIN・保持HALL差分をどう同時に解消するかの判断が必要である。新たな枠の承認を仮定して追加配線しない。

再開時には、現在の選定品・配置で全44-net／4指標0を成立させ、容量／動特性・USB許可・電流上限・製造材料条件の未保証部分を処理し、その候補のCAM／BOM/CPL／POFV／同一Economic PCBA工程を照合して現行のアカウント見積を確定する必要がある。機構方針(b)は維持し、実GH挿抜／筐体支持は後段のM1検証である。

E/verification.jsonは証跡整合の検査であり、seed-bの合格を意味しない。E/README.mdに成果物と実行方法、E/status.jsonに停止状態、E/publication.jsonにcommit／push／Draft PR試行結果を保存する。通常 `.git` を使わず今回のGitメタデータで**コミット後にpushしDraft PR作成を試みる**。Draft PRのbaseは#167ブランチとし、#169だけの差分をレビュー可能にする。mergeは行わない。

内容コミット **`a5a5aa6cc54c8fa9b1c4e7d3bb1945493389682e`** は新ブランチへpush済み。Draft PR作成は実際に試みたが、接続ツールが **`MCP tool call requires approval, but approval policy is never`** として拒否した。別経路でこの拒否を回避していない。作成用タイトル・本文と拒否生結果はEに保存し、[比較リンク](https://github.com/ihsinoky/he-piantor-42/compare/issue-167-main-dual-wing-stage2...issue-169-main-dual-wing-followup?expand=1)を用意した。PRは作成されておらず、Issueは未完了のまま。公開監査記録は別コミットで同じブランチへpushする。
