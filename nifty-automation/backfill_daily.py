"""Resume bounded weekday-file discovery. Missing files are not declared holidays."""
import argparse
import hashlib
import json
import time
import urllib.error
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import pipeline as p
from backfill_history import shift

def candidates(start, end):
    if start > end:
        raise ValueError('Start must not be after end')
    day = end
    while day >= start:
        if day.weekday() < 5:
            yield day
        day -= timedelta(days=1)

def run(root, start, end, max_requests=48, retry_unavailable=False, fetcher=None, delay=.5, session_dates=None):
    if not 1 <= max_requests <= 100:
        raise ValueError('Request budget must be 1–100')
    fetcher = fetcher or p.fetch
    root.mkdir(parents=True, exist_ok=True)
    ledger = root/('special-backfill.json' if session_dates is not None else 'daily-backfill.json')
    state = json.loads(ledger.read_text(encoding='utf-8')) if ledger.exists() else {'files': {}}
    dates = sorted({d for d in session_dates if start <= d <= end}, reverse=True) if session_dates is not None else list(candidates(start,end))
    db = p.connect(root)
    known = {r[0] for r in db.execute('SELECT DISTINCT date FROM observations')}
    attempted = loaded = 0
    stop_reason = None
    def save():
        state['range'] = {'from':start.isoformat(),'to':end.isoformat()}
        state['summary'] = {'attempted_this_run':attempted,'loaded_this_run':loaded,
            ('session_candidates' if session_dates is not None else 'weekday_candidates'):len(dates),'accepted_dates_in_range':sum(d.isoformat() in known for d in dates),
            'remaining_unchecked_or_retryable':sum(d.isoformat() not in known and state['files'].get(d.isoformat(),{}).get('status') not in ('source_unavailable','non_csv_response','rejected') for d in dates),
            'stop_reason':stop_reason,'weekend_sessions_audited':False,
            'note':'Weekday file discovery is not an exchange-calendar audit; absent files do not prove holidays.'}
        state['updated_utc'] = datetime.now(timezone.utc).isoformat()
        temp = ledger.with_suffix('.tmp');temp.write_text(json.dumps(state,indent=2),encoding='utf-8');temp.replace(ledger)
    try:
        for day in dates:
            key = day.isoformat()
            if key in known:
                continue
            previous = state['files'].get(key,{})
            if not retry_unavailable and previous.get('status') in ('source_unavailable','non_csv_response','rejected'):
                continue
            if attempted >= max_requests:
                break
            attempted += 1
            url = f'https://niftyindices.com/Daily_Snapshot/ind_close_all_{day:%d%m%Y}.csv'
            entry = {'url':url,'attempted_utc':datetime.now(timezone.utc).isoformat(),
                     'attempts':previous.get('attempts',0)+1}
            raw = None
            try:
                raw = fetcher(url)
                entry['sha256'] = hashlib.sha256(raw).hexdigest()
                result = p.ingest(db,root,raw,url)
                entry.update(status='accepted',rows=result['rows'])
                known.add(key);loaded += 1
            except urllib.error.HTTPError as exc:
                entry.update(status='source_unavailable' if exc.code == 404 else 'request_failed',http_status=exc.code,error=str(exc))
                if exc.code in (401,403,429):
                    stop_reason = f'HTTP {exc.code}; stopped without bypass or further requests'
            except (ValueError, UnicodeError) as exc:
                non_csv = raw is not None and raw.lstrip().lower().startswith((b'<!doctype html',b'<html'))
                entry.update(status='non_csv_response' if non_csv else 'rejected',error=str(exc))
            except (OSError, TimeoutError) as exc:
                entry.update(status='request_failed',error=str(exc))
            state['files'][key] = entry
            save()
            print(f'{attempted}/{max_requests} {key}: {entry["status"]}',flush=True)
            if stop_reason:
                break
            if delay:
                time.sleep(delay)
        save()
        return state['summary']
    finally:
        db.close()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).parent/'data')
    parser.add_argument('--from-date',type=date.fromisoformat)
    parser.add_argument('--to-date',type=date.fromisoformat)
    parser.add_argument('--max-requests',type=int,default=48)
    parser.add_argument('--retry-unavailable',action='store_true')
    parser.add_argument('--sessions',type=Path,help='JSON manifest with explicit session dates; separate ledger')
    args=parser.parse_args()
    args.root.mkdir(parents=True,exist_ok=True)
    with p.connect(args.root) as db:
        latest=db.execute('SELECT max(date) FROM observations').fetchone()[0]
    if latest is None:
        raise SystemExit('First load a current snapshot with pipeline.py')
    end=args.to_date or date.fromisoformat(latest)
    start=args.from_date or shift(end,-60)
    sessions = [date.fromisoformat(s['date']) for s in json.loads(args.sessions.read_text(encoding='utf-8'))['sessions']] if args.sessions else None
    print(json.dumps(run(args.root,start,end,args.max_requests,args.retry_unavailable,session_dates=sessions),indent=2))

if __name__=='__main__':
    main()
