import hashlib,json,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from pypdf import PdfReader
from parse_lt_research import parse
ROOT=Path(__file__).parent/'data/fundamentals'

class LTResearchTests(unittest.TestCase):
    def test_issuer_publication_dates_from_page_content(self):
        from bs4 import BeautifulSoup
        d=json.loads((ROOT/'lt-primary-research.json').read_text(encoding='utf-8'))
        for source,expected in zip(d['dated_issuer_announcements'],('28 July 2026','27 October 2026')):
            raw=(ROOT/'raw'/(source['sha256']+'.html')).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),source['sha256'])
            page=BeautifulSoup(raw,'html.parser')
            self.assertEqual([x.get_text(strip=True) for x in page.select('.date_sec')],[expected])
    def test_original_hashes_and_total_pat(self):
        d=json.loads((ROOT/'lt-primary-research.json').read_text(encoding='utf-8'))
        for s,end,sales,pat in zip(d['sources'],('2026-06-30','2026-09-30'),('67941.74','78749.94'),('4988.03','5949.15')):
            raw=(ROOT/'raw'/(s['sha256']+'.pdf')).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),s['sha256'])
            f=parse(raw,end)
            self.assertEqual(f['revenue_operations_crore'],sales)
            self.assertEqual(f['pat_total_period_crore'],pat)
            self.assertIsNone(f['filing_date'])
            self.assertFalse(f['publication_ready'])
    def test_changed_scope_and_accounting_fail_closed(self):
        s=json.loads((ROOT/'lt-primary-research.json').read_text(encoding='utf-8'))['sources'][1]
        raw=(ROOT/'raw'/(s['sha256']+'.pdf')).read_bytes()
        texts=[p.extract_text() for p in PdfReader(ROOT/'raw'/(s['sha256']+'.pdf')).pages]
        for old,new in [('CONSOLIDATED','STANDALONE'),('78749.94','78749.95'),('5949.15','5949.16'),('5202.10','5202.11')]:
            pages=[SimpleNamespace(extract_text=lambda t=t:t.replace(old,new)) for t in texts]
            with patch('parse_lt_research.PdfReader',return_value=SimpleNamespace(pages=pages)):
                with self.assertRaises(ValueError):parse(raw,'2026-09-30')

if __name__=='__main__':unittest.main()
