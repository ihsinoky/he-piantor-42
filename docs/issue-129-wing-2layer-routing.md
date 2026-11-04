# Issue #129 — Wing 2層配線評価

**判定：入力構築で停止（INPUT_CONSTRUCTION_STOPPED）。** 3基板を構築・SHA256固定したが、配線前の独立等価性ゲートがフットプリントのライブラリ識別子不一致で不通過となった。指示書の停止条件に従い、その後の修正・ゲート再試行・配線は実施していない。スモーク2経路とStage 1の4セルはすべて未実施であり、2層で配線可能かは未判定である。

対象は [Issue #129](https://github.com/ihsinoky/he-piantor-42/issues/129)。以下の証跡は [`E/`](../hardware/kicad/qualification/issue-129-wing-2layer-routing/evidence/) 配下。指示書全文は `instructions.md`、Issue本文は `issue129.json` に保存した。

## 固定入力と構築範囲

最新 `origin/main` と一致した `96166d3f266f6d423173fcd8cdc3a38a46a6767d` を基準とし、指定ブランチ `issue-129-wing-2layer-routing` で作業した。通常の `.git` は読取り専用のため、管理情報を `.issue129-runtime/git` に複製し、現在のリポジトリをwork-treeとして使用した。既存ファイルは変更していない。

着手時にWing README、#127設計文書と配置レビュー、#103/#115の手順を読んだ。設計・接続・配置の入力は指定の `hardware/jitx/wing/generated/` の3構成のJSON/CSVのみ。`hardware/layout/**` は消費せず、Wingソースと決定文書は編集していない。ルール設定の既存qualificationプロジェクトと既存部品ライブラリは構築用の雛形・ランド形状の出所として使用した。

| 構成 | JSONの外形 | 構築物 |
| --- | --- | --- |
| pitch9-16mm | 64×80 mm | `E/inputs/pitch9-16mm/main.kicad_pcb` / `.kicad_pro` |
| representative21-16mm | 110×100 mm | `E/inputs/representative21-16mm/main.kicad_pcb` / `.kicad_pro` |
| representative21-17mm | 116.5×104.75 mm | `E/inputs/representative21-17mm/main.kicad_pcb` / `.kicad_pro` |

`build-inputs.py` はJSON中心原点・+Y上から `KiCad X=100+x, Y=100−y` へ変換し、CCW角度を保持する。2層F.Cu/B.Cu、厚さ1.2 mm、Defaultとglobalの幅・クリアランス0.20 mm、ビア0.60/0.30 mmを設定した。これらは**構築意図と生成物の記述**であり、ゲート通過を意味しない。全項目の独立照合は完了していない。

各基板に4個のφ2.2 mm NPTHと、取付周囲φ5 mmの両銅箔層rule areaを生成した。rule areaはtracks/vias/pads/copper pour/footprintsを禁止する。円は256辺の外接多角形で表現し、半径の最大余剰は約0.0001883 mm、KiCad保存時の座標量子化は1 nm。GHの `connector_cable_access_mm` はコネクタ自身のランドと重なる上方の機械予約領域なので、Dwgs.Userの矩形と注記として実装した。ケーブルの高さ・曲げ・治具適合の保証はない。これらの独立検証項目も、今回の早期停止により未到達である。

`pinmap.json` に全物理ピン、明示NC、座標変換を保存した。GHのGNDは共通ネット上の**独立した2/4/8/10/12/14番の6接点**を保持する構築であり、MP補強ランド2個はNC。各構成のJSON/CSV出所とhashは `input-provenance.json`、構築PCB・プロジェクト・ピンマップ等の固定hashは `input-hashes.json` にある。ゲート後は入力を変更していない。

## ランド形状の出所

`extract-library.py` は既存JITX部品ライブラリのみからランド形状を抽出した。回路・配置の生成元Pythonを入力として実行せず、JSONの配置を使用した。

- Hall：既存 `components/sensors/texas_instruments_drv5055a3qdbzr.py` のSOT-23ランド。
- MUX：既存 `components/switches/texas_instruments_tmux1208pwr.py` のTSSOP-16ランド。
- GH14：既存 `components/connectors/jst_bm14b_ghs_tbt.py` の信号0.6×1.7 mm・補強1.0×2.8 mmランド。pin1は+X端。
- 容量：既存Wingと同じ `jitxlib.landpatterns.twopin.smt.SMT("0603")`。
- TP：既存 `components/generic_electrical.py` の中心原点・直径1.2 mmの円。近似ポリゴンの外接寸法を円径に転用せず、元モデルの解析的な円を保持した。

寸法と抽出時WKTは `library-pads.json`、部品/依存ライブラリの出所・hashは `library-provenance.json`、KiCad形式の転記物は `Wing129.pretty/`。全て既存ライブラリの転記であり、メーカー推奨形状との追加認定・製造承認を意味しない。基板のピン番号を読むことはできるが、pin1のシルク表示・実ハーネスの機構レビューは今回未完了である。

## 独立ゲートの不通過と原因

`check-equivalence.py` は構築スクリプトをimportせず、KiCad 9.0.9のpublic readerで保存PCBを開き、JSON/CSVに対する配置・物理ピン・ネット/NC・外形・NPTH・keepout・ルールの照合を実装した。ランド寸法については出所を固定した `library-pads.json` と照合する。共通のランド抽出に依存するため、その抽出自体の独立性を主張しない。

**2026-11-04 20:03:29.691092 UTCの単一ゲートはexit 1。** 最初の `pitch9-16mm` のフットプリント識別子検査で停止した。期待値は `Wing129:hall`、実際の保存識別子は `hall` であり、ライブラリnicknameが空だった。これはJSONに別の回路があるという判定ではなく、構築ライブラリの参照先識別子の保存不備を検出したものである。

`p.FootprintLoad(library_path, item)` で読み込んだfootprintはitem-onlyのLIB_IDとなり、構築側が読み込み後にnicknameを再設定していなかった。読み取り専用の `diagnose-library-id.py` で、このloader挙動と3基板の保存識別子を確認した。診断は基板を保存せず、ゲートを再実行せず、失敗判定も上書きしていない。詳細は `failure-diagnosis.json` と `processes/failure-diagnosis/`。

`equivalence-gate.json` の `pass_equivalence=false`、完了基板 `boards={}`、失敗箇所とtracebackをそのまま保持した。**配置・ネットリスト・ピン対応・外形寸法の全項目同一性は未確認**であり、未到達項目を合格扱いしていない。追加したライブラリ識別子検査の失敗であっても、ゲート全体は不通過である。修正によって通過するかも未測定。

ゲート前の構築準備では、容量ランドの辞書添字、KiCadの未対応API、層集合のAPI引数を修正した。失敗ログと最終構築ログを `processes/build-inputs*/`・`library-extraction-attempt*.log` に残した。これらは配線runではない。等価性ゲート自体は1回だけであり、その不通過後の入力修正・再試行はない。

## スモークとStage 1の未実施

| 経路・セル | 対象・予定条件 | 実施結果 |
| --- | --- | --- |
| KRT smoke | pitch9-16mm、直接PCB配線、escalation off | 未実施：入力ゲート不通過 |
| FAB smoke | pitch9-16mm、KiCad DSN→配線→SES取込 | 未実施：入力ゲート不通過 |
| KRT-16 | representative21-16mm、escalation off | 未実施：入力ゲート不通過 |
| KRT-17 | representative21-17mm、escalation off | 未実施：入力ゲート不通過 |
| FAB-16 | representative21-16mm、API defaults、1800000 ms | 未実施：入力ゲート不通過 |
| FAB-17 | representative21-17mm、API defaults、1800000 ms | 未実施：入力ゲート不通過 |

全6経路の独立4指標は **null（未測定）**。実測未配線件数もnullであり、「配線を試して未配線が残った」ケースとは区別する。配線の実効設定readback、KRTの出力プロジェクト・全幅監査、SESの全path幅測定、SES取込、独立DRC/銅箔graph/transfer差分検査はいずれも未実施。成果物が存在するような空のrun/reportは作成せず、`assessment.json` に未実施理由を明記した。

準備したKRTはv0.23.8、commit `c64c0db25e6cf23afa6769ee05665c7ea22b3ff2`、fab_routerは指定commit `69cf598db98c136bff16bbe02bccdded95674b18`。本体を変更せず、過去評価のbackupから `.issue129-runtime/` に複製した。両ソースと既存KiCad/geometry検査ランタイム・KRT binaryのbyte整合性は `runtime-revalidation.json`、各ソースhashは `*-source-hashes.json` に記録した。fab_routerのGPL-3.0側利用を予定していたが、API配線は起動していない。ランタイム・依存パッケージ本体は提出物に含めない。

## 提出・検証

既存ファイルの全byte一致、追加先の限定、固定入力hash、停止ゲートの保持、全経路の未実施、JSON/Pythonの構文検証は `verification.json`。証跡hash一覧は `manifest.json`、提出準備時刻は `submission.json` に保存した。著作ファイルのwhitespace検査は通過。rawのAPI例外ログ `processes/build-inputs-final/stderr` に末尾空行1件があり、全体diff-checkはこれを指摘するため、生ログを整形せず保持した。

保守的開始は実ホスト時計の **2026-11-04 19:56 UTC**、4時間の期限は **23:56 UTC**。ユーザー環境記載の日付は11月5日だが、実ホスト時計は11月4日を返したため、時刻記録は実UTCで統一した。停止条件の発火によって早期提出する。指定ブランチからDraft PRとして提出し、mergeは行わない。


## 修正ラウンド — PMO差し戻し後（最新判定）

上記は初回提出時の記録をそのまま残したもの。以下を最新の経緯・結果として追記する。
**修正ゲートは3基板とも通過。スモーク2経路とStage 1の4セルを各1回実行した。Stage 1の判定は `STAGE1_FAILED`。**
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
| pitch9-16mm | `5c085cbadd39be4688e7a1a9f93e996966c931b3ce15b7d863fd3a4b7f2740e9` |
| representative21-16mm | `d620b227b567c0c2db4caced7adbcbf5359a146fddf2eccf89f8d041686babbf` |
| representative21-17mm | `fd9fd25c168426e137319fbaf25b3df4b095c328c1ce187fa703235996564f0d` |

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
| KRT-smoke | 0 | 0 / 0 / 4 / 0 | 354 tracks / min 0.2 mm; 通過 | 不合格 |
| FAB-smoke | 10 | null / null / null / null | SES 236 paths / min 0.2 mm; 通過 | 不合格 |
| KRT-16 | 2 | null / null / null / null | 1020 tracks / min 0.2 mm; 通過 | 不合格 |
| KRT-17 | 5 | null / null / null / null | 1045 tracks / min 0.2 mm; 通過 | 不合格 |
| FAB-16 | 23 | null / null / null / null | SES 267 paths / min 0.2 mm; 通過 | 不合格 |
| FAB-17 | 23 | null / null / null / null | SES 245 paths / min 0.2 mm; 通過 | 不合格 |

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


### 公開状況（2026-11-04 20:30 UTC）

**ローカルの修正・全run・独立検査は完了したが、PR #130へのpushは未完了。**
Git経由は認証情報がなくdry-runがexit 128となった。認証済みGitHub連携ではtree作成が
`MCP tool call requires approval, but approval policy is never` で拒否されたため、branch refの更新は実施していない。
詳細は `E/repair-publication.json`。承認制限を回避する別経路での書込みは行っていない。
PR #130は初回head `0e82629f7857a3c4590b28039b835f3425367f7b` のままDraft、未mergeであることを再確認した。
修正結果と全証跡はローカルの同一ブランチへ追加コミットとして保持する。
