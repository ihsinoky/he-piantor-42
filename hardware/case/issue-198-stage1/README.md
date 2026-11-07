# Issue #198 Stage 1 mechanical study

[日本語報告書](../../../docs/issue-198-case-stage1.md)。製造承認用データではない。

- `generate.py`: build123d パラメトリックモデル。17mmが既定、`--pitch 16`で切替。
- `17mm/`, `16mm/`: 組立STEP、トレー全体・左右分割STEP/STL、寸法・干渉JSON、上面SVG、検証JSON。
- `assembly.step` はトレー＋Main＋Wing L/R＋UDBの5 solid。スイッチ・キーキャップ・ケーブルは実体部品ではなくJSON/SVGでの包絡検査。ケーブルは未認定。
- `tray-left/right` はX=3.5mmの突合せ切断形状。接合板・ねじ穴の詳細はStage 2。
- `verify.py`: STEP再読込、STL watertight検査・体積照合、入力・出力SHA、穴座標の逆変換、組立5 solidの全10組の体積干渉を検査。

依存: Python 3.12、build123d 0.13.0、Shapely 2.2.0、sexpdata 1.0.2。
標準環境では同じvenvにこれらをインストールして実行する。この作業環境では既設CAD venvと読み取り専用のgeometry環境を併用した。リポジトリrootから:

```bash
mkdir -p ../tmp
export TMPDIR="$PWD/../tmp"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/geometry/lib/python3.12/site-packages
CAD_PY=/home/hatch/workspace/tools/cad-venv/bin/python
"$CAD_PY" hardware/case/issue-198-stage1/generate.py
"$CAD_PY" hardware/case/issue-198-stage1/verify.py
"$CAD_PY" hardware/case/issue-198-stage1/generate.py --pitch 16 --out hardware/case/issue-198-stage1/16mm
"$CAD_PY" hardware/case/issue-198-stage1/verify.py hardware/case/issue-198-stage1/16mm
```

作業コピーの親が `.issue198-runtime/`。スクラッチはその `tmp/` のみ。`--csv-dir`で同じ列構成のCSVセットを差替え可能。GH位置は指定ピッチのWing Phase B definitionも照合する。設計仮定はスクリプト冒頭`P`および各`dimensions.json`に明示。

UDB寸法はリポジトリ内に保存済みの upstream C3 KiCadデータから抽出。upstream commit・入力SHAは寸法JSONに記録し、ライセンスを`UDB-LICENSE`に収録した。STL/STEPの再出力でOCCの内部IDやタイムスタンプが変わり得るため、検証はファイルhashに加えて形状・体積で行う。`exports-sha256.json`は生成時に更新し、検証結果自体はhash対象から除外する。
