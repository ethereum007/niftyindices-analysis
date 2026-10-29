"""Research-only adapter for two explicit L&T consolidated PDF templates."""
import io,re,json,hashlib
from decimal import Decimal
from pathlib import Path
from pypdf import PdfReader

def parse(raw,period_end):
    templates={'2026-06-30':(7,4,'JUNE 30, 2026'),'2026-09-30':(10,6,'SEPTEMBER 30, 2026')}
    if period_end not in templates:raise ValueError('Unsupported LT period')
    pages,columns,title=templates[period_end]
    reader=PdfReader(io.BytesIO(raw))
    if len(reader.pages)!=pages:raise ValueError('Unexpected LT page count')
    text=' '.join(reader.pages[0].extract_text().split())
    if not all(x in text for x in ('LARSEN & TOUBRO LIMITED','L99999MH1946PLC004768',
                                  'STATEMENT OF UNAUDITED CONSOLIDATED FINANCIAL RESULTS',title,'Crore')):
        raise ValueError('LT statement identity/scope/unit mismatch')
    def values(label):
        matches=re.findall(r'(?<![0-9.])'+re.escape(label)+r'\s+'+r'\s+'.join([r'(\(?-?\d[\d,]*\.\d{2}\)?)']*columns),text)
        if len(matches)!=1:raise ValueError('Missing/ambiguous LT row: '+label)
        return [Decimal(v.replace(',','').replace('(','-').replace(')','')) for v in matches[0]]
    sales=values('a) Revenue from operations');other=values('b) Other income (net)');income=values('Total Income')
    pbt=values('5 Profit before tax (3+4)');tax=values('Total tax expense')
    before=values('7 Net profit after tax (5-6)')
    jv=values('8 Share in profit/(loss) after tax of joint ventures/associates (net)')
    total=values('9')
    if any(s+o!=i for s,o,i in zip(sales,other,income)):raise ValueError('LT income bridge mismatch')
    if any(p-t!=n for p,t,n in zip(pbt,tax,before)):raise ValueError('LT tax bridge mismatch')
    if any(n+j!=p for n,j,p in zip(before,jv,total)):raise ValueError('LT JV/PAT bridge mismatch')
    if columns==6 and (sales[0]+sales[1]!=sales[3] or total[0]+total[1]!=total[3]):raise ValueError('LT half-year bridge mismatch')
    return {'symbol':'LT','isin':'INE018A01030','scope':'Consolidated','period_end':period_end,
            'source_unit':'INR crore','revenue_operations_crore':str(sales[0]),
            'pat_total_period_crore':str(total[0]),'statement_page':1,'filing_date':None,
            'publication_ready':False,'pat_definition':'Total period PAT including JV/associate share; not parent-attributable PAT.',
            'quarter_columns_revenue':[str(v) for v in sales], 'quarter_columns_pat':[str(v) for v in total]}

def main():
    root=Path(__file__).parent/'data/fundamentals';p=root/'lt-primary-research.json'
    data=json.loads(p.read_text(encoding='utf-8'))
    for source,end in zip(data['sources'],('2026-06-30','2026-09-30')):
        raw=(root/'raw'/(source['sha256']+'.pdf')).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=source['sha256']:raise ValueError('LT source hash mismatch')
        source['parsed_research_fact']=parse(raw,end)
    p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print('LT June/September source accounting bridges verified; research only.')

if __name__=='__main__':main()
