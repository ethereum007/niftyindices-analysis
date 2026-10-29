"""Listed lending and credit-infrastructure roles, not interchangeable banking peers."""
import json,concurrent.futures
from research_defence import HERE,ROOT,archive
SEEDS=[
 ('ICICIBANK','Private banks','https://rbi.org.in/commonman/Upload/English/Content/PDFs/LAB01112021.pdf','RBI agency-bank list dated4August2026 classifies ICICI Bank as a scheduled private-sector bank. No current market share is inferred. Private-sector ownership classification does not mean private-banking services or deposit guarantees beyond applicable rules.',['scheduled private sector banks','icici bank']),
 ('SBIN','PSU banks','https://rbi.org.in/commonman/Upload/English/Content/PDFs/LAB01112021.pdf','RBI agency-bank list classifies State Bank of India as a scheduled public-sector bank. State ownership is distinct from guaranteed equity returns; The list is dated4August2026; no current ownership percentage or latest financial figure is inferred.',['public sector','state bank of india']),
 ('BAJFINANCE','NBFC lending','https://www.bajajfinserv.in/finance-digital-annual-report-fy24/about-bajaj-finance.html','Bajaj Finance documents consumer, SME and commercial lending. NBFC lending is distinct from a licensed bank; subsidiary housing-finance activity is not automatically parent-only revenue.',['bajaj finance','lending']),
 ('CREDITACC','Microfinance','https://www.creditaccessgrameen.in/about-us/','CreditAccess Grameen describes micro-loans to predominantly rural women customers. This establishes microfinance exposure, not current repayment quality, credit growth or borrower-level data.',['microfinance','micro-loans']),
 ('ICRA','Credit infrastructure','https://www.icra.in/AboutUs/Profile','ICRA provides credit-rating and investment information services. It is credit-assessment infrastructure, not a deposit-taking bank, lender or ownership of the entire Moody\'s group.',['icra limited','credit rating agency'])]

def main():
    identities={m['symbol']:m for t in json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))['indices'].values() for m in t.get('members',[])}
    stocks=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))
    for isin,q in stocks['prices'].items():
        if q['symbol']=='ICRA':identities['ICRA']={'company':'ICRA Limited','isin':isin,'identity_source':'Official NSE EQ bhavcopy '+stocks['date']+'; company name from issuer profile'}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:members=list(pool.map(lambda s:archive(s,identities,'2026-10-29'),SEEDS))
    data={'family':'banking','status':'initial_examples_for_review','reviewed_on':'2026-10-29','note':'Five independently researched business-role examples; not exhaustive banking or credit-universe membership. No holdings, weights, historical membership or quantified theme revenue inferred.','comparison_note':'Banks, NBFCs, microfinance lenders and rating agencies have different balance sheets, regulation and revenue definitions. Credit infrastructure is an adjacent service role, not a bank; this is not a homogeneous valuation or growth peer group.','members':members}
    (ROOT/'banking.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({m['symbol']:m['status'] for m in members}))

if __name__=='__main__':main()
