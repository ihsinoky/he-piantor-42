"""Authoritative unconnected census via KiCad connectivity (ratsnest edges)."""
import pcbnew as p, sys, json
from pathlib import Path
E = Path('.').resolve()
b = p.LoadBoard(str(E/sys.argv[1]))
b.BuildConnectivity()
conn = b.GetConnectivity()
print('unconnected count:', conn.GetUnconnectedCount(False))

def pad_name(item):
    try:
        par = item.GetParent()
        return f"{par.GetReference()}.{item.GetNumber()}"
    except Exception:
        return '?'

out = {}
for code in range(1, 200):
    try:
        name = conn.GetNetNameForNetCode(code)
    except Exception:
        continue
    if not name:
        continue
    rn = conn.GetRatsnestForNet(code)
    if rn is None:
        continue
    n = rn.GetUnconnectedCount()
    if n:
        nodes = rn.GetNodes()
        out[name] = {'unconnected_edges': n,
                     'nodes': [pad_name(x.GetPad()) if hasattr(x, 'GetPad') else '?' for x in nodes]}
print(json.dumps(out, indent=1))
Path('ratsnest.json').write_text(json.dumps(out, indent=1))
