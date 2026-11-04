#!/usr/bin/env python3
"""Calculation-only anonymous POSTs to JLCPCB public quote API (no login/cart/order).
Request = exact-request.json (frontend serializer output, default service options);
only board dimensions vary. Run from repo root."""
import re, subprocess, json, hashlib, gzip, datetime as dt, urllib.request, pathlib, copy, sys
URL="https://cart.jlcpcb.com/api/overseas-core-platform/shoppingCart/calculationGoodsCostsNew"
out=pathlib.Path(sys.argv[1]); out.mkdir(parents=True)
base=json.load(open("hardware/kicad/qualification/issue-133-wing-cost-check/quote-capture/calculation-request-16mm.json"))
recs=[]
for label,L,W in [("16mm",110,100),("17mm",116.5,104.75),("16mm-repeat",110,100)]:
    for variant in ["wing-0.10mm-design","comparison-0.20mm-design"]:
        r=copy.deepcopy(base); p=r["pcbGoodsRequest"]
        p["stencilLength"]=p["stencilLengthInch"]=L; p["stencilWidth"]=p["stencilWidthInch"]=W
        body=json.dumps(r).encode()
        rec=dict(id=f"{label}-{variant}",variant=variant,retrieved_utc=dt.datetime.now(dt.timezone.utc).isoformat(),length_mm=L,width_mm=W,request_sha256=hashlib.sha256(body).hexdigest())
        try:
            c=subprocess.run(["curl","-sS","-m","90","-X","POST","-H","Content-Type: application/json","-H","Origin: https://cart.jlcpcb.com","-H","Referer: https://cart.jlcpcb.com/quote","-H","User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/136.0.0.0 Safari/537.36","--data-binary","@-","-D","-","-o",str(out/"raw.tmp"),"-w","%{http_code}",URL],input=body,capture_output=True,check=True)
            hdr=c.stdout.decode(); rec["http_status"]=int(hdr.strip().splitlines()[-1])
            m=re.search(r"(?im)^date: (.*)$",hdr); rec["response_date"]=m.group(1).strip() if m else None
            raw=(out/"raw.tmp").read_bytes()
            (out/f"{rec['id']}.response.json.gz").write_bytes(gzip.compress(raw,mtime=0))
            rec["response_sha256"]=hashlib.sha256(raw).hexdigest()
            d=json.loads(raw)["data"]; rec["orderCountTolls"]=d["orderCountTolls"]; rec["pcbWeight_kg"]=d["pcbWeight"]
        except Exception as e: rec["error"]=repr(e)
        recs.append(rec); print(rec["id"],rec.get("http_status"),rec.get("orderCountTolls",{}).get("dummyMoney"),rec.get("error"),flush=True)
json.dump(recs,open(out/"quote-records.json","w"),indent=1)
