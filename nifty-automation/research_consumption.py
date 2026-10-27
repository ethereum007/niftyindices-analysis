"""Archive consumer-business exposure, without inferring demand acceleration."""
import concurrent.futures
import json
from research_defence import HERE,ROOT,archive

REVIEWED='2026-10-28'
SEEDS=[
 ('TITAN','Branded retail','https://www.titancompany.in/about-us','Jewellery, watches and other lifestyle categories establish branded-consumption exposure. Brand presence does not establish premiumisation-led sales growth or a quantified discretionary-revenue share.',['jewellery','watches']),
 ('BLUESTARCO','Consumer durables','https://www.bluestarindia.com/products/room-air-conditioners','Room air-conditioners establish consumer-durables exposure within a diversified cooling business. Data-centre cooling is separate exposure and is not labelled as consumer-segment revenue.',['room','conditioner']),
 ('INDHOTEL','Premium experiences','https://www.tata.com/business/the-indian-hotels-company-taj-group','The hospitality portfolio spans luxury and other hotel segments. It is not classified as pure luxury; brand affiliation does not establish ownership of every hotel or a measured occupancy/pricing recovery.',['luxury','hotel']),
 ('BRITANNIA','Food & staples','https://media.britannia.co.in/Analyst_Deck_Q4_26_V7_a870ddfb37.pdf','Packaged-food categories including biscuits and dairy establish food-consumption exposure. This is not raw-commodity ownership or an inferred household-spending growth rate.',['biscuit','dairy']),
 ('HINDUNILVR','Rural demand','https://nsearchives.nseindia.com/corporate/HINDUNILVR_19102023154307_InvestorPresentationSQ2023Signed.pdf','Project Shakti establishes a rural distribution route for consumer products. Rural reach is not proof of current rural-demand recovery or a quantified rural-revenue share.',['shakti','rural'])]

def main():
    ROOT.mkdir(exist_ok=True);(ROOT/'raw').mkdir(exist_ok=True)
    sources=json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))
    identities={m['symbol']:m for t in sources['indices'].values() for m in t.get('members',[])}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records=list(pool.map(lambda seed:archive(seed,identities,REVIEWED),SEEDS))
    manifest={'family':'consumption','status':'initial_examples_for_review','reviewed_on':REVIEWED,
              'note':'Five independently researched consumer-exposure examples, not an exhaustive consumption universe. Products, brands and distribution routes do not establish realised premiumisation, rural recovery, quarterly demand growth or homogeneous valuation peers. No customer records, weights or historical membership inferred.',
              'comparison_note':'This is an exposure map across retail, durables, hospitality, packaged food and rural distribution. It does not establish that premiumisation or rural-demand recovery is happening in the selected period.',
              'members':records}
    (ROOT/'consumption.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({r['symbol']:r['status'] for r in records}))

if __name__=='__main__':main()
