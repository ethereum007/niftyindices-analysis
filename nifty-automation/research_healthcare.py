"""Archive healthcare business exposure; no patient information or clinical inference."""
import concurrent.futures,json
from research_defence import HERE,ROOT,archive
REVIEWED='2026-10-28'
SEEDS=[
 ('MAXHEALTH','Hospitals','https://nsearchives.nseindia.com/corporate/MAXHEALTH_21052026163255_SE_Intimation_Final.pdf','Hospital operations establish care-delivery exposure. Network facilities include varying ownership and operating arrangements; network size is not direct ownership of every property, current occupancy or patient volume growth. Homecare and pathology activity are not ignored.',['max healthcare institute','hospitals']),
 ('LALPATHLAB','Diagnostics','https://www.lalpathlabs.com/about-us','Diagnostic testing services establish pathology exposure. Test capability and laboratory reach are not current patient-volume growth or a clinical accuracy comparison; the listed company is not treated as a drug manufacturer.',['diagnostic','tests']),
 ('SUNPHARMA','Pharma manufacturers','https://sunpharma.com/products/','Generics, specialty products and API offerings establish pharmaceutical product exposure. A portfolio listing does not establish approval in every jurisdiction, clinical efficacy, current launch sales or ownership of every molecule patent.',['generics','special','active pharmaceutical']),
 ('SYNGENE','Contract research','https://esgreport.syngeneintl.com/about-syngene.html','The corporate sustainability report describes research, development and manufacturing services. Providing discovery services does not establish ownership of client drug intellectual property, successful clinical outcomes or current contracted backlog.',['research','development','manufacturing']),
 ('POLYMED','Medical equipment','https://www.polymedicure.com/about-us/','Medical-device manufacturing including infusion and blood-collection products establishes consumables/device exposure. This example is not classified as a hospital operator or assumed to manufacture every category of large diagnostic equipment.',['medical','infusion','blood'])]
def main():
    ROOT.mkdir(exist_ok=True);(ROOT/'raw').mkdir(exist_ok=True)
    source=json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))
    identities={m['symbol']:m for t in source['indices'].values() for m in t.get('members',[])}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(lambda seed:archive(seed,identities,REVIEWED),SEEDS))
    data={'family':'healthcare','status':'initial_examples_for_review','reviewed_on':REVIEWED,
          'note':'Five independent business-role examples, not exhaustive healthcare membership or clinical recommendations. Only public corporate material archived; no patient records, test results, enquiries or bookings accessed. No weights or historical membership inferred.',
          'comparison_note':'Hospitals, laboratories, pharmaceutical products, contract services and device consumables have different economics and regulatory exposures. This is a business-role map, not a homogeneous revenue-growth or valuation peer group, or a clinical-quality ranking.',
          'members':records}
    (ROOT/'healthcare.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    print(json.dumps({r['symbol']:r['status'] for r in records}))
if __name__=='__main__':main()
