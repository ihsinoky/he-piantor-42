# Issue #147 — Wing 素基板の発注準備

**#141 の電源／GND 0.30mm・信号0.10mm合格基板について、16mm／17mm両ピッチの製造ZIPとデータ側の発注前チェックを完了した。** 両方とも外形・穴・銅箔・マスクが入力と一致し、保存済みの最終DRCは違反0／未配線0。ただし、入力に印刷シルクがない。無印基板として受け入れるか、別件でシルクを追加・再検証するかはPO／設計担当に残す。メーカー審査・費用・発注承認も未完了であり、このZIPは審査用候補である。

[Issue #147](https://github.com/ihsinoky/he-piantor-42/issues/147) の再開実行。2026-11-04のPO決定どおり、**素基板を各ピッチ5枚、PCBAなし、手はんだ、ステンシルなし**を前提とする。センサ等の部品購入は別件。実測後に量産ピッチを決める。発注・課金・メーカーサイトへのアップロード・問い合わせ・mergeは実行していない。

以下の `E/` は [`hardware/kicad/qualification/issue-147-wing-order-prep/`](../hardware/kicad/qualification/issue-147-wing-order-prep/)。指示書全文は `E/instructions.md`、取得Issueは `E/issue147.json`。

## 製造データと対象固定

| 項目 | 16mm | 17mm |
| --- | --- | --- |
| #141 合格セル | KRT-16-2L-P0300 | KRT-17-2L-P0300 |
| 元基板 | `issue-141-wing-power-integrity/runs/KRT-16-2L-P0300/out.kicad_pcb` | `issue-141-wing-power-integrity/runs/KRT-17-2L-P0300/out.kicad_pcb` |
| 基板SHA256 | `3f29d24274c6e1834cf344c1c9c3bb234cd1aefa1e85d6eb3e8470eb5f2383f4` | `e7744a86e65459905b7629f2c8a13c60f1c0aa1d26c85139ac1c893d634e5939` |
| 外形（Edge.Cuts中心線） | 110 × 100mm | 116.5 × 104.75mm |
| 配線線分／ビア | 808／196 | 681／198 |
| PTH | φ0.30mm × 196、すべて配線ビア | φ0.30mm × 198、すべて配線ビア |
| NPTH | φ2.2mm × 4 | φ2.2mm × 4 |
| ZIP | [wing-16mm-jlcpcb-review.zip](../hardware/kicad/qualification/issue-147-wing-order-prep/wing-16mm-jlcpcb-review.zip) | [wing-17mm-jlcpcb-review.zip](../hardware/kicad/qualification/issue-147-wing-order-prep/wing-17mm-jlcpcb-review.zip) |
| ZIP SHA256 | `55e3c2e8107a3285f7ac257b427fc4a567f2f40f9b21b5893d285042a8cb5c90` | `ee183ea5eda0fa255df4e2fa029a2e87fee8404c9a96993111f376475cbc7e6f` |

元基板パスは `hardware/kicad/qualification/` 相対。#131 の一律0.10mm出力は使っていない。#141の独立4指標・幅監査の合格と、その出力PCB／プロジェクトのhashを確認し、ランタイムコピーもbyte一致する。全信号0.10mm、HALL_5V／GND 0.30mm、全ビア外径／穴径0.60／0.30mm、2銅層、板厚1.2mm、最小クリアランス設定0.10mmをnative readerで照合した（`E/resumption-verification.json`）。

再開時の説明より実ファイルは先まで進んでおり、**両ピッチともGerber・Excellon・ドリル報告・成功した生成ログが残っていた**。一方、ビューア検査は16mmの穴座標完全一致判定で停止し、保存済みプレビュー／ZIP／検査完了記録はなかった。したがって16mmを再生成せず、17mmも検証で正しさを確認した既存エクスポートを採用した。再開後に追加したのは解析検査・プレビュー・ZIP・報告等で、CADエクスポート／配線／設計変更は行っていない。再開時70ファイルをhash固定し、全件不変を検証した。

各ZIPはルート直下の9ファイル：F.Cu、B.Cu、F.Mask、B.Mask、F.Silkscreen、B.Silkscreen、Edge.CutsのGerber計7本と、PTH／NPTHを分離したExcellon計2本。Gerberはmm・小数6桁、ドリルはmm・絶対原点・小数表記。両ピッチは別々の単一設計で、追加の面付け・タブ・スロットはない。ZIP CRCと全メンバーのbyte一致を確認済み。

`.gbrjob` は生成証跡として保存し、注文ZIPから除外した。Sizeが外形線幅0.05mmを含んで110.05 × 100.05mm／116.55 × 104.8mmとなり、Finishも`None`のため、注文寸法や表面処理の指定根拠にしない。銅厚0.035mmの記録も、メーカーの仕上り銅厚保証に代わるものではない。

## 入力要素・最終データの確認

| 確認項目 | 両ピッチの結果と根拠 |
| --- | --- |
| 単一外形 | 直線4辺の閉じた矩形1周。フットプリント内を含め内部Edge.Cutsなし、切り欠き・切削スロット0。Gerber全外形線分・座標が一致 |
| 取付穴・分類 | 四隅のNPTH φ2.2×4、位置・径が完全一致。PTHはビアだけ。丸穴のみ、長穴0。独立したドリルファイルと報告の穴数も一致 |
| 銅箔 | 全配線の始終点・幅・層、全via flashの位置・径、全190個のSMDパッドの識別子・位置・外接寸法を解析照合。一致しない図形・追加銅箔なし |
| 最小間隔 | 入力と同じプロジェクトで実行済みのKiCad 9.0.9最終DRCを検証。全severity／全track対象、違反0、未配線0。0.10mmルールとエクスポート銅箔の一致を根拠とする。別のCAMによる最小実測値やメーカーDFM認証とは呼ばない |
| マスク | F.MaskはSMD開口190個、開口位置・寸法が銅パッドと一致（拡張0）。B.Maskは開口0、viaは両面テント。裏面に実装パッドがない入力どおりで、欠落ではない |
| シルク | **両面とも印刷図形・可視文字0**。隠されたReference／Valueからエクスポート設定で文字を復元することはできない。F.Silkscreenにはマスク差引きのclear図形だけがあり、印刷像は空。B.Silkscreenも空 |
| ペースト | 入力のF.PasteにはSMD開口190、B.Pasteは0。別フォルダ `paste-reference-not-for-order/` に記録。手はんだなのでZIPに含めず、ステンシル／PCBAは注文しない |

シルク不足は**入力基板の構築側**に由来し、エクスポートの欠落ではない。勝手な設計変更はしていない。無印を受け入れる場合は組立用配置図・pin1／極性・J_WINGの向きを別資料で確認する。文字を必要とする場合は設計担当が別変更で追加し、DRC・製造データ・プレビューを再検証して本候補を置き換える。現ZIPに存在しないシルクが印刷されるとの前提で発注しない。

Excellonの座標出力は0.001mm刻みであり、Gerber／元基板の小数6桁と文字通りの一致にはならない。再開後の検査は、径が同じ穴に対して各軸0.0005mm以内の**一意の1対1対応と全穴消費**を要求した。最大の実ずれは両ピッチとも約0.000075mm（0.075µm）、その位置ずれを引いた公称ビア環状銅箔幅は約0.149925mm。NPTHは完全一致した。これは出力丸めの量だけで、製造時の穴位置公差は含まない。GerbonaraのG90位置に関する警告も記録したが、絶対座標として全穴が一致している（`E/manufacturing-checks.json`）。入力基板の変更は不要と判断した。

## Gerberビューアでの描画確認

Gerbonara 1.5.0で実Gerber／Excellonをオフライン読込みし、全9ファイルの個別描画と銅箔＋外形＋穴の重ね合わせを確認した。レビュー画像は以下。背面銅箔も正面から見た共通座標で、鏡像の製造データを作ったわけではない。

| ピッチ | 全レイヤー | 表銅箔＋穴 | 裏銅箔＋穴 |
| --- | --- | --- | --- |
| 16mm | [一覧](../hardware/kicad/qualification/issue-147-wing-order-prep/16mm/preview-review/all-layers.png) | [表](../hardware/kicad/qualification/issue-147-wing-order-prep/16mm/preview-review/top-copper-holes.png) | [裏](../hardware/kicad/qualification/issue-147-wing-order-prep/16mm/preview-review/bottom-copper-holes.png) |
| 17mm | [一覧](../hardware/kicad/qualification/issue-147-wing-order-prep/17mm/preview-review/all-layers.png) | [表](../hardware/kicad/qualification/issue-147-wing-order-prep/17mm/preview-review/top-copper-holes.png) | [裏](../hardware/kicad/qualification/issue-147-wing-order-prep/17mm/preview-review/bottom-copper-holes.png) |

両ピッチで閉じた外形、四隅4穴、センサ群・下辺のコネクタ／MUXパッド群、配線とvia穴の対応を確認。外形を突き抜ける図形、意図しない面塗り、レイヤーのずれ、余分な切削形状は見つからない。空の裏マスクと両面シルクは上表の入力要因として扱い、全層が有意な画像を持つと誤記しない。画素表示だけで0.10mm間隔の合格を判断せず、前節の解析／DRCと併用した。詳細は `E/visual-review.json`。

初回追加レンダリングではSVGフィルタ／透明背景のCairo表示により低コントラストとなったため、レビューには白背景・フィルタなしの `preview-review/` を使用した。製造ファイルは一切変えていない。

## #138「未」項目の引継ぎ

| #138の未項目 | 今回の到達点 | 発注直前／後続に残ること |
| --- | --- | --- |
| 最終製造データ照合 | **データ側完了**。対象を#141の改定条件出力へ更新し、外形・NPTH・ドリル分類・間隔ルール・全銅箔・ZIP・プレビューを確認 | シルクなしの受入れ、または別改版後の再照合 |
| 銅厚と製造品質 | **データ側注記完了**。2層・板厚1.2mm・外層1oz・via0.60／0.30mm | 注文画面・最終スタックアップ・メーカー能力／審査で仕上り銅厚、線幅公差、ネック、viaめっきを確認。受入検査は別 |
| Keyboard Design料金 | #138の形状自己判定「非該当」を引継ぎ。#141出力／最終データも矩形、内部切削0、長穴0、NPTH4 | **メーカー審査のみで加算有無・カテゴリ・料金単位・面積扱いを確定**。非課金の保証ではない |
| DRV5055供給電流 | 未完了を維持 | RevC表とFig5-13の不整合、調達品改訂・磁界・温度と実電流の確認。10mA／11mA包絡を保証値にしない |
| HALL_5V／GND降下・基準 | #141の0.30mm化による改善結果を引継ぐ | 最低供給電圧・Main／ハーネス／接点損失・GND／ADC基準・実負荷を確定し実測 |
| TMUX1208制御条件 | 未完了を維持 | 3.3V制御・選択周波数の消費、入力範囲、ADC負荷／整定を確認 |
| 起動・故障・環境／実機 | 未完了を維持 | 突入・短絡保護・筐体温度・連続動作・遠端電圧・キー読取り精度を実測 |
| 費用と承認 | 注文候補・数量・指定事項を整理 | 送料・税・加算を含む最終金額と発注GOはPO |

機械可読一覧は `E/checklist.json`。データ側完了を電気仕様・製造品質の保証と混同しない。[#141報告](issue-141-wing-power-integrity.md)では、Wing入力4.75V・11mA/センサ・125°C・最悪幅仮定の17mmが局所4.4813Vで4.5Vを下回る。供給最低値は未確定であり、素基板の実測用発注準備をもって実機全条件を承認していない。

## POが発注へ進む際の残件と入力事項

| 項目 | 指定済み／確認すべき内容 |
| --- | --- |
| 対象と数量 | 16mm ZIPと17mm ZIPを別設計として各5枚。寸法は上表、各単一矩形基板。意図しない合算・面付け・片方の取り違えがないか確認 |
| 必須製造条件 | **2層、板厚1.2mm、外層銅箔1oz、最小線幅／間隔0.10mm、電源／GND 0.30mm、ビア0.60／0.30mm、NPTH φ2.2mm×4**。PTHビアとNPTH取付穴の分類を維持 |
| 実装サービス | 素基板のみ、PCBAなし、ステンシルなし。BOM／CPL不要。paste-reference・gbrjob・解析証跡を誤って提出しない |
| シルクとマスク | シルクなしを明示的に受け入れるか別改版。表マスク190開口／裏0、両面viaテントのCAM解釈を確認。マスク／シルク色やメーカーの調整条件はPOが選択・確認 |
| その他注文欄 | 表面処理、基材／スタックアップ、寸法・厚み公差、電気検査、納期、製造番号配置、配送先・配送方法等、画面にある項目と選択の影響をPOが確認。未決値を自動採用しない。`gbrjob Finish=None`を裸銅指定と解釈しない |
| メーカー審査 | Keyboard Design加算、Routing等の他加算、最小間隔／穴／マスク／テントの製造可否、必要なCAM修正と価格。変更された場合はデータへの影響を確認してから承認 |
| 最終費用と発注ゲート | 両ピッチ各5枚の基板代、加算、配送、税、通貨・合計を確認しPOが発注承認。#133の参考価格$19.20を最終見積として使わない。今回価格取得・アップロード・問い合わせは未実施 |
| 基板以外 | DRV5055等のセンサ、TMUX1208、受動部品、コネクタ／ハーネス、はんだ・組立治具等の調達は別件。無印で組む場合の配置／極性資料を用意し、手はんだ・受入検査・電気実測へ進む |

## 保存・検証・提出

再開の作業開始は2026-11-05 07:10:33 UTC、2時間の期限は09:10:33 UTC。前runの開始時刻は保存した `E/start.json` のまま保持した。通常 `.git` は書込みせず、既存の `.issue147-runtime/git` と指定ブランチ `issue-147-wing-order-prep` を使用。一時状態は `.issue147-runtime/` に限定した。

元run開始時の45,864パス（シンボリックリンクはリンク先文字列を検査）と再開時の70成果物を検査し、変更0。入力PCB・プロジェクト・過去証跡を含む既存ファイルを変更せず、指定報告と証跡だけを追加する。検査スクリプトは構文検査、全JSON読取り、ZIP CRC／メンバーhash、ローカル参照、ステージ差分の追加のみを確認する。対象は製造データのため製品コード／firmwareの無関係な再生成は行わない。既存CIの重いengineeringジョブのpath条件には該当しない。リモートCIはローカル検査と区別する。

検査と再現手順は `E/README.md`、最終監査は `E/final-verification.json`、全成果物hashは `E/manifest.json`。公開試行の記録とPR本文は `E/publication.json`／`E/pr-draft.md` に保存する。pushできない場合も指定ブランチにコミットを残し、次の手順でホスト側から引き継げる（公開の成否は最終メッセージとpublication記録を参照）。

```bash
git fetch ./.issue147-runtime/git issue-147-wing-order-prep
git push origin FETCH_HEAD:issue-147-wing-order-prep
# その後 E/pr-draft.md の本文で Draft PR を作成。mergeはしない。
```
