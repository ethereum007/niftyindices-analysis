import unittest
from datetime import date
from build_dashboard import prepare,target_date,identity

def row(day,close,name='Nifty 50'):
    return {'date':day,'close':close,'name':name}

class HistoryTests(unittest.TestCase):
    def test_calendar_months_and_leap_years(self):
        self.assertEqual(target_date(date(2024,3,31),'1m'),date(2024,2,29))
        self.assertEqual(target_date(date(2024,2,29),'1y'),date(2023,2,28))
        self.assertEqual(target_date(date(2026,10,19),'mtd'),date(2026,9,30))
    def test_mtd_uses_previous_close_not_first_current_day(self):
        r=prepare([row('2026-09-30',100),row('2026-10-01',105),row('2026-10-19',110)])[-1]
        self.assertAlmostEqual(r['return_mtd'],10)
        self.assertEqual(r['base_mtd'],'2026-09-30')
    def test_five_year_cumulative_and_annualized_are_distinct(self):
        r=prepare([row('2021-10-19',100),row('2026-10-19',200)])[-1]
        self.assertEqual(r['return_5y'],100)
        self.assertAlmostEqual(r['cagr_5y'],14.87,places=1)
    def test_only_conservative_aliases(self):
        r=prepare([row('2021-10-19',100,'NIFTY 50'),row('2026-10-19',120)])[-1]
        self.assertAlmostEqual(r['return_5y'],20)
        self.assertNotEqual(identity('Nifty50 PR 1x Inverse'),identity('Nifty50 TR 1x Inverse'))
    def test_same_date_alias_collision_fails(self):
        with self.assertRaises(ValueError):prepare([row('2026-10-19',100,'NIFTY 50'),row('2026-10-19',100)])
    def test_missing_or_stale_baseline_is_unavailable(self):
        for rows in ([row('2026-10-01',100),row('2026-10-19',120)],[row('2021-10-01',100),row('2026-10-19',120)]):
            self.assertIsNone(prepare(rows)[-1]['return_5y'])
    def test_zero_dividend_baseline_not_divided(self):
        r=prepare([row('2021-10-19',0,'Nifty50 Dividend Points'),row('2026-10-19',10,'Nifty50 Dividend Points')])[-1]
        self.assertIsNone(r['return_5y']);self.assertIsNone(r['cagr_5y'])

if __name__=='__main__':unittest.main()
