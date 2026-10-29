"""Primary business-role maps for water/waste, chemicals and services."""
import json,concurrent.futures
from research_defence import HERE,ROOT,archive
SEEDS={
 'waterwaste':[
 ('IONEXCHANG','Water treatment','https://ionexchangeglobal.com/','Ion Exchange describes water and environment management solutions. Treatment equipment/chemicals and services do not establish ownership of municipal water utilities.',['water','treatment']),
 ('WABAG','Wastewater EPC','https://www.wabag.com/total-water-solution/effluent-treatment/','WABAG describes effluent-treatment EPC and design/build/operate models. Project execution and operating contracts are distinct from permanent ownership of client utilities; no current backlog inferred.',['effluent','epc']),
 ('KSB','Pumps & fluid handling','https://www.ksb.com/en-in/about-ksb','KSB Limited issuer profile describes centrifugal pumps and industrial valves. This is equipment exposure serving water and other industries, not a pure-play water utility or quantified water revenue.',['pump','fluid']),
 ('AWHCL','Solid waste services','https://antony-waste.com/','Antony Waste Handling Cell describes waste-management services. Municipal service contracts and processing are not treated as ownership of all municipal waste infrastructure or guaranteed renewals.',['waste','management']),
 ('GRAVITA','Resource recovery','https://www.gravitaindia.com/Upload/PDF/gravita-starts-plastic-recycling-plant-tanzania.pdf','Gravita issuer disclosure identifies recycled polypropylene production through a Tanzania step-down subsidiary. This supports recycling/resource recovery, not standalone-parent-only production or every proposed recycling line.',['gravita india limited','recycled'])],
 'chemicals':[
 ('SRF','Specialty chemicals','https://www.srf.com/business-solutions/specialty-chemicals','SRF describes development and manufacturing of advanced specialty intermediates. Its diversified films/textiles businesses are not silently attributed to specialty-chemical revenue.',['specialty','intermediates']),
 ('UPL','Agrochemicals','https://www.upl-ltd.com/investors/corporate-governance','UPL describes sustainable agriculture products and crop protection. Group product exposure is not product registration in every jurisdiction or current crop-cycle growth.',['crop protection','agriculture']),
 ('NAVINFLUOR','Fluorochemicals','https://nsearchives.nseindia.com/corporate/NAVINFLUOR_07052025020148_NFIL-Intimation-Joint_Press_Release-signed.pdf','Navin Fluorine describes fluorine chemistry and fluorochemical businesses. Capability does not establish commercial volumes for every development molecule or customer programme.',['fluorine','chemical']),
 ('TATACHEM','Commodity chemicals','https://www.tatachemicals.com/','Tata Chemicals documents basic chemistry and soda-ash related business. This is materials/chemical production, not all Tata group businesses or pure-play specialty-chemical exposure.',['soda ash','chemistry']),
 ('LINDEINDIA','Industrial gases','https://www.linde.in/','Linde India supplies industrial gases and engineering solutions. Indian listed-company exposure is distinct from all global Linde revenue and does not imply ownership of customers using the gases.',['industrial','gases'])],
 'services':[
 ('ECLERX','Business services','https://nsearchives.nseindia.com/corporate/ECLERX_13052026193401_BSENSEPR310326.pdf','eClerx describes analytics, digital operations and business-process management services. Client data processing is not ownership of client businesses, and no current AI-specific revenue share is inferred.',['eclerx services','business process']),
 ('TEAMLEASE','Staffing','https://group.teamlease.com/about-teamlease/','TeamLease describes staffing and workforce services. Associates deployed at client sites are distinct from the company owning client operating assets; no current placements or headcount growth inferred.',['teamlease','staffing']),
 ('SIS','Facility services','https://sisindia.com/facility-management-solutions/','SIS describes facility-management solutions delivered through group operating businesses. Managed premises are not company-owned real estate and facility services are distinct from security guarding and cash logistics.',['facility management','sis']),
 ('NAUKRI','Professional platforms','https://www.infoedge.in/About/Overview','Info Edge describes recruitment marketplaces including Naukri. Platform services are distinct from staffing payroll/employer-of-record operations and minority investee revenue is not direct operating revenue.',['naukri','recruitment']),
 ('FSL','Service outsourcing','https://www.firstsource.com/newsroom/press-releases/firstsource-unveils-unbpo-a-bold-redefinition-of-business-process-outsourcing','Firstsource describes business-process and customer-experience outsourcing. Service capability is not ownership of clients or independently verified savings and automation success for every engagement.',['business process','firstsource'])]}

def main():
    ids={m['symbol']:m for t in json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))['indices'].values() for m in t.get('members',[])}
    quotes=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'));names={'AWHCL':'Antony Waste Handling Cell Limited','TEAMLEASE':'TeamLease Services Limited','SIS':'SIS Limited','ECLERX':'eClerx Services Limited'}
    for isin,q in quotes['prices'].items():
        if q['symbol'] in names and q['symbol'] not in ids:ids[q['symbol']]={'company':names[q['symbol']],'isin':isin,'identity_source':'Official NSE EQ bhavcopy '+quotes['date']+'; company name from primary corporate disclosure'}
    for family,seeds in SEEDS.items():
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:members=list(pool.map(lambda s:archive(s,ids,'2026-10-29'),seeds))
        d={'family':family,'status':'initial_examples_for_review','reviewed_on':'2026-10-29','note':'Five independently researched business-role examples; not an exhaustive listed universe. No holdings, weights, historical membership, client records or quantified theme revenue inferred.','comparison_note':'These roles differ in assets, contracts, regulatory exposure and revenue recognition. Group/subsidiary and managed-client-asset boundaries are explicit. This is not a homogeneous valuation or growth peer group.','members':members}
        (ROOT/(family+'.json')).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');print(family,json.dumps({m['symbol']:m['status'] for m in members}))

if __name__=='__main__':main()
