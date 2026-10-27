"""Research membership contracts: evidence, identity, overlap and bounded coverage."""
import json
import unittest
from pathlib import Path

HERE=Path(__file__).parent

class ThemesTest(unittest.TestCase):
    def test_membership_evidence_and_quote_identity(self):
        themes=json.loads((HERE/'themes.json').read_text())
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

if __name__=='__main__':unittest.main()
