"""Read saved boards and verify fixed physical dimensions without changing them."""
from common import *
import sys,collections
cell=sys.argv[1];w=E/'inspection'/cell;source=E/'cell-inputs'/cell
snap=json.loads((w/'snapshot.json').read_text());condition=json.loads((source/'condition.json').read_text())
vias=[t for t in snap['tracks'] if t['kind']=='via'];distribution=collections.Counter(f"{t['size']:g}/{t['drill']:g}" for t in vias)
assert all(t['size']==.6 and t['drill']==.3 for t in vias)
assert snap['thickness']==1.2 and snap['layers']==condition['layers']
save(w/'physical-audit.json',dict(via_pass=True,via_count=len(vias),via_diameter_drill_mm_histogram=dict(distribution),thickness_mm=snap['thickness'],layers=snap['layers'],tracks_per_layer=dict(collections.Counter(str(t['layer']) for t in snap['tracks'] if t['kind']=='track')),fixed_input_rules=snap['rules']))
