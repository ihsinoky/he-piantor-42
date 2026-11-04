# Issue #129 修正ラウンド（PMO 指示）

受領時ホスト時刻 2026-11-04 20:08 UTC。期限は従来の 2026-11-04 23:56 UTC。

- 同一ブランチ issue-129-wing-2layer-routing、Draft PR #130 を継続。merge 禁止。
- 既存実装の修正は build-inputs.py のみ。FootprintLoad 直後、配置・保存前に各 LIB_ID nickname を Wing129 に設定。3基板を再生成し hash を固定する。
- check-equivalence.py のコード、識別子を含む検査項目・基準は一切変更しない。
- 修正ゲートは新たな単一 run。全項目まで完走させる。再不通過なら配線せず記録して停止、3回目は実施しない。
- 通過時は pitch9-16mm の両ツールのスモーク、その後 Stage 1 の KRT escalation off × representative21 両ピッチ、fab_router API defaults × 両ピッチを各単一 run。独立4指標で判定。
- 当初の失敗履歴を保持し、報告書と証跡に修正ラウンドを追記。同一ブランチへ push。
- 一時ランタイムは .issue129-runtime/ を継続使用。

当初証跡は initial-run/ に byte を保持したまま複製。旧報告書は initial-run/report.md にも保存。
