"""Summarize calendar-date file discovery without equating missing files to holidays."""
import json
import sqlite3
from datetime import date,timedelta
from pathlib import Path

def summarize(start,end,accepted,files):
    if start>end:raise ValueError('Invalid discovery range')
    days=[];day=start
    while day<=end:
        days.append(str(day));day+=timedelta(days=1)
    accepted=set(accepted)
    terminal={'source_unavailable','non_csv_response','rejected'}
    missing=[d for d in days if d not in accepted and files.get(d,{}).get('status') not in terminal]
    unavailable=[{'date':d,'status':files[d]['status']} for d in days if d not in accepted and files.get(d,{}).get('status') in terminal]
    return {'from':str(start),'to':str(end),'calendar_dates':len(days),'accepted_dates':sum(d in accepted for d in days),
        'unavailable_dates':len(unavailable),'unchecked_or_retryable':len(missing),'source_file_discovery_complete':not missing,
        'exchange_calendar_completeness_certified':False,
        'note':'All-date file discovery does not certify exchange-calendar completeness or history for every index. No unavailable values are filled.',
        'unchecked_dates':missing,'unavailable_files':unavailable}

def main():
    root=Path(__file__).parent/'data';files={}
    for name in ('daily-backfill.json','special-backfill.json'):
        files.update(json.loads((root/name).read_text(encoding='utf-8'))['files'])
    with sqlite3.connect(root/'warehouse.sqlite') as db:
        accepted={r[0] for r in db.execute('select distinct date from observations')}
    result=summarize(date(2021,10,19),date(2026,10,19),accepted,files)
    (root/'coverage-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('unchecked_dates','unavailable_files')}))
if __name__=='__main__':main()
