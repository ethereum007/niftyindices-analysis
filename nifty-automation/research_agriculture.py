"""Bounded primary-source agriculture value-chain examples."""
import json,concurrent.futures
from research_defence import HERE,ROOT,archive
SEEDS=[
 ('KSCL','Seeds & crop inputs','https://www.kaveriseeds.in/our-story/details-of-business/','Kaveri Seed describes hybrid-seed development and production for agricultural crops. Seed supply does not imply ownership of customer farms or quantified yield improvements; crop-input exposure is not all agrochemicals.',['kaveri','seed']),
 ('ESCORTS','Farm equipment','https://exports.escortskubota.com/','Escorts Kubota describes tractors and agricultural implements. Equipment sales are distinct from owning farms or crop output; no current exports, utilisation or market share inferred.',['tractor','implements']),
 ('JISLJALEQS','Irrigation','https://www.jains.com/Segment/Irrigation.htm','Jain Irrigation describes drip and sprinkler irrigation systems and installation support. Equipment and project services are distinct from ownership of client farms or guaranteed water savings; the diversified company is not a pure-play irrigation utility.',['irrigation','drip']),
 ('KRBL','Food processing','https://krblrice.com/about-us/','KRBL issuer profile describes manufacturing and marketing rice products. This establishes food-processing exposure without inferring current utilisation, output, revenue or ownership of grower land.',['rice','manufacturing']),
 ('SNOWMAN','Cold chain','https://snowman.in/about','Snowman Logistics describes temperature-controlled warehousing and distribution. This is supply-chain service exposure across temperature-sensitive products, not exclusively agriculture revenue or ownership of customer inventory.',['temperature','warehousing'])]
def main():
    q=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))
    names={'KSCL':'Kaveri Seed Company Limited','ESCORTS':'Escorts Kubota Limited','JISLJALEQS':'Jain Irrigation Systems Limited','KRBL':'KRBL Limited','SNOWMAN':'Snowman Logistics Limited'}
    ids={v['symbol']:{'company':names[v['symbol']],'isin':k,'identity_source':'Official NSE EQ bhavcopy '+q['date']+'; name from primary corporate disclosure'} for k,v in q['prices'].items() if v['symbol'] in names}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:members=list(p.map(lambda s:archive(s,ids,'2026-10-29'),SEEDS))
    d={'family':'agriculture','status':'initial_examples_for_review','reviewed_on':'2026-10-29','note':'Five independently researched bounded business-role examples; not an exhaustive listed universe. No paid holdings, weights, historical membership or quantified theme revenue inferred.','comparison_note':'Seeds, machinery, irrigation, food processing and logistics have distinct crop-cycle, asset and revenue models. This is not a homogeneous valuation or growth peer group.','members':members}
    (ROOT/'agriculture.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
    print({m['symbol']:(m['status'],m.get('error'),m.get('keyword_checks')) for m in members})
if __name__=='__main__':main()
