# Issue #182 — マトリクス基板 Rev.3：via とパッドの重なり排除

Rev.3 は **独立4指標すべて0、全158 via のパッド重なり0、最小銅間隔
0.10746250134368196 mm** で合格した。製造データを再生成し、この Rev.3
パッケージについて POFV（樹脂充填＋銅キャップ）要求を取り下げた。
発注・課金・merge は行っていない。

## 起点と引き継ぎ

- [Issue #182](https://github.com/ihsinoky/he-piantor-42/issues/182) の指示書を全文確認。
  起点は [PR #181](https://github.com/ihsinoky/he-piantor-42/pull/181) の
  `issue-178-m1-matrix-board`、SHA `b23716a3d1e9bd1f4c1d06c62d93458797398461`。
  作業ブランチは `issue-182-matrix-rev3`。
- ランタイム再起動前の `GLOBAL-01`、`GLOBAL-02`、`LOCAL-01` は保存済み検査結果を再利用し、
  やり直していない。`GLOBAL-03` は PCB 保存・終了記録前に中断していたため、その配線段階だけ再実行した。
- 作業用 git コピー `.issue182-runtime/git` は起点 SHA のままで、Rev.3 の既存コミットはなかった。
  共有ワークツリーの main や既存の別 Issue 成果物を checkout/reset していない。
  一時処理・ツール・設定は `.issue182-runtime/` を使用。
- 証跡は [qualification ディレクトリ](../hardware/kicad/qualification/issue-182-matrix-rev3/)。
  [起点記録](../hardware/kicad/qualification/issue-182-matrix-rev3/git-base.json)、
  [再開記録](../hardware/kicad/qualification/issue-182-matrix-rev3/resume-state.json)、
  各 `processes/*/record.json` に入力、引数、終了コード、所要時間を保存した。

## 合格条件と結果

**D-021 は変更していない。** 2層／1.2 mm、信号 0.10 mm、HALL_5V・GND 0.30 mm、
間隙 0.10 mm、via 外径／drill 0.60／0.30 mm、KRT escalation off。
最終基板は信号483線分、電源703線分、全158 via。線幅不足・via 寸法違反は0。

| 独立指標（全27ネット） | 最終結果 |
| --- | ---: |
| 必須接続の未接続 | 0 |
| 異ネット銅接触 | 0 |
| 材料／配線 DRC 違反（dangling 警告も含む） | 0 |
| 説明不能な転写変更 | 0 |

[最終判定](../hardware/kicad/qualification/issue-182-matrix-rev3/inspection/final/assessment.json)、
[物理銅グラフ](../hardware/kicad/qualification/issue-182-matrix-rev3/inspection/final/copper-graph.json)、
[全ネット一覧](../hardware/kicad/qualification/issue-182-matrix-rev3/all-net-coverage.json)、
[線幅監査](../hardware/kicad/qualification/issue-182-matrix-rev3/inspection/final/width-audit.json)。

受入判定にルータの成功表示は使っていない。保存 PCB と凍結した元プロジェクトに対する
KiCad 9.0.9 DRC、別実装の銅接続グラフ、非配線 AST 比較、線幅・寸法監査で判定した。
グラフの参照実装・実行ソースは `inspection/final/graph-method.json` に記録している。

## 全 via と全パッドの独立監査

| 項目 | Rev.2 再監査 | Rev.3 |
| --- | ---: | ---: |
| via 数 | 146 | 158 |
| パッド重なりがある via | 31 | 0 |
| annulus 外周からパッド銅まで 0.10 mm 未満の via | 36 | 0 |
| 最小銅間隔 mm | −0.575 | 0.10746250134368196 |

全178銅パッド（うち裸テストパッド18、NC・補強ランドも含む）と全158 via の
**28,124組**をネットに関係なく検査した。円・矩形・カプセルの解析的距離から
via 外周半径を引き、さらに KiCad native effective shape と、via 銅円／半径を
正確に0.10 mm拡張した円との衝突を照合。両方式で重なり・間隔不足0。
NPTH 4穴は非銅パッドとして明示し、別途固定寸法・keepout・DRC で確認した。
判定にクリアランス緩和や許容誤差の引き下げは使っていない。

[全 via CSV](../hardware/kicad/qualification/issue-182-matrix-rev3/all-vias.csv) に
UUID・座標・ネット・外径・drill・最近接パッド・最小間隔・native 照合結果を掲載。
[詳細 JSON](../hardware/kicad/qualification/issue-182-matrix-rev3/inspection/final/via-pad-audit.json) と
[監査実装](../hardware/kicad/qualification/issue-182-matrix-rev3/audit-via-pads.py) を添付。

## 配線の到達経緯

| 候補 | 保存された結果 |
| --- | --- |
| GLOBAL-01（既存） | 未接続3、重なり2、電源線幅不足。未合格 |
| GLOBAL-02（既存） | 未接続3、重なり1、電源線幅不足1。局所修復の起点 |
| LOCAL-01（既存、Rev.2 からの移設） | 36対象のうち27移設、9対象を修復できず。未接続1。未合格 |
| GLOBAL-03（中断段階のみ再開） | 未接続2、重なり2、線幅不足。未合格 |
| LOCAL-02 | GLOBAL-02 の違反 via で直線 dogbone 移設200候補を試し、周囲銅との間隔を確保できず |
| LOCAL-03 | 違反 via を除去、電源1線分を0.30 mmへ修復。via 監査合格、未接続4 |
| LOCAL-04 | MUX付近の H_A0_RAW 1線分を引き直し、WING_EN 接続を回復。次候補への中間結果 |
| LOCAL-05 | GH14 の GND と MUX_A1 を修復。未接続1、不要枝1、via監査合格 |
| LOCAL-06 | MUX_A1 の引き出し位置を分け、MUX_A2 の経路を確保。未接続0、不要枝1 |
| final | 旧 in-pad via への不要な B.Cu 枝1本を除去し、4指標＋via監査すべて合格 |

局所探索は0.05 mmグリッド、有限の探索窓、1探索120万状態以下、各処理1800秒以内で上限付き。
信号・電源の線幅、via 寸法、銅間隙を固定し、受入判定は探索コードから独立させた。
試行ログと経路台帳を `processes/`、`runs/LOCAL-*/out.grid-repair.json` に保存。
初期の native 削除 API 呼び出しの異常終了記録も残し、後続は `RemoveNative` を使用した。

KiCad 保存時の図形座標 `42.0` → `42` 等の表記変化は、元の非配線 AST をそのまま
復元して解消した。例外扱いで判定を通していない。復元前後の銅 AST が同一であることを
`*.nonroute-preservation.json` で検証し、最終 PCB は Rev.2 と非配線 AST が完全一致。

## 不変条件

部品・全パッド・配置・回転・外形128×80 mm・4取付穴と銅禁止域・GH14・
ネットとNC意図・電気構成・アートワーク・ペースト設定は Rev.2 から不変。
16 mm／17 mm の各3×3配列、計18キー、最近接ブロック間キー中心35 mmも継承した。
変更は配線線分と via のみ。プロジェクトファイルは Rev.2 とバイト一致。

[不変性検証](../hardware/kicad/qualification/issue-182-matrix-rev3/design-preservation.json)、
[既存ファイル保全](../hardware/kicad/qualification/issue-182-matrix-rev3/preservation-audit.json)。
`docs/decisions.md` は D-029 追記のみを公開差分に含め、`project-status.md` は編集していない。
既存の基板シルク `M1 MATRIX18 / ISSUE178` も保持した。製造版はフォルダと SHA と製造注記で識別する。

## 製造データと POFV

[製造パッケージ](../hardware/kicad/qualification/issue-182-matrix-rev3/manufacturing/) の
[**FABRICATION.md**](../hardware/kicad/qualification/issue-182-matrix-rev3/manufacturing/FABRICATION.md)
に「パッドに重なる via がないため充填・キャップは不要」と明記し、Rev.3 の POFV 要求を取り下げた。
Rev.2 の履歴データや Main の D-022 は変更していない。

- Gerber 7層、PTH 158穴／NPTH 4穴、表裏ペーストを合格 PCB から再生成。
- Gerbonara 1.5.0 で読み戻し、銅線分の位置・線幅・層、via、パッド、外形、マスク、穴径と位置を照合。
  別途、製造用 PCB に対して DRC を再実行し違反・未接続とも0。
- Excellon の0.001 mm量子化による最大穴位置偏差は0.000001415 mm、残る最小環状銅幅は0.149998585 mm。
  G90ヘッダ位置についてのパーサ警告は記録し、絶対座標の全穴照合で影響なしと確認。
- 表マスク178開口、裏マスク0、全 via 両面 tenting。表ペースト160開口、裏0。
- BOM/CPL は再生成後、Rev.2 とバイト一致を検証したため再利用可能。
  実装43部品・4 MPN、裸テストパッド18とNPTH 4を除外。GH14 の実体重心・原点・回転も不変。
- 組立図SVG/PDF/PNG、全層プレビュー、表裏銅と穴の図を生成して目視確認した。
  製造 ZIP は artwork と drill の9ファイルのみ。PCBA レビューには注記・BOM/CPL・paste を併せて使う。

[製造検証](../hardware/kicad/qualification/issue-182-matrix-rev3/manufacturing-checks.json)、
[BOM/CPL同一性](../hardware/kicad/qualification/issue-182-matrix-rev3/assembly-identity.json)、
[組立図](../hardware/kicad/qualification/issue-182-matrix-rev3/manufacturing/assembly-top.pdf)、
[全層プレビュー](../hardware/kicad/qualification/issue-182-matrix-rev3/manufacturing/preview-review/all-layers.png)。

基板 SHA-256 は `7ad3c6e67aed41f882b87f38f7ea8f812805e56837bf15a1d21dc2479060b8db`。
[総合検証](../hardware/kicad/qualification/issue-182-matrix-rev3/verification.json) を参照。

POFV を要求しない設計成果であり、新たな見積・発注・課金は行っていない。
メーカーの最終DFM・実装方向照合、磁気／ADC／外部治具の実機評価は別のリリース工程に残る。
Draft PR の提出対象であり、merge は行わない。
