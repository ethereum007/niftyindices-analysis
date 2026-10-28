"""Archive bounded mobility supplier examples with technology and group boundaries."""
import concurrent.futures,json
from research_defence import HERE,ROOT,archive
REVIEWED='2026-10-28'
SEEDS=[
 ('SUNDRMFAST','Auto ancillaries','https://sundram.com/about-us.php','Fasteners, powertrain parts and pumps establish automotive-component exposure. The company also serves infrastructure, wind and aviation; automotive-only revenue or EV-only exposure is not inferred.',['automotive','fasteners','pumps']),
 ('SONACOMS','EV powertrain','https://sonacomstar.com/innovation-company','Differential assemblies and traction-motor development establish EV-powertrain capability. The source distinguishes commercial differential production from development-stage applications; development is not treated as commercial revenue or a current order book.',['differential','traction motors']),
 ('EXIDEIND','Batteries & charging','https://www.exideindustries.com/about/subsidiaries.aspx','The listed parent has battery exposure and describes wholly owned Exide Energy Solutions, including advanced-chemistry cells/modules/packs and prior pack operations. Subsidiary activity is not standalone-parent sales; no cell-plant commissioning status, current utilisation or charging-network ownership is inferred.',['exide energy solutions','battery','subsidiary']),
 ('UNOMINDA','Vehicle electronics','https://www.unominda.com/','Switches, sensors, lighting and infotainment offerings establish vehicle-electronics exposure. The portfolio spans vehicle technologies and group operations; this is not evidence of EV-only revenue or ownership of vehicle OEMs.',['switch','sensor','infotainment']),
 ('APOLLOTYRE','Tyres','https://corporate.apollotyres.com/who-we-are/our-brands/','Apollo and Vredestein product ranges establish tyre exposure across passenger, commercial and other vehicles. Replacement demand differs from new-vehicle production; the portfolio is not classified as EV-only and brand reach does not establish current volume growth.',['vredestein','passenger','commercial'])]
def main():
    ROOT.mkdir(exist_ok=True);(ROOT/'raw').mkdir(exist_ok=True)
    source=json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))
    identities={m['symbol']:m for t in source['indices'].values() for m in t.get('members',[])}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(lambda seed:archive(seed,identities,REVIEWED),SEEDS))
    data={'family':'mobility','status':'initial_examples_for_review','reviewed_on':REVIEWED,
          'note':'Five independent current-role examples, not exhaustive membership, an EV pure-play basket or a product-commercialisation forecast. No weights, historical membership or quantified revenue share inferred.',
          'comparison_note':'Components, powertrain systems, batteries, electronics and tyres have different demand and input-cost drivers. Product development is not commercial sales; this is not a homogeneous EV valuation peer group.',
          'members':records}
    (ROOT/'mobility.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(json.dumps({r['symbol']:r['status'] for r in records}))
if __name__=='__main__':main()
