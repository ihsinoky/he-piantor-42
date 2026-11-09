"""Read-only JLCPCB public-page capture. No account, cart, quote, or order API.

Retain an allowlist of stock/price fields, never signed image URLs or customer
metadata. RSC record IDs are resolved rather than confused with related parts.
Usage: python3 capture-stock.py [output.json]
"""
import datetime
import hashlib
import json
import pathlib
import re
import sys
import urllib.request

PARTS = {
    "C3033018": "Coilcraft-XFL4020152MEC",
    "C7417180": "Coilcraft-XGL4020152MEC",
    "C3221841": "BOURNS-SRP4020FA1R5M",
    "C5355380": "Coilcraft-XFL4020102MEC",
}
FIELDS = (
    "componentCode", "componentModelEn", "componentBrandEn",
    "componentSpecificationEn", "overseasStockCount", "canPresaleNumber",
    "preMinPurchaseNum", "initialPrice", "componentLibraryType",
    "assemblyComponentFlag", "isBuyComponent", "allowPostFlag",
    "lossNumber", "leastPatchNumber", "encapsulationNumber",
)


def extract(html, code):
    chunks = []
    for match in re.finditer(r'self\.__next_f\.push\((.*?)\)</script>', html):
        value = json.loads(match[1])
        if len(value) > 1 and isinstance(value[1], str):
            chunks.append(value[1])
    stream = "".join(chunks)
    decoder = json.JSONDecoder()
    # Match this part's full componentInfo object, not related-products stock.
    candidates = []
    pattern = r'\{"componentCode":"' + re.escape(code) + r'","componentModelEn"'
    for match in re.finditer(pattern, stream):
        obj = decoder.raw_decode(stream, match.start())[0]
        if "overseasStockCount" in obj:
            candidates.append(obj)
    assert candidates, f"No componentInfo stock for {code}"
    for key in ("overseasStockCount", "canPresaleNumber", "initialPrice"):
        assert len({obj[key] for obj in candidates}) == 1, (code, key)
    obj = max(candidates, key=lambda v: len(set(v) & set(FIELDS)))

    def resolve(ref):
        for match in re.finditer(re.escape(ref) + ":", stream):
            try:
                return decoder.raw_decode(stream, match.end())[0]
            except json.JSONDecodeError:
                continue
        raise ValueError(f"Unresolved RSC reference {ref}")

    refs = resolve(obj["prices"][1:])
    prices = []
    for ref in refs:
        price = resolve(ref[1:])
        assert price["componentCode"] == code
        prices.append({key: price[key] for key in
                       ("startNumber", "endNumber", "productPrice")})
    return dict(fields={k: obj[k] for k in FIELDS if k in obj},
                price_tiers_USD=prices)


def main():
    records = []
    for code, slug in PARTS.items():
        url = f"https://jlcpcb.com/partdetail/{slug}/{code}"
        request = urllib.request.Request(url, headers={"Cache-Control": "no-cache"})
        with urllib.request.urlopen(request, timeout=45) as response:
            raw = response.read()
            record = dict(url=url,
                          retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                          http_date=response.headers.get("Date"),
                          http_age=response.headers.get("Age"),
                          html_sha256=hashlib.sha256(raw).hexdigest(),
                          **extract(raw.decode(), code))
        records.append(record)
    result = dict(method="GET public JLCPCB product pages; allowlisted RSC componentInfo and price records",
                  stock_semantics="overseasStockCount and canPresaleNumber are distinct published fields; neither is a reservation or an assembly quote",
                  records=records)
    target = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).with_name("stock-snapshot.json")
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    for r in records:
        f = r["fields"]
        print(f["componentCode"], f["overseasStockCount"], f["canPresaleNumber"], f["initialPrice"])


if __name__ == "__main__":
    main()
