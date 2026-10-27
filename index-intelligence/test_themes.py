"""Research membership contracts: evidence, identity, overlap and bounded coverage."""
import json
import unittest
import sqlite3
import tempfile
import hashlib
from build_dashboard import load_family_members
from pathlib import Path

HERE=Path(__file__).parent

class ThemesTest(unittest.TestCase):
    def test_family_evidence_tampering_and_duplicate_identity_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);folder=root/'theme-research';(folder/'raw').mkdir(parents=True)
            raw=b'Original primary evidence';sha=hashlib.sha256(raw).hexdigest()
            evidence=folder/'raw'/(sha+'.html');evidence.write_bytes(raw)
            member={'symbol':'EXAMPLE','isin':'INE000000001','status':'evidence_archived','sha256':sha}
            file=folder/'example.json'
            file.write_text(json.dumps({'family':'example','members':[member]}))
            self.assertEqual(len(load_family_members(root)['example']['members']),1)
            evidence.write_bytes(b'Changed evidence')
            with self.assertRaisesRegex(ValueError,'Changed primary evidence'):load_family_members(root)
            evidence.write_bytes(raw)
            file.write_text(json.dumps({'family':'example','members':[member,member]}))
            with self.assertRaisesRegex(ValueError,'Duplicate family identity'):load_family_members(root)

    def test_membership_evidence_and_quote_identity(self):
        themes=json.loads((HERE/'themes.json').read_text(encoding='utf-8'))
        prices=json.loads((HERE.parent/'nifty-automation/data/stocks/latest.json').read_text())['prices']
        symbols=[p['symbol'] for p in prices.values()]
        self.assertEqual(len(themes['themes']),10)
        self.assertEqual(len({t['id'] for t in themes['themes']}),10)
        for t in themes['themes']:
            self.assertTrue(t['rule'])
            self.assertEqual(len({m['symbol'] for m in t['members']}),len(t['members']))
            for m in t['members']:
                self.assertRegex(m['isin'],r'^INE[A-Z0-9]{9}$')
                if m['isin'] in prices:self.assertEqual(prices[m['isin']]['symbol'],m['symbol'])
                self.assertTrue(m['source_url'].startswith('https://'))
                self.assertTrue(m['rationale'])
        self.assertEqual(themes['status'],'initial_research_coverage')

    def test_catalogue_has_evidence_and_real_related_series(self):
        data=json.loads((HERE/'themes.json').read_text(encoding='utf-8'))['catalogue']
        with sqlite3.connect(HERE.parent/'nifty-automation/data/warehouse.sqlite') as db:
            names={r[0] for r in db.execute('select distinct name from observations')}
        self.assertEqual(len(data['families']),13)
        self.assertEqual(len({f['id'] for f in data['families']}),13)
        for family in data['families']:
            self.assertTrue(family['sources'])
            self.assertTrue(all(u.startswith('https://www.smallcase.com/collection/') for u in family['sources']))
            self.assertTrue(family['subthemes'])
            self.assertTrue(set(family['related_indices'])<=names)
            self.assertNotIn('members',family)
            self.assertIn('context only',family['mapping_note'])

if __name__=='__main__':unittest.main()
