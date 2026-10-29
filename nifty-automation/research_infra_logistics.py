"""Independently sourced infrastructure and logistics role examples."""
import json,concurrent.futures
from research_defence import HERE,ROOT,archive
SEEDS={
 'infrastructure':[
 ('IRB','Roads & highways','https://www.irb.co.in/home/projects/','IRB lists operational and development road concessions. Project concession exposure is not direct ownership of all InvIT assets or an inference that announced projects are operational.',['toll','operational']),
 ('LT','Civil EPC','https://www.larsentoubro.com/businesses','Larsen & Toubro describes infrastructure EPC and heavy civil construction. Contract execution is distinct from permanent ownership or operation of completed infrastructure.',['heavy civil','infrastructure']),
 ('KEC','Urban infrastructure','https://www.kecrpg.com/urban-infra-projects','KEC documents metro construction projects. Urban construction exposure does not imply ownership of the metro operator or all city infrastructure.',['metro','construction']),
 ('ULTRACEMCO','Construction materials','https://www.ultratechcement.com/corporate/media/press-kit','UltraTech manufactures cement and ready-mix concrete used in construction. Material supply is distinct from civil EPC or owning the infrastructure customer.',['cement','concrete']),
 ('ADANIPORTS','Infrastructure operators','https://www.adaniports.com/about-us','APSEZ describes port and terminal operations with integrated logistics. Operations are distinct from EPC contracting; no assumed ownership of all Adani group infrastructure or quantified pure-play revenue.',['ports','terminals'])],
 'logistics':[
 ('ADANIPORTS','Ports & shipping','https://www.adaniports.com/ports-and-terminals','Port and terminal operations establish port logistics exposure. This does not imply ownership of customer shipping fleets or make the company a pure-play ocean carrier.',['ports','cargo']),
 ('MAHLOG','Warehousing','https://mahindralogistics.com/contract-logistics/warehousing-solutions/','Mahindra Logistics describes inventory, storage and warehouse management services. Managed warehouse space is not assumed to be company-owned real estate.',['warehousing','inventory']),
 ('TCI','Road logistics','https://nsearchives.nseindia.com/corporate/ak_bansal_tcil_com_26052026185318_TCIL.pdf','Transport Corporation of India describes TCI Freight surface-transport services. This is the listed TCI operating business, not a consolidation of separately listed TCI Express after demerger.',['tci freight','surface transport']),
 ('INDIGO','Aviation','https://nsearchives.nseindia.com/corporate/Indigo1_10032026192647_Disclosure.pdf','Issuer identifies InterGlobe Aviation Limited as IndiGo airline. This role is airline operations, not ownership of the broader InterGlobe hospitality and logistics group or an airport operator.',['interglobe aviation limited','airline']),
 ('BLUEDART','Express delivery','https://www.bluedart.com/web/guest/about-bluedart','Blue Dart describes express air and integrated transportation/distribution services. Its DHL relationship does not attribute the global DHL network revenues to the Indian listed company.',['blue dart express','express'])]}

def main():
    ids={m['symbol']:m for t in json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))['indices'].values() for m in t.get('members',[])}
    quotes=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))
    names={'TCI':'Transport Corporation of India Limited','BLUEDART':'Blue Dart Express Limited','MAHLOG':'Mahindra Logistics Limited'}
    for isin,q in quotes['prices'].items():
        if q['symbol'] in names and q['symbol'] not in ids:ids[q['symbol']]={'company':names[q['symbol']],'isin':isin,'identity_source':'Official NSE EQ bhavcopy '+quotes['date']+'; company name from primary business disclosure'}
    for family,seeds in SEEDS.items():
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:members=list(pool.map(lambda s:archive(s,ids,'2026-10-29'),seeds))
        d={'family':family,'status':'initial_examples_for_review','reviewed_on':'2026-10-29','note':'Five independently researched value-chain examples; not an exhaustive listed universe. No paid holdings, weights, historical membership, asset ownership or revenue materiality inferred.','comparison_note':'Construction, concessions, material supply and operations have different economics; logistics also distinguishes asset operators from service providers. This is not a homogeneous growth or valuation peer group.','members':members}
        (ROOT/(family+'.json')).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');print(family,json.dumps({m['symbol']:m['status'] for m in members}))

if __name__=='__main__':main()
