import json
import tempfile
import unittest
import urllib.error
from datetime import date
from pathlib import Path
import backfill_daily as daily
from test_pipeline import snapshot

class DailyBackfillTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):
        self.temp.cleanup()
    def test_budget_and_resume_do_not_refetch_accepted_dates(self):
        fetched=[]
        def fetch(url):
            fetched.append(url)
            stamp=url.split('_')[-1].split('.')[0]
            return snapshot(f'{stamp[:2]}-{stamp[2:4]}-{stamp[4:]}')
        first=daily.run(self.root,date(2026,10,14),date(2026,10,16),1,fetcher=fetch,delay=0)
        self.assertEqual(first['loaded_this_run'],1)
        second=daily.run(self.root,date(2026,10,14),date(2026,10,16),2,fetcher=fetch,delay=0)
        self.assertEqual(second['loaded_this_run'],2)
        self.assertEqual(len(set(fetched)),3)
    def test_unavailable_is_cached_without_claiming_holiday(self):
        def missing(url):raise urllib.error.HTTPError(url,404,'Not found',{},None)
        result=daily.run(self.root,date(2026,10,16),date(2026,10,16),1,fetcher=missing,delay=0)
        self.assertIn('do not prove holidays',result['note'])
        second=daily.run(self.root,date(2026,10,16),date(2026,10,16),1,fetcher=lambda _:self.fail('Refetched cached missing file'),delay=0)
        self.assertEqual(second['attempted_this_run'],0)
    def test_html_is_archived_and_bound_to_source_in_ledger(self):
        result=daily.run(self.root,date(2026,10,16),date(2026,10,16),1,fetcher=lambda _:b'<html>Not a report</html>',delay=0)
        entry=json.loads((self.root/'daily-backfill.json').read_text())['files']['2026-10-16']
        self.assertEqual(entry['status'],'non_csv_response')
        self.assertTrue((self.root/'raw'/(entry['sha256']+'.csv')).exists())
        self.assertEqual(result['accepted_dates_in_range'],0)
    def test_explicit_weekend_sessions_are_bounded_deduplicated_and_resumable(self):
        day=date(2026,2,1)
        def fetch(url):return snapshot('01-02-2026')
        result=daily.run(self.root,day,day,1,fetcher=fetch,delay=0,session_dates=[day,day,date(2025,2,1)])
        self.assertEqual(result['session_candidates'],1)
        self.assertEqual(result['loaded_this_run'],1)
        self.assertTrue((self.root/'special-backfill.json').exists())
        self.assertFalse((self.root/'daily-backfill.json').exists())
        again=daily.run(self.root,day,day,1,fetcher=lambda _:self.fail('refetched'),delay=0,session_dates=[day])
        self.assertEqual(again['attempted_this_run'],0)
    def test_explicit_session_rejects_wrong_embedded_date(self):
        day=date(2026,2,1)
        result=daily.run(self.root,day,day,1,fetcher=lambda _:snapshot('30-01-2026'),delay=0,session_dates=[day])
        self.assertEqual(result['loaded_this_run'],0)
        entry=json.loads((self.root/'special-backfill.json').read_text())['files'][str(day)]
        self.assertEqual(entry['status'],'rejected')
        self.assertTrue((self.root/'raw'/(entry['sha256']+'.csv')).exists())
    def test_rate_limit_stops_the_batch(self):
        def limited(url):raise urllib.error.HTTPError(url,429,'Rate limited',{},None)
        result=daily.run(self.root,date(2026,10,14),date(2026,10,16),10,fetcher=limited,delay=0)
        self.assertEqual(result['attempted_this_run'],1)
        self.assertIn('429',result['stop_reason'])

if __name__=='__main__':unittest.main()
