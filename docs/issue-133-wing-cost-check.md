# Issue #133 — Wing 合格条件（2層・0.10mm）の費用確認

[Issue #133](https://github.com/ihsinoky/he-piantor-42/issues/133) の調査結果。対象は Issue #131 で特定した Wing の実現条件（2層・線幅/間隔 0.10mm・ビア 0.60/0.30mm・板厚 1.2mm）。素基板のみ（Wing は手はんだ、PCBA 見積もりなし）。金額は USD、為替換算なし。

## 結論

**0.10mm 条件の採用による追加コストは $0.00。** 両ピッチ5枚ロットの素基板は JLCPCB 公開計算機で 16mm $9.30、17mm $9.90、**両ピッチ同時発注の基板代合計 $19.20（10枚、エンジニアリング費 $4.00×2 を含む）**。0.20mm 前提でも同額（差 $0.00）。送料・税は未取得。

- 公式能力ページ上、1・2層の 1oz 最小線幅/間隔は **0.10/0.10mm（4/4mil）で通常能力**。追加料金の対象は「多層 3.0–3.5mil（4–8層は注文額の20%）」であり、2層には該当しない。
- 例外リスク（金額に含めず）：「Keyboard Design」加算 $16.41＋$49.25/m²（下記）。

## 1. 製造能力区分（一次情報）

出典はすべて JLCPCB 公式。取得記録は [capability-retrieval-records.json](../hardware/kicad/qualification/issue-133-wing-cost-check/capability-capture/capability-retrieval-records.json)（UTC 時刻・HTTP 200・SHA256）、HTML は `.html.gz`、本文は `.text.txt`。

| 項目 | 公式記載 | Wing 条件 | 判定 |
| --- | --- | --- | --- |
| 最小線幅/間隔（1oz） | 1・2層 0.10/0.10mm (4/4mil)。多層 0.09mm。2oz は 2層 0.16mm | 0.10/0.10mm, 1oz | 標準範囲内（下限ちょうど）。特殊仕様扱いの記載なし |
| 線幅公差 | ±20%（0.1mm 線は 0.08–0.12mm） | — | 製造余裕なし。公差は #131 の合格判定で別途考慮 |
| 追加料金規定 | 線幅/間隔の加算は「多層 3.0–3.5mil」のみ（4–8層 20%、10層以上 30%） | 2層 4mil | 該当せず |
| 最小ビア | 2層 0.15mm 穴/0.25mm 径。0.2/0.25mm 穴で径 0.45mm 未満、0.1/0.15mm 穴は「cost more」 | ドリル 0.30mm/外径 0.60mm | 標準（割増域の外）。計算機の既定オプション "0.3mm/(0.4/0.45mm)" 内 |
| 板厚 | FR4: 0.4/0.6/0.8/1.0/1.2/1.6/2.0mm | 1.2mm | 標準選択肢 |
| サイズ | 2層 FR4 最大 1020×600mm。≤102×102mm は特別価格 | 110×100, 116.5×104.75 | 範囲内。102×102 超のため通常の基板料金（特別価格は非適用） |

出典 URL：
- <https://jlcpcb.com/capabilities/pcb-capabilities>
- <https://jlcpcb.com/help/article/in-what-cases-will-there-be-charged-extra>

### 未解消リスク：Keyboard Design 加算

追加料金ページ項目16に「キーボード PCB（密集した切削スロット・切り欠き）には $16.41＋$49.25/m² を追加」とある。#131 の形状証跡（[geometry-evidence.json](../hardware/kicad/qualification/issue-133-wing-cost-check/geometry-evidence.json)）では両基板とも外形4辺のみ・内部 Edge.Cuts なし・NPTH 4個で、該当しない可能性が高いが、**製造側のファイル審査での判定は確認できない**。仮に基板1枚の面積に適用すると 16mm $16.95、17mm $17.01（計 約$33.96）だが、/m² の基準面積の解釈は未確認で、価格に含めていない。0.10mm 条件とは無関係の項目。

## 2. 素基板価格（5枚ロット）

取得方法：JLCPCB 見積もりページが使う公開計算 API（`calculationGoodsCostsNew`）へ、ログイン・アップロード・カート・発注なしの計算専用 POST（curl）。リクエストはサイトのフロントエンド実装が生成する既定のサービス選択を使用。スクリプト：[run-calculation-quotes.py](../hardware/kicad/qualification/issue-133-wing-cost-check/run-calculation-quotes.py)、リクエスト・応答（gz）・記録：[quote-capture/](../hardware/kicad/qualification/issue-133-wing-cost-check/quote-capture/)、集約：[price-evidence.json](../hardware/kicad/qualification/issue-133-wing-cost-check/price-evidence.json)。

条件：FR4 TG135-140、2層、1.2mm、外層 1oz、緑レジスト、白シルク、HASL（有鉛）、既定ビアオプション、納期 2 days（追加 $0）、1デザイン×5枚。

| 基板 | 寸法 (mm) | エンジニアリング費 | 基板料金 | 5枚計 | 1枚あたり |
| --- | --- | ---: | ---: | ---: | ---: |
| representative21-16mm | 110×100 | $4.00 | $5.30 | **$9.30** | $1.86 |
| representative21-17mm | 116.5×104.75 | $4.00 | $5.90 | **$9.90** | $1.98 |
| **合計（10枚）** | | $8.00 | $11.20 | **$19.20** | |

16mm は同条件で2回取得し同額（$9.30）。

**#124 との前提の差**：#124 の基板 $8.00 は PMO 提供値（4層 48×44mm、5枚）で、仕上げ・色・銅厚の記録がなく、前提を揃えられるかは確認不能。層数・寸法も異なるため金額比較には使わない。

## 3. 比較

### 0.10mm と 0.20mm

| 基板 | 0.10mm 前提 | 0.20mm 前提 | 差 |
| --- | ---: | ---: | ---: |
| 16mm | $9.30 | $9.30 | $0.00 |
| 17mm | $9.90 | $9.90 | $0.00 |

**注意（測定の限界）**：計算機の入力に線幅/間隔の項目は存在せず（見積もりフォームのサービス一覧にも無い）、0.10/0.20mm の2リクエストは同一（request_sha256 が同じ）。したがって「同額」は線幅を変えた応答の実測ではなく、「価格が線幅に依存する入力を持たない」ことの証跡である。裏付けは §1 の公式記載（2層 0.10mm は通常能力、加算規定は多層のみ）。線幅が実際に影響するのは、製造側ファイル審査での追加請求のみで、2層 4mil に該当規定は公開されていない。

### 両ピッチ同時発注

| 項目 | 金額 |
| --- | ---: |
| 基板代合計（16mm + 17mm、各5枚） | $19.20（うちエンジニアリング費 $8.00） |
| 送料（参考） | 未取得（宛先・配送業者の選択が必要。応答の送料リストは null） |
| 税 | 未取得 |

参考：基板重量は 5枚で 0.14kg（16mm）/0.16kg（17mm）（梱包除く）。同時発注時の送料の統合は未確認。

## 4. 判断

0.10mm 条件の採用による追加コストは **$0.00（両ロットとも）**。ロット費用は面積で決まり、17mm が 16mm より $0.60 高いのは基板面積差による。判断を覆しうるのは Keyboard Design 加算（0.10mm とは別要因・未確定）と送料のみ。

## 再現

リポジトリルートから：

```
python3 hardware/kicad/qualification/issue-133-wing-cost-check/fetch-capability-pages.py <outdir>
python3 hardware/kicad/qualification/issue-133-wing-cost-check/run-calculation-quotes.py <new-outdir>
```

価格は取得時点（2026-11-04 UTC）の値で、JLCPCB 側の改定で変わる。前任ワーカーの `collect-public-evidence.py`（urllib が接続リセットされ価格未取得のまま停止）は curl 版スクリプトに置き換えた。
