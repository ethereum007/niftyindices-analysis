"""Reconcile unavailable weekday files against explicitly reviewed calendar evidence."""
import json
import sqlite3
from pathlib import Path

def reconcile(files, evidence, accepted):
    by_date={item['date']:item for item in evidence}
    if len(by_date)!=len(evidence):raise ValueError('Duplicate evidence date')
    overlap=set(by_date)&set(accepted)
    if overlap:raise ValueError('Closure evidence conflicts with accepted dates: '+', '.join(sorted(overlap)))
    gaps=[]
    for day,entry in sorted(files.items()):
        if entry['status']=='accepted':continue
        item=by_date.get(day)
        gaps.append({'date':day,'download_status':entry['status'],**(item or {'classification':'unexplained'})})
    return {'scope':'Unavailable weekday-file reconciliation; not a complete exchange session calendar',
            'recorded_gaps':len(gaps),'verified_closures':sum(x['classification']=='verified_exchange_closure' for x in gaps),
            'corroborated_closures':sum(x['classification']=='corroborated_exchange_closure' for x in gaps),
            'pending':sum(x['classification'] not in ('verified_exchange_closure','corroborated_exchange_closure') for x in gaps), 'dates':gaps}

def main():
    root=Path(__file__).parent
    files=json.loads((root/'data/daily-backfill.json').read_text(encoding='utf-8'))['files']
    evidence=json.loads((root/'calendar-evidence.json').read_text(encoding='utf-8'))['dates']
    with sqlite3.connect(root/'data/warehouse.sqlite') as db:accepted={r[0] for r in db.execute('select distinct date from observations')}
    result=reconcile(files,evidence,accepted)
    (root/'data/calendar-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='dates'}))
if __name__=='__main__':main()
