import unittest,json,hashlib,copy
from pathlib import Path
from reviewed_transcriptions import load_transcription
ROOT=Path(__file__).parent/'data/fundamentals'
class ReviewedTranscriptionTests(unittest.TestCase):
    def setUp(self):
        ref=json.loads((ROOT/'kaynes-transcription-reference.json').read_text(encoding='utf-8'))
        self.sha=ref['transcription_sha256'];self.transcript=(ROOT/'raw'/(self.sha+'.json')).read_bytes();self.pdf=(ROOT/'raw'/(ref['source_sha256']+'.pdf')).read_bytes()
    def test_exact_reviewed_million_units_and_primary_provenance(self):
        fact=load_transcription(self.pdf,self.transcript,self.sha,'KAYNES','2026-08-07')
        self.assertEqual(fact['revenue_operations_crore'],'946.017')
        self.assertEqual(fact['pat_total_period_crore'],'56.426')
        self.assertEqual(fact['statement_page'],8)
        self.assertIn('Manually transcribed',fact['extraction_method'])
    def test_changed_source_or_transcription_fails_closed(self):
        for pdf,t,sha in [(self.pdf+b'changed',self.transcript,self.sha),(self.pdf,self.transcript+b' ',self.sha)]:
            with self.assertRaises(ValueError):load_transcription(pdf,t,sha,'KAYNES','2026-08-07')
    def test_scope_identity_dates_and_arithmetic_rejected_even_with_new_hash(self):
        original=json.loads(self.transcript)
        for key,value in [('scope','Standalone'),('source_unit','Lakhs'),('symbol','OTHER'),('filing_date','2026-08-08'),('pat_total_period_million','525.39'),('statement_page',99),('revenue_operations_million','946.017'),('period_end','2026-09-30')]:
            t=copy.deepcopy(original);t[key]=value;raw=json.dumps(t).encode()
            with self.assertRaises(ValueError):load_transcription(self.pdf,raw,hashlib.sha256(raw).hexdigest(),'KAYNES','2026-08-07')
if __name__=='__main__':unittest.main()
