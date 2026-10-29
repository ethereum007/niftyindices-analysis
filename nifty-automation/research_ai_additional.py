"""Audit the five additional legacy AI-adjacent roles, outside the 140-slot count."""
import json,copy
from research_defence import HERE,ROOT,archive
def main():
    d=json.loads((HERE.parent/'index-intelligence/themes.json').read_text(encoding='utf-8'))
    ids={m['symbol']:m for t in d['themes'] for m in t['members']}
    seeds=[
      ('POLYCAB','cables','https://nsearchives.nseindia.com/corporate/ixbrl/INTEGRATED_FILING_INDAS_201397_15102026155523_iXBRL_WEB.html','Polycab issuer segment filing documents cables and wires. General electrical products are not quantified AI/data-centre revenue or pure-play AI exposure.',['polycab','cables']),
      ('CGPOWER','switchgear','https://nsearchives.nseindia.com/corporate/CGPOWER_04022025085223_Disclosure_Presentation_0405022025.pdf','CG Power February2025 presentation describes switchgear and transformer portfolios. Diversified equipment exposure is not quantified AI revenue or ownership of customer power networks. Historical capability is not current utilisation.',['transformers','switchgear'])]
    rows=[archive(s,ids,'2026-10-29') for s in seeds]
    c=copy.deepcopy(rows[1]);c['subtheme']='transformers';rows.append(c)
    e=json.loads((ROOT/'electronics.json').read_text());k=copy.deepcopy(next(m for m in e['members'] if m['symbol']=='KAYNES'));k['subtheme']='ems';rows.append(k)
    c=copy.deepcopy(next(m for m in e['members'] if m['symbol']=='CGPOWER'));c['subtheme']='semiconductors';rows.append(c)
    (ROOT/'legacy').mkdir(exist_ok=True)
    (ROOT/'legacy/ai-additional.json').write_text(json.dumps({'reviewed_on':'2026-10-29','note':'Additional legacy AI-adjacent role examples; not five additional catalogue slots or pure-play AI companies.','members':rows},indent=2)+'\n',encoding='utf-8')
    print([(m['subtheme'],m['status'],m.get('error'),m.get('keyword_checks')) for m in rows])
if __name__=='__main__':main()
