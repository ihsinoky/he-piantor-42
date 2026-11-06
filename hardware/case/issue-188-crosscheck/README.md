# Issue #188 照合の証跡

`docs/issue-188-case-crosscheck.md` の数値の抽出・計算記録。読取り専用（CAD・既存ファイルは書き換えない）。

## 再現

```
python3 hardware/case/issue-188-crosscheck/extract.py --csv hardware/case/issue-188-crosscheck/wing-keys-check.csv > hardware/case/issue-188-crosscheck/extracted.json
```

標準ライブラリのみ（Python 3.12 で確認）。作業ツリーのどこから実行してもよい。同じ入力なら `extracted.json` はbyte一致する。

| ファイル | 内容 |
| --- | --- |
| `extract.py` | 抽出・照合スクリプト。#150 の `measure.py` のS式パーサ関数だけを再利用し、トップレベル処理は実行しない |
| `extracted.json` | 全結果。`input_sha256` に使った入力ファイルのSHA256を記録 |
| `wing-keys-check.csv` | Wing 16/17mm 各21キーの Rev.1 基板座標と #150 `keys-*.csv` の差（全て0） |

## `extract.py` が失敗（assert）で止まる条件

- Main Rev.3 の H1〜H4 が D-023 座標・φ2.2 でない、または全4銅層・tracks/vias/copperpour 禁止の半径2.5予約が無い
- Gerber（Edge_Cuts／NPTH）がネイティブ基板と一致しない（Main、Wing 両ピッチ）
- Wing Rev.1（#149／#151）の外形・穴・部品が #150 の計測値、凍結済み #149 インタフェースと一致しない
- Wing 21キーのセンサ座標が #150 の `keys-*.csv` と一致しない、またはセンサが F.Cu・回転0でない

## 値の区別

- 基板座標・穴・パッド寸法：実データからの抽出（設計値）
- J3 本体投影 X94.625–115.375／Y73.2–77.45、GHR-14V-S 投影（18.75×4.15）：docs/issue-163・160 の公表値／設計値を転記。実ラッチdatumは不明（実測待ち）
- 部品最大高さ・ハーネス実経路：入力が無いため計算していない（判定不能）
- `harness.planar_center_distance_upper_bound_mm`：2つの90°曲げ（曲げ中心線半径R）と水平直線だけで同一平面の2コネクタを結ぶ最短経路の逆算。実ハーネスの上限ではなく、これより長い中心間距離は確実に届かないという**楽観側の上界**
