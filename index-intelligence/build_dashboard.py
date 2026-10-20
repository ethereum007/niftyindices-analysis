"""Generate a self-contained interactive dashboard from the audited local warehouse."""
import bisect
import json
import sqlite3
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

HERE=Path(__file__).parent

def build(db, root, out):
    db.row_factory=sqlite3.Row
    observations=[dict(r) for r in db.execute('SELECT * FROM observations ORDER BY date,name')]
    history={}
    for r in observations:
        history.setdefault(r['name'],[]).append(r)
    dates={name:[r['date'] for r in rows] for name,rows in history.items()}
    for r in observations:
        for label,days in [('1m',30),('3m',90),('1y',365)]:
            target=(date.fromisoformat(r['date'])-timedelta(days=days)).isoformat()
            i=bisect.bisect_right(dates[r['name']],target)-1
            base=history[r['name']][i] if i>=0 else None
            valid=base and (date.fromisoformat(target)-date.fromisoformat(base['date'])).days<=7
            r['return_'+label]=(r['close']/base['close']-1)*100 if valid else None
            r['base_'+label]=base['date'] if valid else None
    payload={'observations':observations,'dates':sorted({r['date'] for r in observations}),
             'batches':[dict(r) for r in db.execute('SELECT * FROM batches ORDER BY observation_date')],
             'generated':datetime.now(timezone.utc).isoformat()}
    encoded=json.dumps(payload,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    page=(HERE/'dashboard.html').read_text(encoding='utf-8').replace('__WAREHOUSE_DATA__',encoded)
    out.mkdir(parents=True,exist_ok=True)
    temp=out/'dashboard.tmp';temp.write_text(page,encoding='utf-8');temp.replace(out/'dashboard.html')
    if root.resolve()==(HERE.parent/'nifty-automation/data').resolve():
        dist=HERE/'dist';dist.mkdir(exist_ok=True)
        temp=dist/'index.tmp';temp.write_text(page,encoding='utf-8');temp.replace(dist/'index.html')
    return out/'dashboard.html'

if __name__=='__main__':
    root=HERE.parent/'nifty-automation/data'
    with sqlite3.connect(root/'warehouse.sqlite') as db:
        print(build(db,root,root/'reports'))
