"""Generate a self-contained interactive dashboard from the audited local warehouse."""
import bisect
import json
import sqlite3
import calendar
import re
import csv
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

HERE=Path(__file__).parent
PERIODS={'mtd':None,'1m':1,'3m':3,'6m':6,'1y':12,'2y':24,'3y':36,'5y':60}

def shift_months(d,months):
    y,m=divmod(d.year*12+d.month-1+months,12);m+=1
    return date(y,m,min(d.day,calendar.monthrange(y,m)[1]))

def target_date(day,period):
    return day.replace(day=1)-timedelta(days=1) if period=='mtd' else shift_months(day,-PERIODS[period])

def identity(name):
    # Case and punctuation only. PR, TR, currency and leverage tokens remain distinct.
    return re.sub('[^a-z0-9]','',name.lower())

def prepare(observations):
    canonical={identity(r['name']):r['name'] for r in observations}
    seen=set()
    for r in observations:
        raw=r['name'];r['name']=canonical[identity(raw)]
        if raw!=r['name']:r['source_name']=raw
        row_key=(r['name'],r['date'])
        if row_key in seen:raise ValueError('Ambiguous same-date alias: '+str(row_key))
        seen.add(row_key)
    history={}
    for r in observations:history.setdefault(r['name'],[]).append(r)
    dates={n:[r['date'] for r in rows] for n,rows in history.items()}
    for r in observations:
        day=date.fromisoformat(r['date'])
        for label in PERIODS:
            target=target_date(day,label).isoformat()
            i=bisect.bisect_right(dates[r['name']],target)-1
            base=history[r['name']][i] if i>=0 else None
            valid=base and base['close']>0 and (date.fromisoformat(target)-date.fromisoformat(base['date'])).days<=7
            r['return_'+label]=(r['close']/base['close']-1)*100 if valid else None
            r['base_'+label]=base['date'] if valid else None
            if label in ('1y','2y','3y','5y'):
                elapsed=(day-date.fromisoformat(base['date'])).days if valid else 0
                r['cagr_'+label]=((r['close']/base['close'])**(365.2425/elapsed)-1)*100 if valid and elapsed>0 else None
    return observations

WIRE_FIELDS=['close','change_pct','open','high','low','pe','pb','yield_pct']

def pack_rows(observations):
    """Store repeated identifiers once; derived horizons are computed on selection."""
    names=sorted({r['name'] for r in observations})
    dates=sorted({r['date'] for r in observations})
    hashes=sorted({r['sha'] for r in observations})
    name_ids={v:i for i,v in enumerate(names)}
    date_ids={v:i for i,v in enumerate(dates)}
    hash_ids={v:i for i,v in enumerate(hashes)}
    rows=[[name_ids[r['name']],date_ids[r['date']],hash_ids[r['sha']]]+[r.get(k) for k in WIRE_FIELDS] for r in observations]
    return {'encoding':'indexed-v1','names':names,'dates':dates,'hashes':hashes,'fields':WIRE_FIELDS,'rows':rows}

def build(db, root, out):
    db.row_factory=sqlite3.Row
    observations=[dict(r) for r in db.execute('SELECT * FROM observations ORDER BY date,name')]
    observations=prepare(observations)
    coverage_file=root/'coverage-audit.json'
    coverage=json.loads(coverage_file.read_text(encoding='utf-8')) if coverage_file.exists() else None
    members_file=root/'constituents/latest.json'
    stocks_file=root/'stocks/latest.json'
    members=json.loads(members_file.read_text(encoding='utf-8')) if members_file.exists() else None
    stocks=json.loads(stocks_file.read_text(encoding='utf-8')) if stocks_file.exists() else None
    family_file=root/'theme-research/defence.json'
    family_members=json.loads(family_file.read_text(encoding='utf-8')) if family_file.exists() else None
    payload={**pack_rows(observations),'coverage':coverage,'constituents':members,'stocks':stocks,'family_members':family_members,'themes':json.loads((HERE/'themes.json').read_text(encoding='utf-8')),
             'batches':[dict(r) for r in db.execute('SELECT * FROM batches ORDER BY observation_date')],
             'generated':datetime.now(timezone.utc).isoformat(),
             'periods':list(PERIODS),'targets':{d:{k:target_date(date.fromisoformat(d),k).isoformat() for k in PERIODS} for d in sorted({r['date'] for r in observations})}}
    encoded=json.dumps(payload,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    page=(HERE/'dashboard.html').read_text(encoding='utf-8').replace('__WAREHOUSE_DATA__',encoded).replace('__THEME_SCRIPT__',(HERE/'themes.js').read_text(encoding='utf-8')+'\n'+(HERE/'theme-catalogue.js').read_text(encoding='utf-8'))
    out.mkdir(parents=True,exist_ok=True)
    latest=payload['dates'][-1]
    latest_rows=[r for r in observations if r['date']==latest]
    columns=['name','date','close','change_pct']+[field for k in PERIODS for field in ('return_'+k,'base_'+k)]+['cagr_'+k for k in ('1y','2y','3y','5y')]+['pe','pb','yield_pct','sha']
    for folder in (out,HERE/'dist') if root.resolve()==(HERE.parent/'nifty-automation/data').resolve() else (out,):
        folder.mkdir(parents=True,exist_ok=True)
        with (folder/'performance-latest.csv').open('w',newline='',encoding='utf-8-sig') as handle:
            writer=csv.DictWriter(handle,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(latest_rows)
    temp=out/'dashboard.tmp';temp.write_text(page,encoding='utf-8');temp.replace(out/'dashboard.html')
    if root.resolve()==(HERE.parent/'nifty-automation/data').resolve():
        dist=HERE/'dist';dist.mkdir(exist_ok=True)
        temp=dist/'index.tmp';temp.write_text(page,encoding='utf-8');temp.replace(dist/'index.html')
    return out/'dashboard.html'

if __name__=='__main__':
    root=HERE.parent/'nifty-automation/data'
    with sqlite3.connect(root/'warehouse.sqlite') as db:
        print(build(db,root,root/'reports'))
