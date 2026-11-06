# Issue #175 — C26配置成立、全体配線1回で独立4指標0、確定見積は未取得

**1210出力Cを維持した候補2はPCB資格合格。製造GOではない。** 最大3候補のうち2候補を試し、C26中心 `(92.2,78.2)mm / 0°` を選んだ。準備DRCを通過してからD-019条件で全体配線を1回実行し、独立検証で全44ネット・4指標すべて0。抵抗再抽出、製造データ再生成、CAM照合、POFV再分類を完了した。**PCBA確定見積と業者受入れは未取得のため、Issue全体の完了は主張しない。** 発注・課金・mergeは0。

以下 E は[今回の証跡フォルダ](../hardware/kicad/qualification/issue-175-main-dual-wing-final2/)を指す。

## 起点と実行枠

`.issue175-runtime/instructions-175.md` を全文読み、[Issue #175](https://github.com/ihsinoky/he-piantor-42/issues/175) と [Draft PR #174](https://github.com/ihsinoky/he-piantor-42/pull/174) を取得。#173 head **`483c73ef7bcb95bb5e4bba84c7c06e3f22011268`** から **`issue-175-main-dual-wing-final2`** を作成した。作業リポジトリは指定の現在ディレクトリ。読取り専用の通常 `.git` を変更せず、`.issue173-runtime/git` のメタデータを `.issue175-runtime/git` に複製し、同じ作業ツリーで使用した。開始記録は2026-11-06 08:47:06 UTC、3時間以内に実施した。

一時ファイル、TMPDIR、XDG、FEM依存パッケージ、プレビュー、Gitメタデータは `.issue175-runtime/`。既設KiCad/KRT/viewerは読取り使用。KRTの2055 source hashesに変更なし。E/runtime-check.json を参照。既存の決定記録・既存成果物は変更しない。

## 2候補のpreflightと幾何学

#173の配線前入力 `inputs/final/main.kicad_pcb` を起点にした。C26とその2個のF.Paste開口だけを移動し、ほか65 footprintの位置・角度、#155由来の既存53部品、すべての種segment/viaを保持した。配線後基板のrip-upではない。

| 候補 | C26中心 mm、角度0° | SW2との銅箔間隔 | J3.15との間隔／重なり | 準備DRC |
| --- | --- | ---: | ---: | --- |
| 1 | (92.3,77.8) | 0（重なり約0.222666mm²） | 0.250mm／0 | shorting_items2、solder_mask_bridge2、不合格 |
| 2 | (92.2,78.2) | **0.150mm** | **0.350mm／0** | **物的違反0、合格** |

候補2のC26–C27ランド間隔は0.150mm、重なり0。C27/C28は移動不要だった。C26を左へ戻すだけでは、y=76.4mm付近の固定SW2配線に大きな1210ランドが接触する。候補2はその配線の下側へ0.4mm動かし、J3.15の左側とC27の上側の隙間を使うことで成立した。**配置不成立を理由に停止する条件には該当せず、D-019緩和が必要という結果でもない。** 候補3は未生成。

各候補のnative KiCad DRC、生の違反、board/project/DRC hashを `inputs/candidate-*/` に保存。E/placement-check.json は独立した幾何学・位置・種配線保持確認。印刷警告3種（text_height/silk_overlap/silk_over_copper）と配線前via_danglingだけを従来どおり区別し、clearance・短絡・mask違反を除外していない。CLI終了コードだけで判定せず、内容を検査した。

## 全体配線1回と独立資格確認

選択候補のhashに結び付けたpreflight receiptを検証し、resolver読み戻し後にattemptを原子的に予約した。**全体配線1回／上限1回、局所修復・局所rip-up0回**。4層、1.2mm、信号幅／間隙0.10mm、via0.60/0.30mm、In1.Cu GND専用、escalation off、keep-input-copper、既定mps順序。条件緩和なし。

ルータ自己判定を最終資格にせず、固定した入力projectの規則でKiCad再fill・DRCを実施し、別の実銅箔グラフとcanonical AST比較で確認した。

| 独立指標 | 結果 |
| --- | ---: |
| 必須未接続 | **0** |
| 異ネット接触（未接続ランドを含む） | **0** |
| 物的違反 | **0** |
| 説明不能な保持配線転送差分 | **0** |
| 全ネット／論理pin照合 | **44／245** |

E/inspection/final/assessment.json、connectivity.json、transfer-diff.json、E/circuit-check-final.json を参照。637本の0.10mm線と保持した太線を含め、全信号幅は0.10mm以上、In1信号track0、GND fill1面、全113 viasは0.60/0.30mm。4層・1.2mmを再確認した。印刷警告61件（44/12/5）は継承しており、印刷整備完了は主張しない。

最終基板は [E/inspection/final/main.kicad_pcb](../hardware/kicad/qualification/issue-175-main-dual-wing-final2/inspection/final/main.kicad_pcb)、SHA256 **`acab039f3b5f5ea30500d2f8537e320e198f881c227a3c3042753fc021c30f1c`**。ルータが出力projectへ書いたmin_via_drill等はtransfer-diffに保存し、資格確認・製造出力には元projectを使用した。

## 実配線からの抵抗再抽出

正側は実segment幅とvia、GNDは実fill・thermal・track・pad・barrelから再抽出した。境界はU6.10 PGND、USB接点、GHの6 GND接点。従来と同じ125°C・track幅−20%、銅35µm・barrel20µm仮定のモデルである。

| 経路 | 抽出値 mΩ |
| --- | ---: |
| USB入力正側／GND／往復 | 122.727／11.367／134.095 |
| Main共通正側／GND／往復 | **31.355／9.875／41.231** |
| J2分岐往復 | **24.833** |
| J3分岐往復 | **26.095** |

共通・分岐50mΩ目標をモデル内で満たす。2段階mesh、相反性、重ね合わせ、KCL、解析解との照合をE/ground-model-verification.jsonへ記録した。E/resistance-summary.json が新基板hashに対応する。E/power-budget.json と connector-current-sensitivity.csv は新抵抗を用いた135条件の再計算。銅厚・plating・stackupの保証最小、効率下限、Main負荷、起動・過渡・逆給電・ADC settling・USB許可firmwareは実証していないため、実動作や最遠センサ電圧の保証ではない。

C26–C28は **TDK C3225X7R1C226K250AC（22µF/16V/X7R/1210）** を維持。#169の38.62485µFは選定スクリーニング値であり保証容量ではない。今回のPCB合格を容量・動特性の保証へ転用しない。[TDKの現行製品ページ](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C3225X7R1C226K250AC)はNRND表示であり、別品への自動置換はしていない。

## 製造データとPOFV

[E/manufacturing/](../hardware/kicad/qualification/issue-175-main-dual-wing-final2/manufacturing/) に新基板から4銅層・mask・silk・outlineのGerber、PTH/NPTH drill、両面paste、BOM/CPL、CAMプレビュー、fabrication-only ZIPを再生成した。62電気部品、実装58個、J1は12 SMD contacts＋4 PTH shell legs、4 testpadは実装BOMから除外。CPL変換は `X=KiCadX−76, Y=122−KiCadY`、全58位置を照合した。

GerbonaraによるCAM照合で、全銅箔線・pad・via、GND面のpolygon対称差0、4穴のφ5mm銅箔予約、113 round drills、4 plated slots、6 NPTH、mask・paste開口、ZIP内容を確認した。プレビューを目視し、4銅層、北側追加Cのpaste、4つの取付穴の予約、USB shell側の裏面pasteを確認。E/cam-check.json と export-provenance.json を参照。基板やCAMに資格後の銅箔編集はしていない。

新POFV分類は **全113 vias中32候補**：mounted-center-in-pad23、mounted-drill-edge-overlap5、mounted-annulus-only3、bare-testpad1。実装padへのdrill重なり28、pasteへのdrill重なり24。E/pofv-reclassification-final.json、pofv-sites-final.csv、all-vias.csv が新基板に対応する。**epoxy fill＋copper capを維持し、J1 PTH脚とNPTHはfill対象外**。適用範囲と加算額の業者受入れは未取得。

## PCBA確定見積の未完了項目

[E/pcba-update-status.json](../hardware/kicad/qualification/issue-175-main-dual-wing-final2/pcba-update-status.json) と manufacturing/quote-handoff.md に引継ぎ条件を固定した。5枚・48×52mm・4層・1.2mm・Economic PCBA、58実装部品／枚、J1を同一工程、POFVを含む条件である。

[JLCPCB公式手順](https://jlcpcb.com/help/article/how-do-i-place-a-pcba-order) と [見積ページ](https://cart.jlcpcb.com/quote/?fromDemo=yes) を取得した。公式手順ではGerber、BOM/CPL処理、部品照合、配置確認を経て見積へ進む。この環境には業者操作用connector／browser機能、認証済み見積session、利用可能な見積APIがなく、公開フォームの読取りまで。アクセス手順をユーザーへ照会したが、確定見積は取得できていない。**金額・quote ID・有効期限はnull**。旧48×44mm見積や旧seed-a価格を流用しない。

R17とTDK出力Cの調達／在庫／MOQ、POFV仕様と範囲・4層加算、J1 PTH脚を同じEconomic PCBAで実装する受入れ、stackup・銅厚・plating、送料・税等が残る。外部へ設計をアップロードせず、カート追加・注文・課金・サポート送信を行っていない。**製造GOへ進めず、PCB合格・見積未完了として引き継ぐ。**

## フォールバック、実行上の修正、公開

#173の [fallback-seed-a](../hardware/kicad/qualification/issue-173-main-dual-wing-final/fallback-seed-a/) は一切変更せず維持。E/fallback-preservation.json で全ファイルを起点Git blobへ照合する。今回の1210 BOM／CAMと混用しない。

初回準備スクリプトは重なり状態のF.Pasteを幾何選択したためassert停止し、基板を生成しなかった。#173の2開口UUID指定に修正して同じ候補1を生成した。初回DRC起動のboard-load失敗も保存。runtime auditは継承した旧base参照のassertを修正した（KRT2055 hashの一致確認自体は両回とも通過）。CAM検証初回はsystem PythonにGerbonaraがなくimport失敗し、既設viewer runtimeで実行した。これらの失敗をprocess証跡に保持し、配置候補追加・再配線に数えていない。正常な配置候補は2つ、実ルータは1回だけである。

報告書と新規Eのみコミットし、指定ブランチへのpushとDraft PR作成を試みる。結果はE/publication.jsonに記録する。Issue自動closeとmergeは行わない。ホスト引継ぎのGitは **`.issue175-runtime/git`**。
