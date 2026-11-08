# Main Rev.4 — JLCPCB 発注用 CPL / Issue #219

JLCPCB の配置ビューアへ既存 Gerber と組み合わせて渡す CPL は
[`CPL-jlcpcb-gerber-frame.csv`](CPL-jlcpcb-gerber-frame.csv)。
元の [`CPL.csv`](CPL.csv) を Gerber 絶対座標フレームへ平行移動した派生ファイル。
この注記と組み合わせて使用する。

- 単位 mm、X 右向き・Y 上向き。`X_order = X_original + 62.107318`、`Y_order = Y_original + (-137.900000)`。
- Edge_Cuts の線中心の外接範囲 `[Xmin,Ymin,Xmax,Ymax]` = `[62.107317, -137.9, 137.892682, -72.267949]` mm。
  外形線の描画幅 0.05 mm は基板寸法に加算していない。
- 移動量は元 CPL と、`../inspection/final/main.kicad_pcb` の部品位置を
  `(KiCadX,−KiCadY)` に変換した座標の差を全 55 点で照合して導出。
  PCB の外形線も Gerber の全外形線と一致。
- 行数 55、行順・Designator・Layer・Rotation は元 CPL と同一。
  回転値は文字列もそのまま保存。両フレームで Y 上向きなので反転・回転補正を加えない。
- 許容差は軸ごとに 0.000001 mm。全 55 点で最大座標誤差は 0 mm。
  全 1485 部品対で元 CPL と PCB→Gerber の符号付き相対ベクトルも一致。

Main の `quote-handoff.md` にある高精度原点 X=62.107317799 mm と、6桁の元 CPL から導出した今回の X 移動量 62.107318 mm の差は 0.000000201 mm。高精度原点で移動して小数6桁へ丸めても、今回の発注用 CPL と全行同一になる。Gerber/PCB の保存済み左端 X=62.107317 mm との差 0.000001 mm は座標の量子化による。

生成は Python 標準ライブラリの `Decimal` で座標だけを加算し、小数6桁・`mm` 付きで出力。
生成コード、全点の照合結果、既存ファイルの SHA-256 不変照合は
[Issue #219 作業報告](../../issue-219-cpl-frame/REPORT.md) と
[機械可読の検証結果](../../issue-219-cpl-frame/verification.json) を参照。
元 CPL・Gerber・BOM・PCB を含む既存の追跡ファイル 14,967 個を変更していない。

| ファイル | SHA-256 |
| --- | --- |
| 元 `CPL.csv` | `7b65636c545658c26c964b619a58e983da0ba15687bf437b00553fd586678aa1` |
| 発注用 `CPL-jlcpcb-gerber-frame.csv` | `67e0c2c0b08f2992d8af044597c4daa979e76d35287cae75446e462dff8a6aee` |

用途は JLCPCB 発注時の Gerber と CPL の座標合わせ。既存の部品重心と回転の定義を維持する。
メーカーライブラリ固有の重心・pin 1・回転の実装確認は既存の製造条件と組立図を併用する。
この作業では業者へのアップロード・発注は行っていない。
