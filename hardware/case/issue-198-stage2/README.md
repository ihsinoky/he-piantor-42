# Issue #198 Stage 2

[日本語報告書](../../../docs/issue-198-case-stage2.md)。入力は **Wing Rev.3 Stage 1b（配線前形状提案）**。基板の最終製造データではない。

- `generate.py`: CSV 入力、17/16mm 選択、南縁の高さ切替。
- `base.py`: Stage 1 の基板抽出・座標変換・外周生成を継承。
- `details.py`: 接合、ねじ／座金、ゴム足、ラック、3Dハーネスと距離計測。
- `verify.py`: STEP再読込、STL閉多様体／体積、印刷包絡、組立干渉、入力hash、穴の逆変換。
- `inputs/wing-rev3-stage1b.json`: 指定ブランチから取得した変更なしの形状入力。
- `inputs/rev3-stage1b/`: 形状から抽出した outline/holes CSV、変更なしの Rev.2 keys CSV。除去された穴を戻さない。
- `17mm/`: 組立・各印刷部品の STEP、各印刷部品の STL、経路 STEP、200mm余長収納包絡 STEP、検証値・上面 SVG。
- `16mm/`: 同じパイプラインによる再生成確認。

`assembly.step` はケース、4基板、ねじ・座金・ゴム足、2本のGH実経路、Main部品およびWing GHの設計包絡。包絡はメーカーCADではない。ねじは外径2mmのねじ山を省略した芯径1.6mmのモデル。`storage-200mm.step` は30mmのアプローチ／サービス割当を除く余長を束ねる収納包絡であり、追加ケーブルや連続200mm配索のSTEPではない。

Python 3.12、依存は `requirements.txt`。本環境では既設のCAD環境を変更せず `.issue198-runtime/pydeps` に Shapely/sexpdata だけを追加した。

```bash
# 作業コピーrootから。スクラッチは .issue198-runtime/ 内のみ。
export TMPDIR="$PWD/../tmp"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$PWD/../pydeps"
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
CAD_PY=/home/hatch/workspace/tools/cad-venv/bin/python
"$CAD_PY" hardware/case/issue-198-stage2/generate.py
"$CAD_PY" hardware/case/issue-198-stage2/verify.py
"$CAD_PY" hardware/case/issue-198-stage2/generate.py --pitch 16
"$CAD_PY" hardware/case/issue-198-stage2/verify.py hardware/case/issue-198-stage2/16mm
```

`--csv-dir DIR` で outline/holes/keys の同じ列構成の最終CSVに差し替える。GH位置・経路・datumも更新された場合は `--geometry FILE` に対応する形状JSONを渡す。入力の最大Yを新datumにしない。北タブで外形が伸びても Stage 1 の内側北角をdatumに保持する。`--prepare-inputs` は指定JSONからCSVバンドルを再作成する操作で、最終CSVを渡す場合は使わない。

`--palm-offset 0` がフラッシュ、`--palm-offset -0.5 --out DIR` は基板上面より0.5mm低い縁。正の値は拒否する。基板・キー高さ・壁厚は変えない。

基礎形状の再計算を省く STEP キャッシュを作業コピーの親 `.issue198-runtime/` に置く。入力ファイル、base.py、南縁設定をhash化しており、入力変更時は無効化される。通常のチェックアウトでは同じ親ディレクトリにスクラッチ用ディレクトリを用意すること。
