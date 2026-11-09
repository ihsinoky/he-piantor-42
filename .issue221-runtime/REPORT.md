# Issue #221 — Main Rev.5 最終報告

**実装・データ上の合格条件・製造パッケージ準備を完了。D-035は提案、POゲート待ち。**
J4のみMolex **781710004 / LCSC C588524**へ変更し局所配線した。
発注・支払い・カート投入・push・PR作成はしていない。Matrix/Wingのデータ変更0。
実物での初回通電前測定・製造GO・ADR採択・発注対象の正式切替は実施範囲外の未実施ゲートとして残す。

要求正本：[Issue #221](https://github.com/ihsinoky/he-piantor-42/issues/221)、
[PMO再開判断](https://github.com/ihsinoky/he-piantor-42/issues/221#issuecomment-6750886847)、
[最新POコメント（付属ケーブルで直接接続・別途調達不要）](https://github.com/ihsinoky/he-piantor-42/issues/221#issuecomment-6750942420)、
`.issue221-runtime/INSTRUCTIONS.md`。起点は独立gitコピー `.issue221-runtime/git` の
`main-rev5-ezmate`、**227eb17a**（前回調査コミット）。親の設計ベースは6006e8be。
成果物を同ブランチへ追加コミットし、PMOが以降の提出を扱う。ユーザー指示によりPRを作成しない。

## 再起動後の棚卸しと引継ぎ

[start inventory](../hardware/kicad/qualification/issue-221-main-rev5/recovery-inventory.json)で
起点の追跡14,981ファイルをSHA-256照合し、**不一致0**。独立gitのHEADとブランチも一致した。
qualificationに残っていたのはREADME、input-contract、inspect-input、issue221、sources、verificationの6ファイルで、
いずれも227eb17aとbyte一致。Rev.5 PCB・配線・製造ZIP・追加検証スクリプトは残っていなかった。
未追跡のINSTRUCTIONS、ランタイムログ・設定・調査画像は別途記録し、基板成果と誤認しない。
外側worktreeのgit状態と独立gitの状態を区別し、外側の履歴・ブランチには書き込んでいない。

既存のRev.4入力同定と出典調査を引き継ぎ、基板と製造成果は今回生成した。
過去の `input-contract.json` と `issue221.json` は**初回HOLD時の履歴**として保持。
現在の要件とPMOコメントは `issue221-current.json` / `issue221-comments.json`、
現在の合格状況は `verification.json` を参照する。旧HOLD報告を最終合格の証拠にしていない。

## ピン順の根拠と部品同定

Rev.4入力：`issue-196-main-rev4-phaseb/inspection/final/main.kicad_pcb`。
SHA-256 `b361a5a010a3ae2b08e5858735d46a5662112af4241ef55bab50d1ba3187b123`。
現行J4はSM04B-SRSS-TB(LF)(SN)/C160404、`Rev4:J4`、(100,90)mm、180°。
PCBと独立回路図XML/BOMを照合済み。

| 端子 | Rev.4ネット | Rev.5ネット | 同梱1:1ケーブルのFly側（PMO採用判断） |
| --- | --- | --- | --- |
| 1 | VBUS | VBUS | VBUS |
| 2 | USB_DM_ESD | USB_DM_ESD | D− |
| 3 | USB_DP_ESD | USB_DP_ESD | D+ |
| 4 | GND | GND | GND |

Flyの番号付き回路図を直接取得したとは扱わない。初回HOLDに対しPMOが承認した根拠は次のチェーン。

1. Rev.4のUDB C3前提の番号付きピン順を、PCB・XML・BOMで確認。
2. Fly公式販売店CannonKeysの[ケーブル規約](https://cannonkeys.com/products/molex-and-jst-cables)は
   Molex↔JSTの1:1／UDB互換を明示。[Fly販売ページ](https://cannonkeys.com/products/fly-daughterboard-and-molex-cable)も
   FlyとMolexケーブルを組にして扱う。
3. [Geon公式Fly情報](https://geon.works/products/fly-daughter-board)と設計者のUDB代替という位置づけ、
   [UDB開発者の説明](https://hackmd.io/w7rV9b1fRHau51bIx631Hw)のGeon Flyも同じケーブルを使うという説明を結ぶ。
4. UDB系PCBと共通ケーブルで接続する製品の互換性主張を、番号対応が同一である根拠として採用するという
   **PMOの明示的判断**。資料の主張からの判断であり、写真・線色だけから推定していない。

組立時には後述の実測を必須とする。この根拠と条件を[D-035草案](../docs/decisions.md#d-035---main-rev5-fly-daughterboard-connector-proposal)にも記載した。
指定品の[LCSC](https://www.lcsc.com/product-detail/C588524.html)と
[JLCPCB](https://jlcpcb.com/partdetail/Molex-781710004/C588524)を確認しBOMへ反映。
JLC掲載はExtended/SMT Assembly/Economic・Standard。実在庫・割当・業者受入れ確定を意味しない。

## ランド・局所変更と差分

[Molex図面](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/781/78171/781710004_sd.pdf)
`781710000-SD PSD000 A / EC677110 / 2022-06-07`のsheet1のcircuit1マークと、sheet2の実装面側ランドを照合。
原本ホストの直接downloadはtimeoutしたため、Molex作成の同図面を[ミラー](https://www.global-ic.com/pdf-21/0781710004.pdf)から取得し、
図番・改訂・4極の型番表・寸法・観察面を確認して `sources/781710000-SD-revA.pdf` として保存した。
KiCad公式フットプリントも原文とhashを保存。信号はpitch1.20mm、0.60×0.85mm、補強ランドは0.70×0.80mm。
信号内側縁から補強外側縁まで3.75mm、pin1中心から補強の近側横縁まで0.80mmを検査した。
銅パッドは推奨の全寸法を保つ矩形とし、補強は無番号・無ネット。図面参考条件はPCB1.0mm/stencil0.1mm/開口100%。
実基板は不変条件の1.2mmを保つ。ステンシル・機構の業者/組立確認は残す。
[land-check.json](../hardware/kicad/qualification/issue-221-main-rev5/land-check.json)参照。

J4の原点(100,90)mm・角度180°を維持し、pin1中心は(101.8,91.875)mm。
VBUS/GNDはランド内を0.60mm幅で引き出し、Y=92.65mmから1.10mmへ拡幅。
メーカーの配線非推奨領域を覆う保守的なF.Cu本体範囲を検査し、指定6ランド以外の配線/via/他padの侵入0を確認した。
[rev4-diff.json](../hardware/kicad/qualification/issue-221-main-rev5/rev4-diff.json)は全差分のUUID・座標・幅を記録。

| 比較項目 | 結果 |
| --- | --- |
| 変更フットプリント | J4のみ `Rev4:J4`→`Rev5:J4`、MPN/LCSCを指定品へ変更 |
| 銅箔変更ネット | VBUS、GND、USB_DM_ESD、USB_DP_ESDの4ネット |
| 配線差分 | F.Cu3線分削除・11線分追加、残る1,262 tracks/viasはAST一致 |
| 変更via | 0（全130個を保持） |
| 配線端点の範囲 | X=98.1…101.8、Y=91.875…95.4mm。銅幅は変更一覧に記録 |
| 位置・角度 | J4を含む全62 footprintで維持。J2/J3・他61 footprintは全AST一致 |
| 外形・穴・ゾーン定義・ネット構成・基板ルール | fill cacheを除く非配線rootノード一致、projectはbyte一致 |
| 回路接続 | 226論理端子（199接続・27 NC）を保持、ネット割付変更0 |
| 非J4基板変更／広域再配線 | 0／不要 |

回路図のnative ERCでは、継承元にグリッド外接続258件・ライブラリ参照118件・power未駆動3件が現れた。
実物基板やネットを変えず、紙面上の部品と接続を一体で1.27mmグリッドへ移し、埋込シンボル/footprintの
ローカル表を整備。外部供給VBUS/GND、buckのL1後のV5V2に明示的PWR_FLAGを付けた。
部品のピン種別を変更せず、ERC項目の無効化・重大度引下げ・違反除外なし。
これらは継承回路図の検証表現の修正で、PCBの他部品位置を動かしたものではない。
XML全端子契約の照合でネット不変を確認。`schematic-repairs.json` と初回 `schematic/erc.json` が履歴。

## 検証結果

KiCad **9.0.9**。最終PCBのSHA-256は
`8b1754ebc5a67cf17bf2a6e54b49814e087d8d09e13f0eedf59a99715c06c286`。

| 検査 | 結果 |
| --- | --- |
| native DRC（全重大度、違反時exit codeを使用） | 違反0、未配線0 |
| native ERC（全重大度、違反時exit codeを使用） | 違反0 |
| 独立実銅箔union-find | 全40ネット、必須未接続0、異ネット接触0 |
| via–pad全数監査 | 130via×232銅pad=30,160組、違反0、最小0.145mm（基準≥0.10mm） |
| Rev.4のvia–pad最小値 | 0.145mm、同等。NPTH3個のみ銅パッド監査から除外 |
| via–両面paste | 全130via、銅/ドリルとも重なり0 |
| GND数値検証 | 解析矩形、相反性、重ね合わせ、KCL合格 |
| 製造CAM読戻し | 4銅層の全track/via/pad・GND実fill・外形・穴・mask・pasteが一致 |
| GerberフレームCPL | 55点の誤差0mm、native posと55点一致、1,485対の相対ベクトル一致 |

全via–全padの非重複組も含む値は `inspection/final/audit/via-pad/all-pairs.json.gz` に保存。
同一ネット・NC・補強・bare TPを含めて共有銅層の実効形状から測定し、ドリル縁で代用していない。
CAM検査は見た目だけでなくGerbonaraによる独立読戻し。9パネルの `manufacturing/cam-review.png` も目視確認した。

## 電源影響（両Revを同一環境で再抽出）

Rev.4/Rev.5の最終実銅箔から正側16条件ずつ、GND4メッシュ/幅条件ずつを新たに抽出。
Rev.4再抽出は既存値に一致した。比較コーナーは125℃・実配線幅−20%、銅35µm・barrel20µm・
仮定積層z=[0,0.2,1.0,1.2]mm。正側は可変幅中心線、GNDは実fill穴/thermal/spoke・配線・pad・viaのDC三角形FEM。
材質下限や完成品の保証値ではない。

| 経路 | Rev.4 mΩ | Rev.5 mΩ | Δ mΩ |
| --- | ---: | ---: | ---: |
| J4.1→U6.12 正側VBUS | 3.009787 | 4.788143 | +1.778356 |
| U6.10→J4.4 GND | 41.900530 | 43.898305 | +1.997775 |
| 入力往復 | 44.910316 | 48.686448 | +3.776131 |
| 下流共通往復 | 37.113969 | 37.108545 | −0.005424 |
| J2分岐往復 | 3.470864 | 3.472698 | +0.001834 |
| J3分岐往復 | 28.227454 | 28.229643 | +0.002189 |

入力往復はモデル上50mΩ以内、500mAで増分約1.888mV。
GND入力の粗→細メッシュ差はRev.4=0.146mΩ、Rev.5=0.117mΩ。KCL残差は4nA未満。
下流の微小差はいずれも粗細メッシュ差より小さく、下流共通・分岐は50mΩ基準内を維持。
GH各導体200mm・断面0.0804mm²以上・各接触50mΩ・6帰線、Wing各127mAという既定条件で
下流最遠点は **4.797985654773 V**、Rev.4比+1.100µV（表示0.001V単位ではともに4.798V）。5.2Vレール設計と検証の結論は維持する。

上流はUSB4.75V・効率75〜95%・Fly/ケーブル等の予約抵抗0.25/0.5/1Ωの15条件を再評価。
converter電圧の追加低下は最大2.281mV、500mA予算の合否分類変化0。
**75%効率条件はRev.4から既に500mA超過であり、今回も無条件合格とは扱わない。**
Flyヒューズ・EZmate接点・付属ケーブルの完成抵抗、実効率、初動/動的電流等の実物検証は残る。
[power-impact.json](../hardware/kicad/qualification/issue-221-main-rev5/power-impact.json)と
`power-budget.json` / `power-sensitivity.csv` に全数値・仮定・制限を保存した。

## 製造パッケージと残るゲート

[qualification一式](../hardware/kicad/qualification/issue-221-main-rev5/README.md)の
`manufacturing/` に、新基板から次を再生成した。

- `main-rev5-fabrication-review.zip`：Gerber9枚＋PTH/NPTH drill2個（11ファイル）、CRCと展開内容hashを照合。
- `BOM.csv`：実装55点、J4=781710004/C588524。それ以外の行はRev.4と一致。TP4点・穴3点を実装対象から除外。
- `CPL.csv` / `CPL-jlcpcb-gerber-frame.csv` / フレーム注記：J4を含む原点・角度を保つため位置CSVはRev.4と同じ値になるが、新PCBから再生成・照合した。
- `gerber/` / `paste/` / native絶対pos / drill-report / CAM画像。
- [quote-handoff.md](../hardware/kicad/qualification/issue-221-main-rev5/manufacturing/quote-handoff.md)：指定部品、製造条件、座標、測定条件、未実施ゲート。

**初回通電前の必須測定：** Mainへまだ接続せずFly単体をUSB電源につなぎ、同梱ケーブル先端の
端子4を基準として端子1が+5V（VBUS=5V/GND=0V）であることを実測・記録する。
端子番号・観察面を記録し、極性異常ならMainに接続しない。電源を切ってからMainに接続する。
本作業は実物にアクセスしておらず、この測定とUSB認識確認は未実施。
D+/D−取り違えが実証された場合のみPMO判断どおりRev.5.1で是正する。

D-035とproject-statusは草案として仕上げた。ADR採択・正式ベースライン更新はしていない。
業者の在庫/DFM/実装向き・ステンシル受入れ、嵌合高さ/配索、完成上流抵抗、実物電源・USB動作はPO/PMOの次ゲート。
旧価格を流用せずPMOが再見積する。広域再配線は不要だった。

## 再検証

`python3 hardware/kicad/qualification/issue-221-main-rev5/verify.py` でmanifest、入力/出力hash、
DRC/ERC、全via–pad組、差分・電源モデル、BOM/CPL/ZIP、保存対象の範囲を検査する。
native処理は同ディレクトリ `env.sh` で既存KiCad環境を読み取り使用し、スクラッチは `.issue221-runtime/` のみに置く。
実行順・個別スクリプト・再実行時の注意はREADMEに記載。
