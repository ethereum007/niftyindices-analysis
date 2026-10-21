import unittest
from audit_calendar import reconcile

class CalendarAuditTests(unittest.TestCase):
    def test_missing_file_is_not_a_holiday_without_evidence(self):
        result=reconcile({'2024-01-22':{'status':'non_csv_response'}},[],set())
        self.assertEqual(result['verified_closures'],0)
        self.assertEqual(result['dates'][0]['classification'],'unexplained')
    def test_explicit_evidence_and_pending_are_distinct(self):
        files={'2023-06-29':{'status':'non_csv_response'},'2024-01-22':{'status':'non_csv_response'}}
        result=reconcile(files,[{'date':'2023-06-29','classification':'verified_exchange_closure'}, {'date':'2024-01-22','classification':'pending_direct_notice'}],{'2023-06-28'})
        self.assertEqual((result['recorded_gaps'],result['verified_closures'],result['pending']),(2,1,1))
    def test_accepted_muhurat_or_amended_date_cannot_be_called_closed(self):
        with self.assertRaises(ValueError):reconcile({},[{'date':'2023-06-28','classification':'verified_exchange_closure'}],{'2023-06-28'})
    def test_corroborated_closure_is_not_counted_as_directly_verified(self):
        result=reconcile({'2024-01-22':{'status':'non_csv_response'}},[{'date':'2024-01-22','classification':'corroborated_exchange_closure'}],set())
        self.assertEqual((result['verified_closures'],result['corroborated_closures'],result['pending']),(0,1,0))
    def test_duplicate_evidence_is_rejected(self):
        with self.assertRaises(ValueError):reconcile({},[{'date':'2023-06-29'},{'date':'2023-06-29'}],set())
if __name__=='__main__':unittest.main()
