"""Recover the exact upstream Git commit from official Codeberg archive/API.
Run after extracting petgraph-source.tar.gz into the supplied directory.
This changes no dependency source files. The SHA assertion authenticates tree,
file modes, commit metadata and parent IDs against the official commit ID.
"""
import datetime,json,pathlib,subprocess,sys
S=pathlib.Path(sys.argv[1]).resolve(); E=pathlib.Path(__file__).resolve().parent
j=json.loads((E/'petgraph-commit.json').read_text()); c=j['commit']
def git(*args,input=None):return subprocess.check_output(['git','-C',str(S),*args],input=input).decode().strip()
git('init');git('add','-f','.');tree=git('write-tree')
raw='tree '+tree+'\n'+''.join('parent '+p['sha']+'\n' for p in j['parents'])
for key in ['author','committer']:
 v=c[key];d=datetime.datetime.fromisoformat(v['date']);raw+=f"{key} {v['name']} <{v['email']}> {int(d.timestamp())} {d.strftime('%z')}\n"
raw+='\n'+c['message'];sha=git('hash-object','-t','commit','-w','--stdin',input=raw.encode());assert sha==j['sha']
git('update-ref','refs/heads/master',sha);(S/'.git/shallow').write_text(sha+'\n');print(sha)
