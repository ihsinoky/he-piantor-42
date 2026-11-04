#!/usr/bin/env python3
"""Fetch public JLCPCB capability/help pages anonymously with curl (urllib was
reset by the server in collect-public-evidence.py). Read-only GETs; no login.

Run from repository root:
  python3 hardware/kicad/qualification/issue-133-wing-cost-check/fetch-capability-pages.py OUTDIR
Writes <id>.html.gz, <id>.text.txt and capability-retrieval-records.json to OUTDIR.
"""
import datetime as dt
import gzip
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from html.parser import HTMLParser

PAGES = {
    "capabilities": "https://jlcpcb.com/capabilities/pcb-capabilities",
    "extra-charges": "https://jlcpcb.com/help/article/in-what-cases-will-there-be-charged-extra",
}


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        self.skip += tag in ("script", "style")

    def handle_endtag(self, tag):
        self.skip -= tag in ("script", "style")

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.parts.append(data.strip())


out = pathlib.Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
records = []
for name, url in PAGES.items():
    rec = dict(id=name, url=url, retrieved_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    body = out / (name + ".raw")
    try:
        c = subprocess.run(
            ["curl", "-sS", "-L", "-m", "60", "--retry", "3", "-A", "Mozilla/5.0",
             "-D", "-", "-o", str(body), "-w", "%{http_code}", url],
            capture_output=True, check=True)
        head = c.stdout.decode(errors="replace")
        rec["http_status"] = int(head.strip().splitlines()[-1])
        m = re.findall(r"(?im)^date: (.*)$", head)
        rec["response_date"] = m[-1].strip() if m else None
        raw = body.read_bytes()
        rec["html_sha256"] = hashlib.sha256(raw).hexdigest()
        rec["html_bytes"] = len(raw)
        (out / (name + ".html.gz")).write_bytes(gzip.compress(raw, mtime=0))
        p = Text()
        p.feed(raw.decode("utf-8", errors="replace"))
        (out / (name + ".text.txt")).write_text("\n".join(p.parts) + "\n")
    except Exception as e:
        rec["error"] = repr(e)
    body.unlink(missing_ok=True)
    records.append(rec)
    print(name, rec.get("http_status"), rec.get("error"))
(out / "capability-retrieval-records.json").write_text(json.dumps(records, indent=2) + "\n")
