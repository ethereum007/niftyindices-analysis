import json,unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from parse_primary_pdf import parse_dynamatic_june2026
ROOT=Path(__file__).parent/'data/fundamentals'
class IssuerPdfTests(unittest.TestCase):
    def setUp(self):
        self.raw=(ROOT/'raw/c33f5ab9af6e5032da66f57635471e5174be5235b2e693f4ff37eda894617a02.pdf').read_bytes()
    def test_matches_visual_review_and_quarter_not_annual(self):
        fact=parse_dynamatic_june2026(self.raw,'2026-08-07')
        reviewed=json.loads((ROOT/'dynamatech-supplementary-research.json').read_text())['pdf_research_fact']
        for key in ('symbol','isin','period_start','period_end','filing_date','scope','revenue_operations_crore','pat_total_period_crore','statement_page'):self.assertEqual(fact[key],reviewed[key])
        self.assertNotEqual(fact['pat_total_period_crore'],'24.97')
        self.assertEqual(fact['ytd_revenue_operations_crore'],fact['revenue_operations_crore'])
    def test_kaynes_visual_research_preserves_million_scale_and_pat_bridge(self):
        from decimal import Decimal
        import hashlib
        data=json.loads((ROOT/'kaynes-primary-research.json').read_text(encoding='utf-8'))
        self.assertFalse(data['publication_ready'])
        fact=data['visual_review']
        self.assertEqual(fact['statement_page'],8)
        self.assertEqual(Decimal(fact['revenue_operations_million'])/10,Decimal(fact['revenue_operations_crore']))
        self.assertEqual(Decimal(fact['pat_total_period_million'])/10,Decimal(fact['pat_total_period_crore']))
        self.assertEqual(Decimal(fact['pbt_million'])-Decimal(fact['current_tax_million'])-Decimal(fact['deferred_tax_million']),Decimal(fact['pat_total_period_million']))
        self.assertEqual(Decimal(fact['revenue_operations_million'])+Decimal(fact['other_income_million']),Decimal(fact['total_income_million']))
        self.assertNotEqual(fact['pat_total_period_million'],fact['comprehensive_income_million'])
        for source in data['sources']:
            self.assertEqual(hashlib.sha256((ROOT/'raw'/(source['sha256']+'.pdf')).read_bytes()).hexdigest(),source['sha256'])

    def test_wrong_company_date_format_and_other_issuer_rejected(self):
        for raw,dt,symbol in [(self.raw,'2026-08-07','BEL'),(self.raw,'2026-08-08','DYNAMATECH'),(b'<html>','2026-08-07','DYNAMATECH')]:
            with self.assertRaises(ValueError):parse_dynamatic_june2026(raw,dt,symbol)
        other=(ROOT/'raw/037d099ff9f48370af798f3b7f199926fac1864f12a00b4615591a54337361c6.pdf').read_bytes()
        with self.assertRaises(ValueError):parse_dynamatic_june2026(other,'2026-08-07')
    def test_corrupt_tax_bridge_or_scope_fails_closed(self):
        from pypdf import PdfReader
        import io
        texts=[p.extract_text() or '' for p in PdfReader(io.BytesIO(self.raw)).pages]
        for modified in [texts[7].replace('2,079','2,078'),texts[7].replace('Consolidated','Standalone')]:
            copies=list(texts);copies[7]=modified
            pages=[SimpleNamespace(extract_text=lambda t=t:t) for t in copies]
            with patch('parse_primary_pdf.PdfReader',return_value=SimpleNamespace(pages=pages)):
                with self.assertRaises(ValueError):parse_dynamatic_june2026(self.raw,'2026-08-07')
if __name__=='__main__':unittest.main()
