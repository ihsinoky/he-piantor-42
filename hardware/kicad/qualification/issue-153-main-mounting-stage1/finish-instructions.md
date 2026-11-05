# Issue #153 仕上げ指示

GitHub Issue #153「Main 機構改版 Stage 1」を完遂してください。先の実行は Codex クレジット枯渇で停止し、報告書ドラフトと証跡が作業ツリーに未コミットで残っています（docs/issue-153-main-mounting-stage1.md と hardware/kicad/qualification/issue-153-main-mounting-stage1/）。

## 作業
1. ドラフト報告書と証跡を全文精査し、内容の完成度を確認する。数値・寸法・図（retained-outline.svg / extended-outline.svg）と報告書本文の整合性を照合し、不整合があれば修正する。未完の箇所があれば補完する
2. 報告書の結論（第一案A：48×44mm 維持・φ2.2mm NPTH×4 の非矩形配置、干渉は既存配線3セグメントのみ。案B：60×44mm 拡張で四隅配置・干渉ゼロ。拡張は必須ではない）が本文と証跡から裏付けられていることを確認する
3. ブランチ issue-153-main-mounting-stage1 に、今回の成果物（報告書＋証跡）のみをコミットする。既存ファイルの変更はしない。未コミットの他 Issue 成果物（#147/#149/#150）は含めないこと
4. Draft PR を作成する。merge はしない

## 制約
- 案A／案B の採用判断は PO ゲートであり、本作業には含まない
- 基板データの変更・再配線・発注・課金は行わない
- 一時ランタイムは .issue153-runtime/ に置く（/tmp は 512MB）
