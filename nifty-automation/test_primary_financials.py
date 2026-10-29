import copy,json,unittest,hashlib
from decimal import Decimal
from fetch_primary_financials import ROOT,parse,number,trailing_four
class PrimaryFinancialTest(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'mazdock.json').read_text(encoding='utf-8'))
        self.facts=[r['fact'] for r in self.data['sources']]
        self.source=next(r for r in self.data['sources'] if r['filing_date']=='2026-10-27')
        self.raw=(ROOT/'raw'/(self.source['sha256']+'.html')).read_bytes()
    def test_additional_company_requires_explicit_matching_identity(self):
        data=json.loads((ROOT/'hal.json').read_text(encoding='utf-8'))
        self.assertFalse(data['publication_ready'])
        source=data['sources'][0];raw=(ROOT/'raw'/(source['sha256']+'.html')).read_bytes()
        with self.assertRaisesRegex(ValueError,'Wrong company'):parse(raw,source['filing_date'])
        fact=parse(raw,source['filing_date'],'HAL')
        self.assertEqual(fact['symbol'],'HAL')
        self.assertEqual(fact['isin'],'INE066F01020')
        self.assertEqual(fact['revenue_operations_crore'],'5515.17')
        self.assertEqual(fact['pat_total_period_crore'],'1589.66')
        self.assertEqual(fact['audit_status'],'Audited')
        self.assertEqual(fact['ytd_revenue_operations_crore'],fact['revenue_operations_crore'])
        for r in data['sources']:
            self.assertEqual(hashlib.sha256((ROOT/'raw'/(r['sha256']+'.html')).read_bytes()).hexdigest(),r['sha256'])

    def test_hal_ttm_reconciles_to_annual_rollforward(self):
        data=json.loads((ROOT/'hal.json').read_text(encoding='utf-8'))
        facts=[s['fact'] for s in data['sources']]
        annual=next(f for f in facts if f['period_end']=='2026-03-31')
        current=next(f for f in facts if f['period_end']=='2026-06-30')
        september=next(f for f in facts if f['period_end']=='2025-09-30')
        result=trailing_four(facts,'2026-10-28')
        for metric in ('revenue_operations_crore','pat_total_period_crore'):
            prior_june=Decimal(september['ytd_'+metric])-Decimal(september[metric])
            expected=Decimal(annual['ytd_'+metric])+Decimal(current[metric])-prior_june
            self.assertEqual(Decimal(result[metric]),expected)
        self.assertEqual(result['pat_total_period_crore'],'9321.41')
        self.assertEqual(result['revenue_operations_crore'],'33784.98')

    def test_legacy_actual_rupees_are_not_treated_as_lakhs_and_blank_ytd_is_not_zero(self):
        data=json.loads((ROOT/'bel.json').read_text(encoding='utf-8'))
        source=next(r for r in data['sources'] if r['filing_date']=='2025-07-28')
        raw=(ROOT/'raw'/(source['sha256']+'.html')).read_bytes()
        f=parse(raw,source['filing_date'],'BEL')
        self.assertEqual(f['source_unit'],'INR actuals')
        self.assertEqual(f['revenue_operations_crore'],'4439.74')
        self.assertEqual(f['pat_total_period_crore'],'969.05')
        self.assertIsNone(f['ytd_revenue_operations_crore'])
        self.assertIsNone(f['ytd_pat_total_period_crore'])
        self.assertEqual(f['period_end'],'2025-06-30')
        self.assertEqual(hashlib.sha256(raw).hexdigest(),source['sha256'])
    def test_standalone_discovery_is_rejected_for_consolidated_pipeline(self):
        for symbol in ('DYNAMATECH','IDEAFORGE'):
            data=json.loads((ROOT/(symbol.lower()+'.json')).read_text(encoding='utf-8'))
            self.assertFalse(data['publication_ready'])
            source=data['sources'][0];raw=(ROOT/'raw'/(source['sha256']+'.html')).read_bytes()
            with self.assertRaisesRegex(ValueError,'Unexpected accounting scope'):parse(raw,source['filing_date'],symbol)
            self.assertNotIn('fact',source)
            self.assertEqual(hashlib.sha256(raw).hexdigest(),source['sha256'])

    def test_bel_missing_quarter_keeps_fetched_facts_and_ttm_unavailable(self):
        data=json.loads((ROOT/'bel.json').read_text(encoding='utf-8'))
        self.assertIsNone(data['ttm'])
        self.assertIn('Noncontiguous',data['ttm_unavailable_reason'])
        facts=[r['fact'] for r in data['sources'] if r.get('fact')]
        self.assertEqual(len(facts),4)
        annual=next(f for f in facts if f['period_end']=='2026-03-31')
        december=next(f for f in facts if f['period_end']=='2025-12-31')
        for metric in ('revenue_operations_crore','pat_total_period_crore'):
            self.assertEqual(Decimal(annual['ytd_'+metric])-Decimal(december['ytd_'+metric]),Decimal(annual[metric]))
        latest=next(f for f in facts if f['period_end']=='2026-06-30')
        self.assertEqual(latest['revenue_operations_crore'],'5546.98')
        self.assertEqual(latest['pat_total_period_crore'],'1054.53')

    def test_dynamatic_consolidated_annual_bridge_and_scope_isolation(self):
        data=json.loads((ROOT/'dynamatech.json').read_text(encoding='utf-8'))
        self.assertFalse(data['publication_ready'])
        self.assertIsNone(data['ttm'])
        facts=[]
        for source in data['sources']:
            raw=(ROOT/'raw'/(source['sha256']+'.html')).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),source['sha256'])
            if source.get('fact'):
                fact=parse(raw,source['filing_date'],'DYNAMATECH')
                self.assertEqual(fact['isin'],'INE221B01012')
                self.assertEqual(fact['scope'],'Consolidated')
                facts.append(fact)
        self.assertEqual(len(facts),3)
        annual=next(f for f in facts if f['period_end']=='2026-03-31')
        december=next(f for f in facts if f['period_end']=='2025-12-31')
        for metric in ('revenue_operations_crore','pat_total_period_crore'):
            self.assertEqual(Decimal(annual['ytd_'+metric])-Decimal(december['ytd_'+metric]),Decimal(annual[metric]))
        self.assertEqual(annual['revenue_operations_crore'],'433.16')
        self.assertEqual(annual['pat_total_period_crore'],'12.56')
        june=next(f for f in facts if f['period_end']=='2025-06-30')
        self.assertEqual(june['source_unit'],'INR actuals')

    def test_ideaforge_losses_half_year_rejection_and_bridge_review(self):
        data=json.loads((ROOT/'ideaforge.json').read_text(encoding='utf-8'))
        self.assertFalse(data['publication_ready'])
        self.assertIsNone(data['ttm'])
        facts=[]
        for source in data['sources']:
            raw=(ROOT/'raw'/(source['sha256']+'.html')).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),source['sha256'])
            if source['filing_date']=='2025-10-28':
                with self.assertRaisesRegex(ValueError,'three-month quarter'):parse(raw,source['filing_date'],'IDEAFORGE')
                self.assertNotIn('fact',source)
            elif source.get('fact'):
                facts.append(parse(raw,source['filing_date'],'IDEAFORGE'))
        self.assertEqual(len(facts),3)
        june=next(f for f in facts if f['period_end']=='2026-06-30')
        self.assertEqual(june['revenue_operations_crore'],'68.588')
        self.assertEqual(june['pat_total_period_crore'],'-2.589')
        for metric in ('revenue_operations_crore','pat_total_period_crore'):
            self.assertEqual(june[metric],june['ytd_'+metric])
        annual=next(f for f in facts if f['period_end']=='2026-03-31')
        december=next(f for f in facts if f['period_end']=='2025-12-31')
        # Preserve small reported quarter versus annual-minus-YTD differences for review.
        self.assertEqual(Decimal(annual['ytd_revenue_operations_crore'])-Decimal(december['ytd_revenue_operations_crore'])-Decimal(annual['revenue_operations_crore']),Decimal('0.001'))
        self.assertEqual(Decimal(annual['ytd_pat_total_period_crore'])-Decimal(december['ytd_pat_total_period_crore'])-Decimal(annual['pat_total_period_crore']),Decimal('0.005'))

    def test_reconciliation_queue_detects_large_and_small_discrepancies(self):
        from reconcile_financials import reconcile
        flagged=[]
        for symbol in ('MAZDOCK','IDEAFORGE','DYNAMATECH'):
            data=json.loads((ROOT/(symbol.lower()+'.json')).read_text(encoding='utf-8'))
            facts=[r['fact'] for r in data['sources'] if r.get('fact')]
            before=copy.deepcopy(facts)
            flagged.extend(c for c in reconcile(facts) if c['status']=='requires_review')
            self.assertEqual(facts,before)
        self.assertEqual({(r['symbol'],r['metric'],Decimal(r['difference_crore'])) for r in flagged},{('MAZDOCK','pat_total_period_crore',Decimal('-177.21')),('IDEAFORGE','revenue_operations_crore',Decimal('0.001')),('IDEAFORGE','pat_total_period_crore',Decimal('0.005'))})
        self.assertEqual(reconcile([]),[])

    def test_dynamatic_pdf_research_comparator_matches_independent_nse_filing(self):
        data=json.loads((ROOT/'dynamatech-supplementary-research.json').read_text())
        self.assertFalse(data['publication_ready'])
        for source in data['sources']:
            raw=(ROOT/'raw'/(source['sha256']+'.pdf')).read_bytes()
            self.assertTrue(raw.startswith(b'%PDF'))
            self.assertEqual(hashlib.sha256(raw).hexdigest(),source['sha256'])
        fact=data['pdf_research_fact']
        self.assertEqual(fact['statement_page'],8)
        records=json.loads((ROOT/'dynamatech.json').read_text())['sources']
        original=next(r for r in records if r.get('fact',{}).get('period_end')=='2025-06-30')
        parsed=parse((ROOT/'raw'/(original['sha256']+'.html')).read_bytes(),original['filing_date'],'DYNAMATECH')
        for metric in ('revenue_operations_crore','pat_total_period_crore'):
            self.assertEqual(Decimal(fact['prior_june_comparative'][metric]),Decimal(parsed[metric]))
        self.assertEqual(fact['isin'],parsed['isin'])

    def test_ideaforge_current_quarter_tax_credit_bridge(self):
        from bs4 import BeautifulSoup
        data=json.loads((ROOT/'ideaforge.json').read_text(encoding='utf-8'))
        source=next(r for r in data['sources'] if r.get('fact',{}).get('period_end')=='2026-06-30')
        raw=(ROOT/'raw'/(source['sha256']+'.html')).read_bytes()
        soup=BeautifulSoup(raw,'html.parser');rows={}
        for tr in soup.find_all('tr'):
            cells=[c.get_text(' ',strip=True) for c in tr.find_all(['td','th'],recursive=False)]
            if len(cells)>=3 and cells[1] in ('Total profit before tax','Total tax expenses','Total profit (loss) for period'):
                rows[cells[1]]=number(cells[2])
        self.assertEqual(rows['Total profit before tax']-rows['Total tax expenses'],rows['Total profit (loss) for period'])
        self.assertEqual(rows['Total profit (loss) for period']/100,Decimal('-2.589'))
        self.assertLess(rows['Total tax expenses'],0)

    def test_calendar_year_abb_june_is_second_quarter_not_april_fiscal_start(self):
        from reconcile_financials import reconcile
        data=json.loads((ROOT/'abb.json').read_text(encoding='utf-8'))
        facts=[]
        for source in data['sources']:
            raw=(ROOT/'raw'/(source['sha256']+'.html')).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),source['sha256'])
            facts.append(parse(raw,source['filing_date'],'ABB'))
        june=next(f for f in facts if f['period_end']=='2026-06-30')
        self.assertEqual(june['financial_year_start'],'2026-01-01')
        from bs4 import BeautifulSoup
        for source in data['sources']:
            soup=BeautifulSoup((ROOT/'raw'/(source['sha256']+'.html')).read_bytes(),'html.parser')
            components={}
            for row in soup.find_all('tr'):
                cells=[c.get_text(' ',strip=True) for c in row.find_all(['td','th'],recursive=False)]
                if len(cells)>=4 and cells[0] in ('11','14','16'):
                    components[cells[0]]=number(cells[2])
            self.assertEqual(components['11']+components['14'],components['16'])
            if source['filing_date']=='2026-07-31':self.assertEqual(components['14']/100,Decimal('-7.77'))
            else:self.assertEqual(components['14']/100,Decimal('1441.74'))
        self.assertEqual(june['revenue_operations_crore'],'3558.87')
        self.assertEqual(june['pat_total_period_crore'],'362.30')
        self.assertNotEqual(june['revenue_operations_crore'],june['ytd_revenue_operations_crore'])
        checks=reconcile(facts)
        self.assertEqual(len(checks),4)
        self.assertTrue(all(c['status']=='exact_match' for c in checks))
        self.assertFalse(data['publication_ready'])

    def test_dixon_primary_annual_bridge_and_missing_ttm(self):
        from reconcile_financials import reconcile
        data=json.loads((ROOT/'dixon.json').read_text(encoding='utf-8'))
        self.assertFalse(data['publication_ready'])
        self.assertIsNone(data['ttm'])
        facts=[]
        for source in data['sources']:
            raw=(ROOT/'raw'/(source['sha256']+'.html')).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),source['sha256'])
            facts.append(parse(raw,source['filing_date'],'DIXON'))
        self.assertEqual(len(facts),3)
        march=next(f for f in facts if f['period_end']=='2026-03-31')
        self.assertEqual(march['revenue_operations_crore'],'10510.51')
        self.assertEqual(march['pat_total_period_crore'],'297.97')
        self.assertEqual(march['financial_year_start'],'2025-04-01')
        self.assertTrue(all(c['status']=='exact_match' for c in reconcile(facts)))
        prior=next(f for f in facts if f['period_end']=='2025-06-30')
        self.assertEqual(prior['source_unit'],'INR actuals')
        self.assertEqual(prior['revenue_operations_crore'],'12835.66')

    def test_exact_quarter_sales_pat_scope_and_unit(self):
        f=parse(self.raw,'2026-10-27')
        self.assertEqual(f['period_start'],'2026-07-01')
        self.assertEqual(f['revenue_operations_crore'],'2446.09')
        self.assertEqual(f['pat_total_period_crore'],'346.40')
        self.assertNotEqual(f['pat_total_period_crore'],'297.91')
        self.assertEqual(f['scope'],'Consolidated')
        self.assertEqual(f['display_unit'],'INR crore')
        self.assertEqual(number('(1,234.50)'),Decimal('-1234.50'))
        self.assertIsNone(number(''))
        for r in self.data['sources']:
            self.assertEqual(hashlib.sha256((ROOT/'raw'/(r['sha256']+'.html')).read_bytes()).hexdigest(),r['sha256'])
    def test_ttm_rejects_mixed_scope_duplicates_and_missing_quarters(self):
        self.assertEqual(trailing_four(self.facts,'2026-10-28')['revenue_operations_crore'],'12840.27')
        self.assertEqual(trailing_four(self.facts,'2026-10-28')['pat_total_period_crore'],'2450.80')
        self.assertEqual(trailing_four(self.facts,'2026-10-26')['period_end'],'2026-06-30')
        mixed=copy.deepcopy(self.facts);mixed[1]['scope']='Standalone'
        with self.assertRaisesRegex(ValueError,'Incompatible TTM'):trailing_four(mixed,'2026-10-28')
        dup=copy.deepcopy(self.facts);dup[1]=dup[2]
        with self.assertRaisesRegex(ValueError,'Noncontiguous or duplicate'):trailing_four(dup,'2026-10-28')
    def test_ytd_bridge_finds_pat_conflict_without_replacing_reported_value(self):
        march=next(f for f in self.facts if f['period_end']=='2026-03-31')
        december=next(f for f in self.facts if f['period_end']=='2025-12-31')
        self.assertEqual(Decimal(march['ytd_revenue_operations_crore'])-Decimal(december['ytd_revenue_operations_crore']),Decimal(march['revenue_operations_crore']))
        self.assertEqual(Decimal(march['ytd_pat_total_period_crore'])-Decimal(december['ytd_pat_total_period_crore']),Decimal('496.95'))
        self.assertEqual(march['pat_total_period_crore'],'674.16')

    def test_wrong_company_units_and_future_period_rejected(self):
        with self.assertRaises(ValueError):parse(self.raw.replace(b'MAZDOCK',b'OTHER'),'2026-10-27')
        with self.assertRaises(ValueError):parse(self.raw.replace(b'Lakhs',b'Crores'),'2026-10-27')
        with self.assertRaisesRegex(ValueError,'Future financial period'):parse(self.raw,'2026-09-01')
        self.assertFalse(self.data['publication_ready'])
if __name__=='__main__':unittest.main()
