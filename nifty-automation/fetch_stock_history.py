"""Archive vendor-adjusted company history for review, never infer historical theme membership.

Yahoo adjusted close includes split/dividend treatment. We never apply a second
split factor. Rights, demergers, symbol changes and vendor actions require review
before publication. The raw vendor payload remains the source of truth.
"""
import bisect,calendar,concurrent.futures,hashlib,json,math
from datetime import date,datetime,timezone,timedelta
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from zoneinfo import ZoneInfo
HERE=Path(__file__).parent
ROOT=HERE/'data/stock-history'
PERIODS={'mtd':0,'3m':3,'6m':6,'1y':12,'2y':24,'3y':36,'5y':60}
def target(day,period):
    if period=='mtd':return day.replace(day=1)-timedelta(days=1)
    y,m=divmod(day.year*12+day.month-1-PERIODS[period],12);m+=1
    return date(y,m,min(day.day,calendar.monthrange(y,m)[1]))
def finite_positive(x):return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) and x>0
def decode(payload,symbol):
    result=payload.get('chart',{}).get('result')
    if not result or payload['chart'].get('error'):raise ValueError('Vendor history unavailable')
    r=result[0];meta=r['meta']
    if meta.get('symbol')!=symbol+'.NS' or meta.get('currency')!='INR' or meta.get('exchangeName') not in ('NSI','NSE'):raise ValueError('Unexpected vendor identity or market')
    stamps=r['timestamp'];quote=r['indicators']['quote'][0];adj=r['indicators']['adjclose'][0]['adjclose']
    if len(stamps)!=len(quote['close']) or len(stamps)!=len(adj):raise ValueError('History array length mismatch')
    rows=[];previous=None
    for stamp,close,adjusted in zip(stamps,quote['close'],adj):
        day=datetime.fromtimestamp(stamp,ZoneInfo('Asia/Kolkata')).date().isoformat()
        if previous and day<=previous:raise ValueError('Duplicate or unsorted trading dates')
        previous=day
        if close is None and adjusted is None:continue
        if not finite_positive(close) or not finite_positive(adjusted):raise ValueError('Invalid close or adjusted close')
        rows.append({'date':day,'vendor_close':close,'adjusted_close':adjusted})
    if not rows:raise ValueError('Empty history')
    return rows,r.get('events',{})
def horizons(rows,asof):
    dates=[r['date'] for r in rows];i=bisect.bisect_right(dates,asof.isoformat())-1
    if i<0 or (asof-date.fromisoformat(dates[i])).days>7:return {'status':'end_price_unavailable','periods':{}}
    end=rows[i];day=date.fromisoformat(end['date']);out={}
    for period in PERIODS:
        wanted=target(day,period);j=bisect.bisect_right(dates,wanted.isoformat())-1
        valid=j>=0 and (wanted-date.fromisoformat(dates[j])).days<=7
        base=rows[j] if valid else None
        elapsed=(day-date.fromisoformat(base['date'])).days if valid else 0
        out[period]={'target_date':wanted.isoformat(),'base_date':base['date'] if valid else None,'end_date':end['date'],'cumulative_pct':100*(end['adjusted_close']/base['adjusted_close']-1) if valid else None,'cagr_pct':100*((end['adjusted_close']/base['adjusted_close'])**(365.2425/elapsed)-1) if valid and period in ('1y','2y','3y','5y') and elapsed>0 else None,'status':'vendor_adjusted_pending_action_review' if valid else 'insufficient_history'}
    return {'status':'vendor_adjusted_pending_action_review','requested_asof':asof.isoformat(),'end_date':end['date'],'periods':out}
def fetch(member,asof,snapshot):
    symbol=member['symbol'];start=date(asof.year-5,asof.month,1)-timedelta(days=15)
    params={'period1':int(datetime.combine(start,datetime.min.time(),timezone.utc).timestamp()),'period2':int(datetime.combine(asof+timedelta(days=1),datetime.min.time(),timezone.utc).timestamp()),'interval':'1d','events':'div,splits','includeAdjustedClose':'true'}
    url='https://query1.finance.yahoo.com/v8/finance/chart/'+symbol+'.NS?'+urlencode(params)
    record={'symbol':symbol,'isin':member['isin'],'company':member['company'],'source_url':url,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'publication_ready':False,'identity_note':'Vendor ticker mapped from current official NSE ISIN/symbol identity; vendor does not supply ISIN. Historical identity and corporate actions require separate review.'}
    try:
        with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0 IndexIntelligence public history research'}),timeout=25) as response:raw=response.read(8_000_001)
        if len(raw)>8_000_000:raise ValueError('History exceeds bounded archive size')
        sha=hashlib.sha256(raw).hexdigest();(ROOT/'raw'/(sha+'.json')).write_bytes(raw);record['sha256']=sha
        rows,events=decode(json.loads(raw),symbol)
        if rows[-1]['date']>asof.isoformat():raise ValueError('Vendor returned future observations')
        match=next((r for r in rows if r['date']==snapshot['date']),None);official=snapshot['prices'].get(member['isin'])
        difference=(match['vendor_close']/official['close']-1)*100 if match and official and official['symbol']==symbol else None
        record.update(rows=rows,events=events,horizons=horizons(rows,asof),status='review_required',crosscheck={'date':snapshot['date'],'official_close':official['close'] if official else None,'vendor_close':match['vendor_close'] if match else None,'difference_pct':difference,'within_0_1_pct':difference is not None and abs(difference)<=0.1},action_review='Pending independent split/dividend/rights/demerger and historical-symbol review. Adjusted returns are vendor methodology, not official index or custom basket returns.')
    except Exception as e:record.update(status='fetch_or_validation_failed',error=str(e))
    return record
def main(family='defence',asof=None):
    asof=date.fromisoformat(asof) if asof else date(2026,10,27)
    (ROOT/'raw').mkdir(parents=True,exist_ok=True)
    members=json.loads((HERE/'data/theme-research'/(family+'.json')).read_text(encoding='utf-8'))['members'];snapshot=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(lambda m:fetch(m,asof,snapshot),members))
    out={'family':family,'asof':asof.isoformat(),'publication_ready':False,'adjustment_methodology_source':'https://in.help.yahoo.com/kb/finance/adjusted-close-sln28256.html','note':'Research only: vendor split/dividend-adjusted company returns; no custom basket history, weights or historical membership inferred. Corporate-action and historical-identity review required. End date and actual baseline dates are explicit.','members':records}
    (ROOT/(family+'.json')).write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({r['symbol']:{'status':r['status'],'rows':len(r.get('rows',[])),'crosscheck':r.get('crosscheck',{}).get('within_0_1_pct')} for r in records}))
if __name__=='__main__':
    import sys
    main(*sys.argv[1:])
