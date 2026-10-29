"""Archive independently researched telecom/media roles, not basket membership."""
import json, concurrent.futures
from research_defence import HERE, ROOT, archive
SEEDS=[
 ('BHARTIARTL','Telecom operators','https://www.airtel.in/about-bharti/about-bharti-airtel/','Bharti Airtel describes mobile and fixed connectivity operations. Group and associate operations are distinct from standalone parent revenue; no subscriber count or market-share ranking is inferred.',['mobile','communications']),
 ('TEJASNET','Network equipment','https://www.tejasnetworks.com/products-and-solutions/optical-aggregation/','Tejas describes optical networking equipment supporting mobile backhaul and broadband. Equipment capability does not establish ownership of operator networks or current order conversion.',['optical','backhaul']),
 ('SUNTV','Broadcasting','https://www.sunnetwork.in/footerpdf/tvch/2026/RIO_IPTV-TVCH-W.E.F_1st_MAY_2026.pdf','Sun TV Network reference interconnect offer identifies television channel distribution through its authorised agent TVCH. Broadcasting rights and signal distribution are distinct from ownership of IPTV operators; no current audience or channel count is inferred.',['sun tv network limited','channels']),
 ('SAREGAMA','Content & entertainment','https://www.saregama.com/static/about-us','Saregama India describes music, film and television content production and entertainment IP. Content rights and production are distinct from broadcasting infrastructure and no quantified revenue share is inferred.',['saregama','music']),
 ('AFFLE','Advertising','https://affle.com/about','Affle 3i Limited identifies NSE AFFLE and consumer advertising technology. Listed-company platform exposure is distinct from all promoter-group revenue and advertiser spending is not assumed to equal platform revenue.',['affle 3i','advertis'])]

def main():
    quotes=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))
    names={'BHARTIARTL':'Bharti Airtel Limited','TEJASNET':'Tejas Networks Limited','SUNTV':'Sun TV Network Limited','SAREGAMA':'Saregama India Limited','AFFLE':'Affle 3i Limited'}
    ids={q['symbol']:{'company':names[q['symbol']],'isin':isin,'identity_source':'Official NSE EQ bhavcopy '+quotes['date']+'; company name from primary corporate disclosure'} for isin,q in quotes['prices'].items() if q['symbol'] in names}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:members=list(p.map(lambda s:archive(s,ids,'2026-10-29'),SEEDS))
    d={'family':'telecommedia','status':'initial_examples_for_review','reviewed_on':'2026-10-29','note':'Five bounded independently researched role examples, not an exhaustive listed universe. No paid holdings, weights, historical membership or quantified revenue materiality inferred.','comparison_note':'Operators, equipment, broadcasters, content rights and ad platforms differ in capital intensity and revenue recognition. This is not a homogeneous valuation or growth peer group.','members':members}
    (ROOT/'telecommedia.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({m['symbol']:(m['status'],m.get('error'),m.get('keyword_checks')) for m in members}))
if __name__=='__main__':main()
