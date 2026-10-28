"""Archive housing ecosystem business roles without inferring a housing upcycle."""
import concurrent.futures
import json
from research_defence import HERE,ROOT,archive

REVIEWED='2026-10-28'
SEEDS=[
 ('DLF','Residential developers','https://www.dlf.in/homes/','Residential project offerings establish developer exposure. Listings do not establish current sales bookings, project completion, ownership of every group asset or a measured housing-demand upcycle.',['residential','dlf']),
 ('ULTRACEMCO','Building materials','https://www.ultratechcement.com/about-us/overview','Cement and ready-mix concrete establish building-material exposure. Demand also comes from non-housing construction; no housing-only revenue share or utilisation trend is inferred.',['cement','concrete']),
 ('LICHSGFIN','Housing finance','https://www.lichousing.com/housing-loan','Housing-loan products establish mortgage-lending exposure at LIC Housing Finance. It is distinct from LIC the listed insurer, and is not classified as the property developer or owner of financed homes.',['housing','loan']),
 ('ASIANPAINT','Home improvement','https://www.asianpaints.com/products/paints-and-textures.html','Interior/exterior painting products and services establish home-improvement exposure. Repainting can differ from new housing demand; no volume or profitability recovery is inferred.',['paint','interior']),
 ('PHOENIXLTD','Commercial property','https://careers.thephoenixmills.com/knowOurStory','The company describes retail-led mixed-use development across commercial and other asset classes. The listed corporate group is not labelled as a REIT, nor is every property attributed as directly owned by the parent.',['retail','commercial'])]

def main():
    ROOT.mkdir(exist_ok=True);(ROOT/'raw').mkdir(exist_ok=True)
    sources=json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))
    identities={m['symbol']:m for t in sources['indices'].values() for m in t.get('members',[])}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records=list(pool.map(lambda seed:archive(seed,identities,REVIEWED),SEEDS))
    manifest={'family':'housing','status':'initial_examples_for_review','reviewed_on':REVIEWED,
              'note':'Five housing-ecosystem examples, not a homogeneous real-estate valuation group, an exhaustive universe or a housing-demand forecast. Developers, materials, mortgage lenders, improvement products and commercial operators have different operating and financial metrics. No customer/loan records, weights or historical membership inferred.',
              'comparison_note':'This is a housing ecosystem exposure map, not evidence of a current housing upcycle. A mortgage lender, cement producer and property developer are not interchangeable revenue-growth or valuation peers.',
              'members':records}
    (ROOT/'housing.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({r['symbol']:r['status'] for r in records}))

if __name__=='__main__':main()
