# Issue #121 — 完全自動配線を実現する条件の探索

**完全自動（手直しなし）の完成条件をセル1で確認した。4層・幅／クリアランス0.10mm・ビア0.60/0.30mm・KRT v0.23.8・escalation offで、独立未配線0件、独立4指標は0 / 0 / 0 / 0。** 指定探索順で最初の完成セルなので、セル2〜4は実行せず停止した。これが今回「確認された最小の完成条件」である。0.10〜0.127mm間の境界や、他の条件を含む数学的な最小値を証明したものではない。

[Issue #121](https://github.com/ihsinoky/he-piantor-42/issues/121) の探索結果。正式な設計ルール変更は行わない。以下 E は [証跡ディレクトリ](../hardware/kicad/qualification/issue-121-full-auto-conditions/evidence/) を指す。指示書全文は E/instructions.md。

## 比較結果（実測）

4指標の順序は **必須未接続／異ネット接触／物的違反／説明不能な転送変更**。

| 条件 | #119 セルB（起点） | #121 セル1 |
| --- | --- | --- |
| 幅／クリアランス mm | 0.127 / 0.127 | 0.10 / 0.10 |
| 指定ビア 外径／drill mm | 0.60 / 0.30 | 0.60 / 0.30 |
| escalation | off | off |
| 独立未配線 | 1件（V3V3） | **0件（ネット／端点リスト空）** |
| 独立4指標 | null / null / null / null | **0 / 0 / 0 / 0** |
| 幅mm:本数 | 0.127:554、0.20:3 | 0.10:537、0.20:3 |
| ビアmm:個数 | 0.60/0.30:80 | 0.60/0.30:66 |
| 層別トラック数 F / In1 / In2 / B | 462 / 0 / 55 / 40 | 471 / 0 / 33 / 36 |
| 配線プロセス経過秒 | 114.561 | 27.264 |
| 停止理由 | CLI正常終了、V3V3 open | CLI正常終了、最終37/37ネット完成 |
| exit / 外側timeout | 0 / false | 0 / false |
| 生DRC（印刷以外） | 0 | 0 |
| 説明不能な転送差分の生件数 | 0 | 0 |

| 未実行セル | 指定条件 | 未実行理由 |
| --- | --- | --- |
| 2 | 0.127mm、ビア0.45/0.20mm、off | セル1完成による停止規則 |
| 3 | 0.10mm、ビア0.45/0.20mm、off | 同上 |
| 4 | 0.127mm、ビア0.60/0.30mm、fab | 同上。ネット別ティア抽出の対象実行なし |

セル2〜4は入力・等価性ゲートだけ準備し、smoke／Main／配線開始前の設定読戻しも行っていない。未実行を失敗や未配線0と記載しない。Main再実行0、smoke再実行0、手動配線0、結果を見た設定変更0。

起点は [#119報告](issue-119-promising-tools-relaxed-conditions.md) と E/source119/inspection/main4/krt/。#119の未完成セルは規定どおり指標nullであり、生DRC 0を完成0に置き換えない。時間の差は各1回の実測であり、速度の一般的な優劣・再現性を意味しない。

## 入力の出典と実行前ゲート

[merge済みPR #120](https://github.com/ihsinoky/he-piantor-42/pull/120) の main commit `ce2e27fe6495dbd08db86bdd9b22a3c93b002347` から、`git show commit:path` により #119 の4層native／corrected DSN／対応smoke／等価性証明／比較検査を取得した。ローカルの未追跡コピーを入力元にしていない。全取得ファイルを同コミットの #119 manifest の SHA256 と再照合した（E/source-provenance.json、source119-manifest.json）。

| #119 4層Mainの取得入力 | SHA256 |
| --- | --- |
| native PCB（0.127mm） | `ff1f6974ee2456a7300959a5ff581df2290c3371c46815398538605edcb8bf01` |
| corrected DSN（0.127mm） | `b3b04edff94b4e2d2a02f0cdd4920cf50957816ce7b8f625258aaebc2476e517` |
| project（0.127mm） | `0744fe4b9aa64e431c1ed8674bfac08d95d309ebb939788cbac78014958261f6` |

配置、部品、ネット、板厚1.2mm、4層構成は固定。F.Cu信号／In1.Cu GNDプレーン／In2.Cu信号／B.Cu信号を維持する。既存0.20mm銅箔3本も保持した。smokeは #119 の4層smokeを再利用し、そのNプレーン・solid接続をMainへ移植していない。

E/prepare.py は各セルのルール変更を明示し、native PCBとDSNをルール値だけ逆変更すると元の全文にbyte一致することを検査した。全projectの再帰差分も保存した（E/equivalence-gate.json）。セル1の変更はnativeのzone clearance/min_thickness/thermal_gap/thermal_bridge_width、DSNのwidth/clearance、projectのmin_clearance/min_track_widthとDefaultクラスの寸法ルールだけである。セル2/3の準備では未使用DSN via padstack定義とproject via下限も指定寸法へ変更し、既存銅箔を変更していない。セル4入力は起点と同値である。

全入力ゲート確定 **10:56:14 UTC** → KRT runtime hash照合完了 **10:56:18 UTC** → セル1対応smokeの独立4指標0 **10:56:38 UTC** → Main配線開始 **10:56:42 UTC**。Stage 0は10:53:39 UTC開始から約3分で通過し、45分制限内だった。

## ツール・実効設定

使用ルータはKRTのみ。v0.23.8、commit `c64c0db25e6cf23afa6769ee05665c7ea22b3ff2`、binary SHA256 `4411ccf3f074f519d8d69be29ac58b46ca7c4c2fe4f4be889d253d40996c2c0f`。#113の全2055ソースファイルと独立検査runtime 26ファイルを再照合し差分0。本体は無改変（E/runtime-revalidation.json）。

```text
--escalation off --track-width 0.1 --clearance 0.1
--via-size 0.6 --via-drill 0.3
--layers F.Cu In1.Cu In2.Cu B.Cu --layer-costs 1.0 -1 1.0 1.0
```

smoke/Main双方で、公式CLIの設定解決後・配線開始前にtraceで停止する読戻しを別プロセスで実施し、GridRouteConfigの寸法・layer costsとescalation offをassertした（E/configuration/）。読戻しでは配線を開始せず、出力PCBも作らない。実配線ログの最終JSON_SUMMARY_MINもescalations=0、min_clearance_used=0.1、failed=0、37ネット完成を報告する。ツール自己値を独立完成判定の代用にしていない。

## 独立検査と出力差分

KiCad 9.0.9でnative出力を読戻し、**入力側0.10mm project**を使ってGND zoneを再充填し、`pcb drc --severity-all --format json` を実行した。KRTによる出力project書戻しに検査下限を依存させていない。必須未接続0、異ネットshort 0、銅箔・穴等の物的DRC 0、非配線AST差分0、元配線欠落0。元配線のnet/layer/widthを固定した中心線被覆（許容2nm）とUUID差分も検査し、3本とも被覆欠落0、UUID差分なしだった。GND再充填済み、In1信号トラック0である。

生DRCは E/inspection/main-cell1/krt/drc.json。#119と同じ評価区分で、印刷のsilk_overlap12／silk_over_copper5／text_height44は4指標の「物的違反（配線・銅箔・穴）」に算入せず、rawに全61件を保持する。「KiCad全指摘0」や「製造・実装承認済み」という意味ではない。対応smokeは印刷を含む生DRC自体も0件。

#119で孤立していたU1.48/U1.49については、保存・再充填済み出力のKiCad GetConnectedPads/GetConnectedTracksをU1.48から追跡し、U1.49と主電源島のU4.5が同一V3V3連結成分に属することも実測確認した（E/inspection/main-cell1/krt/V3V3-connected-component.json）。

**出力projectの全差分**は E/inspection/main-cell1/krt/transfer-diff.json に保存した。`/board/design_settings/rules/min_via_drill` 未定義→0.3mmと、`/kicad_routing_tools` メタデータ追加だけである。後者の内容は repo_rules.min_via_drill=0.3、fab_floor_origin={min_hole_clearance:0.2, min_through_hole_diameter:0.3, min_track_width:0.1, min_via_annular_width:0.1, min_via_diameter:0.6}、records_rev=1。幅／clearance／via下限の追加緩和はない。raw out.kicad_pro と入力projectの双方を保持する。smokeの全差分も対応transfer-diff.jsonに保存した。

KRT最終summaryのvias=67に対し、独立保存出力の実数は66個である。分布・比較表には後者を採用し、自己値も E/inspection/main-cell1/krt/router-structured-log.json に残した。原因を未検証のまま断定しない。

## 製造上の位置づけ（公開事実と解釈）

2026-11-04参照の[JLCPCB公式能力表](https://jlcpcb.com/capabilities/pcb-capabilities/)は、1ozの多層基板で最小幅／間隔0.09/0.09mm、FR4厚1.2mmを掲載する。したがって今回の0.10/0.10mmは掲載された**1oz多層の能力範囲内**である。2oz多層の掲載下限は0.15/0.15mmなので、銅厚を問わず適用できるとは扱わない。

同能力表はvia hole 0.20mmを推奨最小とし、0.20/0.25mm穴で外径0.45mm未満の場合などを追加費用条件としている。未実行セルの外径0.45／穴0.20mmはその「外径未満」条件には該当しないが、今回完成したのは外径0.60／穴0.30mmのままである。発注総額・追加料金なしを断定せず、見積もりはPMOが別途取得する。

実測ログにはKRTのvia-in-pad/paste opening自己検出25箇所（C5.2とboard F.Paste graphic、旧ファイル形式で個別filling/capping未記録）もある。これは独立DRCの違反件数ではなくツールの製造注記であり、実箇所の妥当性や実装工程は今回検証していない。該当座標をstructured logに保持する。公式能力表にはfilled/capped via工程が別掲されており、寸法能力内という事実だけで、その工程や製造費用まで確定しない。

**推定の範囲：** 幅／clearanceの緩和により、この固定配置で完全自動完成へ到達したことは今回の実測で示せた。全幅域の成立境界、電源・信号品質、量産DFM、別seedでの再現性は未検証。正式ルール変更・製造・手動補正は行っていない。

## 監査と提出

E/processes/ はargv・cwd・環境・UTC・elapsed・exit・timeout・stdout/stderrを保持する。E/script-freeze.json は探索前のスクリプトと条件・ゲートhashを固定する。E/verification.json は入力不変、ゲート→smoke→Mainの順序、各1回だけの実行、セル2〜4未実行、全検査・追加のみを確認する。E/manifest.json は成果物全hashを保持する。

配線開始10:56:42 UTC、独立完成確定10:57:12 UTCで停止。全体期限は開始10:53:39 UTCから3時間、13:53:39 UTC。作業gitは `/tmp/issue-121-main/git`、新規ブランチ `issue-121-full-auto-conditions` を使用し、元.gitと既存追跡ファイルを変更しない。成果物は本報告と指定証跡ディレクトリの追加のみ。Draft PRで提出し、mergeしない。提出時刻・PR番号は E/submission.json に記録する。
