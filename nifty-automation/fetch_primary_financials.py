"""Extract exact primary NSE IndAS quarterly facts, without merging accounting scopes."""
import concurrent.futures,hashlib,json,re
from datetime import date,datetime,timezone,timedelta
from decimal import Decimal
from pathlib import Path
from urllib.request import Request,urlopen
from bs4 import BeautifulSoup
HERE=Path(__file__).parent;ROOT=HERE/'data/fundamentals'
SOURCES=[('2025-10-27','https://nsearchives.nseindia.com/corporate/ixbrl/INTEGRATED_FILING_INDAS_122001_27102025221646_iXBRL_WEB.html'),('2026-10-27','https://nsearchives.nseindia.com/corporate/ixbrl/INTEGRATED_FILING_INDAS_204966_27102026182222_iXBRL_WEB.html'),('2026-07-30','https://nsearchives.nseindia.com/corporate/ixbrl/INTEGRATED_FILING_INDAS_180838_30072026190928_iXBRL_WEB.html'),('2026-04-30','https://nsearchives.nseindia.com/corporate/ixbrl/INTEGRATED_FILING_INDAS_155129_30042026224129_iXBRL_WEB.html'),('2026-02-05','https://nsearchives.nseindia.com/corporate/ixbrl/INTEGRATED_FILING_INDAS_140572_05022026183316_iXBRL_WEB.html')]
def clean(s):return ' '.join(s.split()).casefold()
def number(s):
    s=s.strip().replace(',','')
    if not s or s in ('-','NA','N/A'):return None
    if s.startswith('(') and s.endswith(')'):s='-'+s[1:-1]
    v=Decimal(s)
    if not v.is_finite():raise ValueError('Nonfinite financial number')
    return v

def parse(raw,filing_date):
    soup=BeautifulSoup(raw,'html.parser');tables=[];metadata={}
    for table in soup.find_all('table'):
        rows=[[c.get_text(' ',strip=True) for c in r.find_all(['th','td'],recursive=False)] for r in table.find_all('tr')]
        tables.append(rows)
        for r in rows:
            if len(r)==2:metadata[clean(r[0])]=r[1]
    if metadata.get('nse symbol')!='MAZDOCK' or metadata.get('description of presentation currency')!='INR':raise ValueError('Wrong company/currency')
    unit=metadata.get('level of rounding used in financial results')
    if clean(unit or '')!='lakhs':raise ValueError('Unexpected financial units')
    candidates=[rows for rows in tables if any(len(r)>=4 and clean(r[1])=='revenue from operations' and number(r[2]) is not None for r in rows) and any(len(r)>=3 and clean(r[1])=='total profit (loss) for period' for r in rows)]
    if len(candidates)!=1:raise ValueError('Ambiguous financial statement table')
    rows=candidates[0]
    def get(label,column=2):
        values=[r[column] for r in rows if len(r)>column and clean(r[1])==clean(label)]
        if len(values)!=1:raise ValueError('Missing or ambiguous financial fact: '+label)
        return values[0]
    start=datetime.strptime(get('Date of start of reporting period'),'%d-%m-%Y').date();end=datetime.strptime(get('Date of end of reporting period'),'%d-%m-%Y').date()
    if not 88<=(end-start).days<=92 or start.day!=1 or start.month not in (1,4,7,10):raise ValueError('Statement is not a standalone three-month quarter')
    scope=get('Nature of report standalone or consolidated')
    if scope!='Consolidated':raise ValueError('Unexpected accounting scope')
    if end>date.fromisoformat(filing_date):raise ValueError('Future financial period')
    revenue=number(get('Revenue from operations'));pat=number(get('Total profit (loss) for period'))
    if revenue is None or pat is None:raise ValueError('Missing revenue or total period PAT')
    return {'symbol':'MAZDOCK','isin':metadata.get('isin'),'period_start':start.isoformat(),'period_end':end.isoformat(),'filing_date':filing_date,'scope':scope,'audit_status':get('Whether results are audited or unaudited'),'source_unit':unit,'display_unit':'INR crore','revenue_operations_crore':str(revenue/100),'pat_total_period_crore':str(pat/100),'ytd_revenue_operations_crore':str(number(get('Revenue from operations',3))/100),'ytd_pat_total_period_crore':str(number(get('Total profit (loss) for period',3))/100),'pat_definition':'Total profit/loss for period, including equity-accounted associates/JVs where reported; not assumed to be owners-of-parent attributable PAT.','notes':'Exact reported quarter column; YTD/annual columns and other income are not used as quarterly sales. No forecast or quarterly growth rate inferred.'}

def trailing_four(facts,asof):
    eligible=sorted([f for f in facts if f['filing_date']<=asof],key=lambda f:f['period_end'])[-4:]
    if len(eligible)!=4:return None
    if len({(f['symbol'],f['isin'],f['scope'],f['display_unit']) for f in eligible})!=1:raise ValueError('Incompatible TTM scope or identity')
    for left,right in zip(eligible,eligible[1:]):
        if date.fromisoformat(left['period_end'])+timedelta(days=1)!=date.fromisoformat(right['period_start']):raise ValueError('Noncontiguous or duplicate TTM quarters')
    return {'period_start':eligible[0]['period_start'],'period_end':eligible[-1]['period_end'],'available_on':max(f['filing_date'] for f in eligible),'scope':eligible[0]['scope'],'revenue_operations_crore':str(sum(Decimal(f['revenue_operations_crore']) for f in eligible)),'pat_total_period_crore':str(sum(Decimal(f['pat_total_period_crore']) for f in eligible)),'quarters':[f['period_end'] for f in eligible],'growth_yoy':None,'growth_note':'Prior matching four quarters have not yet been collected.'}

def fetch(source):
    filing_date,url=source;record={'source_url':url,'filing_date':filing_date,'retrieved_utc':datetime.now(timezone.utc).isoformat()}
    try:
        with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as response:raw=response.read(8_000_001)
        if len(raw)>8_000_000:raise ValueError('Oversize financial filing')
        sha=hashlib.sha256(raw).hexdigest();(ROOT/'raw'/(sha+'.html')).write_bytes(raw);record['sha256']=sha
        record.update(fact=parse(raw,filing_date),status='parsed_pending_review')
    except Exception as e:record.update(status='fetch_or_validation_failed',error=str(e))
    return record

def main():
    (ROOT/'raw').mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(fetch,SOURCES))
    facts=[r['fact'] for r in records if r.get('fact')]
    out={'symbol':'MAZDOCK','publication_ready':False,'sources':records,'ttm':trailing_four(facts,'2026-10-28'),'note':'Primary financial-fact pilot. Accounting/date/unit review and source verification required before publication. Missing prior-year quarters, ROCE and valuation remain unavailable.'}
    (ROOT/'mazdock.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({'records':[{k:r.get(k) for k in ('filing_date','status','error')} for r in records],'ttm':out['ttm']}))
if __name__=='__main__':main()
