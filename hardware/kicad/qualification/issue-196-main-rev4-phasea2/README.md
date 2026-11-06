# Issue #196 Phase A-2 証跡

報告書は [docs/issue-196-main-rev4-phasea2.md](../../../../docs/issue-196-main-rev4-phasea2.md)。配置提案だけを生成する。元の製造基板・回路図の保存、配線、ベタ再fillはしない。

- `geometry-plan.json`：組立フレーム（X右・Y南、mm）の外形、両ピッチ左右Wing、59電気部品、全232pad形状、3穴、ケーブル経路案、全入力SHA256。
- `placements.csv`：同じ部品位置とKiCad回転角。KiCad位置への提案変換はX+100／Y+70。
- `verification.json`：全1711包絡ペア・外形・穴・Wingの検査と、初期の機能別移動からの調整記録。
- `assembly-proposal.svg`／`main-placement.svg`：16mm版との組立図／Main拡大図。ハーネス破線は経路案。
- `inputs/wing/`：PR #195 `f9084be93faf3defdff3bb3b76e1db1edfe49976` の配置definition4種と報告書。Stage 1座標はそのまま。
- `inputs/udb/`：UDB-C-Legacy `2ecdd7e0482ecbd3ffe9af04966ab3555f7fc33c` の `KiCad/C3/Unified-Daughterboard.kicad_pcb`、`Production/C3/BOM/Unified-Daughterboard_bom_C3.csv`、MIT LICENSE。元の銅箔を含む入力資料であり、Main配線の成果物ではない。KiCad読込み時のlegacy zone警告はメモリ上の読み取り変換であり、保存・再fillは行わない。
- `inputs/issue196.json`／`scope-comment.json`：確認したIssue／PO改訂のスナップショット。
- `analyze.py`：実ネイティブパッドと包絡による配置成立例の生成。小部品の調整は0.5mm格子の近傍探索。配線・部品本体公差・製造適合の証明や面積最適解とは扱わない。
- `verify.py`：KiCad/Shapelyを使わない独立した凸多角形・距離・Wingキー変換・入力ハッシュ検算。

## 再現

リポジトリrootから実行する。KiCad 9.0.9 Python bindingsとShapely 2.2.0を使用した。

```bash
bash hardware/kicad/qualification/issue-196-main-rev4-phasea2/run-analysis.sh
python3 hardware/kicad/qualification/issue-196-main-rev4-phasea2/verify.py
```

ランタイム既定は `/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime`（`KICAD_RUNTIME_PARENT`で変更可）。スクラッチ既定はこの作業コピーの親 `.issue196-runtime/`（`ISSUE196_SCRATCH`で変更可）。`/tmp`を使わない。XDGとTMPDIRは同スクラッチ内に向ける。スクリプトは成果物JSON・CSV・SVGだけを再生成する。

検算PASS：59部品・1711組、最小包絡間隔0.300000mm、最小pad端間隔0.800000mm、両ピッチ左右4種のWing確認。入力とランタイムが同じなら生成物はbyte一致する。報告書の2D包絡・機械datum・ハーネス長の未決条件を併せて読む。
