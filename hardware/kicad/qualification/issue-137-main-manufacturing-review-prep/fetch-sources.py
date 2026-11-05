"""Capture public, unauthenticated sources into the Issue #137 runtime only.

Run from repo root with Python 3 stdlib. Never submits orders or uploads designs.
Review selected passages and record findings in primary-sources.json separately.
"""
import concurrent.futures
import datetime
import hashlib
import html.parser
import json
from pathlib import Path
import subprocess

ROOT = Path('.issue137-runtime/sources')
URLS = {
    'pcb-capabilities': 'https://jlcpcb.com/capabilities/pcb-capabilities/',
    'via-covering': 'https://jlcpcb.com/help/article/pcb-via-covering',
    'extra-charges': 'https://jlcpcb.com/help/article/in-what-cases-will-there-be-charged-extra',
    'pofv-process': 'https://jlcpcb.com/news/free-via-in-pad-6-20-layer-pcbs-pofv',
    'pcba-capabilities': 'https://jlcpcb.com/capabilities/pcb-assembly-capabilities',
    'pcba-price': 'https://jlcpcb.com/help/article/pcb-assembly-price',
    'pcba-terms': 'https://jlcpcb.com/help/article/terms-and-conditions-of-jlcpcb-assembly-service',
    'j1-part': 'https://jlcpcb.com/partdetail/C165948',
    'resin-price-notice': 'https://jlcpcb.com/news/pcb-lead-time-and-price-adjustment-august2026',
}

class Text(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(); self.skip = 0; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip += 1
        if tag in ('p', 'div', 'tr', 'th', 'td', 'li', 'h1', 'h2', 'h3', 'br'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip -= 1
        if tag in ('p', 'div', 'tr', 'th', 'td', 'li', 'h1', 'h2', 'h3'): self.parts.append('\n')
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)

def fetch(item):
    key, url = item
    record = dict(id=key, url=url, started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), method='unauthenticated GET')
    try:
        target=ROOT/(key+'.html')
        proc=subprocess.run(['curl','--http1.1','-L','--max-time','45','-sS','-o',str(target),'-w','%{http_code} %{url_effective}',url],capture_output=True,text=True)
        record.update(curl_exit=proc.returncode, transport='curl --http1.1', stderr=proc.stderr)
        if proc.returncode: raise RuntimeError(f'curl exit {proc.returncode}: {proc.stderr}')
        status, final_url=proc.stdout.split(' ',1)
        if status!='200': raise RuntimeError(f'HTTP {status}')
        raw=target.read_bytes()
        record.update(http_status=int(status), final_url=final_url, sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
        parser=Text(); parser.feed(raw.decode('utf-8'))
        lines=[' '.join(line.split()) for line in ''.join(parser.parts).splitlines() if line.strip()]
        (ROOT / (key+'.txt')).write_text('\n'.join(f'{i+1:04d} {line}' for i,line in enumerate(lines))+'\n')
        record['status']='retrieved; content requires review'
    except Exception as exc:
        record.update(status='未取得', error=str(exc))
    record['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    return record

if __name__ == '__main__':
    ROOT.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records=list(pool.map(fetch, URLS.items()))
    (ROOT/'retrievals.json').write_text(json.dumps(records, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(records, ensure_ascii=False, indent=2))
