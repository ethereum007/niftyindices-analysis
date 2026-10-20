import json
import tempfile
import unittest
from pathlib import Path
import pipeline as p

HEADER='Index Name,Index Date,Open Index Value,High Index Value,Low Index Value,Closing Index Value,Change(%),P/E,P/B,Div Yield\n'
def snapshot(day='19-10-2026', close=110, change=1):
    return (HEADER+f'NIFTY 50,{day},105,120,100,{close},{change},20,3,1.2\n').encode()

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.db=p.connect(self.root)
    def tearDown(self):
        self.db.close();self.tmp.cleanup()
    def test_rerun_and_revision(self):
        first=p.ingest(self.db,self.root,snapshot(),'official test fixture')
        self.assertEqual(p.ingest(self.db,self.root,snapshot(),'fixture')['status'],'unchanged')
        p.ingest(self.db,self.root,snapshot(close=111),'fixture')
        self.assertEqual(self.db.execute('select count(*) from observations').fetchone()[0],1)
        self.assertEqual(self.db.execute('select count(*) from batches').fetchone()[0],2)
        self.assertTrue((self.root/'raw'/f'{first["sha"]}.csv').exists())
    def test_bad_batch_preserves_good_data(self):
        p.ingest(self.db,self.root,snapshot(),'fixture')
        for raw in (snapshot(close='NaN'),snapshot(close=-1),b'<html>Access denied</html>',snapshot()+b'NIFTY BANK,bad,1,2,1,1,1,1,1,1\n'):
            with self.assertRaises(ValueError):p.ingest(self.db,self.root,raw,'fixture')
        self.assertEqual(self.db.execute('select count(*) from batches').fetchone()[0],1)
    def test_returns_and_missing_history(self):
        p.ingest(self.db,self.root,snapshot('19-09-2026',100),'fixture')
        p.ingest(self.db,self.root,snapshot(),'fixture');p.report(self.db,self.root)
        r=json.loads((self.root/'reports/latest.json').read_text())['indices'][0]
        self.assertAlmostEqual(r['return_1m'],10)
        self.assertIsNone(r['return_1y'])
    def test_no_stale_base_substitution(self):
        p.ingest(self.db,self.root,snapshot('01-08-2026',100),'fixture')
        p.ingest(self.db,self.root,snapshot(),'fixture');p.report(self.db,self.root)
        self.assertIsNone(json.loads((self.root/'reports/latest.json').read_text())['indices'][0]['return_1m'])
    def test_url_restrictions_and_discovery(self):
        for url in ('http://niftyindices.com/a','https://evil.test/a','https://niftyindices.com.evil.test/a'):
            with self.assertRaises(ValueError):p.safe_url(url)
        links=p.Links();links.feed('<a href="/Daily_Snapshot/ind_close_all_19102026.csv">csv</a>')
        self.assertEqual(len(links.urls),1)
    def test_duplicate_rows_rejected(self):
        with self.assertRaises(ValueError):p.parse(snapshot()+snapshot().split(b'\n')[1]+b'\n')
    def test_zero_dividend_points_is_a_valid_special_index(self):
        raw=snapshot(close=0).replace(b'NIFTY 50',b'Nifty50 Dividend Points')
        self.assertEqual(p.parse(raw)[0]['close'],0)
        with self.assertRaises(ValueError):p.parse(snapshot(close=0))

if __name__=='__main__':unittest.main()
