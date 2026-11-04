# Issue #109 — AutoRoute 限定反証テスト

判定と測定方法は [分析文書](../../../../docs/issue-109-autoroute-falsification.md) を参照。

`evidence/instructions.md` は受領した指示書全文。`source-provenance.json` と `official/` は公式固定ソース、`build.log` は指定ビルドの全出力。`run-router.py` は固定コマンド・一回限りの stage 実行と Main ゲートを実装する。ルーター実行結果は `processes/<stage>/record.json` と stdout/stderr、SES に保存する。

`inspect-ses.py` は保存 SES の幅を静的測定する。`run-checks.py` は KiCad import・snapshot・DRC と既存の無改変独立 oracle を順に実行する。`measure-result.py` は保存結果から KiCad `unconnected_items` 件数と銅箔接触などの診断を計測する。診断と合否用4指標を混同しない。`verify.py` は既存ファイル・入力・証跡 hash、実行回数とゲート、追加のみ、バイナリ不在を検証する。

ビルド済みバイナリ、依存キャッシュ、開発用 runtime はこの成果物に含めない。検査 runtime は先行 #105/#107 の KiCad 9.0.9・Shapely 環境を参照する。再現時は `installation.json`、`inspection-versions.json`、`kicad-env.json` の環境を用意する。絶対パスは実行時点の記録である。
