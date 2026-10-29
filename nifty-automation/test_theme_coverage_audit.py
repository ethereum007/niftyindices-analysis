import unittest,json,hashlib
from audit_theme_coverage import audit,HERE

class CoverageAuditTest(unittest.TestCase):
    def test_water_chemicals_services_have_five_distinct_source_backed_roles(self):
        catalogue=json.loads((HERE.parent/'index-intelligence/themes.json').read_text(encoding='utf-8'))['catalogue']['families']
        quotes=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))['prices']
        datasets={}
        for family in ('waterwaste','chemicals','services'):
            d=json.loads((HERE/'data/theme-research'/(family+'.json')).read_text(encoding='utf-8'));datasets[family]=d
            self.assertEqual(set(next(f['subthemes'] for f in catalogue if f['id']==family)),{m['subtheme'] for m in d['members']})
            self.assertEqual(len({m['isin'] for m in d['members']}),5)
            for m in d['members']:
                self.assertEqual(m['status'],'evidence_archived')
                self.assertEqual(quotes[m['isin']]['symbol'],m['symbol'])
                self.assertIsNone(m['effective_date'])
                raw=(HERE/'data/theme-research/raw'/(m['sha256']+'.'+m.get('raw_extension','html'))).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),m['sha256'])
        find=lambda family,symbol:next(m for m in datasets[family]['members'] if m['symbol']==symbol)
        self.assertIn('not standalone-parent-only',find('waterwaste','GRAVITA')['rationale'])
        self.assertIn('not company-owned real estate',find('services','SIS')['rationale'])
        self.assertIn('distinct from staffing payroll',find('services','NAUKRI')['rationale'])

    def test_infra_logistics_electronics_roles_keep_operator_and_project_limits(self):
        catalogue=json.loads((HERE.parent/'index-intelligence/themes.json').read_text(encoding='utf-8'))['catalogue']['families']
        quotes=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))['prices']
        manifests={}
        for family in ('infrastructure','logistics','electronics'):
            d=json.loads((HERE/'data/theme-research'/(family+'.json')).read_text(encoding='utf-8'));manifests[family]=d
            self.assertEqual(set(next(f['subthemes'] for f in catalogue if f['id']==family)),{m['subtheme'] for m in d['members']})
            self.assertEqual(len({m['isin'] for m in d['members']}),5)
            for m in d['members']:
                self.assertEqual(m['status'],'evidence_archived')
                self.assertEqual(quotes[m['isin']]['symbol'],m['symbol'])
                raw=(HERE/'data/theme-research/raw'/(m['sha256']+'.'+m.get('raw_extension','html'))).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),m['sha256'])
        find=lambda family,symbol:next(m for m in manifests[family]['members'] if m['symbol']==symbol)
        self.assertIn('not assumed to be company-owned real estate',find('logistics','MAHLOG')['rationale'])
        self.assertIn('after demerger',find('logistics','TCI')['rationale'])
        self.assertIn('does not establish subsequent commercial production',find('electronics','CGPOWER')['rationale'])
        self.assertIn('current certificate validity',find('electronics','HONAUT')['rationale'])

    def test_insurance_and_utilities_roles_have_archived_primary_identity(self):
        catalogue=json.loads((HERE.parent/'index-intelligence/themes.json').read_text(encoding='utf-8'))['catalogue']['families']
        quotes=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))['prices']
        for family in ('insurance','utilities'):
            d=json.loads((HERE/'data/theme-research'/(family+'.json')).read_text(encoding='utf-8'))
            expected=next(f['subthemes'] for f in catalogue if f['id']==family)
            self.assertEqual(set(expected),{m['subtheme'] for m in d['members']})
            for m in d['members']:
                self.assertEqual(m['status'],'evidence_archived')
                self.assertEqual(quotes[m['isin']]['symbol'],m['symbol'])
                self.assertIsNone(m['effective_date'])
                raw=(HERE/'data/theme-research/raw'/(m['sha256']+'.'+m.get('raw_extension','html'))).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),m['sha256'])
        insurance=json.loads((HERE/'data/theme-research/insurance.json').read_text(encoding='utf-8'))
        self.assertIn('not treated as platform revenue',next(m['rationale'] for m in insurance['members'] if m['symbol']=='POLICYBZR'))
        utilities=json.loads((HERE/'data/theme-research/utilities.json').read_text(encoding='utf-8'))
        self.assertIn('distinct from a power exchange',next(m['rationale'] for m in utilities['members'] if m['symbol']=='PTC'))

    def test_banking_roles_preserve_lender_and_rating_agency_boundaries(self):
        d=json.loads((HERE/'data/theme-research/banking.json').read_text(encoding='utf-8'))
        self.assertEqual({m['subtheme'] for m in d['members']},{'Private banks','PSU banks','NBFC lending','Microfinance','Credit infrastructure'})
        quotes=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))['prices']
        for m in d['members']:
            self.assertEqual(m['status'],'evidence_archived')
            self.assertEqual(quotes[m['isin']]['symbol'],m['symbol'])
            self.assertIsNone(m['effective_date'])
            raw=(HERE/'data/theme-research/raw'/(m['sha256']+'.'+m.get('raw_extension','html'))).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),m['sha256'])
        icra=next(m for m in d['members'] if m['symbol']=='ICRA')
        self.assertIn('not a deposit-taking bank',icra['rationale'])
        self.assertIn('not a homogeneous',d['comparison_note'])
        from pypdf import PdfReader
        bank=next(m for m in d['members'] if m['symbol']=='SBIN')
        text=PdfReader(HERE/'data/theme-research/raw'/(bank['sha256']+'.pdf')).pages[0].extract_text()
        self.assertIn('August 04, 2026',text)
        public,private=text.split('Scheduled Private Sector Banks',1)
        self.assertIn('State Bank of India',public)
        self.assertIn('ICICI Bank Ltd.',private)

    def test_telecom_media_roles_and_identity(self):
        d=json.loads((HERE/'data/theme-research/telecommedia.json').read_text(encoding='utf-8'))
        self.assertEqual({m['subtheme'] for m in d['members']},{'Telecom operators','Network equipment','Broadcasting','Content & entertainment','Advertising'})
        prices=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))['prices']
        self.assertEqual(len({m['isin'] for m in d['members']}),5)
        for m in d['members']:
            self.assertEqual(m['status'],'evidence_archived')
            self.assertEqual(prices[m['isin']]['symbol'],m['symbol'])
            self.assertIsNone(m['effective_date'])
            raw=(HERE/'data/theme-research/raw'/(m['sha256']+'.'+m['raw_extension'])).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),m['sha256'])
        affle=next(m for m in d['members'] if m['symbol']=='AFFLE')
        self.assertEqual(affle['company'],'Affle 3i Limited')
        self.assertIn('advertiser spending is not assumed',affle['rationale'])
        sun=next(m for m in d['members'] if m['symbol']=='SUNTV')
        self.assertIn('distinct from ownership of IPTV operators',sun['rationale'])

    def test_travel_roles_preserve_operator_and_asset_boundaries(self):
        d=json.loads((HERE/'data/theme-research/travelleisure.json').read_text(encoding='utf-8'))
        self.assertEqual({m['subtheme'] for m in d['members']},{'Hotels & resorts','Travel platforms','Leisure venues','Restaurants','Entertainment services'})
        prices=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))['prices']
        self.assertEqual(len({m['isin'] for m in d['members']}),5)
        for m in d['members']:
            self.assertEqual(m['status'],'evidence_archived')
            self.assertEqual(prices[m['isin']]['symbol'],m['symbol'])
            self.assertIsNone(m['effective_date'])
            raw=(HERE/'data/theme-research/raw'/(m['sha256']+'.'+m['raw_extension'])).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),m['sha256'])
        self.assertIn('booking value is not platform revenue',d['members'][1]['rationale'])
        self.assertIn('not all owned properties',d['members'][0]['rationale'])
        self.assertIn('global franchisor intellectual property',d['members'][3]['rationale'])

    def test_every_catalogue_subtheme_has_explicit_stage(self):
        d=audit()
        self.assertEqual(len(d['families']),28)
        self.assertEqual(d['total_subthemes'],140)
        self.assertEqual(d['mapped_subthemes'],sum(len(t['examples'])>0 for f in d['families'] for t in f['subthemes']))
        for f in d['families']:
            self.assertEqual(f['total_subthemes'],5)
            for t in f['subthemes']:
                if not t['examples']:self.assertTrue(t['gap_note'])
    def test_it_business_roles_and_listed_identity(self):
        d=json.loads((HERE/'data/theme-research/itservices.json').read_text(encoding='utf-8'))
        self.assertEqual(len({m['subtheme'] for m in d['members']}),5)
        prices=json.loads((HERE/'data/stocks/latest.json').read_text(encoding='utf-8'))['prices']
        for m in d['members']:
            self.assertEqual(m['status'],'evidence_archived')
            self.assertEqual(prices[m['isin']]['symbol'],m['symbol'])
            self.assertIsNone(m['effective_date'])
            raw=(HERE/'data/theme-research/raw'/(m['sha256']+'.'+m.get('raw_extension','html'))).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),m['sha256'])
        self.assertIn('all Oracle group revenue is not attributed',next(m['rationale'] for m in d['members'] if m['symbol']=='OFSS'))

if __name__=='__main__':unittest.main()
