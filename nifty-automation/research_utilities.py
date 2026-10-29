"""Utilities value-chain role examples, separating assets, equipment and trading."""
import json,concurrent.futures
from research_defence import HERE,ROOT,archive
SEEDS=[
 ('NTPC','Power generation','https://ntpc.co.in/about-us','NTPC describes conventional and renewable electricity generation. Diversification and future capacity targets are not treated as commissioned assets or current renewable revenue share.',['power generation','ntpc']),
 ('TORNTPOWER','Distribution utilities','https://www.torrentpower.com/index.php/site/info/aboutUs','Torrent Power describes an integrated generation, transmission and distribution business. Distribution exposure is not pure-play revenue, and service areas are not assumed to be owned land or monopoly rights everywhere.',['distribution','torrent power']),
 ('POWERGRID','Transmission','https://powergrid.in/en/transmission','Power Grid documents electricity transmission assets and HVDC links. Transmission infrastructure is distinct from electricity generation or equipment manufacturing; no current asset-base growth inferred.',['transmission','hvdc']),
 ('ABB','Power equipment','https://www.abb.com/global/en/news/135616/abb-india-posts-solid-start-to-cy2026-with-strong-order-momentum-in-first-jan-mar-quarter','ABB India reports electrification and motion business activity. This is listed-company equipment exposure adjacent to utilities, not ownership of the utilities supplied or all global ABB business.',['abb india','electrification']),
 ('PTC','Energy trading','https://www.ptcindia.com/about-us/the-concept-of-ptc/','PTC India describes licensed trading of power. Electricity trading is distinct from a power exchange and from generation capacity; traded volumes are not net revenue or company-owned output.',['ptc india','trading'])]

def main():
    identities={m['symbol']:m for t in json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))['indices'].values() for m in t.get('members',[])}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:members=list(pool.map(lambda s:archive(s,identities,'2026-10-29'),SEEDS))
    d={'family':'utilities','status':'initial_examples_for_review','reviewed_on':'2026-10-29','note':'Five independently researched business-role examples; not exhaustive utilities membership. No weights, historical membership, capacity forecast achievement or quantified theme revenue inferred.','comparison_note':'Generation, distribution, transmission assets, equipment manufacturing and power trading differ in regulation, asset intensity and revenue recognition. This is a value-chain map, not a homogeneous valuation peer group.','members':members}
    (ROOT/'utilities.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');print(json.dumps({m['symbol']:m['status'] for m in members}))

if __name__=='__main__':main()
