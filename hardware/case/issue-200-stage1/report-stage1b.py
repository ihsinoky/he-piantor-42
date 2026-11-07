"""Render Stage 1b supplement from the checked geometry; no PCB/case writes."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
d=json.loads((HERE/'geometry.json').read_text())
f=lambda n:f'{n:.3f}'
lines=['''# Issue #200 Wing Rev.3 — Stage 1b 北側拡張の再考

北側の矩形タブを、既存北辺から GH 台座へ広く連なる肩状の拡張に置き換える。接合部の入隅を R5 とし、細い付け根をなくす。16/17mm × 左右の全4版を同じ条件で検証した。以下は公称の平面形状案であり、配線・製造データ・ケースは生成していない。

## 方針と基準

`.issue200-runtime/instructions-200-stage1b.md` を全文読み、要件から形状を評価した。Stage 1 のコミット `e41dec9` を基準とし、その geometry.json を `inputs/stage1/geometry.json` にバイト保存して比較する。数値の単位は mm、面積は mm²。Wing ローカルは X右/Y北、組立は X右/Y南。変換と原点は Stage 1 のまま。

候補として矩形タブの付け根だけの丸めと、既存北辺からの幅広い拡張を比較した。小さい丸めだけでは約11.343mmの接合幅が残り、局所的な突起という問題を解消しにくい。採用案は、組立の左台座 `X=−43…−13, Y=−45…−18` と旧北辺の外側端点の凸包を作り、旧北辺より北だけを追加する。右は基材形状のみ左右対称。既存側辺から北肩へつながる面として、荷重を北辺の広い範囲へ渡す。台座に向かう入隅は接線円弧 R5 で埋め、接合部に鋭い切欠きを残さない。

境界線だけが重なった部分を接合幅へ算入しないよう、旧北辺から北へ0.00001mm入った実材断面で幅を測る。単なる境界の長さを接合幅として過大評価しない。

## 要件適合の対照

| 要件 | 判断と根拠 |
| --- | --- |
| 1 目的 | GH は親指帯から北中央の谷へ移設。Main J2/J3→中央通路→UDB横の GH へ R5 経路を設定。両 Wing 計42キーの17mm角包絡との交差0。 |
| 2 コネクタ | BM14B-GHS-TBT のまま。既存ランドを平行移動・回転し、全パッドの番号・net・寸法・原点相対位置が Stage 1 と一致。右も銅箔の鏡像化なし。 |
| 3 組立 | 全4版で基板重なり0、最小間隔は約2mm。GH本体・上面作業予約とMain/UDB/対向Wing/両Wingのキー包絡との干渉0。詳細は下表。 |
| 4 機械 | 単一の有効な単連結ポリゴン、追加部の入隅R5。接合断面幅とGH荷重経路の断面を下表に示す。厚さ1.2mm・2層・4点固定を維持。 |
| 5 大きさ | GH台座北端−45を維持。既存外側角を含む組立全体の北端もStage 1と同値。5mm外周余裕込みの左右2分割包絡が各220×220以内。 |
| 6 ハーネス | φ2/R5、必要長は折れ線長+30mm。キー包絡との交差0、全長と200mmとの差は下表。 |
| 7 不変 | キー/センサー/配線規則/ピン契約/南トリム/取り付け穴・移設候補/トリム棚卸しをStage 1保存値と照合。変更は北側外形とGH位置、およびそれに従属する経路・評価値。 |

## 形状と機械的な接合

| 版 | 接合幅 Stage 1→1b | 荷重経路の最小断面幅 | GH原点から最寄り固定点 | 北追加面積 | Stage 1からの面積増分 |
| --- | --- | --- | --- | --- | --- |''']
for r in d['variants']:
 n=r['north_join'];c=r['stage1_comparison']
 lines.append(f"| {r['variant']} | {f(n['old_attachment_width_mm'])} → {f(n['minimum_attachment_width_mm'])} | {f(n['load_path_min_section_mm'])} | {f(n['connector_to_nearest_mount_mm'])} | {f(r['size']['tab_added_area_mm2'])} | {f(c['area_delta_mm2'])} |")
lines.append('''
「荷重経路」は旧北辺からGH本体包絡の図心までを、旧北辺に平行な断面で評価したもの。ポリゴン頂点の高さと両端で幅を計算し、区間内は幅が線形に変化するため最小値を確定する。各断面が一本の連続線分であることも検証した。先端で幅がゼロになる形状一般の値と、接合部・荷重伝達区間の値を区別する。数表・断面高さ・幅・正確なR5円弧中心/始終点/角度をJSONの `north_join` に収録する。円弧は0.5°以下の弦で離散化し、弦誤差は0.00005mm未満。

4点固定はStage 1の3点維持＋南側1点の移設候補をそのまま使う。固定点を追加せず、厚さも増やさず、幅広い基材と接線円弧で挿抜時の曲げを受ける方針である。狭い付け根より荷重を広く渡せ、鋭い切欠きの応力集中を避けられる。一方、4点ネジ固定は北辺全体の完全固定ではないため、断面幅だけで許容挿抜力を保証しない。材料定数・実ハーネス挿抜力・ケース拘束が未確定なので、強度認定/疲労試験は本段階の成果ではない。後段では実部品で繰返し挿抜と板たわみを確認する。

## GHの位置と上面作業空間

公称本体はStage 1と同じ22×7、指/プラグ予約は32×27、Z=11.2…41.2を開放する。左GH原点は組立(−27,−41)、本体X=−38…−16/Y=−42…−35、予約X=−43…−11/Y=−52…−25。右は予約領域のXを反転するが、フットプリントは回転・移動のみ。本体と全パッドが基材内に入ることを検証した。

| 版 | GHローカル原点 | ローカル角度 | 本体/キー | 作業予約/キー |
| --- | --- | --- | --- | --- |''')
for r in d['variants']:
 c=r['connector'];lines.append(f"| {r['variant']} | ({f(c['local'][0])}, {f(c['local'][1])}) | {c['local_ccw_deg']}° | {f(c['body_to_keycap_mm'])} | {f(c['access_to_keycap_mm'])} |")
lines.append('''
作業予約はStage 1の仮定を踏襲する。実指寸法の保証ではなく、プラグを上面からつまむための確保領域。左右の予約同士も重ならない。上蓋や保持具をこの上へ置かないことを後段へ引き継ぐ。

| 版 | 相手 | PCB間隔 | PCB重なり | GH本体間隔 | 作業予約間隔 |
| --- | --- | --- | --- | --- | --- |''')
for r in d['variants']:
 for name,c in r['clearances'].items():
  lines.append(f"| {r['variant']} | {name} | {f(c['pcb_mm'])} | {f(c['pcb_overlap_mm2'])} | {f(c['connector_mm'])} | {f(c['access_mm'])} |")
lines.append('''
Mainとの最小約1.9999993mmは入力の丸めによる約2mm。UDBの実輪郭はStage 1保存入力を使う。PCB相互の距離/重なり、本体と予約の全障害物への正の距離を数値検証している。

## ハーネス

左の折れ線は `(−15.5,43)→(−13,32)→(−13,−32)→(−19,−41)→(−27,−41)`、右はX反転。各折れ点をR5接線円弧でつなぐ。φ2の掃引領域を両Wing全42キーの回転込み17mm角包絡と比較する。

| 版 | 直線 | 折れ線 | R5経路 | 必要長(+30) | Stage 1必要長 | 200との差 | ケーブル表面/キー | 表面/UDB | キー交差数 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |''')
for r in d['variants']:
 h=r['harness'];c=r['stage1_comparison'];lines.append('| '+r['variant']+' | '+' | '.join(f(h[k]) for k in ['chord_mm','polyline_mm','smooth_length_mm','required_mm'])+f" | {f(c['harness_required_before_mm'])} | {f(h['nominal_minus_required_mm'])} | {f(h['cable_surface_keycap_min_mm'])} | {f(h['cable_surface_udb_min_mm'])} | {h['keycap_intersections']} |")
lines.append('''
余長は谷/北側で保持する。φ2/R5と30mm余裕はStage 1と同じ評価仮定であり、実際の14芯束径・最小曲げ半径・上面嵌合の立上がりを保証する値ではない。Main上面部品とのZ干渉・SHケーブル・保持具の具体化は後段で扱う。

## 北端・印刷包絡

要件の「Y=−45」は北タブ台座の基準として守る。保存済みStage 1 geometryを組立変換すると、既存Wing外側角は16mmで−58.600、17mmで−61.600にある。したがって、組立全体の北端を−45と報告することはできない。今回その外側角を動かさず、Stage 1から北への追加張り出しは0である。

| 版 | 全体北端 Stage 1→1b | 2分割片の包絡 W×H | 220×220に対する残り W/H |
| --- | --- | --- | --- |''')
for r in d['variants']:
 c=r['stage1_comparison'];p=r['print_envelope'];lines.append(f"| {r['variant']} | {f(c['assembly_north_before_mm'])} → {f(c['assembly_north_after_mm'])} | {f(p['width_mm'])} × {f(p['height_mm'])} | {f(220-p['width_mm'])} / {f(220-p['height_mm'])} |")
lines.append('''
包絡はMain/UDB/両Wing/キー/作業予約の和に外周5mmを加え、#198と同じX=±3.5までの重複を許した左右2片の組立軸bbox。既存の壁2mm+クリアランス0.5mmより大きい外周余裕を確保する。ケース再生成はせず、2分割ケースを収める設計空間が十分あることを確認した。後段で追加するラッチ/保持具等もこの包絡以内へ設計する。

## レビュー図と再現

灰線はStage 1外形、緑は採用基材、赤線は接合断面、紫枠はキー、灰色はMain/UDBおよびGH、水色は上面作業予約、橙はφ2ハーネス、青円は4点固定（南側候補を含む）。上面視・組立座標、原寸の数値はJSONを正とする。

![16mm 両側レビュー](../hardware/case/issue-200-stage1/review-stage1b-16mm.svg)

![17mm 両側レビュー](../hardware/case/issue-200-stage1/review-stage1b-17mm.svg)

`python3 hardware/case/issue-200-stage1/generate.py` をPython 3 + shapely 2.2.0 + sexpdata 1.0.2で実行する。実施時はruntime内venvを使用した。生成器は全4版の形状・クリアランス・パッド非鏡像・南側不変・キー/センサー不変・配線規則不変をassertし、geometry.json、両SVG、本追補を更新する。trim-inventory.csvはStage 1と同値で、旧レビュー図と旧報告書は履歴として保持する。Stage 1の `report.py` は旧データ用であり現データには実行しない。

`hardware/kicad/qualification/issue-200-wing-rev3/` の未コミット作業は対象外で、変更・ステージングしていない。製造資格、発注、配線、ケース生成は実施していない。
''')
(ROOT/'docs/issue-200-wing-rev3-stage1b.md').write_text('\n'.join(lines).rstrip()+'\n')
