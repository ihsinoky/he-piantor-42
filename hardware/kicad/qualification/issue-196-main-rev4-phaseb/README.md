# Issue #196 Phase B — Main Rev.4

[報告書](../../../../docs/issue-196-main-rev4-phaseb.md)。このディレクトリのRev.4データだけを組で使用する。

- `inspection/final/main.kicad_pcb` / `.kicad_pro` / `fp-lib-table`：最終native基板。ライブラリは `Rev4.pretty/`。
- `schematic/main.kicad_sch` / `main.net.xml` / `logical-contract.json`：独立回路契約・native回路図・KiCad export。
- `inspection/final/{drc,assessment,connectivity,transfer-diff}.json`：最終40ネット・4指標0、DRC違反/未接続0。
- `inspection/final/audit/via-pad/`：全130via/232pad、最近傍間隔と全pad形状。`via-distribution.json` に分布。`paste-via-check.json` は両面paste重なり検査。
- `design-check.json`：全59部品のPhase A-2位置・角度、226論理pin、三角形外形・3穴の実銅箔予約。
- `power-extraction-final.json` / `ground-extraction-final.json` / `resistance-summary.json`：実銅箔抵抗モデル。`power-budget.json` / `power-sensitivity.csv`：200mm導体経路、96条件、上流C3/SHの予約感度。
- `ground-model-verification.json`：解析矩形・相反性・重ね合わせ・KCL。`copper-equivalence.json`：ステンシル追加前後の非paste AST完全一致により、`power01`抽出と最終基板を結び付ける。
- `manufacturing/`：Gerber/drill/paste、55箇所のBOM/CPL、製造ZIP、CAM画像、[再見積ハンドオフ](manufacturing/quote-handoff.md)。業者受入れ・実装向き・在庫確認はPMOが行う。
- `cam-check.json` / `cam-native-zones.json` / `export-provenance.json`：CAMの独立照合と生成元hash。
- `runs/` / `processes/`：全面1回（auto01）と追加・部分自動配線（auto02–04）、拡幅・GND追加（power01）、ステンシル移管（paste01）の入出力と実行記録。過去中間状態は最終と混ぜない。

## 検証

リポジトリrootで `python3 hardware/kicad/qualification/issue-196-main-rev4-phaseb/verify.py`。
既存のJSONだけでなく、manifest、最終入力hash、via全件、モデルの式、BOM/CPL・ZIP・文書の整合を検査する。

ネイティブ検査の再実行には `bash hardware/kicad/qualification/issue-196-main-rev4-phaseb/env.sh <script.py>` を使う。
ランタイムは `/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime`、CAMは同本体cloneの `.issue147-runtime/viewer-venv`、FEMは `.issue175-runtime/python` を読み取り使用。ルータは `.issue155-runtime/KiCadRoutingTools`。KiCad 9.0.9、Shapely 2.2.0。スクラッチは作業コピーの親 `.issue196-runtime/`、`/tmp`を使わない。

主な処理順は `build.py` → `route.py` → `repair-auto.py` → `inspect-board.py auto02` → `reroute-wing-en.py` → `route-wing-en-rescue.py` → `improve-power.py` → `inspect-board.py power01` → `extract-power.py power01` / `extract-ground.py power01` → `restore-paste.py` → `inspect-board.py paste01`。
最終は `inspection/paste01/` とbyte一致の `inspection/final/`。`finalize-power.py`、`summarize-resistance.py`、`power-budget.py`、`verify-ground-model.py`、`run-audit.py final`、`check-design.py`、`check-paste.py`、`assembly.py`、`export-final.py`、`cam-source.py`、`check-cam.py`、`render-cam.py` が各検査/出力を担当する。

回路図は `circuit-source.py` / `author-schematic.py` で配線前契約から作成し、`kicad-cli sch export netlist --format kicadxml` でexportする。実行ごとに新UUIDが生成され、runnerは既存実行記録の上書きを拒否するので、全工程再生成は別の証跡ディレクトリで行う。過去ログを削除して再実行しない。

ハーネスは各線200mm、AWG28相当0.0804mm²以上、6帰線・接触50mΩ/箇所という明示モデル。未知の完成ハーネスや将来のWing配線への保証ではない。製造GO・実機動作・原価確定は本証跡の合格範囲に含まない。push・見積・注文はしていない。
