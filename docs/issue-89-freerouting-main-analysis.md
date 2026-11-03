# Issue #89 — Freerouting Main 未完了の保存証拠分析

2026-11-03。PMO向け技術推奨は **B：現行の headless Freerouting 2.1.0 方式への追加投資を停止**。形状管理の破綻を防ぐ公開設定上の小対策を特定できず、最良35未配線からの完成見通しも弱い。配置や方式一般の不可能性の証明ではない。別方式の採用・製品要求変更・merge はPO判断。本報告は新規試行を許可しない。

## 開始条件と根拠

開始時、ローカル main と `git ls-remote origin refs/heads/main` はともに `e01750722da8fe0d5ec0303463dc1e1fb78a65f0`。`gh issue view 89 --repo ihsinoky/he-piantor-42 --json title,body,comments` で全文確認。[PR #88](https://github.com/ihsinoky/he-piantor-42/pull/88) は2026-10-15 13:24:55 UTCに同SHAでmerged、Issue #87の停止結果は保持。

既存証拠の基点は [resume-01 evidence](../hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/)。以下の短縮表記 `E/` はこのディレクトリを指す。

- [raw stdout](../hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/main-initial-route/stdout)、同ディレクトリの [record.json](../hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/main-initial-route/record.json) と [保存設定](../hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/main-initial-route/effective-start-settings.json)。stdout/stderrのSHA256はrecord記載値と今回も一致。
- [Main入力照合](../hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/main-dsn-parity.json)、[実効ルール](../hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/effective-rule-acceptance.json)、[前報](issue-87-native-main-routing.md#resume-01)。入力の0.05→0.20 mm補正、小規模の限定合格は既存結果を再利用。
- 公開 v2.1.0 tag は調査時 commit `89512b982cbe8d00cccc1837823d9cdcd7c24c8a`。以下はすべてこのcommit固定ソース。公開ソースと旧実行JARのビルド同一性を再認証したものではないが、保存ログのクラス・行番号と直接経路が一致する。

## A. 配線内部例外（最優先）

**確認済みの直接原因：** stdout L7–18、2026-10-14 21:22:01.930、pass 1完了（21:22:00.388、88未配線）の後、pass 2完了より前に最初の範囲外警告とNPE。呼出順は `RoutingJobSchedulerActionThread.thread_action:131 → BatchAutorouter.runBatchLoop:447 → autoroute_pass:332 → autoroute_item:610 → AutorouteEngine.autoroute_connection:155 → MazeSearchAlgo.find_connection:206 → occupy_next_element:286 → expand_to_room_doors:398 → expand_to_target_doors:534`。

[PolylineTrace.java L137–139, L944–954](https://github.com/freerouting/freerouting/blob/89512b982cbe8d00cccc1837823d9cdcd7c24c8a/src/main/java/app/freerouting/board/PolylineTrace.java#L944) は `p_index < 0 || p_index >= max(lines.arr.length - 2, 0)` なら警告しnullを返す。[MazeSearchAlgo.java L527–534](https://github.com/freerouting/freerouting/blob/89512b982cbe8d00cccc1837823d9cdcd7c24c8a/src/main/java/app/freerouting/autoroute/MazeSearchAlgo.java#L527) は `to_door.tree_entry_no` を渡し、null確認なしで `nearest_point_approx` を呼ぶ。これが最初のNPEの直接経路。値そのもの、対象net・item ID・実際の配列長は記録されていない。

[TargetItemExpansionDoor L24–38](https://github.com/freerouting/freerouting/blob/89512b982cbe8d00cccc1837823d9cdcd7c24c8a/src/main/java/app/freerouting/autoroute/TargetItemExpansionDoor.java#L24) はitem参照とindexを保持する。[CompleteFreeSpaceExpansionRoom L168–175](https://github.com/freerouting/freerouting/blob/89512b982cbe8d00cccc1837823d9cdcd7c24c8a/src/main/java/app/freerouting/autoroute/CompleteFreeSpaceExpansionRoom.java#L168) のdoor作成は同じindexの接続形状をnull確認してから行う。[ShapeSearchTree L1044–1057](https://github.com/freerouting/freerouting/blob/89512b982cbe8d00cccc1837823d9cdcd7c24c8a/src/main/java/app/freerouting/board/ShapeSearchTree.java#L1044) はtrace形状数と同数のtree形状を作る。一方、PolylineTrace.change L980–1027 とShapeSearchTree.change_entries/merge処理は形状・tree indexを変更する。

**仮説：** traceの短縮・結合等と、保持済みdoor/room/tree参照の更新不整合が有力な調査対象。ただし具体的な更新処理の欠陥は未特定。上記の作成時チェックは、作成後の変化を疑う根拠であり、その証明ではない。

**入力／既存配線／生成配線の区別：** 保存済み入力照合は3本の既存USB銅箔を含む。初回passで新規配線が作られた後の発生であり、旧配線だけ、または生成配線だけを原因とは認定できない。DSNの既知間隔欠陥は補正・実効読戻し済み。不正DSNが直接原因という証拠はないが、特定形状が内部欠陥を誘発する可能性は除外できない。元DSNのどのitemが例外対象だったかは不明。

**371件の内訳：** 同一catchのERROR行を数えたもの。詳細付きはtarget_shape NPE 9件、`ObstacleExpansionRoom.create_overlap_door:98` のp_other null 8件、`MazeShoveTraceAlgo.check_shove_trace_line:123` の配列境界例外2件（index 6/length 6、9/9）。残りはNPE null 350件、配列境界例外null 2件でスタックなし。全371件を最初の原因に帰属させない。範囲外警告は382件でERROR件数とは一致しない。スタック省略の理由も未確定。

[AutorouteEngine L151–165](https://github.com/freerouting/freerouting/blob/89512b982cbe8d00cccc1837823d9cdcd7c24c8a/src/main/java/app/freerouting/autoroute/AutorouteEngine.java#L151) は例外をcatchしFAILEDにするため、プロセスexit 0と配線失敗は両立する。単なるnullスキップは探索の完全性・形状管理を修復した証拠にならない。公開設定で不整合を防止する手段は特定できず、内部修正の規模も断定不能。内部修正・再現実験への深追いは行わない。

## B. passes制御

**ソースで確認した経路：** [Freerouting L134,188,344–346](https://github.com/freerouting/freerouting/blob/89512b982cbe8d00cccc1837823d9cdcd7c24c8a/src/main/java/app/freerouting/Freerouting.java#L344) は設定読込→CLI適用→routerSettings.clone()をCLI jobへ設定する。[GlobalSettings L272–285](https://github.com/freerouting/freerouting/blob/89512b982cbe8d00cccc1837823d9cdcd7c24c8a/src/main/java/app/freerouting/settings/GlobalSettings.java#L272) の `-mp` はmaxPassesのみ変更。[RouterSettings L20,48–50,141–174](https://github.com/freerouting/freerouting/blob/89512b982cbe8d00cccc1837823d9cdcd7c24c8a/src/main/java/app/freerouting/settings/RouterSettings.java#L141) はmaxPassesとprivate transient stop_pass_no（既定999）を独立に保持し、cloneもそれぞれ別々にコピーする。保存JSONはmax_passes=100だがtransient停止値は保存されず、runtime状態の証明にはならない。

RoutingJobSchedulerはDSNをboardへロードするがjob設定をDSN設定に置換せず、ActionThreadはそのjobからBatchAutorouterを作る。[BatchAutorouter L54,434–447](https://github.com/freerouting/freerouting/blob/89512b982cbe8d00cccc1837823d9cdcd7c24c8a/src/main/java/app/freerouting/autoroute/BatchAutorouter.java#L434) は `curr_pass_no > get_stop_pass_no()` で停止し、maxPassesを参照しない。固定ソース全src/main/javaの参照検索では、両値を橋渡しする `set_stop_pass_no(start + maxPasses - 1)` はGUIのWindowWelcomeにあるがCLI job経路にはない。DSN AutorouteSettingsはstart値を読むがstop値を設定しない。

**結論：** headless CLI経路の設定接続欠落が100を超過できる根拠ある説明。100が読み取れなかった／512という上限に変換された、とは解釈しない。既定999まで許す経路で、別の停止条件が512付近で働いたと考える。

**未確定：** runtime stop値の直接captureはない。ActionThread L42–95の1200秒監視と、21:21:52.694開始→21:41:52.778最終passは整合するためjob timeoutが有力。ただし最終job stateや明示timeoutログがなく、512で止まった正確なトリガーは認定しない。履歴復元／改善停止も別に存在する。外側1260秒timeoutは発火していない。

公開 `set_stop_pass_no(100)` を適切なjobに適用するAPI呼出は回数制御だけの候補で、CLI設定だけの解決は確認できない。今後もし別途承認するなら、parser値でなく実行ログで100終了・101非実行を検証する必要がある。これはAの内部例外への対策ではない。

## C. 改善傾向

raw stdoutの `Auto-router pass #N ... completed ... (U unrouted)` 512行を集計。現在盤面の値であり、履歴最良や独立物理検査値ではない。

| pass | 未配線 | UTC (2026-10-14) |
| --- | ---: | --- |
| 1 | 88 | 21:22:00.388 |
| 25 | 60 | 21:23:15.049 |
| 50 | 60 | 21:24:32.752 |
| 100 | 53 | 21:26:39.837 |
| 200 | 41 | 21:30:25.367 |
| 201 | 35 | 21:30:27.169 |
| 300 | 38 | 21:34:12.628 |
| 400 | 42 | 21:37:56.617 |
| 500 | 40 | 21:41:29.957 |
| 512 | 36 | 21:41:52.778 |

pass完了値の最小35は201で初到達。残る311passes、約11分26秒で最小値更新なし。終了時は履歴盤面へ戻り35を保存。100→512の追加で最良は改善したが0への外挿根拠はない。例外は21:22:01.930から21:41:45.764まで継続。pass区間1–100 / 101–200 / 201–300 / 301–400 / 401–512のERRORは72 / 110 / 78 / 68 / 43件（直前pass完了後から当該最終pass完了までを区間とする）。早期から起き、後半にも残る。

限定継続には、内部例外を防ぐ具体的な公開対策と、実効pass制御、固定入力・材料条件でMain完了後の独立4指標および受渡し照合を合格させる検証計画が必要。今回は第一条件を満たす最小変更を特定できない。時間追加やpass増加だけの再試行を推奨しない。Main物理4指標は引き続きnull。ERC0・既知印刷61警告・USB NPTH製造リスクは保持。

## D. 次の1件のIssueへの提案（未承認）

[EDA経緯](eda-path-history.md) に基づき、JITX、stock tscircuit、Circuit JSON変換器や古いKiCad直書き経路は再開しない。最も有望な次の一手として、**既存のnative KiCad入力と独立検査を再利用し、担当技術者が公式PCB Editorの対話型配線で固定Mainを完成できるか評価する限定Issue**を提案する。[公式KiCad 9.0マニュアル](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html#routing-tracks) はpush-and-shove等を記載するが、このMainが完成するという証拠ではない。今回GUIも手配線も一切実施していない。

これは旧ファイル直書きやDSN変換・自動routerを再開する案ではなく、公式editor上で既存native boardの銅箔のみを編集する機構への変更。全自動・headlessという作業条件が必須なら、この案は採れずPO判断待ちとなる。製品要求や材料条件の変更は提案しない。

次Issueに記す具体的条件案：

1. POが対話操作、担当者（未定）、新しい上限（提案：技術者4時間、最後30分は報告）、使用入力と保存・独立検査範囲を明示承認してから開始する。新たな配置・材料条件の探索を含めない。
2. 保存済み未配線native Mainをhashで固定しコピーを作業対象にする。部分SESは未検証なので起点にせず、既存USB銅箔を保持する。形状・net・NC・穴・49部品の位置を編集前後で照合する。
3. 最初の反証可能な問いは「公式対話配線で、固定配置・0.20 mm条件のまま、DSN/maze例外経路を使わず接続を進められるか」。最初の60分で進捗と残作業見積を記録し、配置／間隔緩和を要する、又は枠内完成見通しが立たなければ停止して未完了報告。
4. 合格は全required接続0未接続、wrong-net接触0、対象材料違反0、説明不能な受渡し変化0を独立検査で示すこと。既知印刷61件は別記し、新規違反は隠さない。全配線のnative保存・再読込とレビュー可能な差分を残す。製造出力・発注・backend採用は含めない。

作業は人手技能・GUI環境と独立検査の準備を要する。リスクは固定配置の難易度と担当者依存、維持費は部品／回路変更時の再配線と再検査。利点は現在成立したnative入力を残し、router forkや変換器保守を避けられる点。4時間での完成保証ではなく、投資上限付きの実現性評価案。PMOが方法・担当・予算を具体化しPOが採否を決める。

## 作業記録と提出検証

開始2026-11-03 06:08 UTC（最初の時刻観測06:08:24、直前のIssue取得から保守的に分単位切下げ）。60分上限、調査打切り06:53、最終期限07:08 UTC。45分を待たず根拠の限界を確定し報告へ移った。PO回答待ち・除外時間なし。ソース取得やCI待ちも重複加算せず連続経過に含める。提出終了観測と合計はPRに記録する。

実施：全文／開始SHA確認、保存ログの小集計・hash照合、公開固定ソース読取、既存EDA経緯照合、本文・リンク・差分の静的検査、commit/push/Draft PRとCI観測。元workspaceの.gitはread-onlyのため `/tmp/issue89-submit` のローカルcloneで専用ブランチを作成。公開ソースarchiveの全展開が一時領域不足になったため、今回作った展開物だけを除去しJavaソースのみを展開。旧証拠・hashは無変更。

未実施：router起動、新規設定実験、KiCad再生成／import／DRC、既存SES検証、router修正／fork／版変更、配置変更、手配線、材料緩和、製品設計、製造出力、別backend実験。提出は分析文書1件のみ。任意のstatus/Dashboardは更新せず、過去記録を保持した。調査報告の完了はMain技術合格、採用、製造可能、Human Gate通過を意味しない。
