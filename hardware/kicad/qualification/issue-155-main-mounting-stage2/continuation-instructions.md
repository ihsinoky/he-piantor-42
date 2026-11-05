# Issue #155 継続指示

先の Codex 実行はランタイム再起動で約10分で強制終了した。作業ツリーには途中状態が残っている。最初からやり直さず、状態を確認して続きから完遂すること。

## 残っている途中状態（確認すること）
- ブランチ issue-155-main-mounting-stage2（.issue155-runtime/git）。コミットはまだない見込み
- docs/decisions.md が変更済み（D-023 追記の途中または完了）
- hardware/kicad/qualification/issue-155-main-mounting-stage2/ に inspect-board.py／refill.py 等のスクリプトと processes/ の実行出力が残っている
- .issue155-runtime/ に KRT ランタイムと protected-start.json が残っている

## 作業
1. 上記の途中状態と .issue155-runtime/instructions-155.md を確認し、済んでいる工程と未了の工程を切り分ける
2. instructions-155.md の作業（D-023 記録、改版入力構築、D-019 条件での再配線、独立資格確認、製造データ生成と POFV 再分類、報告書と証跡）を、済んだ分は再利用して完遂する
3. ブランチに成果物をコミットし、Draft PR を作成する。merge はしない

## 制約
- 条件緩和と無制限の再試行は禁止。時間枠内に再配線が成立しない場合は状態を報告して止める
- 発注・課金は行わない
- 一時ランタイムは .issue155-runtime/ に置く（/tmp は 512MB）
