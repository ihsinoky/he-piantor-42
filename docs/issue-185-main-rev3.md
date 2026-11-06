# Issue #185 — Main Rev.3：35 via を移設し POFV 不要化の設計条件を達成

**部品配置を変えず、局所接続だけで成立した。** 全44ネットの独立4指標はすべて0、GND zone 再fill 済み。全113 via の annulus 外周–全パッド銅間隔は **最小0.100000mm、未達0**。共通・分岐の電源抵抗も50mΩ目標をモデル内で維持した。製造データを再生成しCAM照合済み。D-030に、今回のRev.3パッケージでPOFV指定を外す提案を記録した。製造GO・業者受入れ・新見積の成立は主張しない。

以下 E は [今回の証跡フォルダ](../hardware/kicad/qualification/issue-185-main-rev3/) を指す。

## 起点と作業枠

`.issue185-runtime/instructions-185.md` を全文読み、[Issue #185](https://github.com/ihsinoky/he-piantor-42/issues/185)、[監査 #183／PR #184](https://github.com/ihsinoky/he-piantor-42/pull/184)、[起点PR #176](https://github.com/ihsinoky/he-piantor-42/pull/176)を取得した。指定worktree `he-piantor-mainrev3`、指定ブランチ `issue-185-main-rev3-nopofv` で実施。起点commitは **`dcf5c61d9b8480da9698f71c5209d516d6231898`**、Main Rev.2最終基板SHA256は **`acab039f3b5f5ea30500d2f8537e320e198f881c227a3c3042753fc021c30f1c`**。監査 #183 の起点と一致する。

一時ファイル・TMPDIR・XDG設定・出力staging・Git管理情報は `.issue185-runtime/`。既設KiCad 9.0.9、geometry、triangle、CAM viewer環境は読み取り使用し、ルータは起動していない。通常worktreeの読み取り専用Git管理情報を変更せず、同じ作業ツリーを参照する `.issue185-runtime/git` でコミットする。PRは #176 の上に積み、baseを `issue-175-main-dual-wing-final2` とする。`project-status.md` とDashboardは編集していない。4時間の上限内で実施し、時刻と公開結果はE/status.json、publication.jsonに記録する。

## 33個から先に、残る2個を最後に

#183の `move-probes.json` にある33個の直線接続候補を、その座標と接続アンカーで同時適用した。既存segmentを切除せず、viaだけを移し、同層・同幅のstubを83本追加した。再fill後のDRCで未接続0、物的違反0。全via再監査では未達が35→2個となり、残ったのは指定のC5.2／GNDとC4.1／V3V3だけだった。E/straight33/ の基板、changes.json、drc-libraries.json、audit/ がこの中間状態を保存する。

この確認後、残る2個を順に処理した。既存銅箔と部品を固定し、元viaから半径3mm以内の移設先を0.025mm格子で探索、接続経路は局所6×6mmの範囲で探索した。viaの全パッド間隔、他ネット配線、他via、外形、穴、禁止領域を避ける条件を課した。配線幅は0.10mmを維持し、最終判断はnative DRCと独立接続グラフで行った。

| via／ネット | 元位置 mm | 採用位置 mm | 接続 |
| --- | --- | --- | --- |
| `6bf1ec76-373b-473d-8a4f-1220e3ffc25f`／GND | (94.5,102.0) | **(94.2,100.525)** | F.Cuは既存配線を避ける8本の局所迂回、In2.Cuは1本で元配線へ接続 |
| `83b6e9ed-f13d-4984-8aac-1d3fee6bd3fb`／V3V3 | (93.5,99.2) | **(92.975,99.675)** | F.CuとIn2.Cuで各1本。#183の最近傍候補とは異なる移設先で成立 |

E/local35/changes.json に全座標と追加segment UUIDを保存した。前者はGND planeだけに接続を任せず、既存F.Cu／In2.Cuへの接続も保持。後者は#183の「直線候補なし」という単独探索の結果を不可能証明として扱わず、33個移設後の銅箔で局所探索した。

**全体再配線0回／上限2回、既存配線rip-up0回、配置変更0、条件緩和0。** 元の693 segmentは全保持し、35 viaの座標変更と94本の追加segmentだけで成立した。難所の連鎖や資格確認の不復帰には至らず、停止条件に該当しなかった。

## 全44ネットと独立4指標

[最終基板](../hardware/kicad/qualification/issue-185-main-rev3/inspection/final/main.kicad_pcb) のSHA256は **`0e81ba42b194e03fb0422b58a64c967fe83166d0495d84f28c4171184b665bae`**。#175の元projectをbyte一致で使用し、GND zoneを再fillした。ルータの自己判定に依存していない。

| 指標 | 最終結果 |
| --- | ---: |
| 必須未接続 | **0** |
| 異ネット接触（未接続パッド含む） | **0** |
| 物的違反 | **0** |
| 説明不能な転送差分 | **0** |
| 検証ネット | **44** |

E/inspection/final/assessment.json、connectivity.json、transfer-diff.jsonを参照。独立した実銅箔union-findは、全パッド、配線、viaの各層接続、実GND fillの外周／穴を使用する。AST照合ではfill cacheだけを正規化し、35個の移設と94本の新設をUUID・端点・幅・層・ネットまで照合した。既存693 segment、その他78 via、配置・パッド・論理ネット・外形・zone規則等に説明不能な変更はない。さらに#175の凍結回路契約・schematic exportと、新PCBの245論理pinを再照合して差分0を確認した（E/circuit-check-final.json）。接続グラフの必須銅パッドは221個で、無接続pin等を含む論理pin数とは区別する。

D-019の4層・1.2mm、信号幅／間隙0.10mm、全113 viaの0.60/0.30mm、In1.Cu GND専用（信号track0）を保持した。66 footprintの位置・角度はすべて一致し、4取付穴のφ5mm銅箔予約も実fillを含めて確認した（E/geometry-check.json）。印刷警告61件（text_height44、silk_overlap12、silk_over_copper5）は継承しており、印刷整備の完了は主張しない。短絡・間隙・mask等の違反は除外していない。

## #183と同じ全via監査

E/source183/audit.py は#183の測定コードをそのまま保存し、E/audit-board.pyから新基板snapshotに適用した。native effective copper shapeで全パッドを走査し、共通銅層における `中心–パッド距離 − via半径` を測る。同ネットもテストパッドも免除せず、NPTHをパッド銅から除外する。合否には丸めた緩い許容差を導入していない。

| 対象 | 全via | 中心／drill縁／annulusのみ／重なりなし | 0.10mm未達 | 最小間隔 |
| --- | ---: | --- | ---: | ---: |
| 起点Main Rev.2（#183） | 113 | 24／5／3／81 | 35 | −0.300000mm |
| **Main Rev.3** | **113** | **0／0／0／113** | **0** | **0.100000mm** |

E/local35/audit/via-pad/all-vias.json/csv、summary.json、pads.jsonに全件を保存した。E/paste-via-check.jsonでは、via銅円とdrill円を両面の全paste図形・pasteパッドに照合し、いずれの重なりも0。CAMのmask開口は部品ランドと一致し、via開口はなく、従来のtentingを保持する。ちょうど0.10mmの箇所も含む名目設計の合格であり、製造公差や任意工程での無条件な受入れ保証ではない。

## 電源抵抗の再抽出

#175と同じ実segment幅・viaの正側モデル、実GND fill／thermal／track／pad／barrelのDC sheet FEMを新基板から再抽出した。条件は125°C・track幅−20%、銅35µm／barrel20µm仮定、PGND=U6.10、USB GND接点、GH各6 GND接点。同じモデル境界で共通と分岐を分離する。

| 経路 | 新抽出値 mΩ |
| --- | ---: |
| USB入力正側／GND／往復 | 127.726／11.372／139.098 |
| Main共通正側／GND／往復 | **31.257／9.878／41.135** |
| J2分岐往復 | **24.834** |
| J3分岐往復 | **26.095** |

共通・分岐とも50mΩ目標を維持。USB入力の139.098mΩはこの50mΩ目標の対象ではなく、#175の134.095mΩから約5mΩ増加したため、E/power-budget.json、connector-current-sensitivity.csvも新抵抗で135条件を再計算した。効率下限、実Main負荷、起動・過渡・逆給電、USB許可firmware、信号品質の実測保証にはしない。

E/resistance-summary.json、power-extraction-final.json、ground-extraction-final.jsonに新基板hashを固定。2段階mesh（最大三角形面積0.03／0.0075mm²）、相反性、重ね合わせ、KCL、解析解との照合を保存した。GND共通値のmesh差は約1.1%（幅−20%）であり、精密な製造上限値を示すものではない。

初回GND抽出は新しい局所接続の境界付近でゼロ面積三角形を検出してassert停止した。解析用の境界座標を1nm格子に揃え、メッシュ生成時だけ原点を平行移動して数値退化を解消した。従来の2µm境界簡略化・モデル条件は維持し、PCB・DRC・配線には変更していない。修正後4ケースをすべて解析し、数値検証を通過した。生の失敗ログもE/processes/ground-resistance/に保存している。

## 製造パッケージ、D-030、残る確認

E/manufacturing/に4銅層・mask・silk・outlineのGerber、113 round via drill・4 plated slot・6 NPTH、両面paste、BOM/CPL、fabrication-only ZIP、CAMプレビューを再生成した。実装58個、テストパッド4個をBOM/CPLから除外し、CPLの `X=KiCadX−76, Y=122−KiCadY` と全58配置を照合した。Gerbonaraで全線・pad・via・実GND面（対称差0）・外形・取付穴予約・mask・paste・drill・ZIP内容を照合済み。drillの最大出力量子化変位は約0.000653mm。E/cam-check.jsonとexport-provenance.jsonを参照。

CAM contact sheetを目視し、4銅層、4取付穴予約、北側C26–C28のpaste、USB shellの裏面pasteを確認した。資格確認後の銅箔編集はない。製造ファイルのprefix `main-stage2` は既存exporterとの整合のため保持するが、このフォルダ内の全出力は上記Rev.3 hashから再生成した。

[decisions.md の D-030](decisions.md#d-030---main-rev3-via-relocation-to-remove-the-pofv-design-requirement)に、今回のRev.3データからD-022のPOFV指定を外す提案を追記した。D-028／D-029は使用せず、旧Rev.2のPOFV仕様や既存成果物を上書きしていない。J1の同一Economic PCBA工程とD-019は維持。E/manufacturing/quote-handoff.mdを新パッケージ用の引継ぎとする。

業者のDFM受入れ、tenting／mask公差、実銅厚・plating・stackup、調達・見積・実機確認は別途必要。#176コメントで報告された見積上の代替部品を、このIssueでrepository BOMへ採用していない。新パッケージを業者へアップロードせず、新見積も取得していないため、POFV料金やvia plating料金の実削減額は未確定。旧見積をRev.3の確定価格に流用しない。

初回33個生成はKiCadのUUIDプロパティがread-onlyのため保存前に停止し、通常の自動UUID生成に修正した。初回中間DRCのlibrary設定不足は、元の凍結footprint libraryを指すfp-lib-tableを用意して再確認した。最終DRCにはlibrary警告なし。いずれも条件変更や全体再配線の試行ではない。

## 提出と検証

E/verify.pyは、4指標、via全件、paste、配置、抵抗、CAM、source hash、変更範囲、文書リンク、manifestを確認する。実行ログと結果はE/verification.json。公開結果はE/publication.jsonに保存する。**Draft PRのみ提出し、発注・課金・mergeは行わない。**
