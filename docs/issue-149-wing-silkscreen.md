# Issue #149 — Wing シルク追加の改版

**16mm／17mm の両ピッチに表シルクを追加し、銅箔・穴・外形・マスクの同一性、再実行DRCの違反0／未配線0、再生成製造データとGerber印刷像を確認した。** 改版は `SILK-149A`。製造データ候補は以下の2 ZIPであり、**#147のシルクなし製造ZIPを本改版のZIPに置き換える**。#147の既存ファイルは保持した。

[Issue #149](https://github.com/ihsinoky/he-piantor-42/issues/149) の継続実行。指示書を全文読み、GitHubから取得した最新Issueと保存済み内容の一致を確認した。作業開始時の16mmフォルダは空で、先runのPCB・DRC・製造出力は存在しなかった。既存の `add-silkscreen.py`、`common.py`、`issue149.json` を保存し、新しい生成・検査スクリプトと成果物を追加した。

以下の `E/` は [issue-149-wing-silkscreen/](../hardware/kicad/qualification/issue-149-wing-silkscreen/)。発注・課金・メーカーサイトへのアップロード・mergeは実施していない。Draft PRで設計レビューに提出する。

## 対象と製造ZIP

| 項目 | 16mm | 17mm |
| --- | --- | --- |
| 入力 | #141 `KRT-16-2L-P0300/out.kicad_pcb` | #141 `KRT-17-2L-P0300/out.kicad_pcb` |
| 入力SHA256 | `3f29d24274c6e1834cf344c1c9c3bb234cd1aefa1e85d6eb3e8470eb5f2383f4` | `e7744a86e65459905b7629f2c8a13c60f1c0aa1d26c85139ac1c893d634e5939` |
| 改版基板 | [wing-16mm-silk149.kicad_pcb](../hardware/kicad/qualification/issue-149-wing-silkscreen/16mm/wing-16mm-silk149.kicad_pcb) | [wing-17mm-silk149.kicad_pcb](../hardware/kicad/qualification/issue-149-wing-silkscreen/17mm/wing-17mm-silk149.kicad_pcb) |
| 外形中心線の寸法 | 110 × 100mm | 116.5 × 104.75mm |
| ZIP | [wing-16mm-silk149-review.zip](../hardware/kicad/qualification/issue-149-wing-silkscreen/wing-16mm-silk149-review.zip) | [wing-17mm-silk149-review.zip](../hardware/kicad/qualification/issue-149-wing-silkscreen/wing-17mm-silk149-review.zip) |
| ZIP SHA256 | `37b5ed1246178bcee28aeb4d2c41f849e2977be189a70c42f10281548d895963` | `622b3b2d806258b67a08114af2c31960794ad2e80370fa1948cb615c7c93c636` |
| 配線線分／ビア／SMDパッド／NPTH | 808／196／190／4 | 681／198／190／4 |
| 再実行DRC | 違反0・未配線0 | 違反0・未配線0 |

入力の完全パスは `hardware/kicad/qualification/issue-141-wing-power-integrity/runs/` 以下。#141の拡幅済み合格出力を使用し、配線変更は行っていない。

各ZIPは #147 と同じ9本構成：F.Cu、B.Cu、F.Mask、B.Mask、F.Silkscreen、B.Silkscreen、Edge.CutsのGerber計7本と、PTH／NPTHを分離したExcellon計2本。単一設計、絶対原点、Gerberはmm・小数6桁、ドリルはmm・小数表記。ZIP CRCと全メンバーのbyte一致を確認した。`gbrjob`、ペースト参考出力、プレビュー、証跡、比較入力はZIPに含めない。PCBA・ステンシルのデータを注文対象に追加していない。

## 追加したシルク

追加は基板レベルの `F.SilkS` 図形・文字183個／ピッチだけ。元の隠されたReference／Valueやフットプリント定義は変更しない。

- 全68フットプリントのReferenceを1回ずつ表示：DRV5055×21、TMUX1208×3、コンデンサ×24、J_WING、テストポイント×15、取付穴×4。
- 全21センサ中心に、各ピッチを一辺とする正方形のキー位置枠。共有辺は重複を除去し、上辺のテストパッド周囲だけ線に切れ目を入れた。最も切れ目の多い枠でも周長の87.06%／87.82%を描き、21位置とピッチ寸法を維持する。これはキー位置の表示であり、実スイッチ外形や筐体クリアランスの認定ではない。
- DRV5055×21、TMUX1208×3、J_WINGのpin1に小円。各マークに最も近いパッドが一意にpin1であることを解析確認。凡例 `DOT = PIN1` を付けた。
- J_WINGに `1 +5V` と `CABLE`、ケーブルアクセス領域方向の矢印。pin1ネットは元基板の `HALL_5V` と一致する。definitionのケーブル領域は基板座標の下方向にあり、向きも一致する。GRM188のコンデンサには極性マークを付けていない。
- 取付穴4点を半径2.1mmのリングとH1〜H4で表示。リングは印刷マークであり、後述のφ5.0mmキープアウトを表す線ではない。
- `HE PIANTOR WING 16mm/17mm Rev SILK-149A`、キー枠の凡例。通常文字高0.8mm、基板名1.0mm、文字線幅0.12mm、図形線幅0.15mm。裏面シルクは空のまま。

配置は `hardware/jitx/wing/generated/representative21-{16,17}mm/` の `placements.csv` と `definition.json` を用い、全配置の座標をnative PCBと照合。#141のinventoryの全配線とも照合した。入力hashと各図形の役割・座標は各ピッチの `design-evidence.json` に保存した。

継承スクリプトはキー枠とテストパッドが干渉するため生成前に停止した。採用スクリプト `E/build-silkscreen.py` で枠の切れ目、pin1マーク、穴リング、基板名の配置を調整した。元のスクリプトと既存ファイルは変更していない。

## 同一性・DRC・製造データ検証

| 検証 | 結果・証跡 |
| --- | --- |
| 全非シルク要素の保持 | 元PCBの最終閉じ括弧直前にだけ追記。追加文字列を除くと元PCBの全バイトが復元される。配線・ビア・パッド・穴・外形・マスク設定・ルールエリアを含む既存要素の書換え0。`identity-checks.json` |
| native解析 | 全配線の始終点・幅・層・ネット、全ビアの位置・径・穴径・層・テント、全194パッドの位置・寸法・穴・向き・属性・層・ネット・UUID、外形線を追加前後で照合。全件一致。プロジェクトもbyte一致 |
| 独立CAM解析 | Gerbonara 1.5.0で全Gerber／Excellonを再読込み。配線・ビア・SMDパッド・外形・マスク・穴をnative在庫と照合。加えて#147の銅箔・マスク・外形・PTH／NPTH全図形を比較して一致。`manufacturing-checks.json`、各 `cam-identity.json` |
| DRC再実行 | KiCad 9.0.9、元プロジェクト、`--severity-all --all-track-errors --exit-code-violations`。両ピッチで終了0・違反0・未配線0。silk_over_copper／silk_overlap／silk_edge_clearanceはwarningとして有効、除外0。`processes/{16,17}mm-drc/`、各 `drc.json` |
| シルクのパッド回避 | パッド外接矩形を0.28mm拡張して避け、枠の端点にも余裕を設ける。マスク差引き出力も使用。DRCはシルク干渉を含め0。`silkscreen-checks.json` |
| マスク | F.Maskは190開口、B.Maskは0。元と同一。ビアは両面テント |
| ドリル | PTH φ0.30mm×196／198、NPTH φ2.2mm×4、長穴0。Excellonの0.001mm丸めに対し、同径・各軸0.0005mm以内の一意対応で全穴消費。最大位置差は約0.000075mm、NPTHは完全一致 |
| 印刷像 | 表シルクのdark図形は3,276／3,257。実Gerberをオフラインビューアで描画して枠・文字・マークの印刷像を確認。裏シルクはdark図形0。`visual-review.json` |

GerbonaraのG90ヘッダ位置警告は記録済み。絶対座標として全穴を一意照合でき、#147とのCAM一致も確認した。最初のCAM比較では描画境界キャッシュの有無が文字列表現に現れたため、両ファイルを新規読込みして比較した。図形データ自体の差はない。

元の最小シルク間隔設定0mmは変更せず、追加配置側でパッドへの余裕を持たせた。DRC合格や画像をメーカーDFM認証とは呼ばない。電気条件、メーカーの印刷能力・番号配置・製造公差・費用承認は従来の後続確認として残る。

## Gerberビューア確認

Gerbonaraで各実Gerber／ExcellonからSVGを生成し、CairoSVGで白背景のPNGを作成。CADの画面やイメージ生成画像を製造証跡に使っていない。

| ピッチ | 表シルク印刷像 | 全9レイヤー一覧 | 表銅箔＋穴 |
| --- | --- | --- | --- |
| 16mm | [表シルク](../hardware/kicad/qualification/issue-149-wing-silkscreen/16mm/preview-review/front-silkscreen.png) | [一覧](../hardware/kicad/qualification/issue-149-wing-silkscreen/16mm/preview-review/all-layers.png) | [表銅箔＋穴](../hardware/kicad/qualification/issue-149-wing-silkscreen/16mm/preview-review/top-copper-holes.png) |
| 17mm | [表シルク](../hardware/kicad/qualification/issue-149-wing-silkscreen/17mm/preview-review/front-silkscreen.png) | [一覧](../hardware/kicad/qualification/issue-149-wing-silkscreen/17mm/preview-review/all-layers.png) | [表銅箔＋穴](../hardware/kicad/qualification/issue-149-wing-silkscreen/17mm/preview-review/top-copper-holes.png) |

両ピッチの表シルクを拡大して確認し、6列×3段＋親指3位置のキー枠、全域のReferenceと小円、J_WINGのpin1と下向き矢印、4穴リング、ピッチ／リビジョン文字を確認した。上部テストパッド周囲の切れ目は意図した回避であり、欠落ではない。全レイヤー一覧の空のB.Mask／B.Silkscreenも入力構成どおり。各層画像と裏銅箔＋穴も保存した。

## 筐体向け取付穴座標

単位はmm。**KiCad基板ファイルの絶対座標系（表から見てX右向き、Y下向き）**。definition座標からは `X = 100 + x_mm`、`Y = 100 - y_mm` に変換する。左右・表裏を反転した筐体座標ではない。16mm外形境界はX=45〜155、Y=50〜150、17mmはX=41.75〜158.25、Y=47.625〜152.375。穴中心は各辺から3mm。

| ピッチ | 穴 | X | Y | NPTH径 | 公称キープアウト径 |
| --- | --- | ---: | ---: | ---: | ---: |
| 16mm | H1 | 48.000 | 147.000 | 2.2 | 5.0 |
| 16mm | H2 | 48.000 | 53.000 | 2.2 | 5.0 |
| 16mm | H3 | 152.000 | 147.000 | 2.2 | 5.0 |
| 16mm | H4 | 152.000 | 53.000 | 2.2 | 5.0 |
| 17mm | H1 | 44.750 | 149.375 | 2.2 | 5.0 |
| 17mm | H2 | 44.750 | 50.625 | 2.2 | 5.0 |
| 17mm | H3 | 155.250 | 149.375 | 2.2 | 5.0 |
| 17mm | H4 | 155.250 | 50.625 | 2.2 | 5.0 |

機械可読表は各ピッチの `mounting-holes.csv`。径・中心はdefinition、native NPTH、出力ドリルを照合した。キープアウトはdefinitionの公称φ5.0mmと元PCBの4ルールエリアを照合し、既存の円近似ポリゴンの半径差0.0003mm以内を確認した。ネジ頭・ワッシャ・ボスの実物寸法や製造穴公差をこの表で認定するものではない。

## 保存・再現・提出

追加先は本報告書と `E/` のみ。再開時の既存49,477パスを `E/protected-resume-hashes.json.gz` で固定し、最終監査で全件不変・変更0を確認した。通常 `.git` は変更せず、`.issue149-runtime/git` に分離した `issue-149-wing-silkscreen` ブランチを使用した。一時ファイルと設定は `.issue149-runtime/` に置き、既存KiCad／Gerbonaraランタイムを読取り専用で再利用した。

#147の比較入力は `E/inputs/issue147/` にbyte一致コピーし、由来とhashを `E/inputs/provenance.json` に残した。未マージの [#147 Draft PR #148](https://github.com/ihsinoky/he-piantor-42/pull/148) の作業ツリーに依存せず検査できる。比較入力を製造用ZIPと取り違えない。

`git diff --check` の空白警告は、byte一致を保つため残した元PCBの253／296行と、継承 `common.py` 末尾の空行だけ。全PCB警告行を元入力行と照合し、新規の空白エラーはない（`E/whitespace-audit.json`）。

再現手順は `E/README.md`。`E/final-verification.json` は保護ファイル・JSON・構文・リンク・ZIP・成果物を検査し、`E/manifest.json` は報告書を含む成果物hashを記録する。公開結果は `E/publication.json` と最終応答で報告し、push不能の場合も分離Gitのコミットを保持する。承認・発注GOとmergeはPO判断に残す。
