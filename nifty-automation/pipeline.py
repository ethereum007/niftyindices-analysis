"""Download published NIFTY daily snapshots, archive, validate and report. Python 3.10+."""
import argparse
import csv
import hashlib
import html
import io
import json
import math
import re
import sqlite3
import time
import urllib.request
import urllib.error
from datetime import date, datetime, timezone, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

PAGE = 'https://niftyindices.com/reports/daily-reports'
FIELDS = ['name', 'date', 'open', 'high', 'low', 'close', 'change_pct', 'pe', 'pb', 'yield_pct']
ALIASES = {'indexname':'name', 'indexdate':'date', 'date':'date', 'openindexvalue':'open',
           'highindexvalue':'high', 'lowindexvalue':'low', 'closingindexvalue':'close',
           'open':'open', 'high':'high', 'low':'low', 'close':'close', 'change':'change_pct',
           'pe':'pe', 'pb':'pb', 'divyield':'yield_pct', 'dividendyield':'yield_pct'}

def key(s):
    return re.sub('[^a-z0-9]', '', s.lower())

def safe_url(url):
    p = urlparse(url)
    if p.scheme != 'https' or p.hostname not in ('niftyindices.com', 'www.niftyindices.com') or p.username or p.password or p.port:
        raise ValueError('Only official HTTPS NIFTY report URLs are supported')
    return url

class Redirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        safe_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def fetch(url):
    safe_url(url)
    opener = urllib.request.build_opener(Redirect())
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'NiftyReportPipeline/1.0', 'Accept':'text/html,text/csv,*/*'})
            with opener.open(req, timeout=25) as response:
                data = response.read(10_000_001)
                if len(data) > 10_000_000:
                    raise ValueError('Report exceeds size limit')
                return data
        except urllib.error.HTTPError as exc:
            if exc.code != 429 and 400 <= exc.code < 500:
                raise
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
        except (OSError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.urls = set()
    def handle_starttag(self, tag, attrs):
        href = dict(attrs).get('href', '')
        if tag == 'a' and re.search(r'/Daily_Snapshot/ind_close_all_\d{8}\.csv$', href, re.I):
            self.urls.add(safe_url(urljoin(PAGE, href)))

def parse(raw):
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    if not reader.fieldnames:
        raise ValueError('Empty CSV')
    mapping = {h: ALIASES.get(key(h)) for h in reader.fieldnames}
    if not {'name','date','close'}.issubset(set(mapping.values())):
        raise ValueError('Unexpected CSV format; required index name, date and close missing')
    rows, seen = [], set()
    for number, source in enumerate(reader, 2):
        if not any(source.values()):
            continue
        row = {mapping[h]: v.strip() for h,v in source.items() if mapping.get(h) and v is not None}
        try:
            for fmt in ('%d-%m-%Y', '%d-%b-%Y', '%Y-%m-%d', '%d %b %Y'):
                try:
                    row['date'] = datetime.strptime(row['date'], fmt).date().isoformat(); break
                except ValueError:
                    pass
            else:
                raise ValueError('Invalid date')
            if date.fromisoformat(row['date']) > datetime.now(timezone.utc).date():
                raise ValueError('Future observation')
            if not row['name'] or (row['name'],row['date']) in seen:
                raise ValueError('Empty or duplicate index')
            seen.add((row['name'],row['date']))
            for field in FIELDS[2:]:
                value = row.get(field, '').replace(',', '').replace('%','')
                row[field] = None if value.upper() in ('','-','--','NA','N/A') else float(value)
                if row[field] is not None and (not math.isfinite(row[field]) or (field != 'change_pct' and row[field] < 0)):
                    raise ValueError('Invalid numeric value: '+field)
            zero_dividend_points = key(row['name']) == 'nifty50dividendpoints' and row['close'] == 0
            if row['close'] is None or (row['close'] <= 0 and not zero_dividend_points):
                raise ValueError('Close must be positive')
            if row['high'] is not None and row['low'] is not None and row['high'] < row['low']:
                raise ValueError('High below low')
            rows.append(row)
        except (ValueError, KeyError) as exc:
            raise ValueError(f'Row {number}: {exc}') from exc
    if not rows or len({r['date'] for r in rows}) != 1:
        raise ValueError('Snapshot must contain one observation date and at least one row')
    return rows

def connect(root):
    db = sqlite3.connect(root/'warehouse.sqlite', timeout=30)
    db.executescript('''PRAGMA journal_mode=WAL;
    CREATE TABLE IF NOT EXISTS batches(sha TEXT PRIMARY KEY, source TEXT, retrieved TEXT, observation_date TEXT, rows INTEGER);
    CREATE TABLE IF NOT EXISTS observations(name TEXT, date TEXT, open REAL, high REAL, low REAL, close REAL, change_pct REAL, pe REAL, pb REAL, yield_pct REAL, sha TEXT, PRIMARY KEY(name,date));''')
    return db

def ingest(db, root, raw, source):
    digest = hashlib.sha256(raw).hexdigest()
    archive = root/'raw'/f'{digest}.csv'; archive.parent.mkdir(exist_ok=True)
    if not archive.exists():
        archive.write_bytes(raw)
    rows = parse(raw)  # Whole-file validation before database mutation.
    dated = re.search(r'ind_close_all_(\d{8})\.csv$', source, re.I)
    if dated and datetime.strptime(dated.group(1),'%d%m%Y').date().isoformat() != rows[0]['date']:
        raise ValueError('Snapshot observation date does not match its source filename')
    with db:
        if db.execute('SELECT 1 FROM batches WHERE sha=?',(digest,)).fetchone():
            return {'status':'unchanged','rows':len(rows),'date':rows[0]['date'],'sha':digest}
        db.execute('INSERT INTO batches VALUES(?,?,?,?,?)',(digest,source,datetime.now(timezone.utc).isoformat(),rows[0]['date'],len(rows)))
        db.executemany('INSERT OR REPLACE INTO observations VALUES('+','.join('?' for _ in range(11))+')',
                       [tuple(row.get(f) for f in FIELDS)+(digest,) for row in rows])
    return {'status':'loaded','rows':len(rows),'date':rows[0]['date'],'sha':digest}

def report(db, root):
    latest = db.execute('SELECT max(date) FROM observations').fetchone()[0]
    if not latest:
        raise ValueError('No stored observations')
    db.row_factory = sqlite3.Row
    rows = [dict(r) for r in db.execute('SELECT * FROM observations WHERE date=? ORDER BY change_pct DESC, name',(latest,))]
    for row in rows:
        for label, days in [('1m',30),('3m',90),('1y',365)]:
            target = (date.fromisoformat(latest)-timedelta(days=days)).isoformat()
            base = db.execute('SELECT date,close FROM observations WHERE name=? AND date<=? ORDER BY date DESC LIMIT 1',(row['name'],target)).fetchone()
            valid = base and base['close'] > 0 and (date.fromisoformat(target)-date.fromisoformat(base['date'])).days <= 7
            row['return_'+label] = (row['close']/base['close']-1)*100 if valid else None
            row['base_'+label] = base['date'] if valid else None
    out = root/'reports'; out.mkdir(exist_ok=True)
    payload = {'as_of':latest,'generated_utc':datetime.now(timezone.utc).isoformat(),'basis':'PRICE index; not TRI',
               'method':'1m/3m/1y: 30/90/365 calendar days, last available base on/before target within 7 days. Missing history stays blank.',
               'indices':rows}
    (out/'latest.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    with (out/'latest.csv').open('w',newline='',encoding='utf-8-sig') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    def cell(value):
        return '—' if value is None else f'{value:,.2f}' if isinstance(value,float) else html.escape(str(value))
    cols=['name','close','change_pct','return_1m','return_3m','return_1y','pe','pb','yield_pct']
    headers=['Index','Close','Daily %','1M %','3M %','1Y %','P/E','P/B','Dividend yield %']
    body=''.join('<tr>'+''.join('<td>'+cell(r.get(c))+'</td>' for c in cols)+'</tr>' for r in rows)
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NIFTY index monitor</title>
    <style>body{font:15px system-ui;margin:40px;color:#152c3c;background:#f5f6f4}h1{font-size:34px}table{border-collapse:collapse;width:100%;background:white}th,td{padding:12px;border-bottom:1px solid #ddd;text-align:right}th:first-child,td:first-child{text-align:left}th{background:#173c45;color:white}.scroll{overflow:auto}p{max-width:1000px;line-height:1.6}</style>'''
    page+=f'<h1>NIFTY index monitor</h1><p><b>Data through {latest} · {len(rows)} indices · Price returns</b><br>Generated {payload["generated_utc"]}. This is the latest stored snapshot; it is not a live quote. Compare its date with your required market session.</p>'
    page+='<p>'+html.escape(payload['method'])+' Daily changes are supplied by the source. India VIX measures implied volatility and is not an investment return; cross-index rankings mix different index types. Valuations are snapshots; unavailable values remain blank. Source: <a href="'+PAGE+'">NSE Indices daily reports</a>.</p>'
    page+='<div class="scroll"><table><thead><tr>'+''.join('<th>'+x+'</th>' for x in headers)+'</tr></thead><tbody>'+body+'</tbody></table></div></html>'
    (out/'latest.html').write_text(page,encoding='utf-8')
    (out/f'{latest}.html').write_text(page,encoding='utf-8')
    builder=Path(__file__).parent.parent/'index-intelligence/build_dashboard.py'
    if builder.exists():
        import importlib.util
        spec=importlib.util.spec_from_file_location('index_dashboard_builder',builder)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        module.build(db,root,out)
    return {'as_of':latest,'indices':len(rows),'report':str(out/'latest.html')}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path(__file__).parent/'data')
    p.add_argument('--file',type=Path,help='Import an already downloaded official daily snapshot')
    p.add_argument('--report-only',action='store_true')
    p.add_argument('--from-date',type=date.fromisoformat,help='Explicit dated public-file backfill start')
    p.add_argument('--to-date',type=date.fromisoformat)
    a=p.parse_args();a.root.mkdir(parents=True,exist_ok=True)
    db=connect(a.root); results=[]; errors=[]
    try:
        if a.file:
            results.append(ingest(db,a.root,a.file.read_bytes(),str(a.file.resolve())))
        elif not a.report_only:
            if a.from_date:
                end=a.to_date or datetime.now(timezone.utc).date()
                if end<a.from_date or (end-a.from_date).days>366:
                    raise ValueError('Backfill range must be 0–366 days')
                urls=[];day=a.from_date
                while day<=end:
                    if day.weekday()<5:
                        urls.append(f'https://niftyindices.com/Daily_Snapshot/ind_close_all_{day:%d%m%Y}.csv')
                    day+=timedelta(days=1)
            else:
                links=Links();links.feed(fetch(PAGE).decode('utf-8-sig'))
                urls=sorted(links.urls,key=lambda u:datetime.strptime(re.search(r'(\d{8})\.csv$',u).group(1),'%d%m%Y'))
                if not urls:
                    raise ValueError('No daily snapshot links found on official page')
            for url in urls:
                try:
                    results.append(ingest(db,a.root,fetch(url),url))
                except Exception as exc:
                    errors.append({'source':url,'error':str(exc)})
                time.sleep(1)
        if not a.file and not a.report_only:
            from backfill_history import run as refresh_anchors
            anchors=refresh_anchors(db,a.root,anchors_only=True)
            errors.extend(anchors['errors'])
        summary=report(db,a.root)
        status={'status':'partial' if errors else 'ok','imports':results,'errors':errors,**summary}
    except Exception as exc:
        status={'status':'failed','imports':results,'errors':errors+[{'error':str(exc)}]}
    finally:
        db.close()
    (a.root/'last-run.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
    print(json.dumps(status,indent=2))
    return 0 if status['status']=='ok' else 1

if __name__=='__main__':
    raise SystemExit(main())
