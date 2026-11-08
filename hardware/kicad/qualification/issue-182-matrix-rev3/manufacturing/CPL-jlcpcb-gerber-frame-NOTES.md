# Matrix Rev.3 — JLCPCB 発注用 CPL / Issue #219

JLCPCB の配置ビューアへ既存 Gerber と組み合わせて渡す CPL は
[`CPL-jlcpcb-gerber-frame.csv`](CPL-jlcpcb-gerber-frame.csv)。
元の [`CPL.csv`](CPL.csv) を Gerber 絶対座標フレームへ平行移動した派生ファイル。
この注記と組み合わせて使用する。

- 単位 mm、X 右向き・Y 上向き。`X_order = X_original + 36.000000`、`Y_order = Y_original + (-140.000000)`。
- Edge_Cuts の線中心の外接範囲 `[Xmin,Ymin,Xmax,Ymax]` = `[36, -140, 164, -60]` mm。
  外形線の描画幅 0.05 mm は基板寸法に加算していない。
- 移動量は元 CPL と、`../board/m1-matrix18.kicad_pcb` の部品位置を
  `(KiCadX,−KiCadY)` に変換した座標の差を全 43 点で照合して導出。
  PCB の外形線も Gerber の全外形線と一致。
- 行数 43、行順・Designator・Layer・Rotation は元 CPL と同一。
  回転値は文字列もそのまま保存。両フレームで Y 上向きなので反転・回転補正を加えない。
- 許容差は軸ごとに 0.000001 mm。全 43 点で最大座標誤差は 0 mm。
  全 903 部品対で元 CPL と PCB→Gerber の符号付き相対ベクトルも一致。

GH14 (`J_WING`) は従来どおり本体重心を使う。PCB のフットプリント原点 (100,133) mm に、`FABRICATION.md` と `../assembly-review.json` に記録された KiCad 座標での本体重心差 (0,+2.325) mm を加え、発注用座標は (100,−135.325) mm。原点との 2.325 mm の差は従来の重心定義であり、フレーム変換や回転の追加補正ではない。

生成は Python 標準ライブラリの `Decimal` で座標だけを加算し、小数6桁・`mm` 付きで出力。
生成コード、全点の照合結果、既存ファイルの SHA-256 不変照合は
[Issue #219 作業報告](../../issue-219-cpl-frame/REPORT.md) と
[機械可読の検証結果](../../issue-219-cpl-frame/verification.json) を参照。
元 CPL・Gerber・BOM・PCB を含む既存の追跡ファイル 14,967 個を変更していない。

| ファイル | SHA-256 |
| --- | --- |
| 元 `CPL.csv` | `1a5b37151a89bd3e6f77f5cb6c3ab2110f8eb13e696847a1c0154d8e6ae66ebb` |
| 発注用 `CPL-jlcpcb-gerber-frame.csv` | `4a275556b8f077b02862d5eafe6a2a58a44b959f4f433259d2bb0f0ce2f98153` |

用途は JLCPCB 発注時の Gerber と CPL の座標合わせ。既存の部品重心と回転の定義を維持する。
メーカーライブラリ固有の重心・pin 1・回転の実装確認は既存の製造条件と組立図を併用する。
この作業では業者へのアップロード・発注は行っていない。
