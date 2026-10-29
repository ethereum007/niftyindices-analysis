"""Explicit issuer/template PDF adapter. Unknown documents fail closed; no OCR guesses."""
import io,re
from datetime import date
from decimal import Decimal
from pypdf import PdfReader

def parse_dixon_june2026_research(raw):
    """Bounded integrated-report adapter. Approval date is NOT filing availability."""
    if not raw.startswith(b'%PDF'):raise ValueError('Unsupported PDF format')
    reader=PdfReader(io.BytesIO(raw))
    if len(reader.pages)!=5:raise ValueError('Unexpected Dixon integrated PDF page count')
    cover=' '.join((reader.pages[0].extract_text() or '').split())
    text=' '.join((reader.pages[1].extract_text() or '').split())
    required=('Dixon Technologies (India) Limited','NSE Symbol* DIXON','INE935N01020',
              'Level of rounding Crores','First quarter','Consolidated','31-07-2026')
    if not all(v in cover for v in required):raise ValueError('Dixon identity/unit/scope mismatch')
    if not all(v in text for v in ('Amount in (Crores)','01-04-202601-04-2026','30-06-202630-06-2026','ConsolidatedConsolidated')):
        raise ValueError('Dixon quarter/YTD/scope mismatch')
    def value(label):
        # Two decimal places delimit even touching quarter/YTD cells in this template.
        matches=re.findall(re.escape(label)+r'\s*([\d,]+?\.\d{2})\s*([\d,]+?\.\d{2})',text)
        if len(matches)!=1:raise ValueError('Missing or ambiguous Dixon fact: '+label)
        a,b=(Decimal(v.replace(',','')) for v in matches[0])
        if a!=b:raise ValueError('Dixon Q1 quarter/YTD mismatch')
        return a
    sales=value('Revenue from operations');other=value('Other income');income=value('Total income')
    expenses=value('Total expenses');pbt=value('Total profit before tax')
    tax=value('Total tax expenses');continuing=value('Net Profit Loss for the period from continuing operations')
    discontinued=value('Net profit (loss) from discontinued operation after tax')
    jv=value('method');pat=value('Total profit (loss) for period')
    parent=value('Profit or loss, attributable to owners of parent')
    nci=value('Total profit or loss, attributable to non-controlling interests')
    if sales+other!=income or income-expenses!=pbt or pbt-tax!=continuing:
        raise ValueError('Dixon income/tax bridge mismatch')
    if continuing+discontinued+jv!=pat or parent+nci!=pat:
        raise ValueError('Dixon total PAT bridge mismatch')
    return {'symbol':'DIXON','isin':'INE935N01020','scope':'Consolidated',
            'period_start':'2026-04-01','period_end':'2026-06-30','financial_year_start':'2026-04-01',
            'board_approval_date':'2026-07-31','filing_date':None,'publication_ready':False,
            'source_unit':'Crores','display_unit':'INR crore','statement_page':2,
            'revenue_operations_crore':str(sales),'pat_total_period_crore':str(pat),
            'ytd_revenue_operations_crore':str(sales),'ytd_pat_total_period_crore':str(pat),
            'comparable_growth_allowed':False,
            'restriction':'Issuer notes lighting-business transfer makes comparative quarters non-comparable; exchange filing date unverified.'}

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
