# Issue #158 evidence — ver.A Wing Stage 1

設計計画の証跡。製造リリース、PCBデータ、配線証明ではない。

- `issue.json`, `issue-comments.json`, `instructions.md`: 指定Issueと手順書の入力固定。
- `start.json`: 最新mainのSHA、作業ブランチ、隔離git管理領域。
- `inputs.json`, `inputs/`: 入力のhashと、未マージ#150/#157の原文スナップショット。`.txt`内の旧Markdownリンクは入力原文のままである。
- `sources/`: メーカー図の既存読取画像、URL・確認方法・日時。Gateron PDFは再取得し#150のhashと一致、PDF本体はランタイムだけに保持。
- `analyze.py`, `analysis.json`: 標準ライブラリのみの既存PCB読取り。21中心・4取付穴・外形・上面Hall・GH pinを照合し、仮の位置決め穴追加による幾何余裕とsegment/via干渉を算出。新基板を生成しない。
- `protected-start.json.gz`, `verify.py`, `verification.json`: 開始時の既存10708ファイルのhash保全、入力照合、再現、追加限定・リンク検査。
- `draft-pr-body.md`, `publication.json`: Draft PRの本文と公開操作結果。実行ログの一時出力は `.issue158-runtime/` に保存。

リポジトリrootで再現する。ランタイム・Git管理領域は作業先に応じて明示する。

```bash
mkdir -p .issue158-runtime
python3 hardware/kicad/qualification/issue-158-vera-wing-stage1/analyze.py > .issue158-runtime/reproduced.json
cmp .issue158-runtime/reproduced.json hardware/kicad/qualification/issue-158-vera-wing-stage1/analysis.json
GIT_DIR="$PWD/.issue158-runtime/git" GIT_WORK_TREE="$PWD" python3 hardware/kicad/qualification/issue-158-vera-wing-stage1/verify.py
GIT_DIR="$PWD/.issue158-runtime/git" GIT_WORK_TREE="$PWD" git log -2 --oneline
```

保全検査はこの共有作業環境の開始時スナップショットを対象とする。別のclean cloneには他Issueの未追跡成果物がなく、`verify.py`の保全・原入力検査は失敗し得る。解析自体はmain既存の#141とWing定義のみを入力とし、未マージの#150/#157スクリプトへ依存しない。再現用解析結果は製造座標・drill入力として使用しない。

解析ではφ1.75最大穴、穴縁から銅へ仮0.25、中心±5.08仮説を使う。穴位置／加工公差、pads、zones、3D、courtyardsは未検査で、DRC合格・磁気成立・配線完了を示さない。試験・実装・切断・発注は今回行っていない。
