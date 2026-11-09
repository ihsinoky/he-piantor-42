# Issue #221 — Main Rev.5 / J4 Pico-EZmate

[最終報告](../../../../docs/issue-221-main-rev5.md)。J4のみ781710004/C588524へ置換した提出用データ。
**D-035は提案、PO採択・製造GO・初回通電前の実測は未実施。** 発注/push/PRは行わない。
このディレクトリのRev.5基板と製造ファイルを組で使用する。

- `inspection/final/main.kicad_pcb` / `.kicad_pro` / `fp-lib-table`：最終PCBと継承ルール。
  他61 footprintはRev.4の `../issue-196-main-rev4-phaseb/Rev4.pretty/`、J4は `Rev5.pretty/`。
- `schematic/`：全端子接続を保持したnative回路図/XML。`erc-final.json`が最終0件。
  `erc.json`は継承回路図の初回エラー履歴。`schematic-repairs.json`が紙面/ライブラリ/電源宣言の修正一覧。
- `rev4-diff.json`：J4 footprintのみ、F.Cuの3線分削除/11線分追加、via変更0。
- `inspection/final/{drc,connectivity,assessment}.json`：DRC/未配線0、独立40ネット検査、最終合格指標。
- `inspection/final/audit/via-pad/`：全130via×232padの30,160組を `all-pairs.json.gz` に記録。
  最近傍もCSV/JSONで保存。最小0.145mm。`paste-via-check.json`は両面pasteとの全via照合。
- `power-extraction-{rev4-reference,final}.json` / `ground-extraction-{rev4-reference,final}.json`：両Revの新規抽出。
  `resistance-summary.json` / `power-impact.json` / `power-budget.json` / `power-sensitivity.csv`に比較と条件。
  入力往復44.910→48.686mΩ、最遠点モデル4.797986V。完成Fly/ハーネスや材質の実測保証ではない。
- `manufacturing/`：Gerber ZIP、BOM、CPL、GerberフレームCPL、CAM、[quote-handoff](manufacturing/quote-handoff.md)。
  `export-provenance.json` / `cam-check.json` / `cpl-frame-check.json`が新基板からの生成元と独立照合。
- `sources/` / `sources.json` / `land-check.json`：Molex作成図面（原本ホストがtimeoutしたためミラー取得）とKiCad公式reference。
  保存した原文は変更せず、`build.py`が矩形ランド・無番号補強・表示設定を調整する。出典とhashを保存。
  KiCad referenceのライセンスは同プロジェクトのCC-BY-SA 4.0＋library exceptionに従う。
- `issue221-current.json` / `issue221-comments.json`：今回取得した正本とPMO判断。
  `issue221.json` / `input-contract.json` / `inspect-input.py`は**初回HOLD時の履歴**。
  candidate未割付という過去記録を現在の状態と混同しない。現在の状態は `verification.json`。
- `recovery-inventory.json`：227eb17aの追跡14,981ファイル照合、不一致0、残存6成果物の棚卸し。
  `manifest.json`は最終成果物のSHA-256。`processes/`は個別native呼出し/抽出のstdout/stderr/終了状態。
  途中試行の記録も保持。最終native結果は `final-native-drc` / `final-native-erc`。
  `processes-initial/`はランド引出し幅の最終調整前の履歴で、最終基板の判定には使わない。
  回路図ERCとRev.4抽出は入力不変なので記録を引き継ぐ。

## 再検証

リポジトリrootで `python3 hardware/kicad/qualification/issue-221-main-rev5/verify.py`。
manifestのハッシュだけでなく、全組監査・BOM/CPL/ZIP・XML契約・電源比較と保存範囲を検査する。

native処理は `bash hardware/kicad/qualification/issue-221-main-rev5/env.sh <script.py> [args]`。
環境は既存clone `/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime`、FEMは`.issue175-runtime/python`、
CAMは`.issue147-runtime/viewer-venv`を読み取り利用。スクラッチはこのworktreeの`.issue221-runtime/`のみ。
旧PhaseBのcommon.py/env.shを直接実行しない（スクラッチ先が異なる）。

生成順は `build.py` → snapshot reader（`../eda-004g/resume-02/read-pcb.py`）→ native DRC →
`prepare-schematic.py` → native ERC/XML export → `check-diff.py` / `connectivity.py final` → `assess.py` →
`run-audit.py` / `check-land.py` / `check-paste.py` → `extract-power.py final` / `extract-ground.py final` →
同抽出を `rev4-reference` 引数でも実行 → `summarize-resistance.py` / `verify-ground-model.py` /
`power-budget.py` / `power-impact.py` → `assembly.py` → `export-final.py` → `cam-source.py` /
`check-cam.py` / `render-cam.py` / `gerber-frame-cpl.py`。

native CLI呼出しは `common.py <unique-run-name> <command...>` で実行記録を保存する。
既存run名・export出力先は上書きを拒否する。全面再生成は隔離コピーで実施し、過去証跡を削除しない。
`extract-ground.py` は既存抽出行を引き継ぐので、同ラベルの結果へ追記して再実行しない。
新PCBのUUIDは再生成されるため、全検証・製造出力・manifestも更新する。

組立ではPMOコメントに従い、Main未接続のFlyをUSBへつないで同梱ケーブル先端pin1/pin4の
+5V極性を実測・記録し、電源を切ってからMainへ接続する。詳細はquote-handoff。
