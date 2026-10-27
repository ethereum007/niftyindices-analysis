"""Bounded primary-source evidence batch for manufacturing research examples."""
import concurrent.futures
import json
from research_defence import HERE,ROOT,archive

REVIEWED='2026-10-28'
SEEDS=[
 ('KAYNES','Electronics manufacturing','https://kaynestechnology.co.in/','Integrated electronics manufacturing and design services establish manufacturing exposure; this overlaps the AI examples without implying AI-specific revenue.',['electronics','manufactur']),
 ('ABB','Industrial automation','https://www.abb.com/global/en/news/135616/abb-india-posts-solid-start-to-cy2026-with-strong-order-momentum-in-first-jan-mar-quarter','ABB India disclosed industrial automation projects and electrification/motion business activity. No separate group subsidiary or robotics revenue is attributed to the listed company.',['abb india','automation']),
 ('LT','Capital equipment','https://www.larsentoubro.com/heavy-engineering/about-us/','Larsen & Toubro heavy engineering manufactures engineered-to-order industrial equipment within a diversified parent. This does not quantify manufacturing revenue share.',['equipment','engineering']),
 ('DYNAMATECH','Precision engineering','https://www.dynamatics.com/aerospace.aspx','Complex flight-critical aerostructures establish precision manufacturing exposure, including both defence and civil customers.',['aerostruct','airbus']),
 ('DIXON','Contract manufacturing','https://www.dixoninfo.com/innovation-hub/digital-transformation','Dixon describes electronics manufacturing services and its manufacturing operations; automation used internally does not establish an automation-products business.',['manufacturing','ems'])]

def main():
    ROOT.mkdir(exist_ok=True);(ROOT/'raw').mkdir(exist_ok=True)
    sources=json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))
    identities={m['symbol']:m for t in sources['indices'].values() for m in t.get('members',[])}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records=list(pool.map(lambda seed:archive(seed,identities,REVIEWED),SEEDS))
    manifest={'family':'manufacturing','status':'initial_examples_for_review','reviewed_on':REVIEWED,
              'note':'Five independently researched examples, not an exhaustive manufacturing universe. Company exposure is distinct from the use of manufacturing technology internally. No weights, historical membership or fundamental statistics inferred. Keyword checks validate archive content only; source claims require research review.',
              'members':records}
    (ROOT/'manufacturing.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({r['symbol']:r['status'] for r in records}))

if __name__=='__main__':main()
