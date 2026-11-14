"""Dated direct product responses; no search-cache counts treated as live stock."""
from pathlib import Path
import urllib.request,datetime,json,re,hashlib,concurrent.futures,gzip
E=Path(__file__).resolve().parent;R=E.parents[4];T=R/'.issue250-runtime';archive=E/'stock-responses';archive.mkdir(exist_ok=True)
urls={
'lcsc-header':'https://www.lcsc.com/product-detail/C5343398.html',
'lcsc-housing':'https://www.lcsc.com/product-detail/C2904692.html',
'lcsc-terminal':'https://www.lcsc.com/product-detail/C506724.html',
'jlcpcb-header':'https://jlcpcb.com/partdetail/HRS-DF52_14S_08H_21/C5343398',
'jlcpcb-housing':'https://jlcpcb.com/partdetail/HRS-DF52_14P_08C/C2904692',
'jlcpcb-terminal':'https://jlcpcb.com/partdetail/HRS-DF52_2832PCF/C506724',
'digikey-header':'https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/DF52-14S-0-8H-21/5721359',
'digikey-housing':'https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/DF52-14P-0-8C/5721346',
'digikey-terminal':'https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/DF52-2832PCF/5721364',
'mouser-housing':'https://www.mouser.com/ProductDetail/Hirose-Connector/DF52-14P-0.8C?qs=%2FKR40Cd6GUphscnWMeDLpg%3D%3D',
'mouser-header':'https://www.mouser.com/ProductDetail/Hirose-Connector/DF52-14S-0.8H21?qs=%2FKR40Cd6GUofAddN3Zbsbg%3D%3D',
'mouser-terminal':'https://www.mouser.com/ProductDetail/Hirose-Connector/DF52-2832PCF'}
def one(kv):
 name,url=kv;d=dict(url=url,checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=45) as res:data=res.read();d['http_status']=res.status;d['final_url']=res.url
  raw=data.decode(errors='replace');s=raw.replace('\\"','"')
  (archive/(name+'.html.gz')).write_bytes(gzip.compress(data,mtime=0));d['response_sha256']=hashlib.sha256(data).hexdigest()
  d['fields']={key:sorted(set(map(int,re.findall('"'+key+'":(\\d+)',s)))) for key in ('stockNumber','stockSz','overseasStockCount','canPresaleNumber','preMinPurchaseNum')}
  if name.startswith('lcsc-'):
   match=re.search(r'<script[^>]+id="__NEXT_DATA__"[^>]*>(.*?)</script>',raw)
   primary=json.loads(match[1])['props']['pageProps']['webData']
   d['primary_product']={key:primary.get(key) for key in ('productCode','productModel','stockNumber','stockSz','minBuyNumber','minPacketNumber','domesticStockVO','overseasStockVO')}
   d['extraction_note']='Primary webData only; alternate-part stock excluded'
  d['inventory_snippets']=re.findall('.{0,70}(?:In-Stock|In Stock|inStock|stockQuantity|availableQuantity|productQuantity).{0,100}',s)[:12]
 except Exception as ex:d['error']=str(ex)
 return name,d
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=dict(pool.map(one,urls.items()))
out=dict(batch_keyboards=15,installed=dict(headers=60,housings=60,terminals=840),spares_assumption='20% on complete batch, explicit conservative procurement allowance; B3 exact spare count not available',required_including_spares=dict(headers=72,housings=72,terminals=1008),preferred_10x_stock=dict(headers=720,housings=720,terminals=10080),observations=results)
out['installed_10x_stock']=dict(headers=600,housings=600,terminals=8400)
# Separately dated page observations must never be relabelled as a new live check.
out['primary_page_recheck']=json.loads((E/'primary-page-recheck.json').read_text()) if (E/'primary-page-recheck.json').exists() else []
out['verdict']='FAIL: housing is not confirmed at required 10x batch stock; assess dated primary product and fallback observations independently'
(E/'stock.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
