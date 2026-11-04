"""Append repair findings while retaining the complete initial report and evidence."""
from common import *
cells={};table=[]
for cell,board,tool in [('KRT-smoke','pitch9-16mm','KRT'),('FAB-smoke','pitch9-16mm','FAB'),('KRT-16','representative21-16mm','KRT'),('KRT-17','representative21-17mm','KRT'),('FAB-16','representative21-16mm','FAB'),('FAB-17','representative21-17mm','FAB')]:
 w=E/'runs'/cell;i=E/'inspection'/cell;a=json.loads((i/'assessment.json').read_text());width=json.loads((i/'width-audit.json').read_text());rec=json.loads((E/'processes'/(cell+'-route')/'record.json').read_text())
 if tool=='FAB':
  result=json.loads((w/'result.json').read_text());eff=result['report']['effectiveSettings'];save(w/'effective.json',eff)
  readback=str((w/'effective.json').relative_to(E));router_unconnected=result['report']['incompleteAfter'];width_text=f"SES {len(width['ses_paths'])} paths / min {width['minimum_ses_path_width_mm']} mm"
 else:
  eff=json.loads((w/'effective.json').read_text());readback=str((w/'effective.json').relative_to(E));router_unconnected=None;width_text=f"{sum(width['track_width_histogram_mm'].values())} tracks / min {width['minimum_track_width_mm']} mm"
 cells[cell]=dict(board=board,tool=tool,status='PASS' if a['pass_acceptance'] else 'FAIL',runs=1,settings_readback=readback,measured_unconnected=a['measured_unconnected'],router_reported_unconnected=router_unconnected,metrics=a['metrics'],output_width_audit=str((i/'width-audit.json').relative_to(E)),independent_material_drc_count=a['independent_material_drc_count'],width_pass=a['width_pass'],route_elapsed_seconds=rec['elapsed_seconds'],pass_acceptance=a['pass_acceptance'])
 metric_text=' / '.join('null' if v is None else str(v) for v in a['metrics'].values())
 table.append(f"| {cell} | {a['measured_unconnected']} | {metric_text} | {width_text}; {'通過' if a['width_pass'] else '不通過'} | {'合格' if a['pass_acceptance'] else '不合格'} |")
main=[cells[k]['pass_acceptance'] for k in ['KRT-16','KRT-17','FAB-16','FAB-17']]
verdict='STAGE1_PASS' if all(main) else 'STAGE1_FAILED'
assessment=dict(verdict=verdict,utc=now(),gate_pass=True,gate_attempts=2,repair_gate_attempts=1,initial_gate_preserved='initial-run/equivalence-gate.json',gate_code_unchanged=True,routing_started=True,all_six_paths_run=True,cells=cells)
save(E/'assessment.json',assessment);save(E/'repair-assessment.json',assessment)
baseline={}
for board in ['pitch9-16mm','representative21-16mm','representative21-17mm']:
 d=json.loads((E/('input-drc-'+board+'.json')).read_text());baseline[board]=dict(unconnected=len(d['unconnected_items']),violation_types=[v['type'] for v in d['violations']])
save(E/'repair-input-drc-summary.json',baseline)
provenance={}
for file,old in [('repair-read-effective.py','issue-115-kicad-routing-tools-escalation-off/evidence/read-effective.py'),('repair-driver.ts','issue-103-fab-router-falsification/evidence/driver.ts')]:
 src=R/'hardware/kicad/qualification'/old;provenance[file]=dict(source=str(src.relative_to(R)),source_sha256=digest(src),sha256=digest(E/file),adaptation='runtime directory only' if file.endswith('.py') else 'byte-identical reuse')
for old in ['eda-004g/resume-02/read-pcb.py','issue-87-native-main-routing/check-main.py','issue-115-kicad-routing-tools-escalation-off/evidence/inspect-output.py','issue-103-fab-router-falsification/evidence/inspect-ses.py']:
 src=R/'hardware/kicad/qualification'/old;provenance[old]=dict(sha256=digest(src),use='public snapshot / actual copper graph / transfer and width inspection procedure')
save(E/'repair-harness-provenance.json',provenance)
gate=json.loads((E/'equivalence-gate.json').read_text());hashrows=[]
for name,v in gate['boards'].items():hashrows.append(f"| {name} | `{v['pcb_sha256']}` |")
text='''

## 修正ラウンド — PMO差し戻し後（最新判定）

上記は初回提出時の記録をそのまま残したもの。以下を最新の経緯・結果として追記する。
**修正ゲートは3基板とも通過。スモーク2経路とStage 1の4セルを各1回実行した。Stage 1の判定は `'''+verdict+'''`。**
初回の入力構築停止を取り消したり、初回runを成功へ書き換えたりしていない。

### 承認範囲と変更

修正指示は `E/repair-instructions.md`。実ホスト時刻20:08 UTCに着手し、当初の23:56 UTC期限を継続した。
既存Python実装の変更は `build-inputs.py` の2行のみ。通常部品と取付部品の各 `FootprintLoad` 直後に
`SetFPID(LIB_ID('Wing129', item))` を呼び、nicknameを設定してから配置・保存する。
ゲートの検査項目・許容差・識別子検査は一切変更していない。
`check-equivalence.py` は初回コミットとSHA256・全byte一致する。
配線・検査・記録のため新規 `repair-*` ハーネスを追加した。KRT/FAB本体は無改変。

初回コミット `0e82629f7857a3c4590b28039b835f3425367f7b` の証跡全体を `E/initial-run/` にbyteを保持して複製した。
初回報告書も `E/initial-run/report.md` に保存した。初回の失敗ゲート・固定hash・入力PCB・診断・process log・manifestは全てそこに残る。
rootの入力とhash・ゲート結果・assessment・manifestは修正ラウンドの現行状態を示す。

### 再構築と独立等価性ゲート

`processes/repair-build-inputs/` で3基板を再生成・hash固定し、その後の修正ゲートを
**2026-11-04 20:08:45.787170 UTCに1回だけ**実行した（`processes/repair-equivalence/`、exit 0）。
ゲート累計は初回失敗1回＋修正成功1回＝2回。3回目は実施していない。
識別子・配置・全物理ピン/ネット/明示NC・CSV照合・外形・NPTH・両層keepout・機械アクセス領域・厚さ/層/ルールまで全3構成で完走した。
部品/銅箔パッド/ネット数はpitch9で40/130/18、代表両ピッチで64/190/30。
GNDの独立6接点（2/4/8/10/12/14番）も照合した。

| 基板 | 修正後PCB SHA256 |
| --- | --- |
'''+ '\n'.join(hashrows)+'''

全プロジェクトのSHA256は `46864da7e7878ed1a1155336b18f93d5853717778def6d221bf01921065cc888`。
その他の固定hashは `E/input-hashes.json`。以降の各runはこの入力のbyte一致コピーを使用し、入力自体は変更していない。

### スモークとStage 1

両スモークはKiCad保存PCBの独立検査まで到達した。FABはKiCad DSN書出し→API配線→保存SES→KiCad取込の全経路を実行できたが、スモークの合否は下表のとおり。
経路の動作確認とスモーク基板の配線合格を区別し、当初指示の「スモーク基板自体の合否はStage 1と分ける」に従って本評価へ進んだ。
Stage 1配線はKRT-16→KRT-17→FAB-16→FAB-17の順に実施。再配線・設定探索なし。

KRTはv0.23.8 / `c64c0db25e6cf23afa6769ee05665c7ea22b3ff2`、全3runで `--escalation off`。
readbackは公式resolverのnet選択直前に中断して採取したもので、配線runを増やさない。
FABは指定commit `69cf598db98c136bff16bbe02bccdded95674b18`、GPL-3.0側、#103のdriver.tsをbyte一致で再利用し、
`timeBudgetMs: 1800000` のみ明示、他はAPI defaults。各resultの `report.effectiveSettings` を `runs/<cell>/effective.json` にも保存した。
タイムアウト枠はKRT 1800秒、FAB 1920秒。途中の条件調整や再試行はしていない。

表の4指標の順は required unconnected / wrong-net contacts / material violations / unexplained transfer changes。
未配線がある場合は指示どおり4指標すべてnullとし、KiCad実測件数を別欄に記載する。

| 経路・セル | KiCad実測未配線 | 独立4指標 | 幅監査 | 判定 |
| --- | ---: | --- | --- | --- |
'''+ '\n'.join(table)+'''

判定根拠は `E/inspection/<cell>/assessment.json`、詳細は `drc.json` / `width-audit.json` / `transfer-diff.json`。
FABのAPI自己申告未配線数とKiCad取込後実測は異なるため、`E/assessment.json` に両方を保存した。
KRT出力プロジェクトを個別監査し、最小幅/クラスの変更と全トラック幅を検査した。
FABは最終SES全pathの実幅と取込後全トラック幅を測定した。幅だけの通過を配線合格としていない。

### 独立検査の範囲と不合格要因

既存public-reader `eda-004g/resume-02/read-pcb.py`、実銅箔graph `issue-87-native-main-routing/check-main.py` の `snapshot_graph`、
#115の非配線オブジェクト差分と出力幅/プロジェクト監査、#103のSES静的幅実測を踏襲した。
各ルートのDRCは**元の固定プロジェクトルール**で検査し、出力プロジェクトの改変は別途監査する。
未配線0のときだけ実銅箔グラフから連結と異ネット接触を実測する。未配線ありの4指標を推定で埋めていない。
rule areaは銅箔ではなく、全非配線オブジェクトの厳密差分およびKiCad DRCで保持と違反を検査する。
ランド抽出自体の独立性や製造認定は主張しない。

KRTスモークの銅箔graphでは全組合せの距離計算が長時間化したため、既存のsnapshot・DRC・幅監査を再使用し、
境界箱がどちらかの軸で厳密に0.000002 mm超離れた組だけを事前除外して完了した。
この除外は接触または2 nm以下の近接になり得ない組のみで、元oracleの形状・接触/距離述語・union-find・判定基準は保持する。
全組合せworkerはexecセッションの割込みで停止（exit 130）。最初の継続処理は別PID namespaceのworker停止で
`ProcessLookupError`となったため、そのログを保持し、workerを正しく割り込んで継続処理を完了した。
詳細は `repair-finish-graph.py`、`inspection/KRT-smoke/graph-completion.json`、
`processes/KRT-smoke-graph-completion*/`。これは独立検査の計算継続であり、ゲート・配線・DRCの再実行ではない。

全入力の追加読取り専用DRC（`E/input-drc-*.json`）で、取付NPTHが自身の「pads禁止」keepoutに入る
`items_not_allowed` が各4件存在した。これは等価性ゲートが検証するJSON配置/禁止設定の一致とは別のDRC条件であり、
配線前から存在する構築上の問題として記録する。今回承認されたnickname以外の修正は行わず、この4件を材料違反から除外しない。
基板内のkeepoutとNPTHを削除したり、ゲート/DRCを緩和したりして合格扱いしていない。
FAB出力には追加DRC違反もあり、その種別・個数は各assessmentに記録した。

全Stage 1セルの合格には独立4指標すべて0と幅条件の両方が必要である。
今回の不合格結果は指定条件の単一runで受入条件を満たさなかったという結果であり、2層での配線が原理的に不可能だという証明ではない。
配置変更・追加構築修正・別設定探索は今回の範囲外で、行っていない。製造承認・実機の機構/アナログ評価も含まない。

### 修正ラウンドの提出検証

`E/repair-verification.json` は基準mainの全byte不変、初回コミット証跡の全byte保存、既存コード変更の限定、ゲートbyte一致、
累計ゲート2回、全6経路の単一配線run、全SES取込成功、固定入力hash、JSON/Python構文、ランタイム非同梱を検査する。
再生成ライブラリ/PCBではUUIDが新しくなるため差分が多いが、等価性ゲートは再固定した実物を検証済み。
全証跡hashは更新した `E/manifest.json`。一時実行物は引き続き `.issue129-runtime/` のみ。
既存の初回rawログの末尾空行は原文保存する。新規著作ファイルはwhitespace検査を行う。
同一ブランチからPR #130へ追加コミットをpushし、Draftのまま保持する。mergeは行わない。
'''
publication=json.loads((E/'repair-publication.json').read_text()) if (E/'repair-publication.json').exists() else {}
if publication and not publication['push_completed']:
 text+='''

### 公開状況（2026-11-04 20:30 UTC）

**ローカルの修正・全run・独立検査は完了したが、PR #130へのpushは未完了。**
Git経由は認証情報がなくdry-runがexit 128となった。認証済みGitHub連携ではtree作成が
`MCP tool call requires approval, but approval policy is never` で拒否されたため、branch refの更新は実施していない。
詳細は `E/repair-publication.json`。承認制限を回避する別経路での書込みは行っていない。
PR #130は初回head `0e82629f7857a3c4590b28039b835f3425367f7b` のままDraft、未mergeであることを再確認した。
修正結果と全証跡はローカルの同一ブランチへ追加コミットとして保持する。
'''
report=R/'docs/issue-129-wing-2layer-routing.md';original=(E/'initial-run/report.md').read_text();report.write_text(original+text)
save(E/'repair-submission.json',dict(utc=now(),deadline_utc='2026-11-04T23:56:00+00:00',verdict=verdict,branch='issue-129-wing-2layer-routing',pull_request=130,draft=True,merge=False,push_completed=publication.get('push_completed'),publication_status=publication.get('status')))
print(json.dumps(assessment,indent=2))
