"""Compare vendor split-adjusted cash distributions with official NSE event records.
This does not certify missing exchange actions, historical ISIN continuity or spin-off methodology.
"""
import concurrent.futures,hashlib,json,re
from datetime import datetime,timezone
from urllib.request import Request,urlopen
from fetch_stock_history import HERE,ROOT

def day(s):return datetime.strptime(s,'%d-%b-%Y').date().isoformat()
def normalize(rows,symbol):
    events=[];ignored=[];unknown=[]
    for r in rows:
        if r.get('symbol')!=symbol or r.get('series')!='EQ':raise ValueError('Wrong exchange symbol/series')
        d=day(r['exDate']);s=r['subject'];low=s.lower()
        if 'split' in low:
            m=re.search(r'from rs\.?\s*([0-9.]+).*to rs\.?\s*([0-9.]+)',low)
            if not m:unknown.append(r);continue
            events.append({'date':d,'type':'split','share_multiplier':float(m[1])/float(m[2]),'subject':s})
        elif 'bonus' in low:
            m=re.search(r'(\d+)\s*:\s*(\d+)',low)
            if not m:unknown.append(r);continue
            events.append({'date':d,'type':'bonus','share_multiplier':1+float(m[1])/float(m[2]),'subject':s})
        elif 'dividend' in low:
            m=re.search(r'(?:rs\.?|re\.?)\s*([0-9.]+)',low)
            if not m:unknown.append(r);continue
            events.append({'date':d,'type':'dividend','cash_per_share':float(m[1]),'subject':s})
        elif 'annual general meeting' in low:ignored.append(r)
        else:unknown.append(r)
    return sorted(events,key=lambda r:(r['date'],r['type'])),ignored,unknown

def compare(events,vendor):
    splits={datetime.fromtimestamp(int(k),timezone.utc).date().isoformat():v for k,v in vendor.get('splits',{}).items()}
    divs={datetime.fromtimestamp(int(k),timezone.utc).date().isoformat():v for k,v in vendor.get('dividends',{}).items()}
    out=[];seen_s=set();seen_d=set()
    for e in events:
        d=e['date']
        if e['type'] in ('split','bonus'):
            v=splits.get(d);seen_s.add(d);actual=v['numerator']/v['denominator'] if v else None;expected=e['share_multiplier']
        else:
            v=divs.get(d);seen_d.add(d);actual=v.get('amount') if v else None
            factor=1
            for action in events:
                if action['date']>d and action['type'] in ('split','bonus'):factor*=action['share_multiplier']
            expected=e['cash_per_share']/factor
        out.append({**e,'expected_vendor_value':expected,'vendor_value':actual,'matched':actual is not None and abs(actual-expected)<=max(0.0001,abs(expected)*0.0001)})
    return {'comparisons':out,'unmatched_vendor_split_dates':sorted(set(splits)-seen_s),'unmatched_vendor_dividend_dates':sorted(set(divs)-seen_d)}

def adjustment_steps(rows,vendor):
    by_date={r['date']:i for i,r in enumerate(rows)};checks=[]
    for k,v in vendor.get('dividends',{}).items():
        d=datetime.fromtimestamp(int(k),timezone.utc).date().isoformat();i=by_date.get(d)
        if i is None or i==0:continue
        prev=rows[i-1];now=rows[i];expected=1-v['amount']/prev['vendor_close']
        actual=(prev['adjusted_close']/prev['vendor_close'])/(now['adjusted_close']/now['vendor_close'])
        checks.append({'date':d,'expected_backward_factor_step':expected,'observed_backward_factor_step':actual,'matched':abs(expected-actual)<=0.00005})
    return checks

def fetch(member):
    symbol=member['symbol'];url='https://www.nseindia.com/api/corporates-corporateActions?index=equities&symbol='+symbol+'&from_date=01-09-2021&to_date=27-10-2026'
    record={'symbol':symbol,'current_isin':member['isin'],'source_url':url,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'publication_ready':False}
    try:
        with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'}),timeout=25) as response:raw=response.read(4_000_001)
        if len(raw)>4_000_000:raise ValueError('Oversize exchange action response')
        sha=hashlib.sha256(raw).hexdigest();(ROOT/'raw'/(sha+'.json')).write_bytes(raw);record['sha256']=sha
        rows=json.loads(raw)
        if not isinstance(rows,list):raise ValueError('Unexpected exchange response')
        events,ignored,unknown=normalize(rows,symbol)
        excluded=[e for e in events if not member['rows'][0]['date']<=e['date']<=member['rows'][-1]['date']]
        events=[e for e in events if member['rows'][0]['date']<=e['date']<=member['rows'][-1]['date']]
        record['outside_history_window_events']=excluded
        record['dividend_factor_steps']=adjustment_steps(member['rows'],member['events'])
        result=compare(events,member['events'])
        record.update(events=events,ignored_meeting_rows=len(ignored),unclassified_actions=unknown,exchange_isins=sorted({r['isin'] for r in rows if r.get('isin')}),**result)
        record['all_reported_events_match']=bool(events) and not unknown and all(r['matched'] for r in result['comparisons']) and not result['unmatched_vendor_split_dates'] and not result['unmatched_vendor_dividend_dates'] and all(c['matched'] for c in record['dividend_factor_steps'])
        record['status']='reported_actions_reconciled' if record['all_reported_events_match'] else 'manual_review_required'
        record['limitations']='Not a completeness certificate. No exchange rows does not prove no actions. ISIN continuity/listing history, rights/reorganizations and vendor price adjustment-factor behaviour still require review.'
    except Exception as e:record.update(status='fetch_or_validation_failed',error=str(e))
    return record

def main():
    history=json.loads((ROOT/'defence.json').read_text(encoding='utf-8'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(fetch,history['members']))
    out={'family':'defence','publication_ready':False,'reviewed_on':'2026-10-28','note':'NSE reported events compared with vendor split-normalised dividend amounts; not a historical-identity/action-completeness certificate. Corporate-action parsing never auto-publishes history.','members':records}
    (ROOT/'defence-action-review.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(json.dumps({r['symbol']:{'status':r['status'],'events':len(r.get('events',[])),'mismatches':[x['date'] for x in r.get('comparisons',[]) if not x['matched']],'unknown':len(r.get('unclassified_actions',[]))} for r in records}))
if __name__=='__main__':main()
