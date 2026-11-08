# Issue #219 — 発注用 CPL の生成と検証

## 成果物と検証結果

Main Rev.4 の55点、Matrix Rev.3 の43点について、元の CPL から Gerber 絶対座標フレームへ
平行移動した `CPL-jlcpcb-gerber-frame.csv` と由来注記を各 manufacturing に新規追加した。
全98点が PCB 由来の実装基準点と一致し、最大誤差は X/Y とも **0 mm**。
許容差は軸ごとに **0.000001 mm**（保存済み PCB/Gerber/CPL の小数6桁の1単位）。

| 基板 | 発注用 CPL | 由来注記 | 実装点 |
| --- | --- | --- | ---: |
| Main Rev.4 | [CSV](../issue-196-main-rev4-phaseb/manufacturing/CPL-jlcpcb-gerber-frame.csv) | [注記](../issue-196-main-rev4-phaseb/manufacturing/CPL-jlcpcb-gerber-frame-NOTES.md) | 55 |
| Matrix Rev.3 | [CSV](../issue-182-matrix-rev3/manufacturing/CPL-jlcpcb-gerber-frame.csv) | [注記](../issue-182-matrix-rev3/manufacturing/CPL-jlcpcb-gerber-frame-NOTES.md) | 43 |

原本は変更せず、追加は上記4ファイルと本報告・[verification.json](verification.json) の計6ファイル。
検証結果 JSON には全98行の Designator、PCB 原点、期待座標、出力座標、誤差、回転、
および入力75ファイルの個別 SHA-256 を記録した。

## データからの導出

基準コミットは `07ffa25ae16ee452e76fc5479ebfd0cdffc66cc2`。読み込んだ指示は `.cpl-runtime/instructions.md` 全文。
作業チェックアウトのローカルクローンを `.cpl-runtime/git` に作り、同じ作業ツリーを
`core.worktree=../..` で参照させた。ブランチは `issue-219-cpl-frame`。
スクラッチは `.cpl-runtime/` のみ。元のチェックアウトの git 状態は使用せず、push は行わない。

### Gerber と PCB 外形

両方の Edge_Cuts は `%FSLAX46Y46*%` / `%MOMM*%`、絶対座標・小数6桁・mm。
D02/D01 の全始終点を読み、線中心の最小・最大値を求めた。両方とも直線のみで曲線なし。
0.05 mm の描画幅は加えない（`.gbrjob` の描画幅を含む寸法とは区別する）。

| 基板 / 外形 Gerber | X 範囲 mm | Y 範囲 mm | 外接寸法 mm | 線分数 |
| --- | --- | --- | --- | ---: |
| Main / `main-rev4-Edge_Cuts.gm1` | 62.107317 … 137.892682 | −137.900000 … −72.267949 | 75.785365 × 65.632051 | 3 |
| Matrix / `m1-matrix18-Edge_Cuts.gm1` | 36.000000 … 164.000000 | −140.000000 … −60.000000 | 128 × 80 | 4 |

Main は `issue-196-main-rev4-phaseb/inspection/final/main.kicad_pcb`、
Matrix は `FABRICATION.md` 指定の `issue-182-matrix-rev3/board/m1-matrix18.kicad_pcb` を直接解析。
PCB の Edge.Cuts 全線分の両端を `(X,Y)→(X,−Y)` に変換すると Gerber の全線分と厳密一致した。
従って Gerber は KiCad シート原点の絶対座標で、Y 符号を反転したフレームと確認できる。

### 配置点による独立した移動量の決定

フットプリント直下の `at` と `property Reference` を S 式として解析し、
CPL の Designator に対応付けた。子要素の pad/text の `at` と混同していない。
各 PCB 実装基準点を `(KiCadX,−KiCadY)` に変換し、元 CPL 座標との差を全行で計算した。
部品ごとの追加補正を行わず、基板ごとに全行で同一の移動量になることを確認した。

| 基板 | データから得た `(ΔX, ΔY)` mm | 発注用変換式 |
| --- | --- | --- |
| Main | (+62.107318, −137.900000) | `X_order=X_original+62.107318; Y_order=Y_original−137.900000` |
| Matrix | (+36.000000, −140.000000) | `X_order=X_original+36; Y_order=Y_original−140` |

Main の `quote-handoff.md` にある理論的原点 `62.107317799` と今回の X 移動量との差は
0.000000201 mm。例えば C1 は PCB (85,125)、元 CPL (22.892682,12.9)。
`85−22.892682=62.107318` となり、全55点でこの差が一致する。
元 CPL が理論原点に対して小数6桁へ丸められているためであり、理論原点で加算してから
小数6桁へ丸めても今回の出力と全行一致する。保存済み Gerber/PCB 左端 62.107317 との差は
0.000001 mm。外形の値だけに合わせて全点へ 0.000001 mm の誤差を加えることはせず、
実装点照合から導出した値を用いた。Main の外接幅も保存済み外形では 75.785365 mm となり、
ハンドオフの高精度由来の 75.785364 mm との差は同じ1単位である。

Matrix は製造条件が示す KiCad 下左原点 (36,140) と一致する。
例として C_HA0 の PCB (53.5,74) と元 CPL (17.5,66) から (+36,−140) を得た。

### Matrix GH14 の既存重心契約

`J_WING` の PCB フットプリント原点は (100,133) mm、回転0°。
CPL が使うのは **本体重心 (100,135.325) mm** であり、フットプリント原点そのものではない。
これは `FABRICATION.md`、`assembly-review.json`、`export-manufacturing.py` に明示された従来仕様。
`hardware/tscircuit/src/qualification/JstGh14.tsx` の本体矩形中心も Y 上向きで (0,−2.325) mm。
PCB の正 Y は下向きなので、PCB 原点へ (0,+2.325) mm を加えて同じ実装基準点を再構成した。
従って期待する Gerber 座標は (100,−135.325) mm、元 CPL (64,4.675) からの差は
他42点と全く同じ (+36,−140) mm。生の PCB 原点へ一致させる変更はしていない。
この1点を除く Matrix の42点と Main の55点はフットプリント原点をそのまま使う。

## 検証と合格条件

1. **外形の導出と新規ファイル**：上記 Gerber の全線分を解析し、基板ごとに発注用 CPL を追加。
2. **PCB による導出の照合**：全55/43点からそれぞれ一意の移動量を得た。
   元 CPL の点集合だけから原点を推測せず、対応する PCB 実装基準点で照合した。
3. **全点と不変性**：生成後の CSV を読み直して全点照合。軸ごとの許容差 0.000001 mm に対し
   最大誤差0 mm。行数は元55/43→出力55/43、同じ行順、Designator 一意、Layer=`top`、
   Rotation は値と文字列表現とも完全同一。フットプリントは全点 F.Cu、PCB 回転値とも一致。
   別経路でも Main の既存 `native-pos-absolute.csv` と Matrix の既存 `assembly-review.json`
   の本体重心へ全98点が厳密一致した。
4. **由来注記**：各 manufacturing の新規注記に入力・用途・移動量・生成方法・許容差・結果・hash を記載。
5. **Y 方向と回転**：元 CPL は `Y=C−KiCadY`、Gerber は `Y=−KiCadY`。どちらも Y 上向きで
   差は定数のみ。全1485（Main）+903（Matrix）部品対の符号付き相対ベクトルを比較し厳密一致。
   線形部分は単位行列、鏡映・軸交換・回転・拡大縮小はないので Rotation を保持する。
   Main の J2=−120° / J3=+120° / J4=180° も保持し、Matrix は全0°。
   Matrix GH14 の重心差は基準点定義の差で、フレーム変換の線形部分を変えない。

原本の不変性は、生成の前後に基準コミットの **全14,967追跡ファイル**について、
`git cat-file --batch` で得た blob と現ファイルをそれぞれ SHA-256 で照合して確認した。
前後とも不一致0。元 CPL・Gerber・BOM・設計データを含め、既存ファイルは全て不変。
この全件 manifest はパス順に `SHA256 + 半角空白2個 + パス + LF` を連結したもので、
その SHA-256 は `408edd2cf9d8706dd5c63d6a86979d2873584bd2d371c0ee1d100a9f2b1be618`。
個別入力75ファイルの hash と新規 CPL の hash は `verification.json` に保存した。

用途は JLCPCB 発注時の座標フレームの整合。この作業ではアップロード・発注・課金は行っていない。
ライブラリ固有の重心・回転確認には引き続き既存の組立図と製造条件を使用する。

## 再現手順

Python 3 標準ライブラリのみ。KiCad の起動、外部ネットワーク、/tmp は不要。
下のコードが実際に実行した生成・検証コードである。
コードの SHA-256 は `a265edeed48f5f836731f5bbca7f747c8647934169a8f4325fe4816046d279aa`。
同じチェックアウトのルートで、次の操作によりスクラッチへ取り出して実行できる。
`.cpl-runtime/git` には上記基準コミットを含むローカルクローンが必要。
既存の入力ファイルは読み取りのみ、書き込み対象は派生 CSV 2個と `verification.json`。

```sh
python3 - <<'PY_REPLAY'
from pathlib import Path
p = Path('hardware/kicad/qualification/issue-219-cpl-frame/REPORT.md')
s = p.read_text().split('<!-- BEGIN REPLAY -->\n```python\n', 1)[1].split('\n```\n<!-- END REPLAY -->', 1)[0]
Path('.cpl-runtime/replay-219.py').write_text(s + '\n')
PY_REPLAY
python3 .cpl-runtime/replay-219.py
```

<!-- BEGIN REPLAY -->
```python
"""Issue 219: run at repository root; Python 3 standard library only."""
import csv
import hashlib
import io
import itertools
import json
from pathlib import Path
import re
import subprocess
from decimal import Decimal as D

BASE = '07ffa25ae16ee452e76fc5479ebfd0cdffc66cc2'
GIT = ['git', '--git-dir=.cpl-runtime/git']
ROOT = Path('hardware/kicad/qualification')
REPORT = ROOT / 'issue-219-cpl-frame'
TOL = D('0.000001')  # mm per axis, one stored coordinate unit
CONFIG = [
    ('Main Rev.4', ROOT / 'issue-196-main-rev4-phaseb',
     'inspection/final/main.kicad_pcb', 'main-rev4', 55),
    ('Matrix Rev.3', ROOT / 'issue-182-matrix-rev3',
     'board/m1-matrix18.kicad_pcb', 'm1-matrix18', 43),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(GIT + list(args))


def parse(path):
    stack = []
    root = None
    for token in re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+', path.read_text()):
        if token == '(':
            node = []
            if stack:
                stack[-1].append(node)
            stack.append(node)
        elif token == ')':
            root = stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    assert not stack and root[0] == 'kicad_pcb'
    return root


def children(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


def child(node, key):
    return children(node, key)[0]


def xy(node):
    return tuple(map(D, node[1:3]))


def gerber_edges(path):
    s = path.read_text()
    assert '%FSLAX46Y46*%' in s and '%MOMM*%' in s and 'G01*' in s
    assert not re.search(r'G0[23]\*', s)  # these two outlines contain only lines
    segments = []
    previous = None
    for x, y, op in re.findall(r'X(-?\d+)Y(-?\d+)D(0[12])\*', s):
        point = (D(x) / 1000000, D(y) / 1000000)
        if op == '01':
            assert previous is not None
            segments.append((previous, point))
        previous = point
    assert segments
    return segments


def bounds(segments):
    points = [p for segment in segments for p in segment]
    return [min(p[0] for p in points), min(p[1] for p in points),
            max(p[0] for p in points), max(p[1] for p in points)]


def read_csv(path):
    with path.open(newline='') as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def mid(row):
    assert row['Mid X'].endswith('mm') and row['Mid Y'].endswith('mm')
    return D(row['Mid X'][:-2]), D(row['Mid Y'][:-2])


def original_hashes():
    """SHA-256 every baseline blob and working file, including non-design files."""
    entries = git('ls-tree', '-r', '-z', BASE).split(b'\0')
    p = subprocess.Popen(GIT + ['cat-file', '--batch'], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    manifest = {}
    for entry in entries:
        if not entry:
            continue
        metadata, raw_path = entry.split(b'\t', 1)
        mode, kind, oid = metadata.split()
        assert kind == b'blob' and mode in (b'100644', b'100755')
        path = raw_path.decode()
        p.stdin.write(oid + b'\n')
        p.stdin.flush()
        header = p.stdout.readline().split()
        data = p.stdout.read(int(header[2]))
        assert p.stdout.read(1) == b'\n'
        expected = sha(data)
        assert sha(Path(path).read_bytes()) == expected, path
        manifest[path] = expected
    p.stdin.close()
    assert p.wait() == 0
    return manifest


def run():
    baseline = original_hashes()
    results = []
    for label, directory, pcb_rel, stem, count in CONFIG:
        pcb = directory / pcb_rel
        board = parse(pcb)
        footprints = {}
        for fp in children(board, 'footprint'):
            props = {v[1]: v[2] for v in children(fp, 'property')}
            ref = props['Reference']
            assert ref not in footprints
            footprints[ref] = fp
        edge_path = directory / f'manufacturing/gerber/{stem}-Edge_Cuts.gm1'
        segments = gerber_edges(edge_path)
        pcb_segments = []
        for line in children(board, 'gr_line'):
            if child(line, 'layer')[1] == 'Edge.Cuts':
                a, b = xy(child(line, 'start')), xy(child(line, 'end'))
                pcb_segments.append(((a[0], -a[1]), (b[0], -b[1])))
        assert sorted(segments) == sorted(pcb_segments)
        box = bounds(segments)
        source = directory / 'manufacturing/CPL.csv'
        output = directory / 'manufacturing/CPL-jlcpcb-gerber-frame.csv'
        fields, rows = read_csv(source)
        assert fields == ['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation']
        assert len(rows) == count == len({r['Designator'] for r in rows})
        points = []
        for row in rows:
            ref = row['Designator']
            fp = footprints[ref]
            at = child(fp, 'at')
            x, y = xy(at)
            origin = (x, y)
            if label == 'Matrix Rev.3' and ref == 'J_WING':
                # Existing body-centroid contract, FABRICATION.md / assembly-review.json.
                assert origin == (D(100), D(133)) and len(at) == 3
                y += D('2.325')
            rotation = D(at[3]) if len(at) > 3 else D(0)
            assert (D(row['Rotation']) - rotation) % 360 == 0
            assert row['Layer'] == 'top' and child(fp, 'layer')[1] == 'F.Cu'
            points.append((row, origin, (x, -y)))
        # Independently derive translation from ALL PCB placement / source CPL pairs.
        shifts = {(target[0] - mid(row)[0], target[1] - mid(row)[1])
                  for row, origin, target in points}
        assert len(shifts) == 1, shifts
        dx, dy = shifts.pop()
        assert abs(dx - box[0]) <= TOL and abs(dy - box[1]) <= TOL
        new_rows = []
        for row in rows:
            x, y = mid(row)
            new_rows.append(dict(row, **{'Mid X': f'{x+dx:.6f}mm',
                                        'Mid Y': f'{y+dy:.6f}mm'}))
        text = io.StringIO()
        writer = csv.DictWriter(text, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(new_rows)
        output.write_bytes(text.getvalue().encode())
        out_fields, actual = read_csv(output)  # verify the on-disk CSV, not just memory
        assert out_fields == fields and len(actual) == count
        details = []
        for (old, origin, target), new in zip(points, actual):
            for key in ('Designator', 'Layer', 'Rotation'):
                assert new[key] == old[key]
            position = mid(new)
            errors = tuple(abs(a-b) for a, b in zip(position, target))
            assert max(errors) <= TOL
            assert tuple(a-b for a,b in zip(position, mid(old))) == (dx, dy)
            details.append(dict(designator=new['Designator'], pcb_origin_mm=origin,
                                expected_gerber_mm=target, actual_gerber_mm=position,
                                absolute_error_mm=errors, rotation=new['Rotation']))
        # Secondary readback against pre-existing qualified assembly exports.
        if label == 'Main Rev.4':
            _, native_rows = read_csv(directory / 'manufacturing/native-pos-absolute.csv')
            reference = {r['Ref']: (D(r['PosX']), D(r['PosY'])) for r in native_rows}
        else:
            ledger = json.loads((directory / 'assembly-review.json').read_text())
            reference = {r['reference']: (D(str(r['body_centroid_kicad_mm'][0])),
                         -D(str(r['body_centroid_kicad_mm'][1]))) for r in ledger['parts']}
        for row in actual:
            assert mid(row) == reference[row['Designator']]
        pairs = 0
        for a, b in itertools.combinations(range(count), 2):
            pa, pb = mid(rows[a]), mid(rows[b])
            ta, tb = points[a][2], points[b][2]
            # Original CPL and PCB->Gerber have identical signed pairwise vectors.
            assert tuple(x-y for x,y in zip(pb, pa)) == tuple(x-y for x,y in zip(tb, ta))
            pairs += 1
        results.append(dict(board=label, pcb=str(pcb), source=str(source), output=str(output),
                            source_sha256=sha(source.read_bytes()), output_sha256=sha(output.read_bytes()),
                            gerber_centerline_bounds_mm=box, edge_segments=len(segments),
                            pcb_gerber_edges_exact=True, secondary_export_matches=count,
                            translation_mm=(dx, dy),
                            source_rows=count, output_rows=len(actual), pairwise_vectors_checked=pairs,
                            designators_layers_rotations_order_unchanged=True,
                            max_absolute_error_mm=max(max(r['absolute_error_mm']) for r in details),
                            points=details))
    # All original tracked files still match baseline, not merely the input subset.
    after = original_hashes()
    assert after == baseline
    selected = {p: h for p,h in baseline.items() if any(
        p.startswith(str(d / 'manufacturing') + '/') or p == str(d / pcb)
        for _,d,pcb,_,_ in CONFIG)}
    for p in ['hardware/kicad/qualification/issue-182-matrix-rev3/assembly-review.json',
              'hardware/tscircuit/src/qualification/JstGh14.tsx']:
        selected[p] = baseline[p]
    manifest = ''.join(f'{h}  {p}\n' for p,h in sorted(baseline.items())).encode()
    report = dict(base_commit=git('rev-parse', BASE).decode().strip(),
                  tolerance_mm_per_axis=TOL, boards=results,
                  preservation=dict(algorithm='SHA-256', original_tracked_files=len(baseline),
                                    mismatches_before=0, mismatches_after=0,
                                    sorted_sha256_manifest_digest=sha(manifest),
                                    selected_original_sha256=selected))
    REPORT.mkdir(exist_ok=True)
    (REPORT / 'verification.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str) + '\n')
    print(json.dumps({r['board']: {'rows': r['output_rows'],
          'translation_mm': r['translation_mm'], 'max_error_mm': r['max_absolute_error_mm']}
          for r in results}, default=str))
    print('SHA-256 preserved original tracked files:', len(baseline))


if __name__ == '__main__':
    run()
```
<!-- END REPLAY -->
