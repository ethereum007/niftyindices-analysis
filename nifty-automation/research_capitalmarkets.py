"""Independently archive capital-market service-provider business evidence."""
import concurrent.futures
import json
from research_defence import HERE,ROOT,archive

REVIEWED='2026-10-28'
SEEDS=[
 ('BSE','Exchanges & depositories','https://www.sebi.gov.in/stock-exchanges.html','The regulator lists BSE as a recognised stock exchange. This establishes exchange exposure only; no current depository ownership, transaction volume or market share is inferred.',['bse','exchange']),
 ('ANGELONE','Brokers','https://www.angelone.in/aboutus','Stock-broking services establish brokerage exposure. No customer-growth rate, trading-volume sensitivity or investment recommendation is inferred.',['broking','angel']),
 ('HDFCAMC','Asset managers','https://files.hdfcfund.com/s3fs-public/2026-07/NSEBSE_30.pdf','HDFC Asset Management Company is identified as the mutual-fund manager. Fund assets under management are not corporate revenue, company market capitalisation or guaranteed earnings.',['asset management','mutual fund']),
 ('CAMS','Registrars & platforms','https://www.camsonline.com/Annual_Report/FY2024-2025/about-cams.html','The listed company annual report describes registrar/transfer-agent and financial-infrastructure services. It is not classified as the investment manager of serviced funds.',['registrar','transfer']),
 ('NUVAMA','Wealth management','https://www.nuvama.com/about-us/','The listed wealth-management group describes advisory, investment and related wealth services. Client assets or group business descriptions are not attributed as direct parent-company revenue.',['wealth','management'])]

def main():
    ROOT.mkdir(exist_ok=True);(ROOT/'raw').mkdir(exist_ok=True)
    sources=json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))
    identities={m['symbol']:m for t in sources['indices'].values() for m in t.get('members',[])}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records=list(pool.map(lambda seed:archive(seed,identities,REVIEWED),SEEDS))
    manifest={'family':'capitalmarkets','status':'initial_examples_for_review','reviewed_on':REVIEWED,
              'note':'Five proposed service-provider examples, not an exhaustive financialisation universe. Regulatory/company evidence establishes business role, not customer popularity, AUM rankings, revenue materiality or future performance. No client records, paid holdings, current market-share claims, weights or historical membership inferred.',
              'members':records}
    (ROOT/'capitalmarkets.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({r['symbol']:r['status'] for r in records}))

if __name__=='__main__':main()
