"""Extract exact primary NSE IndAS quarterly facts, without merging accounting scopes."""
import concurrent.futures,hashlib,json,re
from datetime import date,datetime,timezone,timedelta
from decimal import Decimal
from pathlib import Path
from urllib.request import Request,urlopen
from bs4 import BeautifulSoup
HERE=Path(__file__).parent;ROOT=HERE/'data/fundamentals'
def clean(s):return ' '.join(s.split()).casefold()
def number(s):
    s=s.strip().replace(',','')
    if not s or s in ('-','NA','N/A'):return None
    if s.startswith('(') and s.endswith(')'):s='-'+s[1:-1]
    v=Decimal(s)
    if not v.is_finite():raise ValueError('Nonfinite financial number')
    return v

def parse(raw,filing_date,symbol='MAZDOCK'):
    soup=BeautifulSoup(raw,'html.parser');tables=[];metadata={}
    for table in soup.find_all('table'):
        rows=[[c.get_text(' ',strip=True) for c in r.find_all(['th','td'],recursive=False)] for r in table.find_all('tr')]
        tables.append(rows)
        for r in rows:
            if len(r)==2:metadata[clean(r[0])]=r[1]
    currency=metadata.get('description of presentation currency')
    if metadata.get('nse symbol')!=symbol or currency not in ('INR','INR (in Actuals)'):raise ValueError('Wrong company/currency')
    unit=metadata.get('level of rounding used in financial results')
    if currency=='INR (in Actuals)' and not unit:unit='INR actuals';divisor=Decimal('10000000')
    elif currency=='INR' and clean(unit or '')=='lakhs':divisor=Decimal('100')
    else:raise ValueError('Unexpected financial units')
    candidates=[rows for rows in tables if any(len(r)>=4 and clean(r[1])=='revenue from operations' and number(r[2]) is not None for r in rows) and any(len(r)>=3 and clean(r[1])=='total profit (loss) for period' for r in rows)]
    if len(candidates)!=1:raise ValueError('Ambiguous financial statement table')
    rows=candidates[0]
    def get(label,column=2):
        values=[r[column] for r in rows if len(r)>column and clean(r[1])==clean(label)]
        if len(values)!=1:raise ValueError('Missing or ambiguous financial fact: '+label)
        return values[0]
    def parsed_date(value):
        for fmt in ('%d-%m-%Y','%d-%b-%Y'):
            try:return datetime.strptime(value,fmt).date()
            except ValueError:pass
        raise ValueError('Unsupported financial period date')
    def converted(label,column=2):
        value=number(get(label,column));return str(value/divisor) if value is not None else None
    start=parsed_date(get('Date of start of reporting period'));end=parsed_date(get('Date of end of reporting period'))
    if not 88<=(end-start).days<=92 or start.day!=1 or start.month not in (1,4,7,10):raise ValueError('Statement is not a standalone three-month quarter')
    scope=get('Nature of report standalone or consolidated')
    if scope!='Consolidated':raise ValueError('Unexpected accounting scope')
    if end>date.fromisoformat(filing_date):raise ValueError('Future financial period')
    revenue=number(get('Revenue from operations'));pat=number(get('Total profit (loss) for period'))
    if revenue is None or pat is None:raise ValueError('Missing revenue or total period PAT')
    fiscal_start=metadata.get('date of start of financial year')
    fiscal_start=parsed_date(fiscal_start).isoformat() if fiscal_start else None
    return {'symbol':symbol,'isin':metadata.get('isin'),'financial_year_start':fiscal_start,'period_start':start.isoformat(),'period_end':end.isoformat(),'filing_date':filing_date,'scope':scope,'audit_status':get('Whether results are audited or unaudited'),'source_unit':unit,'display_unit':'INR crore','revenue_operations_crore':str(revenue/divisor),'pat_total_period_crore':str(pat/divisor),'ytd_revenue_operations_crore':converted('Revenue from operations',3),'ytd_pat_total_period_crore':converted('Total profit (loss) for period',3),'pat_definition':'Total profit/loss for period, including equity-accounted associates/JVs where reported; not assumed to be owners-of-parent attributable PAT.','notes':'Exact reported quarter column; YTD/annual columns and other income are not used as quarterly sales. No forecast or quarterly growth rate inferred.'}

def trailing_four(facts,asof):
    eligible=sorted([f for f in facts if f['filing_date']<=asof],key=lambda f:f['period_end'])[-4:]
    if len(eligible)!=4:return None
    if len({(f['symbol'],f['isin'],f['scope'],f['display_unit']) for f in eligible})!=1:raise ValueError('Incompatible TTM scope or identity')
    for left,right in zip(eligible,eligible[1:]):
        if date.fromisoformat(left['period_end'])+timedelta(days=1)!=date.fromisoformat(right['period_start']):raise ValueError('Noncontiguous or duplicate TTM quarters')
    return {'period_start':eligible[0]['period_start'],'period_end':eligible[-1]['period_end'],'available_on':max(f['filing_date'] for f in eligible),'scope':eligible[0]['scope'],'revenue_operations_crore':str(sum(Decimal(f['revenue_operations_crore']) for f in eligible)),'pat_total_period_crore':str(sum(Decimal(f['pat_total_period_crore']) for f in eligible)),'quarters':[f['period_end'] for f in eligible],'growth_yoy':None,'growth_note':'Prior matching four quarters have not yet been collected.'}

def fetch(source,symbol='MAZDOCK'):
    filing_date,url=source;record={'source_url':url,'filing_date':filing_date,'retrieved_utc':datetime.now(timezone.utc).isoformat()}
    try:
        with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as response:raw=response.read(8_000_001)
        if len(raw)>8_000_000:raise ValueError('Oversize financial filing')
        sha=hashlib.sha256(raw).hexdigest();(ROOT/'raw'/(sha+'.html')).write_bytes(raw);record['sha256']=sha
        record.update(fact=parse(raw,filing_date,symbol),status='parsed_pending_review')
    except Exception as e:record.update(status='fetch_or_validation_failed',error=str(e))
    return record

def main(symbol='MAZDOCK'):
    (ROOT/'raw').mkdir(parents=True,exist_ok=True)
    catalogue=json.loads((ROOT/'source-catalogue.json').read_text(encoding='utf-8'))
    sources=[(r['filing_date'],r['source_url']) for r in catalogue[symbol]]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(lambda source:fetch(source,symbol),sources))
    facts=[r['fact'] for r in records if r.get('fact')]
    try:ttm=trailing_four(facts,'2026-10-28');ttm_error=None
    except ValueError as exc:ttm=None;ttm_error=str(exc)
    out={'symbol':symbol,'publication_ready':False,'sources':records,'ttm':ttm,'ttm_unavailable_reason':ttm_error,'note':'Primary financial-fact pilot. Accounting/date/unit review and source verification required before publication. Missing prior-year quarters, ROCE and valuation remain unavailable.'}
    (ROOT/(symbol.lower()+'.json')).write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({'records':[{k:r.get(k) for k in ('filing_date','status','error')} for r in records],'ttm':out['ttm']}))
if __name__=='__main__':
    import sys
    main(*sys.argv[1:])
