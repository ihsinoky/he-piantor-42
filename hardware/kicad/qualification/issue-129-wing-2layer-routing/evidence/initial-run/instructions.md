# Issue #129 指示書：Wing 2層配線評価

- 発行：PMO（2026-11-05、サイドチャット）。PO の GO 済み（起草提示→「この内容で GO」）
- ワーカー：Codex
- タイムボックス：**全体で4時間**（入力構築・等価性ゲート・配線・独立検査・記録すべてを含む）

## 目的

Issue #127 で確定した Wing 設計定義を対象に、2層・0.20mm ルールで自動配線が完走するかを判定する。進め方は Main 評価の標準枠組み（入力の固定→等価性ゲート→単一 run→独立検査4指標）を Wing に適用する。Wing には .kicad_pcb がまだ存在しないため、入力構築が Stage 0 に含まれる。

## 入力（出典はこれだけ）

- `hardware/jitx/wing/generated/pitch9-16mm/`、`representative21-16mm/`、`representative21-17mm/` の `definition.json` / `nets.csv` / `placements.csv` / `bom.csv`
- 着手前に `hardware/jitx/wing/README.md` と `docs/issue-127-wing-design.md` を読むこと。README の消費者向け注意（NPTH・キープアウトの基板側実装、ピンマップの正確な保存、6本に分かれた GND 導体）が入力構築の要件である
- `hardware/jitx/wing/**` は読み取り専用として扱い、編集しない。`docs/decisions.md` は編集しない。`hardware/layout/**` は消費しない

## Stage 0：入力構築＋等価性ゲート＋スモーク

### 入力構築
- 3基板それぞれについて、definition.json から .kicad_pcb を構築する：
  - 配置（位置・回転）、物理ピンの接続関係、明示 NC を定義と一致させる
  - JSON に記録された取付 NPTH とキープアウトを基板に実装する
  - フットプリントのパッド形状は、プロジェクト既存のライブラリ／メーカー推奨形状から採り、使用した出所を記録する
  - 層構成は2層（F.Cu／B.Cu）。基板ルールはピン留め：配線幅・クリアランス 0.20mm、ビア 0.60／0.30mm
  - 外形寸法は生成定義どおり（representative21-16mm＝110×100mm、representative21-17mm＝116.5×104.75mm。pitch9 は定義の外形どおり）
- 構築した入力基板は証跡側に保存し、SHA256 で固定する。以後の全セルで同じ入力を使う

### 等価性ゲート
- 構築基板と definition.json の間で、配置・ネットリスト・ピン対応・外形寸法の同一性を、構築とは独立した照合スクリプトで検証する
- ゲート不通過なら配線に進まず、原因を記録して止まる（その状態で Draft PR を提出し、判定は「入力構築で停止」とする）

### スモーク
- pitch9-16mm で両ツールの経路を通す：KRT は .kicad_pcb 直接配線、fab_router は KiCad から DSN を書き出して配線し SES を取り込む
- 取込後に独立検査（プロジェクト既存の独立検査手順。過去の qualification 証跡にある check-import 系スクリプトを踏襲）を実施し、パイプラインが端から端まで動くことを確認する。スモーク基板自体の合否は Stage 1 の判定とは分けて記録する

## Stage 1：本評価セル（各セル単一 run、設定探索禁止）

| セル | 基板 | 条件 |
|---|---|---|
| KRT-16 | representative21-16mm | KiCad Routing Tools、**escalation off 固定**（Issue #115 の条件）。バージョン／コミットを記録 |
| KRT-17 | representative21-17mm | 同上 |
| FAB-16 | representative21-16mm | fab_router **API デフォルトプロファイル**（Issue #103 の条件）。対象コミット `69cf598db98c136bff16bbe02bccdded95674b18`、GPL-3.0 側で利用、本体無改変、ドライバは #103 のものを流用可、`timeBudgetMs: 1800000` |
| FAB-17 | representative21-17mm | 同上 |

- セル実行の順序は表のとおり（KRT-16 → KRT-17 → FAB-16 → FAB-17）を基本とし、時間配分はワーカーの裁量。ただし全セルに着手できない場合は、着手できなかったセルを未実施として明記する（黙って省略しない）
- 各セルの実効設定は readback を証跡に残す

## 判定（セルごと）

成功条件（すべて）：
- 独立検査の4指標すべて 0：required unconnected / wrong-net contacts / material violations / unexplained transfer changes
- fab_router セルは最終 SES の全 path が 0.20mm 以上（#97 以降の静的実測方式）
- KRT セルは出力側監査で、プロジェクト最小幅の書き換えがないこと・0.20mm 未満のトラックがないこと

失敗条件（いずれか1つ）：
- 未配線が残る／0.20mm 未満の配線がある／取込できない／4指標が 0 でない／時間内に結論が出ない

4指標の扱い：未配線が残る場合は **null** とし、実測の未配線件数を報告する。成功の場合のみ独立検査を実測して数値を報告する

## 環境上の注意

- **一時ランタイム（KiCad・Bun 等の展開物）は /tmp に置かない**。/tmp は 512MB の tmpfs で溢れる。作業ディレクトリ内の `.issue129-runtime/` を使うこと
- fab_router 用の Bun・clone は #103 の証跡手順を踏襲してよい。再取得した場合は取得元と hash を記録する

## 成果物

- 分析・判定文書：`docs/issue-129-wing-2layer-routing.md`（新規追加のみ）
- 証跡一式：`hardware/kicad/qualification/issue-129-wing-2layer-routing/` 配下（構築した入力基板・等価性ゲート結果・各セルの record／report／生成物・独立検査出力を含む。ランタイムや依存パッケージ本体は含めない）
- 作業ブランチ `issue-129-wing-2layer-routing` から **Draft PR** を作成する。main への直接 push・merge は禁止
- 既存ファイルの変更は禁止（追加のみ）
