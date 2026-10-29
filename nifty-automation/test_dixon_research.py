"""Accounting and provenance checks for research awaiting publication review."""
import hashlib,json,unittest
from decimal import Decimal
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).parent/'data/fundamentals'

class DixonResearchTests(unittest.TestCase):
    def test_original_documents_and_scope(self):
        d=json.loads((ROOT/'dixon-current-quarter-research.json').read_text(encoding='utf-8'))
        self.assertFalse(d['publication_ready'])
        for source in d['sources']:
            raw=ROOT/'raw'/(source['sha256']+'.pdf')
            self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(),source['sha256'])
            self.assertEqual(len(PdfReader(raw).pages),source['pages'])
        pdf=PdfReader(ROOT/'raw'/(d['sources'][1]['sha256']+'.pdf'))
        self.assertIn('CONSOLIDATED FINANCIAL RESULTS',pdf.pages[5].extract_text())
        notes=' '.join(pdf.pages[6].extract_text().split())
        self.assertIn('not comparable',notes)
        self.assertIn('31 July 2026',notes)
        self.assertGreaterEqual(len(d['restrictions']),4)

    def test_total_pat_not_parent_or_comprehensive_income(self):
        d=json.loads((ROOT/'dixon-current-quarter-research.json').read_text(encoding='utf-8'))
        f={k:Decimal(v) for k,v in d['visual_review'].items() if k in {
            'revenue_operations','other_income','total_income','total_expenses',
            'profit_before_joint_ventures_and_tax','joint_venture_profit','profit_before_tax',
            'current_tax','deferred_tax','total_tax','total_period_pat',
            'parent_attributable_pat','noncontrolling_pat','comprehensive_income'}}
        self.assertEqual(f['revenue_operations']+f['other_income'],f['total_income'])
        self.assertEqual(f['total_income']-f['total_expenses'],f['profit_before_joint_ventures_and_tax'])
        self.assertEqual(f['profit_before_joint_ventures_and_tax']+f['joint_venture_profit'],f['profit_before_tax'])
        self.assertEqual(f['current_tax']+f['deferred_tax'],f['total_tax'])
        self.assertEqual(f['profit_before_tax']-f['total_tax'],f['total_period_pat'])
        self.assertEqual(f['parent_attributable_pat']+f['noncontrolling_pat'],f['total_period_pat'])
        self.assertNotEqual(f['comprehensive_income'],f['total_period_pat'])

if __name__=='__main__':unittest.main()
