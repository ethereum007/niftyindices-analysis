import hashlib
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).parent/'data/theme-research'

class ThemeEvidenceTest(unittest.TestCase):
    def test_energy_archive_keeps_pending_source_unverified(self):
        manifest=json.loads((ROOT/'cleanenergy.json').read_text(encoding='utf-8'))
        self.assertEqual(len({r['symbol'] for r in manifest['members']}),5)
        for row in manifest['members']:
            self.assertIsNone(row['effective_date'])
            raw=(ROOT/'raw'/(row['sha256']+'.html')).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            if row['status']=='evidence_archived':self.assertTrue(all(row['keyword_checks'].values()))
            elif row['status']=='manual_page_review_required':self.assertFalse(all(row['keyword_checks'].values()))

    def test_manufacturing_archive_and_listed_entity_identity(self):
        manifest=json.loads((ROOT/'manufacturing.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['family'],'manufacturing')
        self.assertEqual(len({r['symbol'] for r in manifest['members']}),5)
        self.assertEqual(len({r['subtheme'] for r in manifest['members']}),5)
        prices=json.loads((ROOT.parent/'stocks/latest.json').read_text(encoding='utf-8'))['prices']
        for row in manifest['members']:
            self.assertIsNone(row['effective_date'])
            self.assertEqual(prices[row['isin']]['symbol'],row['symbol'])
            self.assertTrue(row['rationale'])
            self.assertTrue(row['identity_source'])
            if row.get('sha256'):
                raw=(ROOT/'raw'/(row['sha256']+'.html')).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            if row['status']=='evidence_archived':self.assertTrue(all(row['keyword_checks'].values()))

    def test_defence_archive_provenance_and_unknown_effective_date(self):
        manifest=json.loads((ROOT/'defence.json').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest['members']),5)
        self.assertEqual(len({r['symbol'] for r in manifest['members']}),5)
        for row in manifest['members']:
            self.assertIsNone(row['effective_date'])
            self.assertRegex(row['isin'],r'^INE[A-Z0-9]{9}$')
            if row.get('sha256'):
                raw=(ROOT/'raw'/(row['sha256']+'.html')).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            if row['status']=='evidence_archived':
                self.assertTrue(all(row['keyword_checks'].values()))
            elif row['status']=='fetch_failed':self.assertTrue(row['error'])

if __name__=='__main__':unittest.main()
