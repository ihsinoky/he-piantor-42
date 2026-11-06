# Issue #183 指示：Main Rev.2 と Wing Rev.1 の via-パッド重なり監査

GitHub Issue #183 を取得し、その内容を実行してください。設計変更は行わず、
監査と見通しの報告だけを行います。

## 対象データ（この worktree の main にはないため、ブランチから読み取る）
- Main Rev.2：ブランチ origin/issue-175-main-dual-wing-final2 の
  hardware/kicad/qualification/issue-175-main-dual-wing-final2/ 配下の最終基板
- Wing Rev.1：ブランチ origin/issue-149-wing-silkscreen の
  hardware/kicad/qualification/issue-149-wing-silkscreen/ 配下の 16mm／17mm 基板
- 監査の物差しは Issue #182（マトリクス基板 Rev.3）と同じ：via の annulus
  外周とパッド銅の間隔、分類は中心／drill 縁／annulus のみ／重なりなし。
  #175 の POFV 再分類の手法と結果も参照してよい

## 成果物
1. 基板ごと（Main Rev.2、Wing Rev.1 16mm、Wing Rev.1 17mm）の監査結果：
   全 via 数、分類別の個数、パッド銅との最小間隔、重なるパッドの内訳
   （実装部品／テストパッド）
2. 基板ごとの見通し：配置を変えず via 移設だけで排除できる範囲、配置変更や
   再配線が要る範囲とその根拠。結論（POFV 必要／不要化できる／要追加検討）
3. 報告書 docs/issue-183-via-pad-audit.md と証跡フォルダ。成果物は作業用
   ブランチ issue-183-via-pad-audit の Draft PR

## 制約
- 対象基板の設計データは変更しない（読み取りのみ）
- 発注・課金は行わない。merge はしない
- 一時ランタイムは .issue183-runtime/ に置く（/tmp は 512MB）
- KiCad が必要な場合は ~/workspace/projects/he-piantor-42/.issue129-runtime/
  のランタイムを読み取り専用で使ってよい
