"""Rebuild disappeared temporary environment using unchanged public pinned inputs."""
import os,sys,runpy,shutil,gzip,json
from pathlib import Path
from capture import ROOT,run,save,digest,utc
BASE=Path('/tmp/eda004g-resume02');REPO=ROOT.parents[4]
if __name__=='__main__':
    os.environ['EDA004D_WORK_DIR']=str(BASE);os.environ['EDA004D_EVIDENCE_DIR']=str(ROOT/'evidence')
    prior=REPO/'hardware/tscircuit/qualification/eda-004d';sys.path.insert(0,str(prior))
    runpy.run_path(str(prior/'install-kicad.py'),run_name='__main__')
    archive=REPO/'hardware/kicad/qualification/eda-004f/evidence/library-source.tar.gz'
    assert digest(archive)=='fa7508829945457f9824ae3490bddfb81718f3cacedaeaa6ee6515c030ef398c'
    source=BASE/'library-source';source.mkdir();run('library-extract',['tar','-xzf',str(archive),'-C',str(source)],BASE)
    run('python-venv',['python3','-m','venv',str(BASE/'venv')],BASE)
    pip=str(BASE/'venv/bin/pip')
    run('dependencies-install',[pip,'install','--require-hashes','-r',str(REPO/'hardware/kicad/qualification/eda-004f/requirements-lock.txt'),'--report',str(ROOT/'evidence/pip-install-report.json')],BASE,240)
    run('library-install',[pip,'install','--no-deps',str(source),'--report',str(ROOT/'evidence/library-install-report.json')],BASE,120)
    # Geometry dependency artifact versions/hash match old epoch records.
    old=ROOT.parent/'resume-01/evidence/shapely-install.json'
    requirements=[]
    for item in json.loads(old.read_text())['install']:
        requirements.append(item['metadata']['name']+'=='+item['metadata']['version']+' --hash=sha256:'+item['download_info']['archive_info']['hashes']['sha256'])
    lock=ROOT/'geometry-requirements.txt';lock.write_text('\n'.join(requirements)+'\n')
    run('geometry-library-install',[pip,'install','--require-hashes','-r',str(lock),'--report',str(ROOT/'evidence/geometry-install-report.json')],BASE,120)
    run('dependencies',[pip,'freeze','--all'],BASE)
    lib=ROOT/'library';lib.mkdir()
    oldlib=ROOT.parent/'resume-01/library'
    for p in oldlib.iterdir():
        target=lib/(p.name[:-3] if p.suffix=='.gz' else p.name)
        target.write_bytes(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
    for a in json.loads((ROOT.parent/'resume-01/evidence/library-evidence-archives.json').read_text()):assert digest(lib/a['expanded_name'])==a['expanded_sha256']
    save(ROOT/'evidence/environment-preparation.json',dict(utc=utc(),library_commit='505bca23e91cf3fa6e3b66976e529e775eada3ba',library_source_archive_sha256=digest(archive),libraries={p.name:digest(p) for p in lib.iterdir()},rebuild_occurred=True,full_environment_qualification=False,reason='Previous tmp environment absent; no accepted whole-environment confirmation claimed.'))
    print('fixed KiCad/public library environment prepared')
