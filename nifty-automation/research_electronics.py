"""Distinguish assembly, design, packaging, components and industrial sensors."""
import json,concurrent.futures
from research_defence import HERE,ROOT,archive
SEEDS=[
 ('KAYNES','EMS & assembly','https://kaynestechnology.co.in/','Kaynes describes electronics manufacturing and design services. EMS assembly is distinct from semiconductor wafer fabrication and does not quantify AI revenue.',['electronics','manufactur']),
 ('MOSCHIP','Semiconductor design','https://moschip.com/silicon-engineering-services/','MosChip describes turnkey ASIC and silicon design services. Design exposure is distinct from owning a wafer fabrication plant or the foundry partners of clients.',['design','asic']),
 ('CGPOWER','OSAT & packaging','https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=2093860&lang=2&reg=3','January2025 government disclosure identifies CG Power and CG Semi semiconductor assembly/test project. This is subsidiary/JV project exposure, not parent-only semiconductor revenue; this source alone does not establish subsequent commercial production or capacity utilisation.',['cg power','osat']),
 ('DCXINDIA','Electronic components','https://dcxindia.com/dcx-advantage/capabilities/','DCX documents cable/wire harness, PCB assembly and electronic subsystem integration. These are electronic interconnect/assembly capabilities, not fabrication of every discrete component or semiconductor chip.',['cable','wire harness','pcb']),
 ('HONAUT','Industrial electronics','https://www.honeywell.com/in/en/hail','Honeywell issuer profile explicitly identifies listed Honeywell Automation India and its sensing, control and integrated automation products. This supports industrial-electronics exposure; all global Honeywell revenue and current certificate validity are not inferred.',['honeywell automation india limited','sensing'])]

def main():
    ids={m['symbol']:m for t in json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))['indices'].values() for m in t.get('members',[])}
    quotes=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'));names={'MOSCHIP':'MosChip Technologies Limited','DCXINDIA':'DCX Systems Limited'}
    for isin,q in quotes['prices'].items():
        if q['symbol'] in names and q['symbol'] not in ids:ids[q['symbol']]={'company':names[q['symbol']],'isin':isin,'identity_source':'Official NSE EQ bhavcopy '+quotes['date']+'; company name from primary corporate disclosure'}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:members=list(pool.map(lambda s:archive(s,ids,'2026-10-29'),SEEDS))
    d={'family':'electronics','status':'initial_examples_for_review','reviewed_on':'2026-10-29','note':'Five independently researched business-role examples; not exhaustive electronics membership. Historical capability and project evidence are explicitly labelled; no weights, historical membership, commercial-production status or theme revenue share inferred.','comparison_note':'EMS, fabless design, OSAT project exposure, interconnect/assembly and industrial sensors are distinct roles. Packaging is not wafer fabrication. This is not a homogeneous valuation or growth peer group.','members':members}
    (ROOT/'electronics.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');print(json.dumps({m['symbol']:m['status'] for m in members}))

if __name__=='__main__':main()
