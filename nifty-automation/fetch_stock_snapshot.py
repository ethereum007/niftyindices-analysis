"""Archive and validate an official NSE cash-market closing-price snapshot."""
import math
import argparse,csv,hashlib,io,json,urllib.request,zipfile
from pathlib import Path
from datetime import date,datetime,timezone

def parse(raw,day):
 z=zipfile.ZipFile(io.BytesIO(raw))
 files=[n for n in z.namelist() if n.endswith('.csv')]
 if len(files)!=1 or z.getinfo(files[0]).file_size>30_000_000:raise ValueError('Unexpected archive')
 rows=list(csv.DictReader(io.StringIO(z.read(files[0]).decode('utf-8-sig'))));result={}
 for r in rows:
  if r['TradDt']!=str(day) or r['BizDt']!=str(day):raise ValueError('Stock snapshot date mismatch')
  if r['SctySrs']!='EQ':continue
  close=float(r['ClsPric']);previous=float(r['PrvsClsgPric'])
  if not math.isfinite(close) or not math.isfinite(previous) or close<=0 or previous<0:raise ValueError('Invalid closing price')
  key=r['ISIN']
  if key in result:raise ValueError('Duplicate equity ISIN')
  result[key]={'symbol':r['TckrSymb'],'close':close,'previous_close':previous,'change_pct':(close/previous-1)*100 if previous>0 else None}
 if not result:raise ValueError('No equity prices')
 return result

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--date',type=date.fromisoformat,required=True);args=parser.parse_args()
 url=f'https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{args.date:%Y%m%d}_F_0000.csv.zip'
 raw=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'IndexIntelligence/1.0'}),timeout=25).read(15_000_001)
 if len(raw)>15_000_000:raise ValueError('Stock archive too large')
 root=Path(__file__).parent/'data/stocks';(root/'raw').mkdir(parents=True,exist_ok=True)
 sha=hashlib.sha256(raw).hexdigest();(root/'raw'/(sha+'.zip')).write_bytes(raw)
 prices=parse(raw,args.date)
 result={'date':str(args.date),'source_url':url,'sha256':sha,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'note':'Unadjusted official closes versus previous close; corporate actions may affect price changes. These are stock moves, not weighted index contributions.','prices':prices}
 (root/'latest.json').write_text(json.dumps(result,separators=(',',':')),encoding='utf-8');print(len(prices),'equity prices',args.date)
if __name__=='__main__':main()
