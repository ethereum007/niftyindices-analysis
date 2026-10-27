"""Archive current published equity constituent lists with retrieval provenance."""
import csv,hashlib,io,json,re,time,sqlite3
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,urlparse,quote
import pipeline as p

BASE='https://niftyindices.com'
def identity(n):return re.sub('[^a-z0-9]','',n.lower().replace('index',''))
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.link=None;self.text=[]
 def handle_starttag(self,t,a):
  if t=='a':self.link=dict(a).get('href');self.text=[]
 def handle_data(self,d):
  if self.link:self.text.append(d)
 def handle_endtag(self,t):
  if t=='a' and self.link:self.links.append((urljoin(BASE,self.link),' '.join(''.join(self.text).split())));self.link=None

def parse_members(raw):
 rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
 if not rows or not {'Symbol','ISIN Code'}.issubset(rows[0]):raise ValueError('Unrecognized constituent schema')
 company='Company Name' if 'Company Name' in rows[0] else 'Company' if 'Company' in rows[0] else None
 if not company:raise ValueError('Missing company name column')
 members=[]
 for r in rows:
  isin=r['ISIN Code'].strip();symbol=r['Symbol'].strip();dummy=isin.startswith('DUM') or symbol.startswith('DUMMY')
  if not symbol or not r[company].strip() or (not re.fullmatch(r'IN[A-Z0-9]{10}',isin) and not dummy):raise ValueError('Invalid member identifiers')
  members.append({'company':r[company].strip(),'symbol':symbol,'industry':r.get('Industry','').strip(),'isin':isin,'is_placeholder':dummy})
 if len({r['symbol'] for r in members})!=len(members):raise ValueError('Duplicate symbols')
 return members

def run():
 root=Path(__file__).parent/'data/constituents';rawdir=root/'raw';rawdir.mkdir(parents=True,exist_ok=True)
 def archive(raw,suffix):
  sha=hashlib.sha256(raw).hexdigest();(rawdir/(sha+suffix)).write_bytes(raw);return sha
 def fetch_index(name,page):
  entry={'index':name,'page_url':page,'retrieved_utc':datetime.now(timezone.utc).isoformat()}
  try:
   raw=p.fetch(page);entry['page_sha256']=archive(raw,'.html');links=Links();links.feed(raw.decode('utf-8'))
   urls=sorted({u for u,t in links.links if '/indexconstituent/' in u.lower() and u.lower().endswith('.csv')})
   if len(urls)!=1:raise ValueError('No unique published constituent CSV')
   url=quote(urls[0],safe=':/%');raw=p.fetch(url);entry.update(source_url=url,sha256=archive(raw,'.csv'))
   members=parse_members(raw)
   entry.update(status='accepted',members=members,effective_date=None,note='Current published list retrieved on shown date; effective date not supplied. No historical membership or index weights inferred. Official dummy placeholders have no stock-price mapping.')
  except Exception as exc:entry.update(status='unavailable',error=str(exc))
  return entry
 with p.connect(Path(__file__).parent/'data') as db:
  names={identity(r[0]):r[0] for r in db.execute('select distinct name from observations')}
  if 'niftyoilgas' in names:names['niftyoilandgas']=names['niftyoilgas']
 landing=p.fetch(BASE+'/indices/equity/sectoral-indices/nifty-auto');archive(landing,'.html');links=Links();links.feed(landing.decode('utf-8'))
 pages={}
 for url,label in links.links:
  if '/indices/equity/' in url and identity(label) in names:pages[names[identity(label)]]=url
 manifest={'retrieved_utc':datetime.now(timezone.utc).isoformat(),'scope':'Current published membership; not historical constituents, weights or stock-price returns','indices':{}}
 dest=root/'latest.json'
 with ThreadPoolExecutor(max_workers=3) as pool:
  futures=[pool.submit(fetch_index,n,u) for n,u in pages.items()]
  for future in as_completed(futures):
   entry=future.result();manifest['indices'][identity(entry['index'])]=entry
   dest.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
   print(entry['index']+': '+entry['status'],flush=True)
 print('ACCEPTED',sum(v['status']=='accepted' for v in manifest['indices'].values()),'OF',len(pages))
if __name__=='__main__':run()
