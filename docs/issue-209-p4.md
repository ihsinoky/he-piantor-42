# Issue #209 — 整理計画 P4：履歴索引

## 変更と根拠

[履歴索引](history-index.md)を新設した。対象別の世代系列と、整理計画付録Aの全配置単位への入口、付録Bの全報告・補助文書への入口を併用する。系列を読む入口と、実パスで探す入口の両方を用意することで、配置を変更せずに版・Issue・PR・入力／最終／失敗を辿れるようにした。

Main単Wing→2Wing→Rev.3→Rev.4、Matrix Rev.1→Rev.2→Rev.3、Wing Rev.1→Rev.2→Rev.3、ケースStage 1→Stage 2→最終を接続した。#87〜#121は手法履歴に集め、#124以降は対象別に案内し、MatrixとWingの共有入力・via監査・ケースへの入力供給を横断参照する。計画棚卸し後に追加された#190の報告・形状資産、ADR監査・P3報告・Finding等にも入口を追加した。

現行のMatrix／Main／Wingパッケージは、各READMEと成果物索引に照合して、最終CAD・製造データと候補・工程検査・凍結入力を区別した。Mainのinspection/finalは最終CAD、Matrixのinspection/finalは最終検査でCADはboard、Wingは各単板内のmainが最終でinput／routedが入力／途中となる。Wing Rev.3にはprocessesディレクトリはない。現行4単板・2パネルへの直接リンクは成果物索引を再利用する。

D-030は提案・実装当時には採択根拠が未確認で、Issue #205の監査でも「未確認」に分離されたが、2026-11-08にPOが採択を明示確認し、PR #206で「採択済み（PO確認済み）」として確定した。D-004／D-005／D-006／D-011もPO確認により全件解消済み。D-033は別版の判断であり、D-030の遡及採択ではない。この経緯とD-032／D-033／D-034の後続採択、南辺フラッシュのP3時点の了解は索引側で根拠を併記し、元報告の結論を書き換えない。#198 Stage 1はローカルmainのfirst-parent履歴でPR #202への取り込みを確認した（元commit 6a596e23）。PR番号はこのチェックアウトのマージ履歴・報告・ADR監査による履歴参照で、GitHubの現在の状態を再認定するものではない。

root README、hardware（main案内も含む）、manufacturing、mechanical、project-status、artifacts-indexから履歴索引へリンクを追記した。履歴索引から現行成果物索引へ戻れる。

## task資産の分類根拠

`task/index.html`のscript/linkと、その先の`dashboard.js`・`style.css`・`data/project-status.js`を全文確認した。読み込むJSはproject-status.jsとdashboard.jsのみで、dashboard.jsがwindow.PROJECT_STATUSを描画する。fetch/import等の追加読込やruntime／画像参照はない。

`task/data/runtime-status.js`はwindow.RUNTIME_STATUSを定義するが現行画面では未参照、`task/screenshots/`の6枚も現行HTML・JS・CSS・データから未参照である。したがって両者は旧画面の履歴資産とし、現行表示の証跡や状態入力に使わない。現行表示4ファイルと区別して索引に全構成要素を列挙した。taskファイルは変更していない。

## 検証方法と結果

起点は `2d76a1bb723def260ce783290aa3f394b2e7bb5c`（P3／PR #208）。開始時に`git ls-files -z`で得た追跡14,961ファイルをSHA-256で記録し、終了時に全件照合した。作業用スクリプトと開始時hash・結果JSONは`.p4-runtime/`に保存し、コミット対象に含めない。

付録被覆は、`docs/repo-cleanup-plan.md`の付録A／Bを見出しで分割し、各表の第1列を正規表現 `^\| ` + バッククォート内のパス + ` \|` で抽出する。索引のMarkdownリンクを解析し、索引のあるdocsからroot相対に正規化して、抽出した各パスが実際のリンク先に存在することを検査する。単なる文字列掲載だけで合格にしない。以下の短い検査でも被覆を再確認できる（リポジトリrootで実行）。

```python
from pathlib import Path
import re
from urllib.parse import unquote
plan = Path('docs/repo-cleanup-plan.md').read_text()
a, b = plan.split('## 付録A.', 1)[1].split('## 付録B.', 1)
b = b.split('## 今回の提出', 1)[0]
index = Path('docs/history-index.md').read_text()
targets = set()
for href in re.findall(r'\]\(([^)]+)\)', index):
    if href.startswith(('https:', '#')):
        continue
    targets.add((Path('docs') / unquote(href.split('#')[0])).resolve())
for name, section in [('A', a), ('B', b)]:
    paths = re.findall(r'^\| `([^`]+)` \|', section, re.M)
    missing = [p for p in paths if Path(p).resolve() not in targets]
    assert not missing, (name, missing)
    assert all(Path(p).exists() for p in paths)
    print(name, len(paths), 'covered', 'missing', len(missing))
```

- 付録A **75/75単位**、付録B **82/82ファイル**に実リンクあり、被覆漏れ0。各リンク先の実在も確認。
- 新規索引・本報告の全ローカルリンクと指定アンカー、および既存7案内ファイルへの追加リンクの計309件を検査：欠損0。
- 既存追跡14,961ファイルのうち、案内追記7ファイル以外の**14,954ファイルが開始時SHA-256と一致**。7ファイルも元の全文をprefixとして保持し、履歴索引への案内だけを末尾追記した。元報告・証跡・CAD／CAM・taskは不変。
- `git diff --check`：合格。追加は索引と本報告、既存変更は案内7ファイルのみ。移動・削除・CAD再生成なし。

差し戻し修正（2026-11-08）では、`69f3e266`から履歴索引のD-030記述3箇所と本報告の要約・検証記録だけを更新した。修正後に付録A 75/75・付録B 82/82の被覆、計309件のローカルリンク・アンカーを再確認し、欠損は0。開始時SHA-256との照合も再実行し、既存14,954ファイルの一致と案内7ファイルの末尾追記のみを確認した。`69f3e266`との比較でも変更対象は本索引と本報告の2ファイルのみで、両文書のリンク先一覧に変更はない。`git diff --check`も合格。再検証スクリプトと結果は`.p4-runtime/verify-fix1.py`・`.p4-runtime/verification-fix1.json`に保存した。

ローカルクローンは`.p4-runtime/git`、work-treeはこのチェックアウト。ブランチ`issue-209-p4`へコミットして停止する。pushは行わない。
