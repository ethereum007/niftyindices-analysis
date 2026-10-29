import unittest,json,hashlib
from audit_theme_coverage import audit,HERE

class CoverageAuditTest(unittest.TestCase):
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
