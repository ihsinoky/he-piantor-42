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
