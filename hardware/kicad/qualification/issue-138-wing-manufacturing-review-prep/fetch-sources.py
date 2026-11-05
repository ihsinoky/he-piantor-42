#!/usr/bin/env python3
"""Anonymous GET only. Store authoritative references and retrieval provenance."""
import datetime as dt
import gzip
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent / 'sources'
OUT.mkdir(exist_ok=True)
PAGES = {
    'drv5055': 'https://www.ti.com/lit/ds/symlink/drv5055.pdf',
    'drv5055-revb-url-returned-revc': 'https://www.ti.com/lit/ds/sbas640b/sbas640b.pdf',
    'tmux1208': 'https://www.ti.com/lit/ds/symlink/tmux1208.pdf',
    'ti-current-method': 'https://www.ti.com/lit/ug/tiducs7/tiducs7.pdf',
    'qorvo-current-method': 'https://www.qorvo.com/design-hub/design-tools/interactive/pcb-trace-power-handling-calculator',
}


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        self.skip += tag in ('script', 'style')

    def handle_endtag(self, tag):
        self.skip -= tag in ('script', 'style')

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.parts.append(data.strip())


records = []
for name, url in PAGES.items():
    rawpath = OUT / (name + '.raw')
    record = dict(id=name, url=url, retrieved_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    proc = subprocess.run(['curl', '-sS', '-L', '-m', '60', '--retry', '2',
                           '-D', '-', '-o', str(rawpath), '-w', '%{http_code}\n%{url_effective}', url],
                          capture_output=True)
    record.update(exit_code=proc.returncode, response_headers_and_status=proc.stdout.decode(errors='replace'),
                  stderr=proc.stderr.decode(errors='replace'))
    if rawpath.exists():
        raw = rawpath.read_bytes()
        record.update(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
        if raw.startswith(b'%PDF'):
            target = OUT / (name + '.pdf')
            rawpath.rename(target)
            subprocess.run(['pdftotext', '-layout', str(target), str(OUT / (name + '.text.txt'))], check=True)
        else:
            (OUT / (name + '.html.gz')).write_bytes(gzip.compress(raw, mtime=0))
            parser = Text()
            parser.feed(raw.decode(errors='replace'))
            (OUT / (name + '.text.txt')).write_text('\n'.join(parser.parts) + '\n')
            record['content_is_security_checkpoint'] = 'Vercel Security Checkpoint' in '\n'.join(parser.parts)
            rawpath.unlink()
    records.append(record)
    print(name, record.get('bytes'), proc.returncode, flush=True)
(OUT / 'reference-retrieval-records.json').write_text(json.dumps(records, indent=2) + '\n')
