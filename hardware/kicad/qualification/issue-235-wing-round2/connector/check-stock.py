"""Recheck public product HTML; print observations without overwriting dated evidence."""
import urllib.request,re,json,datetime
urls={'lcsc':'https://www.lcsc.com/product-detail/C265343.html','jlcpcb':'https://jlcpcb.com/partdetail/JST-SM14B_GHS_TB_LF_SN/C265343'}
result={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
for name,url in urls.items():
 s=urllib.request.urlopen(url).read().decode().replace('\\"','"')
 fields=('stockNumber','stockSz') if name=='lcsc' else ('overseasStockCount','canPresaleNumber','preMinPurchaseNum')
 result[name]={'url':url,**{key:sorted(set(map(int,re.findall('"'+key+'":(\\d+)',s)))) for key in fields}}
print(json.dumps(result,indent=2))
