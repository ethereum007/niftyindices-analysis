"""Archive oil/gas value-chain roles without treating them as one crude-price bet."""
import concurrent.futures
import json
from research_defence import HERE,ROOT,archive

REVIEWED='2026-10-28'
SEEDS=[
 ('ONGC','Exploration & production','https://www.ongcindia.com/web/eng/about-ongc/technology','Oil/gas exploration and production capabilities establish upstream exposure. Group refining or renewable activity is not attributed as direct standalone upstream revenue; no reserve valuation or current production share is inferred.',['exploration','production']),
 ('IOC','Refining','https://ppac.gov.in/infrastructure/location-of-refineries','Government PPAC refinery listings identify IndianOil facilities, establishing downstream exposure. Refining margins, marketing margins and inventory effects differ from upstream crude-price exposure; no present margin forecast is inferred.',['indian oil','refiner']),
 ('GAIL','Pipelines & terminals','https://www.gailonline.com/Natural_Gas.html','Natural-gas pipeline infrastructure establishes midstream exposure. This does not imply the company produces all transported gas or that every group activity earns a regulated pipeline tariff.',['gas','pipeline']),
 ('IGL','City gas','https://nsearchives.nseindia.com/corporate/IGL1_24102025145919_BRSRReportFY202425.pdf','City-gas distribution establishes downstream gas-network exposure. It is not classified as the owner of upstream reserves, and input-gas sourcing or retail-margin sensitivity is not estimated.',['city','gas']),
 ('DEEPINDS','Energy services','https://deepindustries.com/docs/Deep%20Industries%20Ltd%20Q1%20FY26%20Presentation.pdf','The company presentation describes gas-compression services. Equipment/service activity is not ownership of client hydrocarbon reserves; historical contract capability is not present unexecuted order value.',['compression','deep industries'])]

def main():
    ROOT.mkdir(exist_ok=True);(ROOT/'raw').mkdir(exist_ok=True)
    sources=json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))
    identities={m['symbol']:m for t in sources['indices'].values() for m in t.get('members',[])}
    stocks=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))
    for isin,quote in stocks['prices'].items():
        if quote['symbol']=='DEEPINDS' and quote['symbol'] not in identities:
            identities[quote['symbol']]={'company':'Deep Industries Limited','isin':isin,
                'identity_source':'Official NSE EQ bhavcopy '+stocks['date']+'; legal name from primary company presentation; ticker checked against corporate investor-support page, not similarly named Deep Energy Resources'}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records=list(pool.map(lambda seed:archive(seed,identities,REVIEWED),SEEDS))
    manifest={'family':'oilgas','status':'initial_examples_for_review','reviewed_on':REVIEWED,
              'note':'Five proposed hydrocarbon-value-chain examples, not an exhaustive universe, reserve valuation, uniform crude-price sensitivity or investment forecast. Upstream, refining, transmission, retail gas and service-company economics differ. No customer records, weights or historical membership inferred.',
              'comparison_note':'These roles can respond differently to crude/gas prices, tariffs, inventory and input costs. This is an exposure map, not one directional commodity-price trade or a homogeneous valuation peer group.',
              'members':records}
    (ROOT/'oilgas.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({r['symbol']:r['status'] for r in records}))

if __name__=='__main__':main()
