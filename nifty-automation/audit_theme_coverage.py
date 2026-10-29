"""Subtheme coverage measures archived business evidence, never full-universe completeness."""
import json,hashlib
from pathlib import Path
HERE=Path(__file__).parent

def audit():
    catalogue=json.loads((HERE.parent/'index-intelligence/themes.json').read_text(encoding='utf-8'))
    folder=HERE/'data/theme-research';families=[]
    for family in catalogue['catalogue']['families']:
        path=folder/(family['id']+'.json');manifest=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'members':[]}
        rows=[]
        for theme in family['subthemes']:
            candidates=[m for m in manifest['members'] if m['subtheme']==theme]
            verified=[]
            for member in candidates:
                if member['status']!='evidence_archived':continue
                raw=folder/'raw'/(member['sha256']+'.'+member.get('raw_extension','html'))
                if hashlib.sha256(raw.read_bytes()).hexdigest()!=member['sha256']:raise ValueError('Changed theme evidence')
                if not member.get('isin') or not member.get('rationale') or not member.get('reviewed_on'):raise ValueError('Incomplete member review')
                verified.append({'symbol':member['symbol'],'isin':member['isin'],'sha256':member['sha256']})
            rows.append({'subtheme':theme,'stage':'source_backed_example' if verified else 'needs_independent_mapping',
                         'examples':verified,'gap_note':None if verified else ('AI legacy examples require the same manifest/archive audit as other families.' if family['id']=='ai' else 'No validated business-exposure example in current manifest.')})
        families.append({'family':family['id'],'name':family['name'],'mapped_subthemes':sum(bool(r['examples']) for r in rows),'total_subthemes':len(rows),'subthemes':rows})
    return {'reviewed_on':'2026-10-29','definition':'At least one archived, independently researched listed-company exposure example per subtheme; not an exhaustive investable universe, recommendation, historical basket or quantified revenue exposure.',
            'families':families,'total_subthemes':sum(f['total_subthemes'] for f in families),
            'mapped_subthemes':sum(f['mapped_subthemes'] for f in families),
            'fully_mapped_example_families':sum(f['mapped_subthemes']==f['total_subthemes'] for f in families)}

if __name__=='__main__':
    result=audit();p=HERE/'data/theme-discovery/coverage-audit.json'
    p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print({k:result[k] for k in ('total_subthemes','mapped_subthemes','fully_mapped_example_families')})
