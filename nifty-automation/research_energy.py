"""Bounded primary evidence for energy-transition and grid company examples."""
import concurrent.futures
import json
from research_defence import HERE,ROOT,archive

REVIEWED='2026-10-28'
SEEDS=[
 ('WAAREEENER','Solar value chain','https://www.waaree.com/press-release/waaree-energies-emerges-as-indias-largest-almm-approved-solar-manufacturer-crossing-20-gw/','Solar-module manufacturing establishes solar supply-chain exposure. No generation-utility or full-group revenue is attributed to the listed entity.',['solar','module']),
 ('SUZLON','Wind equipment','https://www.suzlon.com/our-businesses/products/wind/','Wind-turbine generator products establish wind-equipment exposure; stock-price changes do not measure wind project economics.',['wind','turbine']),
 ('EXIDEIND','Storage & batteries','https://www.exideindustries.com/about/subsidiaries.aspx','Stationary energy storage and lithium-ion modules/packs are disclosed through Exide subsidiaries. The parent also has conventional battery businesses; lithium-ion revenue materiality and commissioning status are not inferred.',['li-ion','stationary']),
 ('CGPOWER','Transmission equipment','https://www.cgglobal.com/about_cg','Power transformers and switchgear establish transmission-equipment exposure within a diversified company. This overlaps AI examples without establishing renewable-only revenue.',['transformer','switchgear']),
 ('POWERGRID','Grid modernisation','https://www.powergrid.in/en/transmission','Transmission-asset operations and adoption of technology establish grid infrastructure exposure. Not all transmission assets are dedicated to renewable energy.',['transmission','technology'])]

def main():
    ROOT.mkdir(exist_ok=True);(ROOT/'raw').mkdir(exist_ok=True)
    sources=json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))
    identities={m['symbol']:m for t in sources['indices'].values() for m in t.get('members',[])}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records=list(pool.map(lambda seed:archive(seed,identities,REVIEWED),SEEDS))
    manifest={'family':'cleanenergy','status':'initial_examples_for_review','reviewed_on':REVIEWED,
              'note':'Five proposed company examples for energy-transition/grid research, not an exhaustive clean-energy universe or pure-play revenue screen. Subsidiary exposure and conventional-energy operations are explicitly retained. Archive keyword checks are not an automated exposure classifier; failed checks remain pending. No adjusted history, fundamentals, weights or historical membership inferred.',
              'members':records}
    (ROOT/'cleanenergy.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({r['symbol']:r['status'] for r in records}))

if __name__=='__main__':main()
