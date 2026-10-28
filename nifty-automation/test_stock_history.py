import unittest,copy,json,hashlib
from datetime import date,datetime,timezone
from pathlib import Path
from fetch_stock_history import decode,horizons,target,ROOT
class AdjustedHistoryTest(unittest.TestCase):
    def payload(self):
        return {'chart':{'error':None,'result':[{'meta':{'symbol':'HAL.NS','currency':'INR','exchangeName':'NSI'},'timestamp':[int(datetime(2026,1,d,tzinfo=timezone.utc).timestamp()) for d in (1,2)],'indicators':{'quote':[{'close':[100,50]}],'adjclose':[{'adjclose':[50,50]}]},'events':{'splits':{'x':{'numerator':2,'denominator':1}}}}]}}
    def test_vendor_adjustment_is_not_applied_twice(self):
        rows,events=decode(self.payload(),'HAL')
        self.assertEqual(rows[0]['vendor_close'],100)
        self.assertEqual(rows[0]['adjusted_close'],50)
        self.assertEqual(rows[-1]['adjusted_close']/rows[0]['adjusted_close']-1,0)
        self.assertIn('splits',events)
    def test_market_identity_dates_and_invalid_prices_fail_closed(self):
        for mutate in (lambda r:r['meta'].update(symbol='OTHER.NS'),lambda r:r['meta'].update(currency='USD'),lambda r:r['timestamp'].reverse(),lambda r:r['indicators']['adjclose'][0]['adjclose'].__setitem__(0,0),lambda r:r['indicators']['quote'][0]['close'].pop()):
            p=self.payload();mutate(p['chart']['result'][0])
            with self.assertRaises(ValueError):decode(p,'HAL')
    def test_horizon_exact_baselines_cagr_missing_history_and_future_exclusion(self):
        rows=[{'date':'2025-09-30','adjusted_close':100},{'date':'2026-09-30','adjusted_close':150},{'date':'2026-10-27','adjusted_close':165},{'date':'2026-10-28','adjusted_close':999}]
        result=horizons(rows,date(2026,10,27))
        self.assertEqual(result['end_date'],'2026-10-27')
        self.assertAlmostEqual(result['periods']['mtd']['cumulative_pct'],10)
        self.assertEqual(result['periods']['mtd']['base_date'],'2026-09-30')
        self.assertIsNone(result['periods']['mtd']['cagr_pct'])
        self.assertEqual(result['periods']['1y']['status'],'insufficient_history')
        rows=[{'date':'2025-10-27','adjusted_close':100},{'date':'2026-10-27','adjusted_close':110}]
        self.assertAlmostEqual(horizons(rows,date(2026,10,27))['periods']['1y']['cagr_pct'],100*(1.1**(365.2425/365)-1))
        self.assertEqual(horizons(rows,date(2026,11,15))['status'],'end_price_unavailable')
        self.assertEqual(target(date(2024,5,31),'3m'),date(2024,2,29))
    def test_ideaforge_listing_limits_history_without_approving_empty_actions(self):
        data=json.loads((ROOT/'defence.json').read_text(encoding='utf-8'))
        member=next(m for m in data['members'] if m['symbol']=='IDEAFORGE')
        evidence=json.loads((ROOT/'ideaforge-listing-research.json').read_text(encoding='utf-8'))
        raw=(ROOT/'raw'/(evidence['sha256']+'.pdf')).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),evidence['sha256'])
        self.assertFalse(evidence['publication_ready'])
        rows,_=decode(json.loads((ROOT/'raw'/(member['sha256']+'.json')).read_text()),'IDEAFORGE')
        self.assertEqual(rows[0]['date'],evidence['listing_date'])
        periods=horizons(rows,date(2026,10,26))['periods']
        self.assertEqual(periods['5y']['status'],'insufficient_history')
        self.assertIsNotNone(periods['3y']['cumulative_pct'])
        actions=json.loads((ROOT/'defence-action-review.json').read_text(encoding='utf-8'))
        action=next(m for m in actions['members'] if m['symbol']=='IDEAFORGE')
        self.assertFalse(action['all_reported_events_match'])
        self.assertEqual(action['status'],'manual_review_required')

    def test_archived_defence_data_keeps_review_gate_and_quote_reconciliation(self):
        data=json.loads((ROOT/'defence.json').read_text(encoding='utf-8'))
        self.assertFalse(data['publication_ready']);self.assertEqual(len(data['members']),5)
        for r in data['members']:
            self.assertFalse(r['publication_ready']);self.assertEqual(r['status'],'review_required')
            raw=(ROOT/'raw'/(r['sha256']+'.json')).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),r['sha256'])
            self.assertTrue(r['crosscheck']['within_0_1_pct'])
            self.assertLessEqual(r['rows'][-1]['date'],data['asof'])
            if r['symbol']=='IDEAFORGE':self.assertEqual(r['horizons']['periods']['5y']['status'],'insufficient_history')
if __name__=='__main__':unittest.main()
