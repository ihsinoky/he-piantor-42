# work 層方式と一次発信の入口についての議論

2026-11-08／PO・PMO向けの提案。基準は `repo-cleanup-plan` の `7e530399987391d9a3484e89251eb51529629a4d`。`.cleanup-runtime/discussion2-brief.md` を全文読み、[整理計画](repo-cleanup-plan.md)、[前回議論](publication-discussion.md)、実ファイルと照合した。既存文書の変更や配置方式の採択は本書では行わない。

## 1. 見解と前回議論の修正

**版を固定した成果物を Release 時だけ選別してコピーする運用には賛成する。一方、その前提として既存 hardware 全体を今すぐ一段下げることには反対する。** コスト最優先なら、まず既存パスを維持して薄い入口と固定版の配布を作る方が安い。work 層の構造自体に価値を置くなら、後述の移行検証を費用に含めた条件付き採用としたい。

「公開」はリポジトリの可視性ではなく、POがX等の一次発信で明示的に触れることだった。前回議論2節の可視性を中心とした前提整理は、この問いへの応答としてずれていた。また前回のA（別リポジトリ）推奨を今回は引き継がない。一次発信の入口を厳選する目的には、同じリポジトリの編集した文書や Release ページでも対応できる。別リポジトリを維持する費用を先に負う根拠は弱くなった。

PO案は「開発の原本は残し、読者に渡す成果だけを節目に選ぶ」という点で合理的である。ただし、フォルダを一段下げても入口の編集は自動では済まない。Release前の一次発信には、概要・数件の知見・現段階の限界だけを示す文書を入口にし、必要な人が成果物索引、D/F、原資料へ進めればよい。正式Release前なので成果物を work にだけ置く、という運用は可能だが、未Releaseを理由に現在のパスを必ず変更する必要はない。

優先順位 **コスト > 後戻りの少なさ > 自由度 > 早さ** に対する推奨順は次の通り。

1. 現在の配置＋編集した入口＋固定タグ／選別した Release 配布物。日々の作業パスは維持する。
2. 物理的な二層が必要なら、hardware の work 化と版付き凍結コピー。リンク・検査器・manifestの対応を先に確定する。
3. mechanical／manufacturing／docs／firmwareまで一律に work 化する案は当面採らない。

## 2. リンク整合性：実参照を数えた結果

### 2.1 対象と数え方

基準commitの追跡対象は **14,922ファイル**（計画作成後に計画書と前回議論が加わった数）、うち `hardware/` は **14,810ファイル**。UTF-8で読め、NULを含まない13,972ファイルを文字列検査した。未追跡の `.cleanup-runtime/` やGit内部は除外した。

模擬した移動は **すべての `hardware/X` → `hardware/work/X`**。README・ライブラリ・凍結入力を含み、他ツリーは動かさない。ファイルも参照文字列も実際には変更せず、移動後の仮想パス集合に対して参照先の存在を比較した。rootにREADME等を残す案は例外対応が増えるため、この単純案とは別の調査になる。

Markdownは `](target)` 型のインライン相対参照を対象に、fragmentを除いたファイル／ディレクトリの存在を確認した。同じ参照の繰り返しも1出現として数える。コードブロック内の同形式も含む機械的な概数であり、見出しanchor、参照定義型、HTML、動的生成URL、実行時の文字列結合まで完全解析した件数ではない。ファイル数は各行内の重複を除く。異なる行のファイル数や候補数を足して修正件数としてはいけない。

### 2.2 内部相対参照と境界を越える参照

| 分類 | 現在存在する参照：出現数／参照元ファイル数 | 一段移動だけの結果 |
| --- | ---: | --- |
| hardware 内から同じ移動対象内への相対参照 | 119／27 | 119件とも維持、新規不通0 |
| (a) 外から hardware 内への相対参照 | 414／77 | 414件とも新規不通。内訳は root README 1、LICENSE 1、docs 412 |
| (b) hardware 内から移動対象外への相対参照 | 75／49 | 75件とも新規不通。root LICENSEへの1件も含む |
| 移動と無関係な相対参照 | 172／48 | 新規不通0 |

この検査で移動前から存在する780件のうち、**489件が新規不通になる**。別にhardware内部として解釈される参照が326件／20ファイル、移動前から存在確認できなかった。これらには凍結された文書コピー内の参照等が含まれ、今回の移動による破損へ加算していない。全インライン相対参照の抽出数は1,106件。

具体例（行番号は基準commit）：

| 分類 | 実在する参照元と記述 | 影響 |
| --- | --- | --- |
| 内部 | `hardware/jitx/ARCHITECTURE.md:35` の `../rev-m1/architecture.md` | 両方がwork下へ移るので維持 |
| (a) | `LICENSE.md:37`、`README.md:65` の `hardware/lib/THIRD_PARTY.md` | 旧パスに対象がなくなる |
| (a) | `docs/alternate-physical-backend-converter-repair.md:13` の `../hardware/tscircuit/qualification/eda-004d/evidence/authority.json` | `../hardware/work/...` 等への対応が必要 |
| (b) | `hardware/case/issue-198-final/README.md:3` の `../../../docs/issue-198-case-final.md` | 移動後は `hardware/docs/...` を探す。rootへ出る `../` を一つ増やす必要がある |
| (b) | `hardware/kicad/qualification/eda-004e/README.md:39` のLICENSE参照 | root LICENSEへの相対距離が変わる |

POの見立てのうち「サブツリー内部の相対参照は保たれる」は、この119件について裏付けられた。「したがってリンク整合性はほとんど崩れない」という全体評価は支持できない。現在有効な境界越えの参照だけでも489件あり、さらに次の実行・証跡への影響がある。

### 2.3 スクリプト・CI・記録パス

| 分類・検索パターン | 出現数／ファイル数 | 読み方 |
| --- | ---: | --- |
| (a) hardware外のテキスト中の `\bhardware/` | 701／87 | Markdown、コード例、ライセンス表、CI、taskの出典文字列等を含む候補。414件のリンクと重なる |
| (c) hardware内の `.py/.js/.ts/.tsx/.sh` 中の同パターン | 502／277 | root相対パスや説明文字列等の点検候補。すべて実行箇所とは断定しない |
| (c) hardware内Pythonの `.parents[数字]`（空白許容） | 204／196 | 階層固定の候補。すべてがroot取得ではないため全件破損とは断定しない |
| (c) 上記スクリプト内の `/home/hatch/workspace/projects/he-piantor-42` | 10／8 | 既存の実行環境依存。work化とは別に再現環境の確認が要る |
| (c) `.github/workflows/` 中の `\bhardware/` | 24／2 | 起動条件、working-directory、cache、実行コマンド、収集パス等 |
| (c) `.gitignore` 中の同パターン | 3／1 | 出力除外が新しい作業場所に効くか確認する |
| (d) JSONの「`hardware/`で始まるキー → 64桁hex値」 | 35,548／79 | パス付きSHA-256記録の延べ数。35,543件は基準commitに同名ファイルが実在、5件は非実在。過去版・凍結コピーを含む |
| (d) JSONの「それ以外の `/` を含むキー → 64桁hex値」 | 73,821／154 | パッケージ内相対パスや絶対パス等。自動的に破損・保存とは判定しない |

(d)はJSONを再帰探索したキーと値の組の数であり、同じ実体を複数の証跡が記録している。hashそのものが移動で変わるという意味ではない。また `tray-left.stl` のように `/` を含まないキー、値として記録されたパス、SHA-1等はこの数に入らない。

実害を確認できる例は次の通り。

- `hardware/case/issue-198-final/base.py:14` は `Path(__file__).resolve().parents[3]` をrootとし、その下の `hardware/kicad/...` を読む。移動後のroot解釈は実際の `hardware/` になり、`hardware/hardware/kicad/...` を探す。`verify.py:6` も同じroot取得を使う。
- `hardware/kicad/qualification/issue-196-main-rev4-phaseb/common.py:5` の `parents[4]` と、同 `verify.py:4` の `E.parents[3]` も一段ずれる。root取得だけを一段上げても、`R/'hardware/...'` の固定パスは旧配置のままなので、それだけでは直らない。`verify.py` はrootのdocsも読むため、Rをworkの親へ単純置換する解決も成立しない。
- `.github/workflows/engineering-ci.yml:109` は `python3 hardware/layout/generate_layout.py` を実行し、110行で生成差分を検査する。`tscircuit-native-spike.yml:23` は `working-directory: hardware/tscircuit`。CIコマンドだけでなく変更検出のパスも直さないと、検査が起動しなくなる可能性がある。
- Matrix Rev.3 の `manifest.json` は、root相対のhardwareパス→SHA-256を521組持つ。一方、Main Rev.4 Phase B の `manifest.json` は主に証跡ディレクトリ相対の `files` とroot相対の `documents` を分け、同 `verify.py:43-44` が両者を照合する。manifestは名前が同じでも基準が違う。
- ケース最終17mmの `dimensions.json` にはhardwareから始まる入力hashのキーが11組あり、`verify.py` は `ROOT/p` で読む。`exports-sha256.json` は出力ディレクトリ相対で照合するので、出力一式をそのまま動かす場合には別の扱いになる。
- Main最終基板の `inspection/final/fp-lib-table` は `${KIPRJMOD}/../../Rev4.pretty`。依存一式を同じ相対位置で動かせば維持できるが、Releaseへ基板単体だけコピーするとこの前提を満たさない。

**生データの保存と、移動後に同じ検証が走ることは別の合格条件**である。凍結したmanifest・ログの文字列を一括置換すると記録内容とそのhashが変わる。原記録は保持し、旧パス→新パスの対応表と、新配置を検査した新しい記録を別に作る必要がある。過去の絶対パスや実行ログを「修正済みの当時の記録」に変えてはいけない。

## 3. Releaseコピーを採用するなら

### 3.1 可変な複製との違い

整理計画4.1節の「最新という名前で複製しない」は、開発上の正本が複数になることを避ける方針である。**採択した特定版の凍結配布コピーは別物として認めてよい。** workを唯一の編集元、版付きコピーを配布の記録と定義する。配布側を直接編集せず、訂正はwork側の根拠を更新して別の版として出す。

常時同期なら設計変更ごとに二箇所の内容・状態・権利表示を合わせる。凍結版なら、費用は各Release時の選別・梱包・検査に限定される。ただし無料ではなく、対象選定、出典対応、コピー先での読込み、ライセンス表示、訂正案内の費用は残る。重大な誤りの通知は次の大きな節目を待たない。

物理二層を採る場合の配置例は **`hardware/releases/v0.1.0/`（未作成）**。PO案の「hardwareの直下へコピー」を、その直下に版付きパッケージを置く意味で具体化する。`hardware/main.kicad_pcb` を上書きし続ける形や、可変の `latest/` は推奨しない。バージョン名は例であり、正式な初版番号はPO判断とする。

### 3.2 出典の結び方と手順

各パッケージに、ファイル単位の対応manifestと人が読める案内を置く。ここでいうmanifestは新設案であり、既存証跡のmanifestを書き換える指示ではない。

| 記録 | 必須内容 |
| --- | --- |
| 版と用途 | パッケージID、版、作成日、対象基板／ピッチ／左右、配布用途、未検証範囲。Release済みと製造GO・実機合格を別項目にする |
| 出典 | 元リポジトリ、完全なsource commit SHA、元パス、元ファイルSHA-256。必要なD/Fや報告も同commitに固定したパス／見出しで示す |
| 配布物 | コピー先パス、配布ファイルSHA-256、対応する入力・ライブラリ・回路源・生成器・検査結果、パッケージ全体のhash |
| 判断 | 採択D番号とその適用範囲。MainはD-033、WingはD-034、MatrixはD-029を原典照合し、ケース等に未確認のD番号を作らない |
| 権利 | ファイル別のライセンス識別子、著作権・第三者通知、本文／対応ソース／出典の所在。単一の一括ライセンスで上書きしない |
| 変換 | 原則byteコピー。パス修正や書出しを行った場合は変換理由・手順・ツール版と、変換前後のhash・対応を残す |

手順は、source commitを確定→そのcommitから必要な依存一式を選ぶ→作業用出力にコピー→対応manifestと通知を付す→隔離して取得・読込み・必要な検査を行う→配布commit／タグと取得物hashを固定、の順とする。source commitと配布commitは異なってよい。配布commit自身のSHAをそのcommit内に自己記録する循環を避け、source SHAを内部に、配布commit／タグと取得物hashをRelease案内側に記録する。

現在の最終成果物には入力・失敗試行も同居するため、ディレクトリ丸ごとのコピーを配布対象選定の代わりにしない。Mainは基板／project／footprint／回路源／Gerber／BOM／CPLを、Wingは単板4種と面付け2種の用途を、ケースは17mm正／16mm検証版と印刷ピースを区別する。配布に必要なソースや依存を落としてファイル数だけを減らさない。

### 3.3 ライセンス対応で見落としてはいけない点

以下は既存 [LICENSE map](../LICENSE.md) と [THIRD_PARTY](../hardware/lib/THIRD_PARTY.md) の対応を保持する提案であり、新たな権利判定ではない。

- `hardware/**`、`mechanical/**`、`manufacturing/**` は基本CERN-OHL-P-2.0、docsやfirmware等は基本MIT。コピー先にライセンス本文と出典・通知を伴わせ、READMEだけで済ませない。
- `hardware/layout/layout_source.json` と生成物 `key_positions.csv`／`layout_preview.svg` はQMK由来のGPL-2.0-only例外である。Cantor/Piantorの上流revision・パス・blob記録とGPL本文を対応させる。Releaseへ含める場合もこの例外を維持する。
- **移動だけでも現在のLICENSE mapの例外パスは古くなる。** `hardware/work/layout/...` やRelease先では現行の特例パスに一致せず、広い `hardware/**` 行だけが目に入る。work側と配布側の両方に特例対応を明記する必要がある。`hardware/lib/...` の第三者資産も同様である。
- KeebioのMIT、RP2040-minimal由来のBSD-3-Clause、marbastlibの通知など、配布に含む依存を台帳と照合する。docsからMIT文書をhardwareの配布フォルダへコピーした場合も、格納先の広い規則だけでCERNへ変更したように見せない。

## 4. 対象範囲と名前

| 対象 | 現状と推奨 |
| --- | --- |
| hardware | 現在CAD/CAMとケース実体を収容する。二層案を採る場合の主対象だが、先に全体の移行表を作る。ケースだけ先行移動すると他のhardwareへの相対参照も内部扱いできなくなる |
| mechanical／manufacturing | 各READMEだけの案内用ツリー。workを新設しても実体の整理にならない。当面は採択した正本／Releaseへの入口とする |
| docs | ADR・仕様・状態・索引は開発と一次発信の共有入口なので現在位置を保つ。Issue報告群の物理移動は別判断。`docs/work/` への一律移動はD/F・task・READMEの参照も広く変える |
| firmware | 4ファイルのセンサ試験用実装。製品版ファームウェアのReleaseが必要になった時に、実際のビルド／配布単位で判断する |
| task／.github／ライセンス | workへ押し込まない。taskはマイルストーン＋現在位置の大局ビューというPO決定を維持し、出典とCI・権利のパスだけ対象に応じて直す |

ケースが現在hardware配下にあることを理由に、今回の案へmechanicalへの引越しまで混ぜない。また、複数の最上位ツリーを同時に一段下げても、ツリーをまたぐ相対参照が自動で保存されるわけではない。たとえば `docs/report.md` の `../hardware/...` をそのまま `docs/work/report.md` に移せばrootへ届かない。対象を増やすほど境界調査も増える。

名前は、PO案を採るなら **work** が短く分かりやすい。ただし「消してよい一時領域」ではなく「追跡・保存する編集元、採択済み原本と失敗証跡も含む」と運用規約に書く。

| 候補 | 評価 |
| --- | --- |
| `work/` | 短く、AIの作業場所という意図に合う。保存原本も入ることを明示する必要がある |
| `development/` | 開発用と伝わるが長い。採択済みの設計源も置くことは同じく説明が要る |
| `source/` | 編集元として明瞭だが、途中ログ・生成CAM・調査記録まで含む現状とはずれる |
| `archive/` | 活発な作業場所には不適切。旧版のみという誤解を招く |
| `staging/` | Release直前の一時置き場と読まれやすく、全履歴の原本保存には合わない |

## 5. 整理計画への変更案

本節は既存計画本文を変更する提案であり、今回その変更を実施しない。P3を物理移行待ちにせず、まず現行パスで正本を選べる状態を作る。

| 現行工程 | 維持／修正案と合格条件 |
| --- | --- |
| P0 | 「一次発信の入口」と「開発実体の配置」を分けてPO判断。薄い入口を先行し、work化の費用を負うか決める。Release前の発信も可能とする |
| P1／P2 | D-031/F-001取り込みとD番号・状態監査を維持。コピーや移動を理由に判断・知見の正本を複製しない |
| P3 | 成果物索引の「開発上の正本」と「配布版」を別欄にする。Release前は前者を現パス（移行後はwork）へ、後者は「未Release」と表示。Release後は版付きコピー／Release asset、元commit、hashを併記する。無条件に上層のファイルを正本と呼ばない |
| P4 | 履歴索引は原証跡を指す。移動したら現行workパスへの案内と、記録時点の固定commit参照を区別する |
| P5a/b/c／P6 | Finding登録・プロセス昇格は維持。発信用には原典を選別して参照し、別の知見台帳を常時同期しない |
| P7 | work化を採る場合、「基板別design/archive案の調査」から「hardware一括一段移動の依存調査」へ置換。旧→新全数対応、(a)〜(d)、ライセンス例外、旧URL対応、移行検査を成果物にする。調査そのものは省略しない |
| P8 | P7承認後にwork化の移動と修復を実施。元の基板ごとPR方式は、内部参照保存を崩すため機械的には引き継げない。hardware全体の移動PRを、内容不変の移動commitと参照／検査修復commitに分け、PR完了時に両者が揃うようにする。試行は別作業領域で行う |
| P9 | 削除を別判断とする方針を維持。workに移ったことや配布から省いたことを削除理由にしない |

追加工程は既存番号に割り込ませず、以下のW群とする。前回の別repo前提Q群は自動では実行せず、採用方式に合わせて統合する。

| 工程 | 作業・依存 | 合格条件／PO判断 |
| --- | --- | --- |
| W0：入口試作 | P3と並行し、一次発信用に概要・選別した知見・現在の到達点／限界を1入口へ編集する。Releaseを待たなくてよい | 初見者が目的別に辿れ、未実施の製造・実機評価を完了と読まない。POが発信で示す入口と範囲を選ぶ |
| W1：配布契約 | 初回Release準備時。版、対象、編集元、manifest、ライセンス、責任者、更新／訂正方法を決める | タグ／asset中心か、フォルダコピー併用かをPO判断。work化を必須依存にしない |
| W2：配布試作 | W1と対象設計版確定後。選別コピーと出典対応を対象別PRで試す | 原本hash不変、コピー対応全件、依存・通知・用途・未了ゲート完備。空の作業ディレクトリから取得物を開けることを確認 |
| W3：版固定と一次発信 | W2検証後、承認対象のsource／配布commitと取得物hashを確定 | POが版の配布と一次発信をそれぞれ判断。発信リンクの読者側取得確認。製造GOとは別 |

P8の合格条件は、移動対象14,810ファイルの過不足なし、移動commitでbyte hash一致、修復差分の明示、既存の不通と新規不通の分離、新規不通0、対象CIの起動条件と実行の確認、CAD・ライブラリの読込み、主要な生成／検査の隔離実行、manifest対応と権利表示の確認とする。全過去ツールを復活させる費用は別に見積もり、環境依存で走らないものを合格済みとしない。新配置の対応検査と保存原本の検査を分ける。

旧ブランチURLやIssue本文など、リポジトリ外の参照は本計数の範囲外であり移動後も残る。旧入口に案内READMEを残すだけでは各データファイルの旧URLは救えない。履歴参照は固定commit URLを使い、現在の入口に旧→新対応を置く。将来のReleaseコピーがたまたま旧パスを埋めることを移行の修復とみなさない。

## 6. GitHub Release／タグとの関係

GitHubのReleaseはタグを基に説明・配布物をまとめる機能で、タグ時点のリポジトリ全体のZIP／tarballへのリンクも付く。この自動アーカイブは、選別した製造パッケージと同じものではない。[GitHub公式：About releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)（2026-11-08確認）。

本件の低コスト案は、**編集した入口＋source commitを指す版タグ＋選別したRelease asset**。選別ZIP内にmanifest、必要ソース・依存・通知を含めれば、既存ツリーの大規模移動も、Gitツリー内への成果物コピーも必須ではない。タグだけでは選別・説明・コピー先での読込み検証を代替しない。

ブラウザで版付きの成果物を直接辿りたい、通常cloneで配布物も得たい、という要求があるなら `hardware/releases/<版>/` との併用にも理由がある。その場合はコピーを含む配布commitに版タグを付け、assetはそこから生成し、同一manifestで対応を照合する。フォルダ版とasset版を別々に手作業編集しない。版付きフォルダを増やす容量・一覧の混雑と、assetの取得導線のどちらを重視するかはPO判断となる。

タグ名だけを不変性の根拠にせず、完全commit SHAと取得物hashを残し、同じ版の差替えを禁止する運用にする。訂正は新しい版と旧版への注意書きで扱う。Release／タグの作成、配布、一次発信は今回は行わない。

## 7. 弱点と採用を見送る条件

- **移行の初期費用が大きい。** 14,810ファイルを一括で動かすレビュー、489件の境界リンク、検査器・CI・manifest・ライセンスの対応が要る。文字列一括置換では凍結証跡まで変えてしまう。入口改善だけが目的なら、この費用を先に払う理由は弱い。
- **パスが5文字（`work/`）長くなる。** それ自体がAI能力を大きく下げるとの実測根拠はないが、既存Issueや手順のパスが陳腐化し、rootの取り違え・長いコマンドの転記負担が増す。root引数や共通ヘルパーの導入は候補だが、その整備にも費用が掛かる。
- **上層コピーを編集元と取り違えやすい。** 「上にあるものが正」という説明だけではAIも人も誤る。唯一の編集元、凍結版、製造用入力を索引と各版READMEに明示し、可能ならコピー対応検査で直接編集を検出する。
- **workの中身は自動では整理されない。** 原本・失敗例・最終データが同居する問題は索引で解く必要がある。フォルダ深度だけでP3/P4を代替できない。
- **凍結コピーにも保守がある。** 版の増加、出典と通知の欠落、訂正伝達、配布物の取得確認が残る。管理担当と更新契機が決まらないならコピー層は作らず、まず固定commitへの索引に留める。
- **戻す費用もある。** 通常revertで履歴を壊さず戻せるが、移行後に新規成果がworkへ加わったり発信リンクが使われたりすると、単純なrevertでは足りない。移行前の固定commitと全数対応表、移行後作業の取扱いを先に用意する。

PO判断として残すのは、(1)入口先行かwork化先行か、(2)Git内の版付きコピーが必要かassetで足りるか、(3)初回にどの対象と限界を発信するか、(4)配布・訂正の担当である。推奨は入口先行とasset中心。work化を選ぶ場合も、原本保存と境界修復を検証した後に採用する。

## 付録：計数の再現方法と今回の検証範囲

作業用の全結果は `.cleanup-runtime/work-layer-audit.json` に保存した（コミット対象外）。以下は同じ基準commitのチェックアウトで主要数値を再計数するPythonコード。通常cloneでは `G = ['git']` とする。Markdownは存在確認済みの参照だけを移動破損へ数え、JSONは同じキーの繰返し記録も延べ数に含む。正規表現は動的なプログラム依存解析の代替ではない。

```python
from pathlib import Path
import subprocess, re, json, posixpath, collections
G = ['git', '--git-dir=.cleanup-runtime/git/.git']
BASE = '7e530399987391d9a3484e89251eb51529629a4d'
paths = subprocess.check_output(
    G + ['ls-tree', '-r', '--name-only', BASE], text=True).splitlines()
text = {}
for p in paths:
    b = Path(p).read_bytes()
    if b'\0' not in b:
        try: text[p] = b.decode('utf-8')
        except UnicodeDecodeError: pass

def move(p):
    return 'hardware/work/' + p[9:] if p.startswith('hardware/') else p
old, new = set(paths), set(map(move, paths))
def exists(p, tree):
    return p in tree or any(q.startswith(p.rstrip('/') + '/') for q in tree)
def count(rows):
    return len(rows), len(set(rows))  # 出現数、参照元ファイル数
rows = collections.defaultdict(list)
for p, s in text.items():
    if not p.endswith('.md'): continue
    for m in re.finditer(r'\]\(([^)\s]+)(?:\s+[^)]*)?\)', s):
        t = m[1].split('#')[0]
        if not t or re.match(r'(?:[a-zA-Z][\w+.-]*:|/)', t): continue
        a = posixpath.normpath(posixpath.join(posixpath.dirname(p), t))
        b = posixpath.normpath(posixpath.join(posixpath.dirname(move(p)), t))
        if p.startswith('hardware/'):
            group = 'internal' if a.startswith('hardware/') else 'outbound'
        else:
            group = 'inbound' if a.startswith('hardware/') else 'unaffected'
        rows[group, 'total'].append(p)
        if exists(a, old):
            rows[group, 'valid'].append(p)
            if not exists(b, new): rows[group, 'broken'].append(p)
        else: rows[group, 'already_missing'].append(p)
print('tracked, hardware, text:', len(paths),
      sum(p.startswith('hardware/') for p in paths), len(text))
for k, v in sorted(rows.items()): print(k, count(v))

scripts = {'.py', '.js', '.ts', '.tsx', '.sh'}
patterns = [
    ('external', lambda p: not p.startswith('hardware/'), r'\bhardware/'),
    ('scripts', lambda p: p.startswith('hardware/') and
     Path(p).suffix in scripts, r'\bhardware/'),
    ('parents', lambda p: p.startswith('hardware/') and p.endswith('.py'),
     r'\.parents\s*\[\s*\d+\s*\]'),
    ('absolute', lambda p: p.startswith('hardware/') and
     Path(p).suffix in scripts, r'/home/hatch/workspace/projects/he-piantor-42'),
    ('ci', lambda p: p.startswith('.github/workflows/'), r'\bhardware/'),
    ('ignore', lambda p: p == '.gitignore', r'\bhardware/'),
]
for name, pred, pattern in patterns:
    hits = [p for p, s in text.items() if pred(p)
            for _ in re.finditer(pattern, s)]
    print(name, count(hits))
hashes = collections.defaultdict(list)
existing = 0

def walk(obj, p):
    global existing
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and re.fullmatch('[0-9a-fA-F]{64}', v) and '/' in k:
                group = 'root_hardware' if k.startswith('hardware/') else 'other'
                hashes[group].append(p)
                if group == 'root_hardware' and k in old: existing += 1
            walk(v, p)
    elif isinstance(obj, list):
        for v in obj: walk(v, p)
for p, s in text.items():
    if p.endswith('.json'):
        try: obj = json.loads(s)
        except ValueError: continue
        walk(obj, p)
for group, hits in hashes.items(): print('hash', group, count(hits))
print('root_hardware hash keys existing:', existing)
```

実測したのは参照の静的抽出と移動後の存在照合であり、CAD再生成や移行後CIの実行ではない。今回の成果はこの議論文書のみ。コミット前の検証で、基準commitの全追跡14,922ファイルのSHA-256が開始時から不変、新規文書のローカルMarkdownリンク4件の参照先が存在することを確認した。付録コードを実行し、上表の計数も一致した。差分対象は本書だけとし、移動・削除・既存文書の改変・pushは行わない。
