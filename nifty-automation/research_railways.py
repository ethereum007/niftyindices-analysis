"""Primary evidence for initial rail investment value-chain company examples."""
import concurrent.futures
import json
from research_defence import HERE,ROOT,archive

REVIEWED='2026-10-28'
SEEDS=[
 ('TITAGARH','Rolling stock','https://www.titagarh.in/service/railway-freight','Freight-wagon and rolling-stock manufacturing establishes railway-equipment exposure. No present order-book value or delivery forecast is inferred.',['freight','wagon']),
 ('KEC','Rail electrification','https://www.kecrpg.com/railways','Railway EPC offerings include overhead electrification and traction substations. KEC also operates in other infrastructure segments; rail revenue materiality is not quantified.',['electrification','railway']),
 ('HBLENGINE','Signalling & safety','https://www.hbl.in/reports/kavachorder01052025.pdf','A primary Kavach order disclosure establishes train-protection-system exposure. This is historical capability/order evidence, not a claim about current unexecuted order value; other businesses remain.',['kavach','railway']),
 ('IRCON','Rail EPC','https://www.ircon.org/','Railway construction and turnkey infrastructure activity establish rail-EPC exposure. No pure-play rail revenue percentage is inferred.',['railway','construction']),
 ('CONCOR','Freight infrastructure','https://www.pib.gov.in/PressReleasePage.aspx?PRID=2298580&lang=2&reg=48','A government port disclosure names CONCOR among container-train operators supporting rail-connectivity initiatives. This establishes freight-logistics exposure, not ownership of port assets or a quantified infrastructure-spend sensitivity.',['concor','rail'])]

def main():
    ROOT.mkdir(exist_ok=True);(ROOT/'raw').mkdir(exist_ok=True)
    sources=json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))
    identities={m['symbol']:m for t in sources['indices'].values() for m in t.get('members',[])}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records=list(pool.map(lambda seed:archive(seed,identities,REVIEWED),SEEDS))
    manifest={'family':'railways','status':'initial_examples_for_review','reviewed_on':REVIEWED,
              'note':'Five independently researched examples, not an exhaustive rail investment universe. Older source disclosures establish business capability only, not current order values, historical membership or pure-play revenue. No weights, stock-history returns or fundamental statistics inferred.',
              'members':records}
    (ROOT/'railways.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({r['symbol']:r['status'] for r in records}))

if __name__=='__main__':main()
