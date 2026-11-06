# Issue #173 — preflight 不合格で停止、合格済み seed-a を整理

**1210品を用いた最終候補は不合格。製造GOではない。** C26 の移動で SW2 seed との接触は解消したが、移動先で J3 の未接続ランドとの接触を作ってしまった。配置調整の不備であり、D-019 条件で成立不能という証拠ではない。準備DRCがこの接触を検出したため、指示の「衝突・短絡があれば配線に入らず止める」に従って停止した。**全体配線0回／上限1回、局所rip-up0回。** 不合格後の再配置・再試行で埋め合わせていない。

指定された不合格時の成果物として、#169 の **seed-a（0805出力C、paste整備済み、全44ネット・4指標0）** を変更せず整理した。**出力容量の余裕の弱さは既知の制限**であり、どの基板を採用するかはPO判断に戻す。発注・課金・mergeは行っていない。D-019を緩和していない。

以下 E は[今回の証跡フォルダ](../hardware/kicad/qualification/issue-173-main-dual-wing-final/)を指す。

## 起点と実行範囲

`.issue173-runtime/instructions-173.md` を全文読み、[Issue #173](https://github.com/ihsinoky/he-piantor-42/issues/173)と[Draft PR #172](https://github.com/ihsinoky/he-piantor-42/pull/172)を取得した。PR #172 の `issue-169-main-dual-wing-followup` head **`c741ade9550157333443784b90e2fe66f95ca297`** から **`issue-173-main-dual-wing-final`** を作成した。作業ツリーは指定の現在ディレクトリ `he-piantor-42`。通常 `.git` は読取りのみとし、Gitメタデータを `.issue173-runtime/git` に複製して同じ作業ツリーで使用した。既存の追跡ファイル・決定記録・関連外成果物を変更しない。

開始 **2026-11-06 08:36:13 UTC**、3時間期限 **11:36:13 UTC**。期限ではなくpreflight停止条件により終了。新規ランタイム、TMPDIR、XDG、Gitは `.issue173-runtime/` に置き、既設KiCad/KRTを読取り使用した。KRT 2055 source hashesを既存台帳と照合し変更0件。E/start.json、routing-scope.json、runtime-check.jsonを保存。

## 配置調整と停止の根拠

#169 の**配線前入力** `inputs/seed-b/main.kicad_pcb` を起点とした。配線後基板の局所rip-upではない。C26のみ **(91.8,77.5) → (94.5,77.2)mm、0°** に移動し、対応する2個のF.Paste開口も同じ量だけ移動した。C26–C28は1210 TDK C3225X7R1C226K250ACのまま。ライブラリはStage173へ凍結保存。

独立比較で、全66 footprint中ほか65個の座標・角度、#155由来の既存53部品、J3=(105,73)・0°を維持した。種配線の全segment／viaはcanonical ASTで完全一致。C26とSW2の種配線の最小銅箔間距離は **1.274999mm** となった。しかしC26.2[GND]とJ3.15[未接続]のランドは **0.400000mm²** 重なった。未接続ランドとの接触も許可していない。

| 準備DRC | 観測 |
| --- | --- |
| clearance | **1**：C26.2 (95.9,77.2) と J3.15 (95.025,76.35) |
| solder_mask_bridge | **1**：同じランド対 |
| shorting_items | 0（未接続ランドなので短絡件数だけでは安全と判定できない） |
| 継承印刷警告 | text_height44／silk_overlap12／silk_over_copper5 |
| 配線前のvia_dangling | 15 |
| 配線前の未接続 | 130（未配線入力であり、最終資格指標として扱わない） |

E/preflight.json はnative KiCad DRCの生出力。KiCad CLIの終了コード0だけを合格判定に使わず、**内容中の物的違反**で不合格にした。#169の修正済みガードと同じ除外集合（印刷3種と配線前via_dangling）を用い、clearance／mask違反は除外しない。board／project／DRCのSHA256をE/preflight-receipt.jsonへ固定した。E/route.pyを実際に呼び出した拒否検査はexit1となり、`runs/`・実ルータのprocess記録・attempt予約はいずれも作られなかった。E/processes/guard-rejection/ に失敗をそのまま保存した。

予定条件は **4層・1.2mm・信号幅／間隙0.10mm・via0.60/0.30mm・In1.Cu GND専用・escalation off・keep-input-copper**。今回はルータに到達していないため、resolver readbackや配線完了を主張しない。全体配線を1回実行する予定より、preflight不合格時の明示的な停止指示を優先した。最終候補の独立4指標、実抵抗再抽出、製造データ再生成、POFV再分類、PCBA確定見積には進んでいない。

## 不合格時成果物：seed-a

[fallback-seed-a](../hardware/kicad/qualification/issue-173-main-dual-wing-final/fallback-seed-a/) は#169のpaste整備済みseed-a専用パッケージ。コピーの全ファイルを元ファイルと起点コミットのGit blobへ照合し、E/fallback-provenance.jsonに出所とSHA256を記録した。**銅箔編集・再配線・新しい抵抗抽出・CAM生成・POFV分類は0**。今回の候補へ旧資格を転用しない。

| seed-aの継承資格 | 値 |
| --- | ---: |
| 確認ネット | 44 |
| 必須未接続／異ネット接触／物的違反／説明不能な保持配線転送差分 | **0／0／0／0** |
| 論理pin照合 | 245 |
| 基板SHA256 | `19da98f4804c0117e7dd2b6606a8ddf02e0f3c263d1c14d5696beab10febc176` |
| 共通正側／GND／往復抵抗（既存125°C・幅−20%モデル） | 33.295／9.916／43.211mΩ |
| 既存POFV台帳 | 全110 vias、候補28 |

パッケージ内 `inspection/final/main.kicad_pcb` とproject、Stage169.pretty、`design-seed-a/`の回路資料、`manufacturing-seed-a-review/BOM.csv`・`CPL.csv`・Gerber/drill/paste・レビューZIPが対応する。**1210品のBOMと混用しない。** 回路図archiveは#169で再exportした意味的同等版であり、旧circuit-checkのexport SHA256とバイト一致を主張しない。基板・CAM・POFVのsource hashは同じseed-aを指す。

このパッケージの `final` は旧フォルダ名であり、#173の1210候補の合格や製造リリースを意味しない。CAMも旧レビュー資料の変更なしの写しであり、今回の最終製造データとして再生成していない。

## 既知の制限とPO判断

**seed-a出力C26–C28はGRM21BC81C226ME44L、22µF・16V・X6S・0805を3個。公称合計66µFを実効容量として扱えない。** #169のメーカー典型DCバイアス曲線では約5.35Vで容量が半分以下に減る。許容差・温度・経時変化はさらに余裕を減らす。保証最小の実効出力容量、50mV動特性、起動overshootを満たした証拠はなく、配線合格で電源性能を保証しない。

1210品側の38.62485µFは#169の選定スクリーニング値であり、0805のseed-aに転用しない。seed-aを既知の制限付きで進めるか、1210配置の再検討を新たな範囲で認めるかはPO判断。本結果だけからD-019の緩和が必要とは結論しない。

USB許可firmware、効率・Main他負荷、動特性・逆給電・ADC settling、製造stackup／銅厚／plating、POFVのepoxy fill＋copper cap、J1の12 SMD contacts＋4 PTH shell legsを同じEconomic PCBAで実装する受入れは#169の未確認事項を継承する。**確定PCBA見積は未取得、金額null**。旧見積を確定見積として流用せず、発注・カート・課金・サポート送信を行わない。

## 検証と公開

E/verification.jsonはpreflight停止・配線0回・元データ保持・seed-aパッケージ整合の検証結果。1210候補の配線資格合格ではない。E/status.jsonに停止状態、E/manifest.jsonに成果物ハッシュを保存する。報告書と証跡のみコミットし、指定ブランチへpush後、#169ブランチをbaseにDraft PR作成を試みる。結果はE/publication.jsonに記録する。Issueの自動close、mergeは行わない。
