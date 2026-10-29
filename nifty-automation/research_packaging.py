"""Primary-source examples for five packaging business roles."""
import json,concurrent.futures
from research_defence import HERE,ROOT,archive
SEEDS=[
 ('JKPAPER','Paper & pulp','https://www.jkpaper.com/','JK Paper describes paper and packaging-board production. Product capability does not establish current pulp self-sufficiency, utilisation, or ownership of customers using the paper.',['paper','packaging']),
 ('UFLEX','Flexible packaging','https://www.uflexltd.com/packaging.php','UFlex describes flexible packaging laminates and pouches. Packaging capability is distinct from ownership of packaged consumer brands; no theme-specific revenue share or universal recyclability inferred.',['flexible packaging','pouches']),
 ('MOLDTKPAC','Rigid packaging','https://nsearchives.nseindia.com/corporate/MOLDTKPAC_11052026151142_Press_Relese_SE_Intimation.pdf','Mold-Tek Packaging describes rigid plastic packaging. Containers supplied to client brands are distinct from client product revenue; no current market share or environmental performance is inferred.',['rigid','packaging']),
 ('TIMETECHNO','Industrial containers','https://www.timetechnoplast.com/business-division/industrial-packaging/','Time Technoplast describes industrial drums, containers and pails. Packaging manufacture is distinct from transporting or owning the chemicals and other goods carried; no current capacity or commodity exposure share inferred.',['drums','containers']),
 ('PAKKA','Sustainable materials','https://nsearchives.nseindia.com/corporate/yashpakka_10062026032102_Pakka_Limited_Investor_Call_Transcript_02062026.pdf','Pakka describes bagasse-based and compostable packaging products. Sustainable-materials classification reflects disclosed product positioning, not independently proven life-cycle benefit, universal compostability certification, or commercial operation of every announced project.',['bagasse','compostable'])]
def main():
    q=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))
    names={'JKPAPER':'JK Paper Limited','UFLEX':'UFlex Limited','MOLDTKPAC':'Mold-Tek Packaging Limited','TIMETECHNO':'Time Technoplast Limited','PAKKA':'Pakka Limited'}
    ids={v['symbol']:{'company':names[v['symbol']],'isin':k,'identity_source':'Official NSE EQ bhavcopy '+q['date']+'; name from primary corporate disclosure'} for k,v in q['prices'].items() if v['symbol'] in names}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:members=list(p.map(lambda s:archive(s,ids,'2026-10-29'),SEEDS))
    d={'family':'packaging','status':'initial_examples_for_review','reviewed_on':'2026-10-29','note':'Five independently researched bounded business-role examples; not an exhaustive listed universe. No paid holdings, weights, historical membership or quantified theme revenue inferred.','comparison_note':'Paper, flexible film, rigid plastics, industrial drums and fibre-based alternatives differ in feedstock, end markets and recovery systems. This is not a homogeneous valuation or growth peer group.','members':members}
    (ROOT/'packaging.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
    print({m['symbol']:(m['status'],m.get('error'),m.get('keyword_checks')) for m in members})
if __name__=='__main__':main()
