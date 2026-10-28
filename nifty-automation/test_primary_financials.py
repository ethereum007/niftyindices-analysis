import copy,json,unittest,hashlib
from decimal import Decimal
from fetch_primary_financials import ROOT,parse,number,trailing_four
class PrimaryFinancialTest(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'mazdock.json').read_text(encoding='utf-8'))
        self.facts=[r['fact'] for r in self.data['sources']]
        self.source=self.data['sources'][0]
        self.raw=(ROOT/'raw'/(self.source['sha256']+'.html')).read_bytes()
    def test_exact_quarter_sales_pat_scope_and_unit(self):
        f=parse(self.raw,'2026-10-27')
        self.assertEqual(f['period_start'],'2026-07-01')
        self.assertEqual(f['revenue_operations_crore'],'2446.09')
        self.assertEqual(f['pat_total_period_crore'],'346.40')
        self.assertNotEqual(f['pat_total_period_crore'],'297.91')
        self.assertEqual(f['scope'],'Consolidated')
        self.assertEqual(f['display_unit'],'INR crore')
        self.assertEqual(number('(1,234.50)'),Decimal('-1234.50'))
        self.assertIsNone(number(''))
        for r in self.data['sources']:
            self.assertEqual(hashlib.sha256((ROOT/'raw'/(r['sha256']+'.html')).read_bytes()).hexdigest(),r['sha256'])
    def test_ttm_rejects_mixed_scope_duplicates_and_missing_quarters(self):
        self.assertEqual(trailing_four(self.facts,'2026-10-28')['revenue_operations_crore'],'12840.27')
        self.assertEqual(trailing_four(self.facts,'2026-10-28')['pat_total_period_crore'],'2450.80')
        self.assertIsNone(trailing_four(self.facts,'2026-10-26'))
        mixed=copy.deepcopy(self.facts);mixed[0]['scope']='Standalone'
        with self.assertRaisesRegex(ValueError,'Incompatible TTM'):trailing_four(mixed,'2026-10-28')
        dup=copy.deepcopy(self.facts);dup[0]=dup[1]
        with self.assertRaisesRegex(ValueError,'Noncontiguous or duplicate'):trailing_four(dup,'2026-10-28')
    def test_wrong_company_units_and_future_period_rejected(self):
        with self.assertRaises(ValueError):parse(self.raw.replace(b'MAZDOCK',b'OTHER'),'2026-10-27')
        with self.assertRaises(ValueError):parse(self.raw.replace(b'Lakhs',b'Crores'),'2026-10-27')
        with self.assertRaisesRegex(ValueError,'Future financial period'):parse(self.raw,'2026-09-01')
        self.assertFalse(self.data['publication_ready'])
if __name__=='__main__':unittest.main()
