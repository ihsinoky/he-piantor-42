"""Isolated fixed frontend + router acquisition; does not route any board."""
import json
import os
import shutil
from pathlib import Path
from capture import ROOT, run, save, digest, utc

BASE = Path('/tmp/eda004g-resume02/runtime')
REPO = ROOT.parents[4]
if __name__ == '__main__':
    BASE.mkdir(exist_ok=False)
    front = BASE/'frontend'; front.mkdir()
    prior = REPO/'hardware/tscircuit/qualification/eda-003c/latest-stock'
    for name in ('package.json','package-lock.json'):
        shutil.copyfile(prior/name,front/name)
    run('frontend-install',['npm','ci','--ignore-scripts'],front,240,
        env={'npm_config_cache':str(BASE/'npm-cache')})
    run('bun-download',['curl','-fL','https://github.com/oven-sh/bun/releases/download/bun-v1.2.22/bun-linux-x64.zip','-o',str(BASE/'bun.zip')],BASE,120)
    assert digest(BASE/'bun.zip')=='4c446af1a01d7b40e1e11baebc352f9b2bfd12887e51b97dd3b59879cee2743a'
    run('bun-extract',['unzip','-q',str(BASE/'bun.zip')],BASE)
    for name in ['qualification/revm1-routing-proof.tsx','qualification/native-support-footprints.tsx','qualification/JstGh14.tsx','components/HallKey.tsx']:
        target=front/'src'/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(REPO/'hardware/tscircuit/src'/name,target)
    source=front/'src/qualification/revm1-routing-proof.tsx'
    original=source.read_text()
    assert original.count('const boardRules = { layers:2 as const,')==1
    source.write_text(original.replace('const boardRules = { layers:2 as const,','const boardRules = { routingDisabled:true, layers:2 as const,'))
    run('source-copy-diff',['git','diff','--no-index','--',str(REPO/'hardware/tscircuit/src/qualification/revm1-routing-proof.tsx'),str(source)],BASE,30) if False else None
    save(ROOT/'evidence/frontend-copy.json',dict(recorded_utc=utc(),original_sha256=digest(REPO/'hardware/tscircuit/src/qualification/revm1-routing-proof.tsx'),copy_sha256=digest(source),only_change='public routingDisabled:true board property; ordinary source wiring and local bond unchanged',lock_sha256=digest(front/'package-lock.json'),source_inputs=[str(p) for p in (front/'src').rglob('*.tsx')]))
    run('freerouting-release',['curl','-fL','https://api.github.com/repos/freerouting/freerouting/releases/tags/v2.1.0','-o',str(BASE/'freerouting-release.json')],BASE,120,artifacts=[('release.json',BASE/'freerouting-release.json')])
    release=json.loads((BASE/'freerouting-release.json').read_text())
    asset=next(x for x in release['assets'] if x['name']=='freerouting-2.1.0.jar')
    run('freerouting-download',['curl','-fL',asset['browser_download_url'],'-o',str(BASE/'freerouting.jar')],BASE,180)
    for name in ('build.gradle','README.md','docs/command_line_arguments.md'):
        out=ROOT/'evidence'/('freerouting-'+name.replace('/','-'))
        run('router-doc-'+name.replace('/','-').replace('.','-'),['curl','-fL','https://raw.githubusercontent.com/freerouting/freerouting/v2.1.0/'+name,'-o',str(out)],BASE,120,artifacts=[(out.name,out)])
    java=Path('/home/codespace/java/21.0.12+1-ms')
    run('java-version',[str(java/'bin/java'),'-version'],BASE)
    save(ROOT/'evidence/runtime-freeze.json',dict(recorded_utc=utc(),router_version='2.1.0',router_url=asset['browser_download_url'],router_sha256=digest(BASE/'freerouting.jar'),release_asset_digest=asset.get('digest'),java_home=str(java),java_file_sha256={str(p.relative_to(java)):digest(p) for p in sorted(java.rglob('*')) if p.is_file()},frontend_lock_sha256=digest(front/'package-lock.json'),bun_sha256=digest(BASE/'bun.zip'),production_unchanged=True))
    print('runtime prepared; zero routing attempts')
