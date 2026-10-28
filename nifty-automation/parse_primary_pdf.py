"""Explicit issuer/template PDF adapter. Unknown documents fail closed; no OCR guesses."""
import io,re
from datetime import date
from decimal import Decimal
from pypdf import PdfReader

def parse_dynamatic_june2026(raw,filing_date,symbol='DYNAMATECH'):
    if symbol!='DYNAMATECH' or not raw.startswith(b'%PDF'):raise ValueError('Unsupported PDF company or format')
    reader=PdfReader(io.BytesIO(raw))
    if len(reader.pages)!=11:raise ValueError('Unexpected issuer PDF page count')
    cover=' '.join((reader.pages[0].extract_text() or '').split())
    text=' '.join((reader.pages[7].extract_text() or '').split())
    if not all(x in cover for x in ('DYNAMATIC TECHNOLOGIES LIMITED','DYNAMATECH','August 2026')):raise ValueError('PDF cover identity/date mismatch')
    if not all(x in text for x in ('L72200KA1973PLC002308','Statement of Consolidated Financial Results for the quarter ended 30 June 2026','INR in lakhs','30 June 2025','31 March 2026')):raise ValueError('PDF statement identity/scope/period/unit mismatch')
    if filing_date!='2026-08-07' or date.fromisoformat(filing_date)<date(2026,6,30):raise ValueError('Unexpected PDF filing date')
    def values(label):
        matches=re.findall(re.escape(label)+r'\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)',text)
        if len(matches)!=1:raise ValueError('Missing or ambiguous PDF fact: '+label)
        return [Decimal(v.replace(',','')) for v in matches[0]]
    sales=values('a) Revenue from operations');pat=values('7 Profit after tax (5 - 6)')
    pbt=values('5 Profit before tax (3 - 4)');tax=values('Total tax expense (a+b)')
    income=values('Total income (a+b)');other=values('b) Other income')
    if any(p-t!=v for p,t,v in zip(pbt,tax,pat)):raise ValueError('PDF tax/PAT bridge mismatch')
    if any(s+o!=v for s,o,v in zip(sales,other,income)):raise ValueError('PDF operations/total income mismatch')
    def crore(v):return str(v/Decimal(100))
    return {'symbol':symbol,'isin':'INE221B01012','period_start':'2026-04-01','period_end':'2026-06-30','filing_date':filing_date,'scope':'Consolidated','audit_status':'Unaudited','source_unit':'Lakhs','display_unit':'INR crore','revenue_operations_crore':crore(sales[0]),'pat_total_period_crore':crore(pat[0]),'ytd_revenue_operations_crore':crore(sales[0]),'ytd_pat_total_period_crore':crore(pat[0]),'statement_page':8,'identity_note':'Explicit issuer CIN/template mapping to reviewed current ISIN; PDF does not independently print ISIN. Requires hash-bound publication review.','pat_definition':'Reported consolidated profit after tax; comprehensive income excluded.','notes':'Explicit June 2026 issuer PDF adapter; first quarter column only. No custom basket or growth inference.'}
