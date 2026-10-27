"""Archive current digital-finance business examples with entity/role boundaries."""
import concurrent.futures
import json
from research_defence import HERE,ROOT,archive

REVIEWED='2026-10-28'
SEEDS=[
 ('PAYTM','Payments infrastructure','https://ir.paytm.com/our-business','Merchant payment-platform and gateway offerings support payments exposure. This does not attribute a banking licence, deposit-taking activity or all partner/group revenue to the listed parent.',['merchant','payment']),
 ('BAJFINANCE','Digital lenders','https://www.bajajfinserv.in/personal-loan','An online loan application establishes digital origination at Bajaj Finance, a diversified lender. It is distinct from listed parent Bajaj Finserv; no fintech-only revenue mix or exclusively digital loan book is inferred.',['bajaj finance','online']),
 ('INTELLECT','Financial software','https://www.intellectdesign.com/','Banking and financial-technology products establish financial-software exposure. A software supplier is not classified as the lender or owner of client bank deposits.',['banking','technology']),
 ('POLICYBZR','Insurance distribution','https://www.pbfintech.in/','Policybazaar and Paisabazaar marketplace offerings establish distribution/platform exposure through the listed group. This does not classify the company as an insurance underwriter or equate distributed premiums with corporate revenue.',['policybazaar','insurance']),
 ('AUBANK','Digital banking','https://www.au.bank.in/personal-banking/savings-account/digital-savings-account','Online account opening and AU 0101 services establish digital-channel exposure at AU Small Finance Bank. It also operates physical touchpoints; this is not a pure-play neobank or an inferred digital-revenue percentage.',['digital','au 0101'])]

def main():
    ROOT.mkdir(exist_ok=True);(ROOT/'raw').mkdir(exist_ok=True)
    sources=json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))
    identities={m['symbol']:m for t in sources['indices'].values() for m in t.get('members',[])}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records=list(pool.map(lambda seed:archive(seed,identities,REVIEWED),SEEDS))
    manifest={'family':'fintech','status':'initial_examples_for_review','reviewed_on':REVIEWED,
              'note':'Five proposed digital-finance examples, not a pure-play fintech universe or a common valuation peer group. Platforms, diversified lenders, software vendors, insurance distributors and banks have different roles and financial statements. No banking licence, underwriting role, revenue materiality, customer records, weights or historical membership inferred.',
              'comparison_note':'These examples span payments, diversified lending, financial software, distribution and banking. They are a business-exposure map, not a homogeneous group for comparing revenue growth or valuation multiples.',
              'members':records}
    (ROOT/'fintech.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({r['symbol']:r['status'] for r in records}))

if __name__=='__main__':main()
