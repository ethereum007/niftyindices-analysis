import hashlib
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).parent/'data/theme-research'

class ThemeEvidenceTest(unittest.TestCase):
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
