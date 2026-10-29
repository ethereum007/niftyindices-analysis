"""Bind reviewed LT facts to dated issuer announcements without inventing filing times."""
import hashlib,json
from datetime import datetime,date
from pathlib import Path
from bs4 import BeautifulSoup
from parse_lt_research import parse

ROOT=Path(__file__).parent/'data/fundamentals'

def dated_issuer_availability(raw,expected_date):
    page=BeautifulSoup(raw,'html.parser')
    dates=[n.get_text(strip=True) for n in page.select('.date_sec')]
    if len(dates)!=1:raise ValueError('Ambiguous issuer publication date')
    actual=datetime.strptime(dates[0],'%d %B %Y').date().isoformat()
    if actual!=expected_date:raise ValueError('Issuer publication date mismatch')
    return actual

def load_research(root=ROOT,asof=None):
    data=json.loads((root/'lt-primary-research.json').read_text(encoding='utf-8'))
    if len(data['sources'])!=2 or len(data['dated_issuer_announcements'])!=2:
        raise ValueError('Unexpected LT review scope')
    def original(source,extension):
        raw=(root/'raw'/(source['sha256']+extension)).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=source['sha256']:raise ValueError('LT evidence hash mismatch')
        return raw
    facts=[]
    for source,announcement,end in zip(data['sources'],data['dated_issuer_announcements'],('2026-06-30','2026-09-30')):
        fact=parse(original(source,'.pdf'),end)
        html=original(announcement,'.html')
        available=dated_issuer_availability(html,announcement['issuer_publication_date'])
        page=BeautifulSoup(html,'html.parser')
        expected_title='June 30, 2026' if end=='2026-06-30' else 'September 30, 2026'
        if expected_title not in (page.title.get_text() if page.title else ''):
            raise ValueError('LT issuer announcement period mismatch')
        if date.fromisoformat(available)<date.fromisoformat(end):raise ValueError('Publication before reporting period')
        fact.update(available_on=available,availability_basis='Dated issuer publication; end-of-day cutoff',
                    source_url=source['source_url'],sha256=source['sha256'],
                    availability_source_url=announcement['source_url'],availability_sha256=announcement['sha256'])
        if asof is None or available<=date.fromisoformat(asof).isoformat():facts.append(fact)
    return {'publication_ready':False,'facts':facts,
            'restriction':'Availability evidence only; dashboard publication review still required. No intraday timestamp or exchange filing date inferred.'}

if __name__=='__main__':
    result=load_research()
    (ROOT/'lt-availability-review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('LT issuer availability dates verified for two research quarters.')
