"""Primary evidence for bounded travel and leisure business roles."""
import json,concurrent.futures
from research_defence import HERE,ROOT,archive
SEEDS=[
 ('INDHOTEL','Hotels & resorts','https://nsearchives.nseindia.com/corporate/INDHOTEL_05022026173633_Pressrelease.pdf','Indian Hotels describes hospitality and hotel brands. Managed or branded hotels are not all owned properties; strategy targets are not current operating assets or realised revenue.',['ihcl','hospitality']),
 ('EASEMYTRIP','Travel platforms','https://www.easemytrip.com/terms.html','Easy Trip Planners identifies itself as operator of the EaseMyTrip booking platform. Airline and hotel bookings do not imply ownership of partner airlines or hotels, and booking value is not platform revenue.',['easy trip planners','travel']),
 ('WONDERLA','Leisure venues','https://www.wonderla.com/','Wonderla Holidays describes amusement parks and rides. This establishes leisure-venue exposure, not verified current footfall, park counts or ownership of every branded property.',['wonderla holidays','amusement']),
 ('JUBLFOOD','Restaurants','https://nsearchives.nseindia.com/corporate/JUBLFOOD_20052026161011_EarningsPresentation.pdf','Jubilant FoodWorks May 2026 issuer presentation documents restaurant operations including Domino pizza restaurants. Brand operation does not imply ownership of global franchisor intellectual property; no current store counts or sales growth inferred.',['jubilant','restaurant']),
 ('PVRINOX','Entertainment services','https://nsearchives.nseindia.com/corporate/ixbrl/INTEGRATED_FILING_INDAS_177428_23072026175649_iXBRL_WEB.html','PVR INOX issuer filing identifies film exhibition business. Cinema exhibition is distinct from ownership of all films screened, content production and ownership of every cinema property.',['pvrinox','film exhibition business'])]
def main():
    quotes=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))
    names={'INDHOTEL':'The Indian Hotels Company Limited','EASEMYTRIP':'Easy Trip Planners Limited','WONDERLA':'Wonderla Holidays Limited','JUBLFOOD':'Jubilant FoodWorks Limited','PVRINOX':'PVR INOX Limited'}
    ids={q['symbol']:{'company':names[q['symbol']],'isin':isin,'identity_source':'Official NSE EQ bhavcopy '+quotes['date']+'; name from primary corporate disclosure'} for isin,q in quotes['prices'].items() if q['symbol'] in names}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:members=list(p.map(lambda s:archive(s,ids,'2026-10-29'),SEEDS))
    d={'family':'travelleisure','status':'initial_examples_for_review','reviewed_on':'2026-10-29','note':'Five independently researched bounded examples, not an exhaustive listed universe. No holdings, weights, historical membership or quantified revenue share inferred.','comparison_note':'Hotels, booking platforms, amusement parks, restaurants and cinemas have different asset, franchise and revenue models. This is not a homogeneous valuation or growth peer group.','members':members}
    (ROOT/'travelleisure.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
    print({m['symbol']:(m['status'],m.get('error'),m.get('keyword_checks')) for m in members})
if __name__=='__main__':main()
