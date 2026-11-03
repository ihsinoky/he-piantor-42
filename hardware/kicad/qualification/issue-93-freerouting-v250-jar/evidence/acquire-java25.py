import pathlib,json,urllib.request,hashlib,tarfile,subprocess,zipfile,struct
p=pathlib.Path('hardware/kicad/qualification/issue-93-freerouting-v250-jar/evidence').resolve();t=pathlib.Path.home()/'workspace/tools/issue-93';a=json.loads((p/'official/temurin25-assets.json').read_text())[0]['binary']['package'];dest=t/a['name'];urllib.request.urlretrieve(a['link'],dest);h=hashlib.sha256(dest.read_bytes()).hexdigest();assert h==a['checksum'];urllib.request.urlretrieve(a['checksum_link'],p/'official/temurin25.sha256.txt');assert (p/'official/temurin25.sha256.txt').read_text().split()[0]==h
with tarfile.open(dest) as f:f.extractall(t,filter='data')
java=next(t.glob('jdk-25*/bin/java'));v=subprocess.run([str(java),'-version'],capture_output=True,text=True);(p/'official/java25-version.txt').write_text(v.stdout+v.stderr)
r=json.loads((p/'official/distribution.json').read_text());r.append(dict(url=a['link'],path=str(dest),sha256=h,official_sha256=a['checksum'],match=True,selected_for_routing=True));(p/'official/distribution.json').write_text(json.dumps(r,indent=2)+'\n')
with zipfile.ZipFile(t/'freerouting-2.5.0.jar') as z:
 (p/'official/jar-manifest.txt').write_bytes(z.read('META-INF/MANIFEST.MF'));(p/'official/jar-bytecode.json').write_text(json.dumps(dict(class_name='app/freerouting/Freerouting.class',major_version=struct.unpack('>IHH',z.read('app/freerouting/Freerouting.class')[:8])[2],required_java=25,selection_reason='Java 21 cannot load class major 69; discovered by static archive inspection before any router invocation.'),indent=2)+'\n')
print(java)
