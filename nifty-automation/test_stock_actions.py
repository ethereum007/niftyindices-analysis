import unittest,json,hashlib
from review_stock_actions import normalize,compare,adjustment_steps,ROOT
class ActionReviewTest(unittest.TestCase):
    def row(self,subject):return {'symbol':'BEL','series':'EQ','subject':subject,'exDate':'15-Sep-2022'}
    def test_bonus_is_threefold_and_prior_dividend_uses_postbonus_units(self):
        events,ignored,unknown=normalize([self.row('Bonus 2:1')],'BEL')
        self.assertEqual(events[0]['share_multiplier'],3)
        events.insert(0,{'date':'2022-08-08','type':'dividend','cash_per_share':1.5})
        vendor={'splits':{'1663200000':{'numerator':3,'denominator':1}},'dividends':{'1659916800':{'amount':0.5}}}
        result=compare(events,vendor)
        self.assertTrue(all(r['matched'] for r in result['comparisons']))
        self.assertEqual(result['comparisons'][0]['expected_vendor_value'],0.5)
    def test_unknown_reorganisation_and_wrong_identity_do_not_silently_pass(self):
        events,ignored,unknown=normalize([self.row('Rights 1:5'),self.row('Annual General Meeting')],'BEL')
        self.assertEqual(len(unknown),1);self.assertEqual(len(ignored),1);self.assertEqual(events,[])
        with self.assertRaises(ValueError):normalize([self.row('Bonus 2:1')],'HAL')
        result=compare([],{'splits':{'1663200000':{'numerator':3,'denominator':1}}})
        self.assertEqual(result['unmatched_vendor_split_dates'],['2022-09-15'])
    def test_special_and_regular_same_day_dividends_sum_without_losing_evidence(self):
        records=json.loads((ROOT/'manufacturing-action-review.json').read_text(encoding='utf-8'))
        review=next(m for m in records['members'] if m['symbol']=='LT')
        raw=json.loads((ROOT/'raw'/(review['sha256']+'.json')).read_text())
        events,ignored,unknown=normalize(raw,'LT')
        history=json.loads((ROOT/'manufacturing.json').read_text(encoding='utf-8'))
        member=next(m for m in history['members'] if m['symbol']=='LT')
        result=compare(events,member['events'])
        combined=next(e for e in result['comparisons'] if e['date']=='2023-08-02')
        self.assertEqual(combined['expected_vendor_value'],30)
        self.assertTrue(combined['matched'])
        self.assertEqual(sorted(e['cash_per_share'] for e in combined['components']),[6,24])
        self.assertTrue(any(r['subject']=='Buy Back' for r in unknown))
        self.assertFalse(review['publication_ready'])
        with self.assertRaisesRegex(ValueError,'Duplicate exchange action'):compare(events+[events[0]],member['events'])

    def test_hash_bound_buyback_disposition_does_not_change_prices_or_auto_publish(self):
        from review_stock_actions import apply_event_dispositions
        import copy,tempfile,shutil
        from pathlib import Path
        records=json.loads((ROOT/'manufacturing-action-review.json').read_text(encoding='utf-8'))
        original=next(r for r in records['members'] if r['symbol']=='LT')
        decisions=json.loads((ROOT/'event-dispositions.json').read_text(encoding='utf-8'))['decisions']
        original=copy.deepcopy(original)
        if original.get('reviewed_non_price_events'):
            original['unclassified_actions']=[r['event'] for r in original.pop('reviewed_non_price_events')]
            original['all_reported_events_match']=False
        before=copy.deepcopy(original)
        updated=apply_event_dispositions(original,decisions)
        self.assertEqual(original,before)
        self.assertTrue(updated['all_reported_events_match'])
        self.assertFalse(updated['publication_ready'])
        self.assertEqual(updated['comparisons'],original['comparisons'])
        self.assertEqual(len(updated['reviewed_non_price_events']),1)
        self.assertEqual(apply_event_dispositions(updated,decisions),updated)
        stale=copy.deepcopy(decisions);stale[0]['action_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Stale event disposition'):apply_event_dispositions(original,stale)
        changed=copy.deepcopy(decisions);changed[0]['date']='2023-09-13'
        with self.assertRaisesRegex(ValueError,'Missing or ambiguous'):apply_event_dispositions(original,changed)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'raw').mkdir()
            for ref,ext in [(original['sha256'],'json')]+[(r['sha256'],'pdf') for r in decisions[0]['evidence']]:shutil.copy2(ROOT/'raw'/(ref+'.'+ext),root/'raw'/(ref+'.'+ext))
            pdf=next((root/'raw').glob('*.pdf'));pdf.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'Changed event disposition evidence'):apply_event_dispositions(original,decisions,root)

    def test_dividend_adjustment_step_flags_unadjusted_series(self):
        rows=[{'date':'2022-08-05','vendor_close':100,'adjusted_close':99},{'date':'2022-08-08','vendor_close':99,'adjusted_close':99}]
        vendor={'dividends':{'1659916800':{'amount':1}}}
        self.assertTrue(adjustment_steps(rows,vendor)[0]['matched'])
        rows[0]['adjusted_close']=100
        self.assertFalse(adjustment_steps(rows,vendor)[0]['matched'])
    def test_archives_and_review_gate_remain_intact(self):
        data=json.loads((ROOT/'defence-action-review.json').read_text(encoding='utf-8'))
        self.assertFalse(data['publication_ready'])
        for r in data['members']:
            self.assertFalse(r['publication_ready'])
            self.assertEqual(hashlib.sha256((ROOT/'raw'/(r['sha256']+'.json')).read_bytes()).hexdigest(),r['sha256'])
            if r['symbol']=='IDEAFORGE':self.assertFalse(r['all_reported_events_match'])
            else:
                self.assertTrue(r['all_reported_events_match'])
                self.assertTrue(all(c['matched'] for c in r['dividend_factor_steps']))
if __name__=='__main__':unittest.main()
