# Issue #207 — 整理計画 P3

## 変更と根拠

[整理計画5.5／5.6節](repo-cleanup-plan.md)とP3作業要件に従い、
[成果物索引](artifacts-index.md)、[現行状態・残件・MS1〜MS8計画](project-status.md)、
[ダッシュボード](../task/index.html)を更新した。PMOのマイルストーン案はP3のPO PRゲートで確認する。

索引は既存の版別正本を直接指す。Main／Matrixの製造ZIP・BOM・CPL、Wingの
4単板と2製造パネル、12確定CSVとケース凍結入力、17mm正／16mm検証版の
組立STEPと印刷5ピースを区別した。元データの移動・複製・再生成はしていない。
実在確認で判明した Main の参照先は、ライブラリが証跡rootの `Rev4.pretty/`、
回路契約がrootの `logical-contract.json`（いずれもschematic／final直下ではない）だったため、索引は実配置へリンクした。

現行はD-033／D-034採択済み、ハーネス各200mm、別基板UDB C3、ケース固定15点。
採択は[ADR監査](issue-205-adr-audit.md)、ケース出力は[最終報告](issue-198-case-final.md)を根拠とする。
南辺フラッシュはP3作業要件の「PO了解済み」を現行状態として反映した。
過去報告の「持ち越し」はその当時の記録として保持した。
量産ピッチ、実機・物理検証、発注1のPO GO（CPL原点・UDB上流抵抗実測が前提）、
ケース印刷のPO判断を残件として明示した。

2026-10-14時点のCurrent situation／Roadmap／Human Gates／Workstreams等は
日付付き履歴として本文を保存し、旧見出しへの主要アンカーも維持した。
旧EDAのSTOPを取り消さず、版表の現行ラベルと採択状態を訂正した。
root／hardware／manufacturing／mechanicalの案内から索引へ進める。

Dashboardは詳細状態の複写をやめ、docs側のマイルストーン表と現在位置を同じ変更で手動同期する。
MS1完了、MS2〜MS8未着手と短い根拠／次ゲートを表示し、MS2の現在位置と着手済みを区別する。
正本の優先順位・同一PR更新・mainとPreviewの区別は [task規約](../task/README.md)に保持した。
未使用runtime-statusと既存screenshotsは変更せず、分類はP4へ残した。

## 検証

- `node --check task/dashboard.js` と `node --check task/data/project-status.js`：合格。
- Playwright＋Chromium 140.0.7339.186 headless shellによる実ブラウザ描画：1440×1000、390×844、320×900、320×900の文字200%で確認。
  データとスクリプトの読込、8マイルストーン、完了1／未着手7、MS2現在位置、次のゲート表示、横溢れなしを確認。
  全8行のID・名称・状態・根拠／ゲートがdocsの表と一致。ページ例外・読込失敗0。
  1440pxスクリーンショットを目視し、現在位置と全8カード・正本リンクの描画も確認。
- 索引と更新した案内の相対リンク、および新規project-statusリンク計190件の実在・指定アンカーを検査し、欠損0。
- `git diff --check`：合格。変更範囲は案内文書とtaskの表示・データのみ。CAD／CAM差分なし。
- ブラウザのスクリーンショット、DOM、検査スクリプト・結果はスクラッチ `.p3-runtime/` に保存し、コミット対象外。
  描画確認はUIの検証であり、設計の再認定・実機検証ではない。

ローカルクローンは `.p3-runtime/git`、作業ツリーはこのチェックアウト。
起点は `aa0b05d15e68e9c775cc27978a127a3258440abd`（開始時のHEADとorigin/mainが一致）。
成果物は `issue-207-p3` にコミットして停止し、push・発注・印刷・公開用リポジトリ作成は行わない。
