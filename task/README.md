# Project Dashboard

`index.html` は「マイルストーン計画と現在位置」の大局ビューです。
詳細ステータス・評価結果・タスク・ライブPR/CI情報は複写せず、docsへ案内します。

正本の優先順位は従来どおりです。

1. `docs/`
2. `main` にマージされた実装・設計成果物
3. GitHub Issues / PR
4. Dashboard

`data/project-status.js` は [docs/project-status.md](../docs/project-status.md) の
現行マイルストーン表と現在位置を手動同期した read model です。
相違時は docs が正。状態や計画の変更は同じレビュー対象PRで両方を更新します。
ジェネレータや自動同期はありません。MS1〜MS8 は PMO 案で、P3 の PO PR ゲートで確認します。
完了／進行中／未着手と根拠または次のゲートを記載し、次の工程の現在位置と着手済みを区別します。
従来のフェーズ M0／M1／M2 と MS1〜MS8 は別体系です。

ビルド不要の静的ページです。`index.html` をブラウザで開いて確認できます。
本番はマージされたmain、PR Previewは提案中の内容で承認ではありません。
確認日は資料の確認日であり、閲覧時刻に置き換えません。
heartbeatコミットやmainへ更新を書き戻すActionは作りません。

`data/runtime-status.js` と `screenshots/` の既存ファイルは今回のビューから参照しません。
現行・履歴の分類は整理計画P4で扱います。AIの稼働や過去画像から現行状態を推測しません。

今回の描画検証と同期・リンク検査は [P3報告](../docs/issue-207-p3.md) を参照してください。
