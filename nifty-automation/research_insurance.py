"""Map insurance underwriting, reinsurance and distribution as separate roles."""
import json,concurrent.futures
from research_defence import HERE,ROOT,archive
SEEDS=[
 ('HDFCLIFE','Life insurance','https://www.hdfclife.com/about-us','HDFC Life offers long-term life, protection, pension and annuity solutions. It is the listed insurer, not all HDFC Bank businesses; product breadth is not current new-business growth.',['hdfc life','life insurance']),
 ('ICICIGI','General insurance','https://nsearchives.nseindia.com/corporate/ixbrl/INTEGRATED_FILING_GI_174881_15072026211206_iXBRL_WEB.html','ICICI Lombard underwrites motor, health, crop, fire and other general insurance. General-insurance premium and claims economics differ from life insurance; this does not attribute the whole ICICI group.',['general insurance','motor']),
 ('STARHEALTH','Health insurance','https://nsearchives.nseindia.com/corporate/STARHEALTH_21082025102256_PR210825.pdf','Star Health identifies as a standalone health insurer and offers health, accident and travel products. Its network hospitals are service partners, not hospitals owned by the insurer.',['standalone','health insurance']),
 ('GICRE','Reinsurance','https://www.gicre.in/en/index.php?Itemid=102&id=8&lang=en&option=com_content&view=article','GIC Re provides reinsurance to direct insurers. Reinsurance risk transfer is distinct from retail insurance distribution; no monopoly, market share or current premium growth is inferred.',['gic re','reinsurance']),
 ('POLICYBZR','Distribution platforms','https://www.pbfintech.in/','PB Fintech operates insurance and credit distribution platforms. Insurance distribution is distinct from underwriting risk; distributed premiums are not treated as platform revenue.',['policybazaar','insurance'])]

def main():
    identities={m['symbol']:m for t in json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))['indices'].values() for m in t.get('members',[])}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:members=list(pool.map(lambda s:archive(s,identities,'2026-10-29'),SEEDS))
    d={'family':'insurance','status':'initial_examples_for_review','reviewed_on':'2026-10-29','note':'Five source-backed business-role examples, not exhaustive insurance membership. No policyholder/customer records accessed, paid holdings, weights, revenue materiality or historical membership inferred.','comparison_note':'Life, general and health underwriting, reinsurance and distribution platforms use different accounting and operating metrics. Distributed premium is not broker revenue; network hospitals are not owned hospital assets. This is not a homogeneous valuation peer group.','members':members}
    (ROOT/'insurance.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');print(json.dumps({m['symbol']:m['status'] for m in members}))

if __name__=='__main__':main()
