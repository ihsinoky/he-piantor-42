# Issue #198 最終データ

[日本語報告書](../../../docs/issue-198-case-final.md)。入力は Wing Rev.3 の確定データ（Issue #200、PR #201、D-034、main 932b880）。Stage 2（`../issue-198-stage2/`）の生成器を引き継ぎ、入力の差し替えと検証の追加のみを行った。

- `inputs/rev3-final/`: `hardware/case/issue-200-rev3/` の確定 CSV（outline/holes/keys、16/17mm、左右）を変更なしで複製。
- `inputs/wing-rev3-geometry.json`: `hardware/case/issue-200-stage1/geometry.json`（main 932b880、Stage 2 入力と同一）。GH 組立位置 (∓27,−41)、ハーネス経路、datum。
- `generate.py` / `base.py` / `details.py`: Stage 2 と同じ。固定点は holes CSV の `mounting` 行から取り、手作業の形状修正はない。固定点15点・GH位置の一致・各ボスの存在は生成時に assert する。
- `verify.py`: STEP再読込、STL、印刷包絡、組立干渉、入力hash、穴の逆変換、固定点15点とボス。
- `17mm/`（正）、`16mm/`（再生成と検証）: 組立・各ピース STEP/STL、経路、200mm 収納包絡、`dimensions.json`、`verification.json`、`review.svg`。

```bash
# 作業コピーrootから。スクラッチは .issue198-runtime/ 内のみ。
export TMPDIR="$PWD/../tmp" PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/../pydeps" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
CAD_PY=/home/hatch/workspace/tools/cad-venv/bin/python
"$CAD_PY" hardware/case/issue-198-final/generate.py
"$CAD_PY" hardware/case/issue-198-final/verify.py
"$CAD_PY" hardware/case/issue-198-final/generate.py --pitch 16
"$CAD_PY" hardware/case/issue-198-final/verify.py hardware/case/issue-198-final/16mm
```

`--palm-offset 0`（既定、フラッシュ）／`-0.5 --out DIR`（南縁を0.5mm下げる）。南辺の最終判断は PO 持ち越し。基礎形状の STEP キャッシュは作業コピーの親ディレクトリに作られ、入力変更で無効になる。
