"""Resume a bounded monthly NIFTY snapshot backfill and exact latest-period anchors."""
import argparse
import calendar
import json
import time
import urllib.error
import urllib.request
from datetime import date,timedelta
from pathlib import Path
import pipeline as p

def shift(d,months):
    n=d.year*12+d.month-1+months;y,m=divmod(n,12);m+=1
    return date(y,m,min(d.day,calendar.monthrange(y,m)[1]))

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--years',type=int,default=5)
    a=parser.parse_args()
    if not 1<=a.years<=10:raise ValueError('Years must be 1–10')
    root=Path(__file__).parent/'data';db=p.connect(root)
    latest=date.fromisoformat(db.execute('select max(date) from observations').fetchone()[0])
    targets={shift(latest,-months) for months in [1,3,6,12,24,36,60] if months<=a.years*12}
    for i in range(a.years*12+1):
        month=shift(latest.replace(day=1),-i)
        target=date(month.year,month.month,calendar.monthrange(month.year,month.month)[1])
        if target<=latest:targets.add(target)
    available={x[0] for x in db.execute('select distinct observation_date from batches')}
    status_path=root/'history-backfill.json'
    previous=json.loads(status_path.read_text()) if status_path.exists() else {}
    absent=set(previous.get('unavailable_files',[]));loaded=[];errors=[]
    for n,target in enumerate(sorted(targets),1):
        found=None
        for lag in range(8):
            d=target-timedelta(days=lag)
            if d.weekday()>4:continue
            if d.isoformat() in available:found=d.isoformat();break
            url=f'https://niftyindices.com/Daily_Snapshot/ind_close_all_{d:%d%m%Y}.csv'
            if url in absent:continue
            try:
                req=urllib.request.Request(url,headers={'User-Agent':'NiftyReportPipeline/1.0'})
                with urllib.request.urlopen(req,timeout=18) as response:
                    raw=response.read(10_000_001)
                if len(raw)>10_000_000:raise ValueError('File too large')
                item=p.ingest(db,root,raw,url);available.add(d.isoformat());loaded.append(item);found=d.isoformat();break
            except urllib.error.HTTPError as exc:
                if exc.code==404:absent.add(url)
                else:errors.append({'url':url,'error':str(exc)});break
            except Exception as exc:
                errors.append({'url':url,'error':str(exc)});break
            finally:time.sleep(.3)
        if not found:errors.append({'target':target.isoformat(),'error':'No verified snapshot within 7 days; not assumed to be a holiday'})
        status={'latest':latest.isoformat(),'completed_targets':n,'total_targets':len(targets),'loaded':loaded,'errors':errors,'unavailable_files':sorted(absent)}
        temp=status_path.with_suffix('.tmp');temp.write_text(json.dumps(status,indent=2));temp.replace(status_path)
        print(f'{n}/{len(targets)} target={target} source={found or "UNAVAILABLE"}',flush=True)
    db.close()
    print(json.dumps({'loaded_files':len(loaded),'errors':len(errors),'status_file':str(status_path)}),flush=True)

if __name__=='__main__':main()
