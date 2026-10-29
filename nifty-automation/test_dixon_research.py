"""Accounting and provenance checks for research awaiting publication review."""
import hashlib,json,unittest
from decimal import Decimal
from pathlib import Path
from pypdf import PdfReader
from parse_primary_pdf import parse_dixon_june2026_research
from unittest.mock import patch
from types import SimpleNamespace

ROOT=Path(__file__).parent/'data/fundamentals'

class DixonResearchTests(unittest.TestCase):
    def test_dated_issuer_outcome_preserves_comparability_gate(self):
        from review_dixon_availability import load_research,outcome_date
        d=json.loads((ROOT/'dixon-current-quarter-research.json').read_text(encoding='utf-8'))
        raw=(ROOT/'raw'/(d['issuer_outcome_source']['sha256']+'.pdf')).read_bytes()
        result=load_research()
        self.assertEqual(result['available_on'],'2026-07-31')
        self.assertIsNone(result['filing_date'])
        self.assertFalse(result['publication_ready'])
        self.assertFalse(result['comparable_growth_allowed'])
        texts=[p.extract_text() for p in PdfReader(ROOT/'raw'/(d['issuer_outcome_source']['sha256']+'.pdf')).pages]
        for old,new in [('INE935N01020','OTHER'),('31st July, 2026','1st August, 2026'),('also being uploaded','not published')]:
            pages=[SimpleNamespace(extract_text=lambda t=t:t.replace(old,new)) for t in texts]
            with patch('review_dixon_availability.PdfReader',return_value=SimpleNamespace(pages=pages)):
                with self.assertRaises(ValueError):outcome_date(raw)

    def test_independent_bse_source_agreement_and_mutation_rejection(self):
        from reconcile_dixon_sources import reconcile
        data=json.loads((ROOT/'dixon-current-quarter-research.json').read_text(encoding='utf-8'))
        html=(ROOT/'raw'/(data['bse_primary_html']['sha256']+'.html')).read_bytes()
        pdf=(ROOT/'raw'/(data['sources'][0]['sha256']+'.pdf')).read_bytes()
        result=reconcile(html,pdf)
        self.assertEqual(len(result['checks']),2)
        self.assertIsNone(result['filing_date'])
        self.assertFalse(result['comparable_growth_allowed'])
        for old,new in [(b'DIXON',b'OTHER'),(b'Crores',b'Lakhs'),(b'15,547.66',b'15,547.67'),(b'30-06-2026',b'30-09-2026')]:
            with self.assertRaises(ValueError):reconcile(html.replace(old,new),pdf)

    def test_bounded_parser_retains_unavailable_date_and_growth_restriction(self):
        raw=(ROOT/'raw/d273532c5a19702886e58b1d3d64be2c540603b7d6662527b1b960283c5b5779.pdf').read_bytes()
        fact=parse_dixon_june2026_research(raw)
        self.assertEqual(fact['revenue_operations_crore'],'15547.66')
        self.assertEqual(fact['pat_total_period_crore'],'717.83')
        self.assertIsNone(fact['filing_date'])
        self.assertFalse(fact['publication_ready'])
        self.assertFalse(fact['comparable_growth_allowed'])
        reader=PdfReader(ROOT/'raw/d273532c5a19702886e58b1d3d64be2c540603b7d6662527b1b960283c5b5779.pdf')
        original=[p.extract_text() for p in reader.pages]
        for old,new in [('Crores','Lakhs'),('DIXON','OTHER'),('30-06-2026','30-09-2026'),('717.83','718.00'),('15,547.66','15,547.67')]:
            pages=[SimpleNamespace(extract_text=lambda t=t:t.replace(old,new)) for t in original]
            with patch('parse_primary_pdf.PdfReader',return_value=SimpleNamespace(pages=pages)):
                with self.assertRaises(ValueError):parse_dixon_june2026_research(raw)

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
