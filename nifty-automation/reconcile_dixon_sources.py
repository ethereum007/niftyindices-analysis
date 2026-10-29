"""Compare Dixon's original BSE HTML with issuer-hosted integrated PDF.

This is research evidence, not permission to infer a dissemination timestamp.
"""
import hashlib,json
from pathlib import Path
from bs4 import BeautifulSoup
from decimal import Decimal
from parse_primary_pdf import parse_dixon_june2026_research

ROOT=Path(__file__).parent/'data/fundamentals'

def reconcile(html,pdf):
    rows=[[c.get_text(' ',strip=True) for c in row.find_all(['td','th'],recursive=False)]
          for row in BeautifulSoup(html,'html.parser').find_all('tr')]
    def metadata(label,expected):
        found=[r[1] for r in rows if len(r)==2 and r[0]==label]
        if found!=[expected]:raise ValueError('BSE identity/scope mismatch: '+label)
    for label,value in [('NSE Symbol*','DIXON'),('ISIN*','INE935N01020'),
                        ('Level of rounding','Crores'),('Description of presentation currency','INR'),
                        ('Nature of report standalone or consolidated','Consolidated')]:
        metadata(label,value)
    parsed=parse_dixon_june2026_research(pdf)
    checks=[]
    for label,key in [('Revenue from operations','revenue_operations_crore'),
                      ('Total profit (loss) for period','pat_total_period_crore')]:
        matches=[r for r in rows if len(r)==4 and r[1]==label]
        if len(matches)!=1:raise ValueError('Ambiguous BSE quarterly fact')
        quarter,ytd=[Decimal(v.replace(',','')) for v in matches[0][2:]]
        if quarter!=ytd or quarter!=Decimal(parsed[key]):raise ValueError('BSE/PDF fact mismatch')
        checks.append({'metric':key,'quarter_crore':str(quarter),'ytd_crore':str(ytd),'status':'match'})
    for label,expected in [('Date of start of reporting period','01-04-2026'),
                           ('Date of end of reporting period','30-06-2026')]:
        matches=[r for r in rows if len(r)==3 and r[0]==label]
        if not matches or any(r[1:]!=[expected,expected] for r in matches):raise ValueError('BSE period mismatch')
    return {'symbol':'DIXON','publication_ready':False,'filing_date':None,
            'checks':checks,'comparable_growth_allowed':False,
            'restriction':'Source agreement verifies facts, not dissemination time or economic comparability.'}

def main():
    data=json.loads((ROOT/'dixon-current-quarter-research.json').read_text(encoding='utf-8'))
    html_source=data['bse_primary_html'];pdf_source=data['sources'][0]
    def original(source,extension):
        raw=(ROOT/'raw'/(source['sha256']+extension)).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=source['sha256']:raise ValueError('Original source checksum mismatch')
        return raw
    result=reconcile(original(html_source,'.html'),original(pdf_source,'.pdf'))
    result['html_sha256']=html_source['sha256'];result['pdf_sha256']=pdf_source['sha256']
    (ROOT/'dixon-source-reconciliation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Dixon original BSE HTML / issuer PDF reconciliation passed; publication remains gated.')

if __name__=='__main__':main()
