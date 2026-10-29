"""Dated issuer outcome evidence; deliberately separate from exchange filing time."""
import io,json,hashlib
from pathlib import Path
from pypdf import PdfReader
from reconcile_dixon_sources import reconcile
from parse_primary_pdf import parse_dixon_june2026_research
ROOT=Path(__file__).parent/'data/fundamentals'

def outcome_date(raw):
    reader=PdfReader(io.BytesIO(raw))
    if len(reader.pages)!=12:raise ValueError('Unexpected Dixon outcome document')
    text=' '.join(reader.pages[0].extract_text().split())
    for required in ('Dixon Technologies (India) Limited','31st July, 2026','INE935N01020',
                     'Scrip Code- DIXON','Quarter ended 30th June, 2026',
                     "also being uploaded on the Company's Website"):
        if required not in text:raise ValueError('Dixon issuer outcome identity/date mismatch')
    return '2026-07-31'

def load_research(root=ROOT):
    d=json.loads((root/'dixon-current-quarter-research.json').read_text(encoding='utf-8'))
    def original(source,ext):
        raw=(root/'raw'/(source['sha256']+ext)).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=source['sha256']:raise ValueError('Changed Dixon evidence')
        return raw
    outcome=d['issuer_outcome_source'];available=outcome_date(original(outcome,'.pdf'))
    result=reconcile(original(d['bse_primary_html'],'.html'),original(d['sources'][0],'.pdf'))
    result.update(available_on=available,availability_basis='Dated issuer outcome and website-publication statement; end-of-day cutoff',
                  availability_sha256=outcome['sha256'],availability_source_url=outcome['source_url'])
    fact=parse_dixon_june2026_research(original(d['sources'][0],'.pdf'))
    fact.update(available_on=available,availability_basis=result['availability_basis'],
                availability_sha256=outcome['sha256'],availability_source_url=outcome['source_url'],
                source_url=d['sources'][0]['source_url'],sha256=d['sources'][0]['sha256'])
    result['fact']=fact
    result['restriction']='Issuer publication date does not establish exchange/intraday filing time. Lighting-business transfer prevents comparable growth inference. Review before UI publication.'
    return result

if __name__=='__main__':
    (ROOT/'dixon-availability-review.json').write_text(json.dumps(load_research(),indent=2)+'\n',encoding='utf-8')
    print('Dixon dated issuer outcome and original financial evidence verified; research only.')
