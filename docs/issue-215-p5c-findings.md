# Issue #215 — 整理計画 P5c：Finding 遡及登録・履歴／見積群

2026-11-08、`.p5c-runtime/instructions.md` を全文読み、
[整理計画5.2・5.4節](repo-cleanup-plan.md)とP5a／P5bの登録形式を確認した。
基準はP5b取り込み済みmain／origin/mainの
`da78ee18b90753a30945249bfd712aa5eea50688`。
[Finding台帳](findings.md)へ次の4件を追記した。

| 候補 → Finding | 原証跡との照合 | 結論の境界 |
| --- | --- | --- |
| K01 → F-010 | importer両版のmaterial records・geometry・warnings、version-matrix、入力asset hash | 0.0.117／0.0.142の固定footprintに限りkeepout欠落・半径差。将来版の能力や電気parityを断定しない |
| K02 → F-011 | C4B5のsurface・pipeline・2候補のDRC/captureと電気reconciliation | 電気PASSと物理40／39未接続を分離。NO-GO判断はD-016、完全配線の不可能性は主張しない |
| K04 → F-012 | #103 assessment、#117修正01 assessment、#121 verificationと各報告の入力等価性・条件 | 固定Mainのツール／層／ルール別に表記。自己接続数と独立数を区別し、未実行セルを失敗にしない |
| K10 → F-013 | #133 geometry・price・6取得記録と圧縮元応答、#147発注条件、#194 panel/CAM照合 | 当時の旧裸基板各5枚の費目に限定。両面Standard PCBAパネルや現行Rev.3価格へ転用しない |

CAD・配線・製造データや過去実験は再生成せず、保存証跡を読み取り照合した。
新規FindingのEvidenceから原報告と個別証跡へ辿れる。
F-002はKRTのexit／project差分を扱うため、K04は層・幅／間隔と到達条件の比較に限定した。
F-006／F-009の電圧モデル、F-004のvia監査とは別の観測を登録し、既存9件は変更していない。

## 未確認事項と登録判断

登録保留の候補はない。指示書要件4に従い、未確認事項は推測で補わず、
確認できた保存結果・試行単位に結論を限定した。次の未確認部分の一般化は保留する。

- K01：Node実行版、upstream再生成を含む全変換起動総数、過去#13の試行総数は未確認。
  両版各1件の固定asset保存結果とproject経路1回を区別し、clean installと合成対照を加算しない。
- K02：C0〜C4Bの全配線起動総数は未確認。C4B5のfresh異候補各1回と先行探索を分け、
  同一sourceの再現性を認定しない。Python／package／runtime／独立KiCad版は保存記録で特定した。
- K04：KRT／検査Pythonの正確な実行版は本照合資料では未確認。
  Main対象・入力hash・ツールcommit・セル条件・実行日・回数と独立結果は特定できる。
  幅とclearance等の同時変更から幅単独の因果や混雑だけが原因との断定はしない。
  #117 Wingの寸法／escapeは仮定モデルであり、Wing実配線の成否に転用しない。
- K10：#133実行Python／curl・サーバ計算機版、#194の発注ロット数量・見積額、
  全CAM検査起動総数は未確認。保存6応答は16mm 4件／17mm 2件で、
  同ピッチの0.10／0.20mm request hashは同一。差$0を線幅変更の価格応答実験とは扱わない。
  #147の新規価格取得は0、#194は個別4＋パネル2の保存検査で価格試行ではない。
  #133送料税とKeyboard Design追加費は未確定。現在の料金を調査・更新する作業も行っていない。

全4件のPromoted toは未昇格。計画5.4節に本群の具体的昇格候補はないため、
P6の判断対象と記載した。プロセス・テンプレート・skillへの昇格実装は行っていない。

## 検証と提出

作業用 `.p5c-runtime/verify-registration.py` と結果 `verification.json` で確認する。

- F-001〜F-013は各1件・番号競合なし。旧台帳全体がbyte一致のprefixとして残る。
  新規4件は必須6欄、確信度・試行単位・条件・未確認事項・根拠・未昇格を持つ。
- 新規台帳と本報告のローカルリンク31件が実在し、D-016アンカーも解決する。
- 両importerのkeepout 0・半径0.075・警告空、固定asset SHA256を照合。
- JITX両候補の未接続数・requests・via・DRC種別と電気PASSを照合。
- #103の1回・自己未接続16・独立null、#117のMain各1回・独立26／28・null、
  #121の実行セル1のみ・独立4指標0・他セル未実行を照合。
- #133の6圧縮応答を展開して記録SHA256と照合し、同一request・当時金額を確認。
  Rev.2両パネルの面別実装84＋14とpanel転写検査合格を確認。
- 基準commitの追跡14,965ファイル全件をGit blob hashで照合し、既存変更は台帳だけ。
  追加成果物は本報告だけ。報告・ADR・証跡・CADなど他14,964ファイルは不変。
- ローカルクローン側の `git diff --check` を通過し、コミット対象は2文書に限定する。

このチェックアウトのローカルクローンを `.p5c-runtime/git` に作成し、
その `.git` と現在のチェックアウトをwork-treeとして `issue-215-p5c` にコミットする。
スクラッチ・検証スクリプト・結果JSONは `.p5c-runtime/` 内に置き、コミットしない。
通常チェックアウトのgit状態へはコミットせず、pushせず停止する。
