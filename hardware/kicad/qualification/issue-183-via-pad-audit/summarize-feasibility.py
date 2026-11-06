"""Summarize saved single-via probes and nearest-path obstacles; no KiCad needed."""
from pathlib import Path
import collections,json
E=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
lines=['# 配置固定・単独via移設の探索詳細','',
       '各候補は独立。全候補の同時成立・DRC・接続・zone再fillは未確認。',
       '直線stubが見つからないことは、配置変更や広域再配線が必須だという証明ではない。',
       '障害列は最寄りの固定銅箔回避候補への直線接続で当たる対象。全探索点の障害集合ではない。','']
summaries=[]
for s in read(E/'sources.json'):
    w=E/s['board'];probes=read(w/'move-probes.json');counts=collections.Counter(q['status'] for q in probes)
    difficult=read(w/'reroute-obstacles.json')
    assert {q['via_uuid'] for q in difficult}=={q['via_uuid'] for q in probes if q['straight_stub_candidate_mm'] is None}
    bodies=[q for q in probes if q['fixed_copper_nearest_mm'] is not None]
    straight=[q for q in probes if q['straight_stub_candidate_mm'] is not None]
    summaries.append(dict(board=s['board'],source_sha256=s['sha256'],violating_vias=len(probes),status_counts=dict(counts),pad_only_candidate_vias=sum(q['pad_only_candidate_count']>0 for q in probes),fixed_copper_candidate_vias=len(bodies),straight_stub_candidate_vias=len(straight),max_straight_stub_displacement_mm=max((q['straight_stub_displacement_mm'] for q in straight),default=None),placement_change_necessity_proven=False,pofv_removal_qualified=False,classification_by_status={k:dict(collections.Counter(q['classification'] for q in probes if q['status']==k)) for k in counts}))
    lines += ['## '+s['board'],'',f'{len(probes)}件の0.10mm未達。直線接続候補 {len(straight)}、迂回等の追加検討 {len(bodies)-len(straight)}、固定銅箔回避候補なし {len(probes)-len(bodies)}。','',
              '| via UUID | 元座標 mm | 対象パッド（重なりがなければ最近傍） | net | 最寄り移設候補 mm | 直線上の障害（層・Reference／ネット） |',
              '| --- | --- | --- | --- | --- | --- |']
    for q in difficult:
        obstacles=sorted(set(f['layer']+':'+(f['ref']+('.'+f['pad'] if 'pad' in f else '') if 'ref' in f else f['kind']+':'+f.get('net',f.get('uuid',''))) for f in q['nearest_direct_connection_obstacles']))
        lines.append('| '+' | '.join([q['via_uuid'],str(q['origin_mm']),', '.join(q['hit_pads'] or [q['nearest_pad']]),q['net'],str(q['nearest_fixed_candidate_mm']),'; '.join(obstacles) or '固定銅箔回避候補なし／別の形状制約を確認'])+' |')
    lines += ['']
(E/'feasibility-details.md').write_text('\n'.join(lines).rstrip()+'\n')
(E/'feasibility-summary.json').write_text(json.dumps(summaries,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(summaries,indent=2,ensure_ascii=False))
