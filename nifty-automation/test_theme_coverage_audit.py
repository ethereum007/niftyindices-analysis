import unittest,json,hashlib
from audit_theme_coverage import audit,HERE

class CoverageAuditTest(unittest.TestCase):
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
