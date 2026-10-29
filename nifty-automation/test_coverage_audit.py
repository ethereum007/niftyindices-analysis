import unittest
from datetime import date
from audit_coverage import summarize

class CoverageAuditTests(unittest.TestCase):
    def test_includes_weekends_and_keeps_retryable_dates_open(self):
        result=summarize(date(2026,2,1),date(2026,2,3),{'2026-02-01'},{'2026-02-02':{'status':'request_failed'},'2026-02-03':{'status':'non_csv_response'}})
        self.assertEqual(result['calendar_dates'],3)
        self.assertEqual((result['accepted_dates'],result['unavailable_dates'],result['unchecked_or_retryable']),(1,1,1))
        self.assertFalse(result['source_file_discovery_complete'])
    def test_terminal_absence_completes_discovery_but_never_certifies_calendar(self):
        result=summarize(date(2026,2,1),date(2026,2,2),{'2026-02-01'},{'2026-02-02':{'status':'non_csv_response'}})
        self.assertTrue(result['source_file_discovery_complete'])
        self.assertFalse(result['exchange_calendar_completeness_certified'])
    def test_accepted_warehouse_date_wins_over_old_failed_attempt(self):
        result=summarize(date(2026,2,1),date(2026,2,1),{'2026-02-01'},{'2026-02-01':{'status':'request_failed'}})
        self.assertEqual((result['accepted_dates'],result['unchecked_or_retryable']),(1,0))
if __name__=='__main__':unittest.main()
