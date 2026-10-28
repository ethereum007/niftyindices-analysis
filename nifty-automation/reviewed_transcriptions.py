"""Load explicitly reviewed manual source transcriptions, with both byte hashes bound.
This is not OCR or automatic extraction. Every newly sourced document needs a new review.
"""
import hashlib,json,io
from datetime import date,timedelta
from decimal import Decimal
from pypdf import PdfReader

def load_transcription(pdf_raw,transcript_raw,expected_sha,symbol,filing_date):
    if hashlib.sha256(transcript_raw).hexdigest()!=expected_sha:raise ValueError('Changed reviewed transcription')
    t=json.loads(transcript_raw)
    if t['kind']!='manual_visual_primary_transcription' or t['status']!='reviewed':raise ValueError('Unreviewed transcription')
    if t['symbol']!=symbol or t['filing_date']!=filing_date:raise ValueError('Transcription identity/date mismatch')
    if hashlib.sha256(pdf_raw).hexdigest()!=t['source_sha256']:raise ValueError('Changed transcription primary PDF')
    if t['scope']!='Consolidated' or t['source_unit']!='INR million':raise ValueError('Unsupported transcription scope/units')
    start=date.fromisoformat(t['period_start']);end=date.fromisoformat(t['period_end'])
    if start.month!=4 or start.day!=1 or end!=date(start.year,6,30) or end>date.fromisoformat(filing_date):raise ValueError('Unsupported transcription quarter')
    if not 1<=t['statement_page']<=len(PdfReader(io.BytesIO(pdf_raw)).pages):raise ValueError('Invalid transcription statement page')
    fields=('revenue_operations','other_income','total_income','pbt','current_tax','deferred_tax','pat_total_period')
    values={k:Decimal(t[k+'_million']) for k in fields}
    if not all(v.is_finite() for v in values.values()):raise ValueError('Nonfinite transcription fact')
    if values['revenue_operations']+values['other_income']!=values['total_income']:raise ValueError('Transcription income bridge mismatch')
    if values['pbt']-values['current_tax']-values['deferred_tax']!=values['pat_total_period']:raise ValueError('Transcription PAT bridge mismatch')
    revenue=str(values['revenue_operations']/10);pat=str(values['pat_total_period']/10)
    return {'symbol':symbol,'isin':t['isin'],'period_start':t['period_start'],'period_end':t['period_end'],'filing_date':filing_date,'scope':t['scope'],'audit_status':'Unaudited','source_unit':'INR million','display_unit':'INR crore','revenue_operations_crore':revenue,'pat_total_period_crore':pat,'ytd_revenue_operations_crore':revenue,'ytd_pat_total_period_crore':pat,'statement_page':t['statement_page'],'extraction_method':'Manually transcribed and visually reviewed primary PDF; original PDF and transcription byte hashes verified.','pat_definition':'Reported consolidated total profit for period; comprehensive income excluded.','notes':'First fiscal quarter only. No prior-year comparison or TTM inferred from unreviewed columns.'}
