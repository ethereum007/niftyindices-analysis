"""Independent IT business-role examples; no portfolio holdings inferred."""
import json,concurrent.futures
from research_defence import HERE,ROOT,archive
SEEDS=[
 ('HCLTECH','IT services','https://www.hcltech.com/advisory-and-consulting','IT services, consulting and business solutions establish services exposure; internal AI use is not a separately quantified AI revenue stream.',['it transformation','consulting']),
 ('LTTS','Engineering R&D','https://www.ltts.com/services','Engineering and embedded-system development services establish outsourced engineering exposure; services for clients do not imply ownership of their end products.',['engineering','embedded']),
 ('OFSS','Enterprise software','https://docs.oracle.com/en/industries/financial-services/banking-origination/14.9.0.0.0/oborn/background.html','Oracle documentation explicitly attributes development of Banking Origination to Oracle Financial Services Software Limited. Exposure is banking software; all Oracle group revenue is not attributed to this listed subsidiary.',['oracle financial services software limited','banking origination']),
 ('NAUKRI','Digital platforms','https://www.infoedge.in/About/Overview','Info Edge operates recruitment and property-classified internet platforms. Minority investments are distinct from fully owned operating businesses and are not counted as direct platform revenue.',['naukri','99acres']),
 ('QUICKHEAL','Cybersecurity','https://www.seqrite.com/about/','Seqrite identifies itself as the enterprise arm of Quick Heal Technologies Limited providing cybersecurity software. Product capability claims do not establish customer growth or quantified theme revenue.',['quick heal technologies limited','cybersecurity'])]

def main():
    identities={m['symbol']:m for t in json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))['indices'].values() for m in t.get('members',[])}
    stocks=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))
    for isin,q in stocks['prices'].items():
        if q['symbol']=='QUICKHEAL':identities['QUICKHEAL']={'company':'Quick Heal Technologies Limited','isin':isin,'identity_source':'Official NSE EQ bhavcopy '+stocks['date']+'; company name from issuer business disclosure'}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:members=list(pool.map(lambda s:archive(s,identities,'2026-10-29'),SEEDS))
    data={'family':'itservices','status':'initial_examples_for_review','reviewed_on':'2026-10-29','note':'Five source-backed business-role examples covering five proposed subthemes; not an exhaustive listed universe. No Smallcase paid holdings, weights, theme revenue share or historical membership inferred. Keyword checks are archive checks, not exposure classification.','comparison_note':'IT outsourcing, engineering services, software licensing, classifieds and cybersecurity have different business economics; they are not a homogeneous valuation peer group.','members':members}
    (ROOT/'itservices.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({m['symbol']:m['status'] for m in members}))

if __name__=='__main__':main()
