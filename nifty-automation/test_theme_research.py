import hashlib
import json
import unittest
import tempfile
import io
from unittest.mock import patch,MagicMock
from pathlib import Path

ROOT=Path(__file__).parent/'data/theme-research'

class ThemeEvidenceTest(unittest.TestCase):
    def test_healthcare_business_roles_and_nonclinical_evidence(self):
        data=json.loads((ROOT/'healthcare.json').read_text(encoding='utf-8'))
        self.assertEqual(len({r['subtheme'] for r in data['members']}),5)
        self.assertIn('no patient records',data['note'])
        self.assertIn('not a homogeneous',data['comparison_note'])
        prices=json.loads((ROOT.parent/'stocks/latest.json').read_text(encoding='utf-8'))['prices']
        for r in data['members']:
            self.assertEqual(prices[r['isin']]['symbol'],r['symbol'])
            self.assertIsNone(r['effective_date'])
            self.assertEqual(r['status'],'evidence_archived')
            self.assertTrue(all(r['keyword_checks'].values()))
            raw=(ROOT/'raw'/(r['sha256']+'.'+r.get('raw_extension','html'))).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),r['sha256'])
            if r['symbol']=='MAXHEALTH':self.assertIn('not direct ownership of every property',r['rationale'])
            if r['symbol']=='SYNGENE':self.assertIn('does not establish ownership of client drug intellectual property',r['rationale'])
            if r['symbol']=='SUNPHARMA':self.assertIn('does not establish approval in every jurisdiction',r['rationale'])
            if r['symbol']=='POLYMED':self.assertIn('not classified as a hospital operator',r['rationale'])

    def test_mobility_roles_preserve_development_and_group_boundaries(self):
        data=json.loads((ROOT/'mobility.json').read_text(encoding='utf-8'))
        self.assertEqual(len({r['subtheme'] for r in data['members']}),5)
        prices=json.loads((ROOT.parent/'stocks/latest.json').read_text(encoding='utf-8'))['prices']
        for r in data['members']:
            self.assertEqual(prices[r['isin']]['symbol'],r['symbol'])
            self.assertIsNone(r['effective_date'])
            self.assertEqual(r['status'],'evidence_archived')
            self.assertTrue(all(r['keyword_checks'].values()))
            raw=(ROOT/'raw'/(r['sha256']+'.'+r.get('raw_extension','html'))).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),r['sha256'])
            if r['symbol']=='SONACOMS':self.assertIn('development is not treated as commercial revenue',r['rationale'])
            if r['symbol']=='EXIDEIND':self.assertIn('not standalone-parent sales',r['rationale'])
            if r['symbol']=='APOLLOTYRE':self.assertIn('Replacement demand differs',r['rationale'])

    def test_minerals_roles_do_not_imply_pureplay_or_operating_refineries(self):
        data=json.loads((ROOT/'minerals.json').read_text(encoding='utf-8'))
        self.assertEqual(len({r['subtheme'] for r in data['members']}),5)
        self.assertIn('not a pure-play',data['comparison_note'])
        prices=json.loads((ROOT.parent/'stocks/latest.json').read_text(encoding='utf-8'))['prices']
        for r in data['members']:
            self.assertEqual(prices[r['isin']]['symbol'],r['symbol'])
            self.assertIsNone(r['effective_date'])
            if r.get('sha256'):
                raw=(ROOT/'raw'/(r['sha256']+'.'+r.get('raw_extension','html'))).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),r['sha256'])
            if r['status']=='evidence_archived':self.assertTrue(all(r['keyword_checks'].values()))
            else:self.assertTrue(r.get('error') or r.get('keyword_checks'))
            if r['symbol']=='HINDCOPPER':self.assertIn('suspended since 2019',r['rationale'])
            if r['symbol']=='GRAPHITE':self.assertIn('not classified as natural graphite mining',r['rationale'])
            if r['symbol']=='BEML':self.assertIn('not classified as a mineral-reserve owner',r['rationale'])

    def test_oilgas_distinct_roles_and_corporate_identity(self):
        manifest=json.loads((ROOT/'oilgas.json').read_text(encoding='utf-8'))
        self.assertEqual(len({r['subtheme'] for r in manifest['members']}),5)
        self.assertIn('not one directional',manifest['comparison_note'])
        prices=json.loads((ROOT.parent/'stocks/latest.json').read_text(encoding='utf-8'))['prices']
        for row in manifest['members']:
            self.assertIsNone(row['effective_date'])
            self.assertEqual(prices[row['isin']]['symbol'],row['symbol'])
            self.assertEqual(row['status'],'evidence_archived')
            self.assertTrue(all(row['keyword_checks'].values()))
            raw=(ROOT/'raw'/(row['sha256']+'.'+row.get('raw_extension','html'))).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            if row['symbol']=='IOC':self.assertIn('ppac.gov.in',row['source_url'])
            if row['symbol']=='DEEPINDS':
                self.assertEqual(row['isin'],'INE0FHS01024')
                evidence=row['identity_evidence']
                self.assertEqual(evidence['status'],'evidence_archived')
                raw=(ROOT/'raw'/(evidence['sha256']+'.html')).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),evidence['sha256'])
                self.assertIn(b'DEEPINDS',raw)
                self.assertIn('not ownership of client',row['rationale'])

    def test_housing_roles_are_distinct_from_owned_assets_and_demand_cycle(self):
        manifest=json.loads((ROOT/'housing.json').read_text(encoding='utf-8'))
        self.assertEqual(len({r['subtheme'] for r in manifest['members']}),5)
        self.assertIn('not evidence of a current housing upcycle',manifest['comparison_note'])
        prices=json.loads((ROOT.parent/'stocks/latest.json').read_text(encoding='utf-8'))['prices']
        for row in manifest['members']:
            self.assertIsNone(row['effective_date'])
            self.assertEqual(prices[row['isin']]['symbol'],row['symbol'])
            raw=(ROOT/'raw'/(row['sha256']+'.'+row.get('raw_extension','html'))).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            self.assertEqual(row['status'],'evidence_archived')
            self.assertTrue(all(row['keyword_checks'].values()))
            if row['symbol']=='LICHSGFIN':self.assertIn('distinct from LIC the listed insurer',row['rationale'])
            if row['symbol']=='PHOENIXLTD':self.assertIn('not labelled as a REIT',row['rationale'])

    def test_consumption_exposure_is_not_claimed_demand_growth(self):
        manifest=json.loads((ROOT/'consumption.json').read_text(encoding='utf-8'))
        self.assertEqual(len({r['subtheme'] for r in manifest['members']}),5)
        self.assertIn('does not establish',manifest['comparison_note'])
        prices=json.loads((ROOT.parent/'stocks/latest.json').read_text(encoding='utf-8'))['prices']
        for row in manifest['members']:
            self.assertIsNone(row['effective_date'])
            self.assertEqual(prices[row['isin']]['symbol'],row['symbol'])
            raw=(ROOT/'raw'/(row['sha256']+'.'+row.get('raw_extension','html'))).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            self.assertEqual(row['status'],'evidence_archived')
            self.assertTrue(all(row['keyword_checks'].values()))
            if row['symbol']=='HINDUNILVR':self.assertIn('not proof of current rural-demand recovery',row['rationale'])
            if row['symbol']=='INDHOTEL':self.assertIn('does not establish ownership of every hotel',row['rationale'])
            if row.get('raw_extension')=='pdf':self.assertTrue(raw.startswith(b'%PDF-'))

    def test_fintech_identities_and_distinct_provider_roles(self):
        manifest=json.loads((ROOT/'fintech.json').read_text(encoding='utf-8'))
        self.assertEqual(len({r['subtheme'] for r in manifest['members']}),5)
        prices=json.loads((ROOT.parent/'stocks/latest.json').read_text(encoding='utf-8'))['prices']
        for row in manifest['members']:
            self.assertIsNone(row['effective_date'])
            self.assertEqual(prices[row['isin']]['symbol'],row['symbol'])
            raw=(ROOT/'raw'/(row['sha256']+'.'+row.get('raw_extension','html'))).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            self.assertEqual(row['status'],'evidence_archived')
            self.assertTrue(all(row['keyword_checks'].values()))
            if row['symbol']=='BAJFINANCE':self.assertIn('distinct from listed parent Bajaj Finserv',row['rationale'])
            if row['symbol']=='POLICYBZR':self.assertIn('does not classify the company as an insurance underwriter',row['rationale'])
            if row['symbol']=='AUBANK':self.assertIn('not a pure-play neobank',row['rationale'])

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
