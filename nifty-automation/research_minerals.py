"""Archive distinct minerals/materials roles; no uniform critical-mineral purity implied."""
import concurrent.futures,json
from research_defence import HERE,ROOT,archive
REVIEWED='2026-10-28'
SEEDS=[
 ('HINDCOPPER','Critical mineral producers','https://hindustancopper.com/Page/CompanyProfile','Copper exploration, mining and beneficiation establish producer exposure. The corporate profile says smelting/refining at Jhagadia and Ghatsila has been suspended since 2019; historical integrated facilities are not treated as currently operating refining capacity. No reserve value or critical-mineral-only revenue share is inferred.',['copper','suspended','2019']),
 ('GRAPHITE','Specialty materials','https://www.graphiteindia.com/investors/documents/654e043d76c71REVISED_EP_30092023.pdf','The 2023 corporate disclosure establishes graphite electrode capability for electric-arc steelmaking. Synthetic electrodes are not classified as natural graphite mining or proven battery-anode sales; historical capability does not establish current product mix.',['graphite electrodes','electric arc']),
 ('NATIONALUM','Processing & refining','https://www.dpe.gov.in/static/uploads/2025/08/5b8897f2dffacc1c0c807c4468585237.pdf','A historical government DPE company profile documents bauxite mining, alumina refining and aluminium smelting as an integrated processing chain; this older capability source does not establish present output. Aluminium exposure is not a lithium or rare-earth production claim, and no current capacity utilisation or commodity-price forecast is inferred.',['bauxite','alumina','smelter']),
 ('GRAVITA','Recycling','https://www.gravitaindia.com/about-us','Lead battery, aluminium, plastic and tyre recycling establish secondary-material processing exposure. Recycling is not ownership of virgin mineral reserves; emerging battery-material activity is not assigned a quantified revenue share.',['lead','aluminium','recycling']),
 ('BEML','Mining equipment','https://www.bemlindia.in/mining-construction/','Mining machinery such as excavators and dump trucks establishes equipment-supplier exposure. BEML is not classified as a mineral-reserve owner or mining pure play; rail and defence activities remain distinct.',['mining','excavators','dump trucks'])]
def main():
    ROOT.mkdir(exist_ok=True);(ROOT/'raw').mkdir(exist_ok=True)
    source=json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))
    identities={m['symbol']:m for t in source['indices'].values() for m in t.get('members',[])}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(lambda seed:archive(seed,identities,REVIEWED),SEEDS))
    data={'family':'minerals','status':'initial_examples_for_review','reviewed_on':REVIEWED,
          'note':'Five independently researched proposed roles, not exhaustive membership, statutory critical-mineral classification or quantified revenue exposure. Source keywords only check archived evidence; no weights or historical membership inferred.',
          'comparison_note':'Producers, processors, synthetic-material makers, recyclers and equipment suppliers have different economics. This is not a pure-play critical-minerals basket or homogeneous valuation peer group.',
          'members':records}
    (ROOT/'minerals.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(json.dumps({r['symbol']:r['status'] for r in records}))
if __name__=='__main__':main()
