"""Read-only manufacturer/assembler references. No account/quote/cart/order API."""
from common import *
import urllib.request,gzip,concurrent.futures
urls={
 'hall-catalog':'https://jlcpcb.com/partdetail/TexasInstruments-DRV5055A3QDBZR/C266128',
 'mux-catalog':'https://jlcpcb.com/partdetail/TexasInstruments-TMUX1208PWR/C494728',
 'capacitor-catalog':'https://jlcpcb.com/partdetail/MurataElectronics-GRM188R71C104KA01D/C45000',
 'connector-catalog':'https://www.lcsc.com/product-detail/C265384.html',
 'bom-format':'https://jlcpcb.com/help/article/bill-of-materials-for-pcb-assembly',
 'cpl-format':'https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly',
 'gh-drawing':'https://www.jst-mfg.com/product/pdf/eng/eGH.pdf',
}
w=E/'references';w.mkdir(exist_ok=True)
def fetch(item):
 name,url=item
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=60) as r:data=r.read();final=r.url;status=r.status
  p=w/(name+('.pdf' if name=='gh-drawing' else '.html.gz'))
  p.write_bytes(data if name=='gh-drawing' else gzip.compress(data,mtime=0))
  return name,dict(url=url,final_url=final,status=status,fetched_utc=now(),path=str(p.relative_to(E)),sha256=digest(p),uncompressed_bytes=len(data),note='Read-only evidence; part matching, not procurement/stock/price guarantee')
 except Exception as ex:return name,dict(url=url,error=str(ex),utc=now())
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:results=dict(ex.map(fetch,urls.items()))
save(w/'sources.json',results)
print({k:v.get('status',v.get('error')) for k,v in results.items()})
