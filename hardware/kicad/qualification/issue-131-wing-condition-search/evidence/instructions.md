# Issue #131 指示書：Wing 自動配線の実現条件探索

- 発行：PMO（2026-11-05、サイドチャット）。PO の GO 済み（起草提示→「この内容で GO」）
- PO 方針：自動配線の実現が最優先。実現できるツール・条件を先に特定し、費用判断はその後に行う
- ワーカー：Codex
- タイムボックス：**全体で4時間**

## 前提（Issue #129 の結果）

- 固定条件（2層・0.20mm・ビア0.60/0.30・配置固定）では全セル未達。KRT-16 未配線2件（MUX 周辺の短い GND 接続）が最接近。fab_router は両ピッチ23件
- #129 の証跡は `hardware/kicad/qualification/issue-129-wing-2layer-routing/` にある。入力基板の再構築手順（build-inputs.py）、等価性ゲート（check-equivalence.py）、独立検査の手順はそちらを正として再利用すること
- 報告書 `docs/issue-129-wing-2layer-routing.md` を着手前に読むこと

## Stage 0：入力改訂

- 対処対象：取付 NPTH が自身の pads 禁止 keepout に入る `items_not_allowed`（全基板各4件、配線前から存在）
- 根拠：生成 JSON（`hardware/jitx/wing/generated/*/definition.json`）が定義するのは取付穴 φ2.2mm＋keepout φ5.0mm の形状のみ。禁止対象の種別は JSON に含まれず、#129 の pads 禁止は KiCad 側 rule area の実装選択だった
- 改訂内容：rule area の禁止対象から **pads のみを外す**（tracks／vias／copper pour／footprints の禁止は維持する）。NPTH は銅を持たないため、取付穴周囲に銅を近づけない意図は維持される。JSON の形状・寸法・配置・ネットは一切変更しない
- 改訂した入力基板（pitch9-16mm、representative21-16mm、representative21-17mm）について、#129 の等価性ゲートを再実行する。ゲートの検査項目・基準は変更しない（keepout の禁止対象そのものは今回の改訂点として記録し、ゲートでは改訂後の設定と基板の一致を確認する範囲とする）。通過後に hash を再固定する
- ゲート不通過なら配線に進まず報告して止まる

## Stage 1：条件探索（KRT のみ）

- ツール：KiCad Routing Tools（#129 と同一バージョン／コミット。readback で実効設定を記録）、**escalation off 固定**
- 対象は representative21-16mm で探索し、セルは以下の順に実行する。**合格セルが出た段で探索を打ち止める**（残りセルは未実施として記録する）
  1. 2層・幅／クリアランス 0.127mm
  2. 2層・0.10mm
  3. 4層・0.127mm（層構成：F.Cu 信号／In1.Cu GND プレーン／In2.Cu 信号／B.Cu 信号。D-019 の Main 構成と同じ考え方。入力基板の層構成変更は Stage 0 の改訂入力から派生させ、配置・ネット・外形の等価性を保つ）
  4. 4層・0.10mm
- ビアは全セル 0.60／0.30mm で維持。板厚 1.2mm も維持する
- 16mm で合格条件が見つかったら、**同条件で representative21-17mm を1セル**実行する
- 各セル単一 run。セルの途中で条件を調整したり再試行したりしない

## 判定（セルごと）

成功条件（すべて）：
- 独立検査の4指標すべて 0：required unconnected / wrong-net contacts / material violations / unexplained transfer changes
- 幅監査：出力プロジェクトの最小幅書き換えがないこと、当該セルのピン留め幅未満のトラックがないこと

失敗条件（いずれか1つ）：未配線が残る／幅未満の配線がある／取込できない／4指標が 0 でない／時間内に結論が出ない

未配線が残る場合は4指標を **null** とし、実測の未配線件数を報告する。成功セルのみ4指標を実測して報告する。独立検査の手順は #129 の踏襲（固定プロジェクトルールでの DRC、実銅箔 graph、非配線オブジェクト差分、幅／プロジェクト監査）。

## 環境上の注意

- 一時ランタイムは **.issue131-runtime/** を使う（/tmp は 512MB の tmpfs）。#129 の `.issue129-runtime/` の中身（KRT／KiCad ランタイム等）は読み取り専用の再利用元として使ってよい
- GitHub への push がサンドボックスからできない場合は、コミットをブランチに積んだ状態で報告すればよい（PMO がホスト側から push する）

## 成果物

- 報告書：`docs/issue-131-wing-condition-search.md`（新規追加のみ）
- 証跡一式：`hardware/kicad/qualification/issue-131-wing-condition-search/` 配下（改訂入力基板・ゲート結果・各セルの record／report／生成物・独立検査出力。ランタイム本体は含めない）
- 作業ブランチ `issue-131-wing-condition-search` から **Draft PR** を作成する（push できない場合はその旨を報告）。main への直接 push・merge は禁止
- 既存ファイルの変更は禁止（追加のみ）。`hardware/jitx/wing/**` と `docs/decisions.md` は編集しない
