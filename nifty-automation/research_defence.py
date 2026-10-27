"""Archive public primary evidence for the first independently mapped defence examples.

This creates a review dataset, not historical membership or a complete defence universe.
"""
import concurrent.futures
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request,urlopen

HERE=Path(__file__).parent
ROOT=HERE/'data/theme-research'
SEEDS=[
 ('HAL','Aerospace & engines','https://www.pib.gov.in/PressReleasePage.aspx?PRID=1707214&lang=2&reg=48','Aircraft, helicopter and related service offerings support aerospace exposure. Defence-only revenue share is not inferred.',['aircraft','helicopter']),
 ('BEL','Defence electronics','https://www.pib.gov.in/PressReleasePage.aspx?PRID=1910393&lang=2&reg=48','Defence radar and electronic-warfare products establish defence-electronics exposure.',['radar','warfare']),
 ('MAZDOCK','Shipbuilding','https://www.mazagondock.in/English/modernization','Warship and submarine construction facilities establish naval shipbuilding exposure.',['warship','submarine']),
 ('DYNAMATECH','Precision components','https://www.dynamatics.com/aerospace.aspx','Flight-critical aerostructures for aerospace OEMs establish precision-aerospace exposure; the parent also serves civil aerospace and other businesses.',['aerostruct','airbus']),
 ('IDEAFORGE','Drones','https://ideaforgetech.com/lp/indigenize-with-ideaforge','UAV products serving armed forces and industrial applications establish dual-use drone exposure.',['armed forces','drone'])]

def archive(seed,identities):
    symbol,subtheme,url,rationale,keywords=seed
    record={'symbol':symbol,'subtheme':subtheme,'source_url':url,'rationale':rationale,
            'reviewed_on':'2026-10-27','effective_date':None,'exposure_materiality':'Not quantified',
            'identity_source':identities[symbol].get('identity_source','Current official Nifty constituent archive; not historical membership'),
            **{k:identities[symbol][k] for k in ('company','isin')}}
    try:
        with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0 IndexIntelligence public-source research'}),timeout=20) as response:
            raw=response.read(8_000_001)
            if len(raw)>8_000_000:raise ValueError('Evidence page exceeds bounded archive size')
            if response.status!=200:raise ValueError('Non-200 evidence page')
            record['resolved_url']=response.url
        sha=hashlib.sha256(raw).hexdigest();(ROOT/'raw'/f'{sha}.html').write_bytes(raw)
        record.update(sha256=sha,retrieved_utc=datetime.now(timezone.utc).isoformat())
        content=raw.decode('utf-8',errors='replace').lower()
        record['keyword_checks']={k:k in content for k in keywords}
        record['status']='evidence_archived' if all(record['keyword_checks'].values()) else 'manual_page_review_required'
    except Exception as exc:record.update(status='fetch_failed',error=str(exc))
    return record

def main():
    ROOT.mkdir(exist_ok=True);(ROOT/'raw').mkdir(exist_ok=True)
    sources=json.loads((HERE/'data/constituents/latest.json').read_text(encoding='utf-8'))
    identities={m['symbol']:m for t in sources['indices'].values() for m in t.get('members',[])}
    stocks=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))
    for isin,quote in stocks['prices'].items():
        if quote['symbol']=='IDEAFORGE' and quote['symbol'] not in identities:
            identities[quote['symbol']]={'company':'ideaForge Technology Limited','isin':isin,
                'identity_source':'Official NSE EQ bhavcopy '+stocks['date']+'; company name from primary company disclosure'}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        records=list(pool.map(lambda seed:archive(seed,identities),SEEDS))
    manifest={'family':'defence','status':'initial_examples_for_review','reviewed_on':'2026-10-27',
              'note':'Five independently researched examples covering five proposed sub-themes, not an exhaustive universe. Source keywords are archive checks, not an automated exposure classifier. No weights, adjusted history or fundamentals inferred. Current evidence cannot establish historical membership.',
              'members':records}
    (ROOT/'defence.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({r['symbol']:r['status'] for r in records}))

if __name__=='__main__':main()
