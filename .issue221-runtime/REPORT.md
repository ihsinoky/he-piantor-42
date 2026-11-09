# Issue #221 — Main Rev.5 調査報告（実装保留）

**未完了／HOLD：Fly Daughterboard のピン1〜4のネット対応が一次資料で未確認。**
指定部品 Molex 781710004 の LCSC/JLCPCB コードは **C588524** と特定済み。
停止理由は調達コードではなく、Fly の番号付き USB ネット対応を確定できないこと。
指示書 `.issue221-runtime/INSTRUCTIONS.md` の手順2
「裏付けが取れない項目は推測で進めず、報告書に『未確認』と明記して PMO 判断を仰ぐ」
に従い、ネット割付・フットプリント変更・再配線を保留した。合格や製造可能とは報告しない。

作業起点：`6006e8beed60c4b2f1644841243b75946ec8c5b7`。
要求正本：[GitHub Issue #221](https://github.com/ihsinoky/he-piantor-42/issues/221)。
作業ツリーで成果物を作成し、独立 git コピー `.issue221-runtime/git` の
`main-rev5-ezmate` にコミットする。push／PR作成は指示書に従い PMO 担当。

## Rev.4 入力の同定（変更前）

入力は `hardware/kicad/qualification/issue-196-main-rev4-phaseb/`。
native KiCad 9.0.9 の pcbnew で最終 PCB を読み、回路図 XML netlist と
製造 BOM を独立に照合した。XML の root-sheet 接頭辞 `/` のみ正規化。
4本すべて一致し、BOM の型番と C160404 も一致した。

| J4 pin | Rev.4 PCB net | 回路図 XML net | Fly pin net |
| --- | --- | --- | --- |
| 1 | VBUS | /VBUS | 未確認 |
| 2 | USB_DM_ESD | /USB_DM_ESD | 未確認 |
| 3 | USB_DP_ESD | /USB_DP_ESD | 未確認 |
| 4 | GND | /GND | 未確認 |

現行部品は **SM04B-SRSS-TB(LF)(SN)**、footprint `Rev4:J4`、
配置 (100.000, 90.000)mm、180°。
PCB SHA256：`b361a5a010a3ae2b08e5858735d46a5662112af4241ef55bab50d1ba3187b123`。
照合スクリプトと入力 hash は
[input-contract.json](../hardware/kicad/qualification/issue-221-main-rev5/input-contract.json)／
[inspect-input.py](../hardware/kicad/qualification/issue-221-main-rev5/inspect-input.py)参照。

## 一次資料の調査結果

2026-11-10 調査。確認内容と限界は
[sources.json](../hardware/kicad/qualification/issue-221-main-rev5/sources.json)に記録した。

- [Geon 公式商品情報](https://geon.works/products/fly-daughter-board)：Fly by Wolf、
  Molex 781710004 と相手側 781720004 へのリンク、EZmate↔EZmate 同梱を確認。
  番号付き pin-net 表／回路図は見当たらない。
- [LCSC C588524](https://www.lcsc.com/product-detail/C588524.html)と
  [JLCPCB C588524](https://jlcpcb.com/partdetail/MOLEX-781710004/C588524)：
  指定 Molex 型番との一致を確認。JLCPCB は Extended、SMT Assembly、Economic/Standard
  と表示。発注時の実在庫確保や納期の保証ではない。代替他社品は選定していない。
- [Molex customer drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/781/78171/781710004_sd.pdf)：
  `781710000-SD PSD 000 A`、2022-06-07、3枚。sheet 1 に circuit 1 マーク、
  sheet 2 に実装面側推奨ランドを確認。これはコネクタの端子番号を定義する資料で、
  Fly 回路の VBUS/D−/D+/GND 割付を定義しない。実ランドの作成／照合は未実施。
- [CannonKeys Fly 商品情報](https://cannonkeys.com/products/fly-daughterboard-and-molex-cable)：
  Molex cable 同梱、170mm を確認。
  [同店ケーブル規約](https://cannonkeys.com/products/molex-and-jst-cables)は1:1／UDB互換を明記。
  それでも Fly 自体の番号付きネット表は確認できない。
- [UDB 開発者の説明](https://hackmd.io/w7rV9b1fRHau51bIx631Hw)にも1:1規約と
  Geon Fly が同じケーブルを使う説明がある。UDB と Fly の回路上のピン割付が
  同一であるという番号付き定義までは得られず、推論だけで実装を進めない。
- [Wolf サイト](https://www.vwolf.be/)は検索インデックスに UDB 代替と今後の
  オープンソース化を述べるが、直接取得は404。設計者 GitHub の公開リポジトリも
  調べたが Fly 回路図は発見できなかった。Geon の Autodesk 3D リンクも
  ブラウザ取得に失敗し、電気接続の証拠として扱っていない。

Geon 公式写真も確認したが、線色やコネクタの見え方から番号とネットの対応を
推定していない。「UDB の代替」という説明とケーブル互換性だけでは誤配線を除外できない。

## 合格条件の状況

| 項目 | Rev.5 の実施状況／結果 |
| --- | --- |
| 指定部品／LCSC コード | 781710004 / C588524 特定済み。製造BOM反映は未実施 |
| ピン順の一次資料照合 | Rev.4 は PCB/XML/BOM 照合済み。Fly pin1〜4 は未確認 |
| 推奨ランド・J4 局所再配線 | 未実施（先行条件未成立） |
| native DRC／ERC／未配線 | Rev.5 未実施、数値 N/A。Rev.4 の結果を流用して合格にしない |
| ビア–パッド全数監査 | Rev.5 未実施、最小値 N/A |
| Rev.4 との差分 | 電気・基板・製造入力の変更0。変更ネット0、変更フットプリント0（未実装） |
| VBUS 抵抗変化・電源結論 | Rev.5 未評価、ΔR=N/A。4.798V の新設計での維持は未証明 |
| Gerber ZIP／BOM／CPL／Gerber-frame CPL／quote-handoff | Rev.5 未生成。旧パッケージの改名・転用なし |
| D-035／project-status | 提案／更新草案を追加。採択・ベースライン切替なし |

比較用の **既存 Rev.4 証跡値** は verification.json／Phase B 報告書で
DRC違反0・未接続0・ERCクリーン、全130 via × 232銅pad、via–pad最小0.145mm。
今回これらの検査を再実行した値ではない。
Rev.4入力→U6 往復44.910mΩ（正側3.010mΩ／GND41.901mΩ）、
共通37.114mΩ、J2分岐3.471mΩ、J3分岐28.227mΩ、最遠点4.797984555V。
Rev.5 では J4 の信号／電源ランドと局所銅が変わるため、入力VBUSとGNDの抵抗を
再抽出して比較する必要がある。5.2Vレールを変更しないことだけでは入力側の同等性を証明しない。
Fly と付属ケーブルの完成上流抵抗も未測定。

## 差分と再開条件

既存 PCB／回路図／BOM／CPL／CAM は一切変更していない。変更は本報告、
D-035 提案、project-status 草案と新 qualification ディレクトリの調査記録のみ。
Matrix／Wing データの変更0。外形・穴・部品配置・電源設計の変更0。

PMO に必要な判断材料：Geon／Wolf／公式販売店による **Fly の番号付きピン表または
回路図・明示的回答** と、付属ケーブルの端子番号間対応。pin1の観察面／キー方向、
コネクタ端子番号、VBUS/D−/D+/GND を結び付けられる資料が必要。
一般的なUSB線色や別製品UDBのピン表のみでは再開しない。

確認後に行う作業は、Molexランド作成と寸法照合、J4のみ置換・局所配線、
DRC/ERC/未配線、全via×全pad監査（≥0.10mm、Rev.4との最小値比較）、
全非J4差分監査、VBUS/GND抵抗比較と電源影響評価、CAM再生成／独立照合、
PR #220 と同じ Gerber フレーム CPL、quote-handoff、D-035と状態草案の仕上げ。
広域再配線が必要なら再度停止する。

発注・支払い・カート投入・対外問い合わせ・GitHub push／PR作成は行っていない。
本報告は停止条件に基づく引継ぎであり、Issue #221 の合格完了ではない。
