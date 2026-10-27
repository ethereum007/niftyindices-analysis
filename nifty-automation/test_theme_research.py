import hashlib
import json
import unittest
import tempfile
import io
from unittest.mock import patch,MagicMock
from pathlib import Path

ROOT=Path(__file__).parent/'data/theme-research'

class ThemeEvidenceTest(unittest.TestCase):
    def test_capitalmarkets_roles_identity_and_primary_pdf(self):
        manifest=json.loads((ROOT/'capitalmarkets.json').read_text(encoding='utf-8'))
        self.assertEqual(len({r['subtheme'] for r in manifest['members']}),5)
        prices=json.loads((ROOT.parent/'stocks/latest.json').read_text(encoding='utf-8'))['prices']
        for row in manifest['members']:
            self.assertIsNone(row['effective_date'])
            self.assertEqual(prices[row['isin']]['symbol'],row['symbol'])
            raw=(ROOT/'raw'/(row['sha256']+'.'+row.get('raw_extension','html'))).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            self.assertEqual(row['status'],'evidence_archived')
            self.assertTrue(all(row['keyword_checks'].values()))
            if row['symbol']=='HDFCAMC':
                self.assertTrue(raw.startswith(b'%PDF-'))
                self.assertTrue(row['evidence_pages'])
                self.assertIn('not corporate revenue',row['rationale'])
            if row['symbol']=='CAMS':self.assertIn('not classified as the investment manager',row['rationale'])

    def test_railways_identity_pdf_provenance_and_no_order_amount_inference(self):
        manifest=json.loads((ROOT/'railways.json').read_text(encoding='utf-8'))
        self.assertEqual(len({r['subtheme'] for r in manifest['members']}),5)
        prices=json.loads((ROOT.parent/'stocks/latest.json').read_text(encoding='utf-8'))['prices']
        for row in manifest['members']:
            self.assertIsNone(row['effective_date'])
            self.assertEqual(prices[row['isin']]['symbol'],row['symbol'])
            raw=(ROOT/'raw'/(row['sha256']+'.'+row.get('raw_extension','html'))).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            self.assertEqual(row['status'],'evidence_archived')
            self.assertTrue(all(row['keyword_checks'].values()))
            if row['symbol']=='HBLENGINE':
                self.assertEqual(row['raw_extension'],'pdf')
                self.assertTrue(raw.startswith(b'%PDF-'))
                self.assertTrue(row['evidence_pages'])
                self.assertIn('not a claim about current unexecuted order value',row['rationale'])

    def test_pdf_bytes_are_archived_as_pdf_without_invented_text_evidence(self):
        from pypdf import PdfWriter
        from research_defence import archive
        writer=PdfWriter();writer.add_blank_page(width=72,height=72);stream=io.BytesIO();writer.write(stream);raw=stream.getvalue()
        response=MagicMock();response.status=200;response.url='https://example.com/evidence.pdf';response.read.return_value=raw
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'raw').mkdir()
            with patch('research_defence.ROOT',root),patch('research_defence.urlopen') as request:
                request.return_value.__enter__.return_value=response
                row=archive(('TEST','Example','https://example.com/evidence.pdf','No inferred exposure.',['transformer']),{'TEST':{'company':'Example','isin':'INE000000001'}},'2026-10-28')
            self.assertEqual(row['raw_extension'],'pdf')
            self.assertEqual(row['status'],'manual_page_review_required')
            self.assertEqual(row['evidence_pages'],[])
            self.assertEqual((root/'raw'/(row['sha256']+'.pdf')).read_bytes(),raw)

    def test_energy_archive_keeps_pending_source_unverified(self):
        manifest=json.loads((ROOT/'cleanenergy.json').read_text(encoding='utf-8'))
        self.assertEqual(len({r['symbol'] for r in manifest['members']}),5)
        for row in manifest['members']:
            self.assertIsNone(row['effective_date'])
            raw=(ROOT/'raw'/(row['sha256']+'.'+row.get('raw_extension','html'))).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            if row['status']=='evidence_archived':self.assertTrue(all(row['keyword_checks'].values()))
            elif row['status']=='manual_page_review_required':self.assertFalse(all(row['keyword_checks'].values()))

    def test_manufacturing_archive_and_listed_entity_identity(self):
        manifest=json.loads((ROOT/'manufacturing.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['family'],'manufacturing')
        self.assertEqual(len({r['symbol'] for r in manifest['members']}),5)
        self.assertEqual(len({r['subtheme'] for r in manifest['members']}),5)
        prices=json.loads((ROOT.parent/'stocks/latest.json').read_text(encoding='utf-8'))['prices']
        for row in manifest['members']:
            self.assertIsNone(row['effective_date'])
            self.assertEqual(prices[row['isin']]['symbol'],row['symbol'])
            self.assertTrue(row['rationale'])
            self.assertTrue(row['identity_source'])
            if row.get('sha256'):
                raw=(ROOT/'raw'/(row['sha256']+'.'+row.get('raw_extension','html'))).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            if row['status']=='evidence_archived':self.assertTrue(all(row['keyword_checks'].values()))

    def test_defence_archive_provenance_and_unknown_effective_date(self):
        manifest=json.loads((ROOT/'defence.json').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest['members']),5)
        self.assertEqual(len({r['symbol'] for r in manifest['members']}),5)
        for row in manifest['members']:
            self.assertIsNone(row['effective_date'])
            self.assertRegex(row['isin'],r'^INE[A-Z0-9]{9}$')
            if row.get('sha256'):
                raw=(ROOT/'raw'/(row['sha256']+'.'+row.get('raw_extension','html'))).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            if row['status']=='evidence_archived':
                self.assertTrue(all(row['keyword_checks'].values()))
            elif row['status']=='fetch_failed':self.assertTrue(row['error'])

if __name__=='__main__':unittest.main()
