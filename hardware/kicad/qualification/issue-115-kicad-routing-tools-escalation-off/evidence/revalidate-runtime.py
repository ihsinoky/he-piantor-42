"""Verify reused official tool sources, binary and independent inspector byte identity."""
import runpy,subprocess
from pathlib import Path
E=Path(__file__).resolve().parent;globals().update(runpy.run_path(str(E/'prepare-inputs.py')))
prior=R/'hardware/kicad/qualification/issue-113-kicad-routing-tools-falsification/evidence';T=TMP/'KiCadRoutingTools'
checks={}
for name,root in [('source-manifest.json',T),('inspection-runtime-hashes.json',RT)]:
 rows=json.loads((prior/name).read_text());bad={p:dict(expected=h,actual=digest(root/p)) for p,h in rows.items() if digest(root/p)!=h};assert not bad,bad;checks[name]=dict(verified_files=len(rows),mismatches=bad)
binary=list(T.rglob('grid_router*.so'));expected=json.loads((prior/'binary-provenance.json').read_text())['download_sha256'];assert len(binary)==1 and digest(binary[0])==expected
assert not subprocess.check_output(['git','-C',str(T),'diff','--name-only'])
save(E/'runtime-revalidation.json',dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks,binary=dict(path=str(binary[0].relative_to(R)),sha256=expected),official_commit=subprocess.check_output(['git','-C',str(T),'rev-parse','HEAD'],text=True).strip(),tracked_source_unchanged=True))
