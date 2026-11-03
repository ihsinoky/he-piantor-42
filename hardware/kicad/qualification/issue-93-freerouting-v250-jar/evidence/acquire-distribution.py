import pathlib,json,urllib.request,hashlib,tarfile,subprocess,datetime
p=pathlib.Path('hardware/kicad/qualification/issue-93-freerouting-v250-jar/evidence').resolve(); t=pathlib.Path.home()/'workspace/tools/issue-93';t.mkdir(exist_ok=True)
r=json.loads((p/'official/freerouting-release.json').read_text());jar=next(a for a in r['assets'] if a['name']=='freerouting-2.5.0.jar');a=json.loads((p/'official/temurin-assets.json').read_text())[0]['binary']['package']
records=[]
for url,name,expected in [(jar['browser_download_url'],jar['name'],jar['digest'].split(':')[1]),(a['link'],a['name'],a['checksum'])]:
 dest=t/name;urllib.request.urlretrieve(url,dest);h=hashlib.sha256(dest.read_bytes()).hexdigest();assert h==expected;records.append(dict(url=url,path=str(dest),sha256=h,official_sha256=expected,match=True))
urllib.request.urlretrieve(a['checksum_link'],p/'official/temurin.sha256.txt');assert (p/'official/temurin.sha256.txt').read_text().split()[0]==a['checksum']
with tarfile.open(t/a['name']) as f:f.extractall(t,filter='data')
java=next(t.glob('*/bin/java'));v=subprocess.run([str(java),'-version'],capture_output=True,text=True);(p/'official/java-version.txt').write_text(v.stdout+v.stderr)
(p/'official/distribution.json').write_text(json.dumps(records,indent=2)+'\n')
checks={}
for n,expected in [('main','75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2'),('smoke','7214a0299ce19fae8163fa82a7d844e71c5bbf43b077392cfff7c7b5a9d1f3e9')]:
 f=pathlib.Path(f'hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/processes/{n}-restore/corrected.dsn');h=hashlib.sha256(f.read_bytes()).hexdigest();assert h==expected;checks[n]=dict(path=str(f),sha256=h,expected=expected,match=True)
(p/'start.json').write_text(json.dumps(dict(start_utc='2026-11-03T11:00:00+00:00',router_cutoff_utc='2026-11-03T12:40:00+00:00',deadline_utc='2026-11-03T13:00:00+00:00',main=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip(),pr92='OPEN; mergedAt=null',inputs=checks),indent=2)+'\n')
print(java)
