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

def run(db,root,years=5,anchors_only=False):
    latest=date.fromisoformat(db.execute('select max(date) from observations').fetchone()[0])
    targets={shift(latest,-months) for months in [1,3,6,12,24,36,60] if months<=years*12}
    targets.add(latest.replace(day=1)-timedelta(days=1))
    for i in range(0 if anchors_only else years*12+1):
        month=shift(latest.replace(day=1),-i)
        target=date(month.year,month.month,calendar.monthrange(month.year,month.month)[1])
        if target<=latest:targets.add(target)
    available={x[0] for x in db.execute('select distinct observation_date from batches')}
    status_path=root/('history-anchors.json' if anchors_only else 'history-backfill.json')
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
                raw=p.fetch(url)
                if len(raw)>10_000_000:raise ValueError('File too large')
                item=p.ingest(db,root,raw,url);available.add(d.isoformat());loaded.append(item);found=d.isoformat();break
            except urllib.error.HTTPError as exc:
                if exc.code==404:absent.add(url)
                else:errors.append({'url':url,'error':str(exc)});break
            except ValueError as exc:
                if 'raw' in locals() and raw.lstrip().lower().startswith((b'<!doctype html',b'<html')):
                    absent.add(url)
                else:
                    errors.append({'url':url,'error':str(exc)});break
            except Exception as exc:
                errors.append({'url':url,'error':str(exc)});break
            finally:time.sleep(.3)
        if not found:errors.append({'target':target.isoformat(),'error':'No verified snapshot within 7 days; not assumed to be a holiday'})
        status={'latest':latest.isoformat(),'completed_targets':n,'total_targets':len(targets),'loaded':loaded,'errors':errors,'unavailable_files':sorted(absent)}
        temp=status_path.with_suffix('.tmp');temp.write_text(json.dumps(status,indent=2));temp.replace(status_path)
        print(f'{n}/{len(targets)} target={target} source={found or "UNAVAILABLE"}',flush=True)
    print(json.dumps({'loaded_files':len(loaded),'errors':len(errors),'status_file':str(status_path)}),flush=True)
    return status

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--years',type=int,default=5);parser.add_argument('--anchors-only',action='store_true')
    a=parser.parse_args()
    if not 1<=a.years<=10:raise ValueError('Years must be 1-10')
    root=Path(__file__).parent/'data';db=p.connect(root)
    try:run(db,root,a.years,a.anchors_only)
    finally:db.close()

if __name__=='__main__':main()
