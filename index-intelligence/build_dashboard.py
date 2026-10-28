"""Generate a self-contained interactive dashboard from the audited local warehouse."""
import bisect
import json
import sqlite3
import calendar
import re
import csv
import hashlib
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

def load_family_members(root, enabled=None):
    """Reject ambiguous identities or changed primary evidence before publication."""
    result={}
    for file in sorted((root/'theme-research').glob('*.json')):
        if enabled is not None and file.stem not in enabled:continue
        data=json.loads(file.read_text(encoding='utf-8'))
        family=data['family']
        if family!=file.stem or family in result:raise ValueError('Ambiguous family manifest: '+str(file))
        symbols=set();isins=set()
        for member in data['members']:
            if member['symbol'] in symbols or member['isin'] in isins:raise ValueError('Duplicate family identity: '+family)
            symbols.add(member['symbol']);isins.add(member['isin'])
            if member['status']=='evidence_archived':
                sha=member['sha256']
                if not re.fullmatch('[0-9a-f]{64}',sha):raise ValueError('Invalid evidence hash')
                extension=member.get('raw_extension','html')
                if extension not in ('html','pdf'):raise ValueError('Unsupported evidence extension')
                raw=(file.parent/'raw'/(sha+'.'+extension)).read_bytes()
                if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('Changed primary evidence: '+family)
        result[family]=data
    if enabled is not None and set(enabled)-result.keys():raise ValueError('Missing enabled family manifest: '+', '.join(sorted(set(enabled)-result.keys())))
    return result

def load_reviewed_company_history(root):
    folder=root/'stock-history';out={}
    def verify(sha,extension):
        if not re.fullmatch('[0-9a-f]{64}',sha) or extension not in ('json','pdf'):raise ValueError('Invalid history evidence reference')
        raw=(folder/'raw'/(sha+'.'+extension)).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('Changed reviewed history evidence')
    for file in folder.glob('*-publication-review.json'):
        review=json.loads(file.read_text(encoding='utf-8'));family=review['family']
        history=json.loads((folder/(family+'.json')).read_text(encoding='utf-8'))
        actions=json.loads((folder/(family+'-action-review.json')).read_text(encoding='utf-8'))
        for item in review['reviews']:
            if item['status']!='reviewed_vendor_methodology':continue
            m=next(r for r in history['members'] if r['symbol']==item['symbol'])
            a=next(r for r in actions['members'] if r['symbol']==item['symbol'])
            if m['isin']!=item['isin'] or m['sha256']!=item['history_sha256'] or a['sha256']!=item['action_sha256']:raise ValueError('Stale company history review')
            if not m['crosscheck']['within_0_1_pct']:raise ValueError('Company history checks failed')
            verify(m['sha256'],'json');verify(a['sha256'],'json')
            for evidence in item['identity_evidence']:verify(evidence['sha256'],evidence['extension'])
            if m['isin'] in out:raise ValueError('Duplicate reviewed stock history')
            # Decode the original vendor payload again; never trust edited derived rows.
            import sys
            sys.path.insert(0,str(HERE.parent/'nifty-automation'))
            from fetch_stock_history import decode
            rows,_=decode(json.loads((folder/'raw'/(m['sha256']+'.json')).read_text()),m['symbol'])
            from review_stock_actions import reconstruct_action_review
            decisions=[]
            if item.get('event_dispositions_sha256'):
                decision_raw=(folder/'event-dispositions.json').read_bytes()
                if hashlib.sha256(decision_raw).hexdigest()!=item['event_dispositions_sha256']:raise ValueError('Changed reviewed event decisions')
                decisions=json.loads(decision_raw)['decisions']
            reconstructed=reconstruct_action_review(m,a,folder,decisions)
            if not reconstructed['all_reported_events_match']:raise ValueError('Original company action checks failed')

            out[m['isin']]={'symbol':m['symbol'],'family':family,'rows':rows,'method':review['method'],'review':item,'source_url':m['source_url'],'asof':history['asof']}
    return out

def load_reviewed_financials(root):
    folder=root/'fundamentals';out={}
    import sys
    sys.path.insert(0,str(HERE.parent/'nifty-automation'))
    from fetch_primary_financials import parse
    for file in folder.glob('*-publication-review.json'):
        review=json.loads(file.read_text(encoding='utf-8'))
        if review['status']!='reviewed_with_field_restrictions':continue
        facts=[]
        for source in review['source_hashes']:
            sha=source['sha256']
            if not re.fullmatch('[0-9a-f]{64}',sha):raise ValueError('Invalid financial evidence hash')
            kind=source.get('format','nse_indas_html')
            if kind not in ('nse_indas_html','dynamatic_june2026_pdf'):raise ValueError('Unsupported reviewed financial source format')
            raw=(folder/'raw'/(sha+('.pdf' if kind=='dynamatic_june2026_pdf' else '.html'))).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('Changed reviewed financial evidence')
            if kind=='dynamatic_june2026_pdf':
                from parse_primary_pdf import parse_dynamatic_june2026
                fact=parse_dynamatic_june2026(raw,source['filing_date'],review['symbol'])
            else:fact=parse(raw,source['filing_date'],review['symbol'])
            if fact['symbol']!=review['symbol'] or fact['isin']!=review['isin']:raise ValueError('Financial review identity mismatch')
            fact.update(source_url=source['source_url'],sha256=sha)
            for blocked in review['blocked_fields']:
                if blocked['period_end']==fact['period_end']:fact[blocked['metric']]=None
            facts.append(fact)
        out[review['isin']]={'symbol':review['symbol'],'facts':facts,'review':review}
    return out

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
    theme_data=json.loads((HERE/'themes.json').read_text(encoding='utf-8'))
    enabled={f['id'] for f in theme_data['catalogue']['families'] if f.get('company_data_ready') is True}
    family_members=load_family_members(root,enabled)
    payload={**pack_rows(observations),'coverage':coverage,'constituents':members,'stocks':stocks,'family_members':family_members,'company_history':load_reviewed_company_history(root),'company_financials':load_reviewed_financials(root),'themes':theme_data,
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
