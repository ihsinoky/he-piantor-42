# Issue #217 — 整理計画 P6：教訓のプロセス昇格

2026-11-08、`.p6-runtime/instructions.md` を全文読み、
[整理計画5.4節](repo-cleanup-plan.md#54-教訓の昇格)、
[D-031](decisions.md#d-031---knowledge-recording-adr-finding-records-and-promotion)、
[Finding台帳](findings.md)、既存workflow・テンプレート・governanceと照合した。
基準commitはP5cマージ済みの `f5429385be3000dea4a61b6f018d794cb6f1c8ce`。
本PRの識別子は Issue #217 / ブランチ `issue-217-p6`。今回はローカルコミットで
停止するためPR番号は未発行であり、番号やURLを推測しない。
`Promoted to` に採用先の節、本PR識別子、P6提案版を記録した。
PMOによるpush・PR起票時に実番号との対応を引き継ぐ。マージ前はプロセス変更の提案である。

## 変更と組み込み方の根拠

| 源Finding | 採用先 | 手戻りを防ぐ検査・停止条件 |
| --- | --- | --- |
| F-002 / K03 | [workflow: Independent acceptance](development-workflow.md#independent-acceptance)、[PR: Verification / CI](../.github/pull_request_template.md#verification--ci) | 保存出力を元の承認ルールで独立検査し、設定差分も記録。exit codeや未配線数・違反数の自己申告では合格にしない。未検査・不合格・無承認設定差分は受入れ／依存工程を停止、nullを0にしない |
| F-008 / K07 | [workflow: Retained-artifact comparison](development-workflow.md#retained-artifact-comparison)、PR同節 | 局所変更の前に保持配線・データ集合を固定し、後の差分を合否に含める。PCBは同層・同幅・同ネット被覆、via、非配線AST、全体接続・DRCを確認。保持対象未定義・未検査・範囲外変更／欠落なら停止 |
| F-004 / K09 | [workflow: Full via-pad audit](development-workflow.md#full-via-pad-audit)、PR同節 | 共通銅層の全via×全銅padをannulus外周から監査。同ネット・NC等も含める。重なりだけ／drill縁だけの検査は不可。全件性不足・承認基準未達なら停止し全件再監査。名目幾何の0.10mmは業者DFMや製造公差の保証ではない |
| F-003 / K08 | [Engineering work: Measurement boundaries and guarantees](../.github/ISSUE_TEMPLATE/engineering-work.md#measurement-boundaries-and-guarantees) | 比較・測定境界と保証要件を別欄とし、測定位置・基準・損失、設計負荷とストレス／包絡を分記。要件・モデル／測定設定・負荷ケースを入力とし、不明／矛盾／保証根拠不足なら実装・配線前に停止してPOへ照会 |
| F-005 / K12 | [workflow: PCB-to-case handoff](development-workflow.md#pcb-to-case-handoff)、PR同節 | 基板側の確定入力とケース受領側の全ファイル集合・hash・固定点集合を各variantで照合。点数・外形一致だけでは不可。穴・ボス・逆変換・許容差も確認。不一致・未検査は引継ぎ受入れと下流利用を停止 |

workflowは既存のMerge gatesに必要な証拠を具体化する位置に追記し、既存本文は
そのまま残した。各手順に適用条件・入力・検査・停止条件・責任者を明記した。
実装者／Codexが証拠を作成、PMOがread-onlyレビュー、POが受入れ・要件変更を判断する。
PRテンプレートには同手順への参照と証拠チェック欄を加え、非該当時にも理由を残す。
IssueテンプレートはRequired CI / verificationの前で境界を確定できる構成とした。
新しい台帳や実行skillは作らず、Findingの観測条件・本文も書き換えていない。

## 昇格しないFindingの判断

| Finding | P6判断と理由／将来条件 |
| --- | --- |
| F-006 / K05 | 昇格しない。旧Wing固定条件のDC比較で、最低電圧保証は残る。現行Rev.3の設計規則へ一般化せず、将来の電源予算手順を別Issueで定義する際の候補とする。境界・負荷の分離は今回F-003から昇格 |
| F-007 / K06 | 将来候補、今回は昇格しない。NPTH自己違反と全層実銅予約の別検証は有用だが、円近似・座標量子化・再fillを含む入力／許容差を定める独立の手順が必要。4nm補正を一般規則にはしない |
| F-009 / K11 | 昇格しない。特定PCB hash・材料・メッシュ・負荷のモデル結果で実測保証ではない。将来の抵抗抽出／電源予算手順で環境・収束・入力更新条件を定義してから再検討 |
| F-010 / K01 | 将来候補、今回は昇格しない。固定assetとimporter二版の観測。変換忠実度ゲートにするには対象形式・形状・権限・許容差の契約を別途定義する。特定版の欠落を全版へ一般化しない |
| F-011 / K02 | 昇格しない。固定JITX候補の電気parityと物理接続の区別は、今回F-002由来の独立判定に整合するが、JITX固有の再資格手順の採用は範囲外。既存D-016を変更しない |
| F-012 / K04 | 昇格しない。層／幅／間隔の複合条件での有限試行であり、層追加や特定寸法による成功保証を手順化できない。再試行時は既存EDA method changes and retriesと今回の独立検査を適用 |
| F-013 / K10 | 将来候補、今回は昇格しない。旧裸基板価格から現行PCBAへの転用不可という観測。費目・版・数量・工程・業者審査を入力にした再見積手順は別Issueで定義する |

これら7件の `Promoted to` はP6未昇格と本節への参照に置換し、「P6で判断予定」を
残さない。F-001は今回の判断対象外で、未昇格表記も保持した。

## 既存規約との関係と引継ぎ

- 整理計画5.4節末尾の「今回はskillや手順を実装しない」は計画作成時の記述で、
  P6の手順／テンプレート実装を求める今回指示とは文面が異なる。
  今回はP6指示と同計画のP6合格条件に従い、計画本文を勝手に修正しない。
- workflowのDraft PR早期作成と、governanceのPMO read-only／CodexによるPR作成に対し、
  今回指示はローカルコミット後に停止・pushはPMO担当とする。
  今回の提出経路としてその明示指示に従い、push・PR作成は行わない。
  恒常的な役割変更は採用せず、既存workflow・governanceも書き換えない。
- 追記した独立検査は既存のCI・ERC/DRC・再現性確認を補強する。
  緑CIや数値0だけでHuman Gateを通過させる記述は追加していない。
  技術受入れ、製造承認、モデルと実物評価は分けたままである。

別PR候補として、via–pad全件監査は反復性があり、PCB・承認基準を入力、
全ペア／最小値／違反一覧を出力にできる。native effective copper形状の取得法、
KiCad・Python・幾何ライブラリの固定環境、自己検査と例外処理を定義した上で
skill化の必要性を判断する。今回はskillの作成・採用を行わない。

[既存横断ノート](lessons-learned-device-development.md)への将来の案内候補は、
「本ノートは2026-11-06時点の記録。現行判断はdecisions、状態はproject-status、
新知見はfindings、実務手順はdevelopment-workflowを参照」とする注記である。
旧POFV推奨やケース未着手を現在状態に転用しないための案内に留め、本文は変更しない。

## 検証と提出

`.p6-runtime/verify-promotion.py` と `.p6-runtime/verification.json` で次を照合し、PASSを確認した。

- 既存workflow・両テンプレートは追記のみで、元の文章・順序を保持。
  各手順の5要素、Finding参照、PRチェック欄、Issueの5入力欄を確認。
- 台帳F-001〜F-013は一意。変更はF-002〜F-013の `Promoted to` のみで、
  その他の本文はbyte一致。昇格5件に採用先と本PR識別子、未昇格7件に判断参照がある。
- 追加したローカルリンク・節アンカー30件が解決する。内容レビューで同ネット免除なし、
  annulus外周・全件監査、独立合否、保持差分、境界と保証、固定点集合の区別を確認。
- 基準commitの追跡14,966ファイル全件をGit blob hashで照合し、既存変更はworkflow・
  両テンプレート・findingsの4ファイルだけ。追加成果物は本報告だけ。
  他14,962ファイル（設計データ・証跡・既存横断ノート・ADR・他の報告）は不変。
- ローカルクローンの `git diff --check` を通過。文書変更のため、CAD生成・配線・
  DRC等の設計実験は再実行せず、この検証を技術設計の新規合格とは扱わない。

このチェックアウトを元に `.p6-runtime/git` へローカルクローンを作成し、
その `.git` と現在のチェックアウトをwork-treeとして `issue-217-p6` にコミットする。
スクラッチ・検証スクリプト・結果JSONは `.p6-runtime/` 内に置き、コミットしない。
通常チェックアウトのgit状態へコミットせず、pushせず停止する。
