import csv,io,unittest,zipfile
from datetime import date
from fetch_constituents import parse_members
from fetch_stock_snapshot import parse

class DrilldownDataTests(unittest.TestCase):
 def test_official_dummy_placeholders_are_retained_and_flagged(self):
  rows=parse_members(b'Company,Industry,Symbol,Series,ISIN Code\nDummy HEG Ltd.,Capital Goods,DUMMYHEG,EQ,DUM545A01024\n')
  self.assertTrue(rows[0]['is_placeholder'])
 def test_bad_or_duplicate_member_identifiers_are_rejected(self):
  with self.assertRaises(ValueError):parse_members(b'Company Name,Symbol,ISIN Code\nBad,BAD,XXX\n')
  with self.assertRaises(ValueError):parse_members(b'Company Name,Symbol,ISIN Code\nA,A,INE000A01010\nA,A,INE000A01010\n')
 def stock(self,day='2026-10-26',close='100',previous='80'):
  raw=io.BytesIO()
  with zipfile.ZipFile(raw,'w') as z:z.writestr('prices.csv','TradDt,BizDt,SctySrs,ClsPric,PrvsClsgPric,ISIN,TckrSymb\n'+f'{day},{day},EQ,{close},{previous},INE000A01010,TEST\n')
  return raw.getvalue()
 def test_official_close_return_is_computed_from_previous_close(self):
  r=parse(self.stock(),date(2026,10,26));self.assertEqual(r['INE000A01010']['change_pct'],25)
 def test_wrong_date_and_nonfinite_prices_are_rejected(self):
  with self.assertRaises(ValueError):parse(self.stock(day='2026-10-23'),date(2026,10,26))
  with self.assertRaises(ValueError):parse(self.stock(close='nan'),date(2026,10,26))
 def test_zero_previous_close_stays_unavailable(self):
  self.assertIsNone(parse(self.stock(previous='0'),date(2026,10,26))['INE000A01010']['change_pct'])
if __name__=='__main__':unittest.main()
