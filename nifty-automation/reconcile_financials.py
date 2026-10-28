"""Create an exact-decimal review queue; never modifies source facts or publication gates."""
import json
from decimal import Decimal
from datetime import date,timedelta
from pathlib import Path
ROOT=Path(__file__).parent/'data/fundamentals'
METRICS=('revenue_operations_crore','pat_total_period_crore')
def reconcile(facts):
    checks=[]
    for current in facts:
        start=date.fromisoformat(current['period_start'])
        previous_end=(start-timedelta(days=1)).isoformat()
        prior=[f for f in facts if f['period_end']==previous_end]
        # Q1 compares with its own YTD; other quarters require the immediately preceding fiscal YTD.
        fiscal_start=current.get('financial_year_start') or str(start.year if start.month>=4 else start.year-1)+'-04-01'
        if current['period_start']==fiscal_start:previous=None
        elif len(prior)==1:previous=prior[0]
        else:continue
        if previous and any(previous[k]!=current[k] for k in ('symbol','isin','scope','display_unit')):continue
        for metric in METRICS:
            ytd=current.get('ytd_'+metric);before=previous.get('ytd_'+metric) if previous else '0'
            if ytd is None or before is None or current.get(metric) is None:continue
            expected=Decimal(ytd)-Decimal(before);reported=Decimal(current[metric]);delta=expected-reported
            checks.append({'symbol':current['symbol'],'period_end':current['period_end'],'metric':metric,'reported':str(reported),'ytd_difference':str(expected),'difference_crore':str(delta),'status':'exact_match' if delta==0 else 'requires_review','note':'No tolerance or inferred rounding explanation; source values remain unchanged.'})
    return checks

def main():
    out=[]
    for symbol in ('HAL','BEL','MAZDOCK','DYNAMATECH','IDEAFORGE','ABB'):
        data=json.loads((ROOT/(symbol.lower()+'.json')).read_text(encoding='utf-8'))
        out.extend(reconcile([r['fact'] for r in data['sources'] if r.get('fact')]))
    (ROOT/'reconciliation-queue.json').write_text(json.dumps({'publication_ready':False,'checks':out},indent=2),encoding='utf-8')
    print(json.dumps({'checks':len(out),'requires_review':sum(r['status']=='requires_review' for r in out)}))
if __name__=='__main__':main()
