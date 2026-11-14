from pathlib import Path
import os,sys,json,hashlib,datetime
sys.dont_write_bytecode=True
E=Path(__file__).resolve().parent;R=E.parents[3];T=R/'.issue250-runtime';BASE=Path('/home/hatch/workspace/projects/he-piantor-42');B=BASE/'.issue129-runtime'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path,data):Path(path).write_text(json.dumps(data,indent=2)+'\n')
