# Issue #153 Stage 1 evidence

報告書：[docs/issue-153-main-mounting-stage1.md](../../../../docs/issue-153-main-mounting-stage1.md)。
このディレクトリは調査・配置案のみ。KiCad基板／project、ルータ出力、製造用ファイルを新規生成・変更していない。

| ファイル | 内容 |
| --- | --- |
| instructions.md / issue.json | 指定指示書全文／取得したIssue #153本文 |
| finish-instructions.md | 中断後の仕上げ指示書全文。今回のタイムボックスは1時間 |
| inputs.json | main起点、入力SHA256、Wing穴前例、開始時未追跡だった#150のMain支持段落 |
| measure.py / measurements.json | S式の独立読取り、199パッド・540線・66ビア・40 courtyardの実形状、19候補、全板0.5mm格子の評価 |
| native-check.py / native-crosscheck.json | KiCad 9.0.9の実効形状で寸法・干渉・既存72ドリル・GND充填との重なりを再照合 |
| candidates.csv | 19候補のXY、各案外形左上を原点とするローカルXY、板端距離、φ5と各既存形状の符号付き隙間 |
| affected-copper.csv | 第一案Aでφ5にかかる3セグメントのnet／層／端点／幅／UUID |
| plans.json | Aの4穴、A0の3穴、Bの拡張4穴、全組の穴間距離と直接影響UUID |
| retained-outline.svg / extended-outline.svg | 既存基板形状への配置案重ね合わせ。図の穴は基板へ反映していない |
| survey-map.svg | 全板走査の候補中心分布。緑でもGNDの抜きは必要 |
| build-assets.py | CSV・図・入力記録の再生成。書込み先はこの新規証跡フォルダのみ |
| verify.py / verification.json | 寸法とnative結果・派生7ファイルのbyte再現、SVG穴・強調配線・本文寸法表の照合、元#121合格指標、入力保全の確認 |
| finish-review.json / clean-checkout-verification.json | 仕上げ時の修正・図の目視確認、他Issue成果物のない入力環境での再現結果 |
| publication.json | commit後のpush／Draft PR試行結果。mergeなし |

## 再現

リポジトリrootで実行する。`measure.py`と通常の`verify.py`はPython標準ライブラリのみ。

```bash
mkdir -p .issue153-runtime/tmp .issue153-runtime/config
export TMPDIR="$PWD/.issue153-runtime/tmp"
export XDG_CONFIG_HOME="$PWD/.issue153-runtime/config"
export PYTHONDONTWRITEBYTECODE=1
python3 hardware/kicad/qualification/issue-153-main-mounting-stage1/measure.py > .issue153-runtime/measurements-reproduced.json
cmp .issue153-runtime/measurements-reproduced.json hardware/kicad/qualification/issue-153-main-mounting-stage1/measurements.json
python3 hardware/kicad/qualification/issue-153-main-mounting-stage1/verify.py
```

KiCad照合は、開始時から存在したKiCad 9.0.9抽出runtimeを読取り専用で使った。新規キャッシュ・一時ファイルは`.issue153-runtime/`へ置く。別環境では同バージョンの`pcbnew`を使用し、runtimeパスを合わせる。CAD保存・再充填・配線APIは呼ばない。

```bash
export PYTHONPATH="$PWD/.issue129-runtime/kicad/usr/lib/python3/dist-packages"
export LD_LIBRARY_PATH="$PWD/.issue129-runtime/kicad/usr/lib/x86_64-linux-gnu:$PWD/.issue129-runtime/kicad/usr/lib/kicad"
/usr/bin/python3 hardware/kicad/qualification/issue-153-main-mounting-stage1/verify.py --native
```

CSV／図の再生成は次のコマンド。入力#150報告は開始時未追跡だったため、後日のcheckoutで存在しなければ`inputs.json`の保存済みhashと抜粋を使い、同じCSV／図を再生成できる。`verify.py`もこの2件の不在だけを許容して明記する。寸法JSON／native照合はcommitted #121 PCBを起点に再計算する。入力文書が後日変更されたcheckoutでは、当該コミットの入力を用いる。

```bash
python3 hardware/kicad/qualification/issue-153-main-mounting-stage1/build-assets.py
# 比較用の出力を一時ランタイムに置く場合
python3 hardware/kicad/qualification/issue-153-main-mounting-stage1/build-assets.py --output-dir .issue153-runtime/assets-review
```

`verify.py`は元タスクruntimeの`before-hashes.json`がある場合、開始時10,250ファイルを照合する。他環境ではこの監査は未実施と表示する。報告書・既存CAD等のローカルリンクはこのコミットのリポジトリ相対パスで解決される。

仕上げ時の`verification.json`は`--native --task-finalization --task-start-utc 2026-11-05T12:15:56+00:00`で更新した。これは仕上げ作業の1時間枠の記録であり、先の実行からの待機時間を作業時間に加算しない。後日の再現では時刻固定の2オプションを外す。

## 測定の意味

- φ5円と既存銅箔外周との距離を使用。正=隙間、負=食込み。viaは外径0.60を使用。
- 絶対XYはKiCad表面視、X右・Y下。CSV／寸法JSONのローカル原点はA／A0=(76,78)、B=(70,78)。Bの4穴はローカル(3,3)、(57,3)、(3,41)、(57,41)。
- 0.5mm格子は6,545中心、板端から3mm以上。40実courtyard＋全パッド包絡の各辺0.5mm追加＋コネクタ仮予約で部品空間をスクリーニングする。body予約は公称検討用で、部品公差・3Dモデルではない。
- 格子の「clear」はパッド・トラック・ビアについての値。GND zoneは別判定。表の19候補中、48×44内の15候補すべてが保存GND充填に重なる。拡張案の4点は元の充填外。
- 板端はEdge.Cuts中心線。穴／切削公差、頭の偏心、工具、座、ボス、はんだ高さ、締付け強度、荷重、ハーネス曲げはStage 2の対象。
- 再現検査は新基板のDRC・製造承認・発注の代用にはならない。

## 手元のブランチ

通常の`.git`は読取り専用なので、同じworktreeを指す`.issue153-runtime/git`に指定ブランチを作成した。

```bash
git --git-dir=.issue153-runtime/git log -1 --oneline
git --git-dir=.issue153-runtime/git diff --stat main..issue-153-main-mounting-stage1
```

pushできなかった場合は、このメタデータ内のコミットをホスト側から取得できる。既存成果物を含める`git add .`は使用していない。
