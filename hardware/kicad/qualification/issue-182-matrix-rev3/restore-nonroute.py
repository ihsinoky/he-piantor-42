"""Preserve the exact source nonrouting AST after native KiCad serialization.
Only segment/via nodes come from candidate. No copper geometry is modified.
"""
from common import *
import sexpdata as sx,sys,collections
source,candidate=map(Path,sys.argv[1:]);a=sx.loads(source.read_text());b=sx.loads(candidate.read_text())
def route(n):return isinstance(n,list) and n and str(n[0]) in ['segment','via']
routes=[n for n in b[1:] if route(n)]
before=collections.Counter(sx.dumps(n) for n in routes)
result=[a[0]]+[n for n in a[1:] if not route(n)]+routes
candidate.write_text(sx.dumps(result)+'\n')
after=collections.Counter(sx.dumps(n) for n in sx.loads(candidate.read_text())[1:] if route(n))
assert before==after
save(candidate.with_suffix('.nonroute-preservation.json'),dict(utc=now(),source_sha256=digest(source),candidate_sha256=digest(candidate),routing_nodes=len(routes),copper_AST_unchanged=True,nonrouting_AST_exact_source=True,reason='Native serialization changed numeric spelling 42.0 to 42 in artwork; restore exact source nonrouting nodes, without acceptance exemptions.'))
