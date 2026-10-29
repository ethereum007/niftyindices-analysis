"""Audit legacy AI examples with the same immutable primary-evidence contract."""
import json,concurrent.futures
from research_defence import HERE,ROOT,archive
SEEDS=[
 ('NETWEB','AI compute hardware','https://www.netwebindia.com/investors/press-release/Intimation_of_Press_release_AMD_Make-in-India_Servers.pdf','Netweb June2024 issuer release describes servers supporting AI/ML workloads. This is documented hardware capability, not quantified AI revenue, current shipments or ownership of processor designs.',['netweb','ai']),
 ('ANANTRAJ','Data centres','https://nsearchives.nseindia.com/corporate/ANANTRAJ_21012026201339_Outcome_Jan_2026.pdf','Anant Raj January2026 issuer disclosure describes data-centre business through Anant Raj Cloud. Diversified-parent exposure includes subsidiary operations; announced capacity and future phases are not all commissioned or currently utilised.',['anant raj','data']),
 ('BLUESTARCO','Cooling & HVAC','https://www.bluestarindia.com/products/central-air-conditioning/chillers/data-center-chillers','Blue Star describes chillers designed for data centres. Product capability is distinct from operating data centres or quantified AI-specific revenue; vendor performance claims are not independent measurements.',['data center chillers','chilled']),
 ('STLTECH','Fibre & connectivity','https://stl.tech/solutions/optical-connectivity-solutions/','Sterlite Technologies describes optical fibre and connectivity products. Connectivity exposure is not quantified AI revenue or ownership of telecom operators, cloud platforms or customer networks.',['optical','fibre']),
 ('TATAELXSI','Embedded design','https://nsearchives.nseindia.com/corporate/TELNSE_05032026164002_Reg30PressRelease05032026.pdf','Tata Elxsi March2026 disclosure describes automotive AI software development. Engineering service capability is distinct from manufacturing vehicles or quantified AI revenue; customer deployment and commercial volumes are not inferred.',['tata elxsi','ai'])]
def main():
    q=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))
    names={'NETWEB':'Netweb Technologies India Limited','ANANTRAJ':'Anant Raj Limited','BLUESTARCO':'Blue Star Limited','STLTECH':'Sterlite Technologies Limited','TATAELXSI':'Tata Elxsi Limited'}
    ids={v['symbol']:{'company':names[v['symbol']],'isin':k,'identity_source':'Official NSE EQ bhavcopy '+q['date']+'; name from primary corporate disclosure'} for k,v in q['prices'].items() if v['symbol'] in names}
    ids['STLTECH']={'company':'Sterlite Technologies Limited','isin':'INE089C01029','identity_source':'Official NSE integrated issuer filing approved29April2026, filed6May2026; latest local EQ quote unavailable'}
    identity=archive(('STLTECH','Issuer identity','https://nsearchives.nseindia.com/corporate/ixbrl/INTEGRATED_FILING_INDAS_155756_06052026125624_iXBRL_WEB.html','NSE filing explicitly identifies listed symbol STLTECH and ISIN INE089C01029. Latest local EQ quote unavailable; do not substitute separately listed STLNETWORK.',['stltech','ine089c01029']),ids,'2026-10-29')
    if identity['status']!='evidence_archived':raise ValueError('STLTECH identity evidence unavailable')
    (ROOT/'identity').mkdir(exist_ok=True)
    (ROOT/'identity/STLTECH.json').write_text(json.dumps(identity,indent=2)+'\n',encoding='utf-8')
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:members=list(p.map(lambda s:archive(s,ids,'2026-10-29'),SEEDS))
    d={'family':'ai','status':'initial_examples_for_review','reviewed_on':'2026-10-29','note':'Five independently researched bounded business-role examples; not an exhaustive listed universe. No paid holdings, weights, historical membership or quantified AI revenue inferred.','comparison_note':'Computing hardware, data-centre subsidiaries, cooling, optical connectivity and software design have different business models. This is not a homogeneous valuation or growth peer group.','members':members}
    (ROOT/'ai.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
    print({m['symbol']:(m['status'],m.get('error'),m.get('keyword_checks')) for m in members})
if __name__=='__main__':main()
