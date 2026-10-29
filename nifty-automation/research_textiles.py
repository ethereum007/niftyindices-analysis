"""Archive bounded textile business roles without inferring holdings or materiality."""
import json,concurrent.futures
from research_defence import HERE,ROOT,archive
SEEDS=[
 ('VTL','Yarn & fabrics','https://vardhman.com/document/Resources/Yarn_Brochure.pdf','Vardhman brochure explicitly attributes cotton/blended yarn and woven/processed fabric units to Vardhman Textiles Limited. Other group companies, including threads and special steels, are not silently attributed to this listed issuer. Historical brochure capacities are not current utilisation.',['vardhman textiles','yarn']),
 ('GOKEX','Garment manufacturing','https://nsearchives.nseindia.com/corporate/GOKEX_19052026172415_intimationofinvestorscall.pdf','Gokaldas Exports issuer disclosure describes apparel manufacturing and exporting. Contract manufacture is distinct from owning customer fashion brands or their retail revenue; no current orders or customer concentration inferred.',['gokaldas exports','apparel']),
 ('GARFIBRES','Technical textiles','https://nsearchives.nseindia.com/corporate/GARFIBRES_11022026174210_PressRelease11022026.pdf','Garware Technical Fibres describes application-focused nets, ropes and geosynthetics. Industrial technical textiles are distinct from fashion apparel; product capability is not current installed utilisation or quantified exposure to any one end market.',['technical textiles','garware']),
 ('WELSPUNLIV','Home textiles','https://www.welspunliving.com/about-us','Welspun Living identifies home-textile manufacturing. Listed-company exposure excludes other Welspun group line-pipe, oil/gas and infrastructure businesses; licensed brands do not imply ownership of global brand intellectual property.',['welspun living limited','home textile']),
 ('KITEX','Export supply chain','https://www.kitexgarments.com/wp-content/uploads/2024/09/KGL-AR-23-24.pdf','Kitex Garments FY2023-24 issuer report documents infant-garment manufacture and exports. Export supply-chain exposure is historical business evidence, not current export share or tariff resilience; client outlets and brands are not company-owned retail assets.',['kitex garments','export'])]
def main():
    q=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))
    names={'VTL':'Vardhman Textiles Limited','GOKEX':'Gokaldas Exports Limited','GARFIBRES':'Garware Technical Fibres Limited','WELSPUNLIV':'Welspun Living Limited','KITEX':'Kitex Garments Limited'}
    ids={v['symbol']:{'company':names[v['symbol']],'isin':k,'identity_source':'Official NSE EQ bhavcopy '+q['date']+'; name from primary corporate disclosure'} for k,v in q['prices'].items() if v['symbol'] in names}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:members=list(p.map(lambda s:archive(s,ids,'2026-10-29'),SEEDS))
    d={'family':'textiles','status':'initial_examples_for_review','reviewed_on':'2026-10-29','note':'Five independently researched bounded business-role examples; not an exhaustive listed universe. No paid holdings, weights, historical membership or quantified theme revenue inferred.','comparison_note':'Yarn, garment contracts, industrial fabrics, home textiles and exports have different input, currency and demand exposures. This is not a homogeneous valuation or growth peer group.','members':members}
    (ROOT/'textiles.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
    print({m['symbol']:(m['status'],m.get('error'),m.get('keyword_checks')) for m in members})
if __name__=='__main__':main()
