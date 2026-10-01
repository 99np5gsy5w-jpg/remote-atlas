import datetime as dt,json,sqlite3,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from registry import import_registry,clean_name
from normalize import normalize,work_mode,salary_from_text,level
from adapters import detect_ats,greenhouse,lever,jsonld,workday
from discover import apply_seeds,discover_board
from http_client import CrawlError
from run import save_company_jobs

C={'id':'company','name':'Example Inc','symbols':'["EX"]','industry':'Software','adapter':'greenhouse','board':'example','careers_url':'https://example.com/careers','website':'https://example.com'}
class Tests(unittest.TestCase):
 def test_external_employer_survives_csv_reimport(self):
  c=sqlite3.connect(':memory:');import_registry(c)
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'seeds.json';p.write_text(json.dumps([{'name':'New Employer','website':'https://new.example','careers':'https://new.example/jobs','industry':'Software'}]))
   apply_seeds(c,p);apply_seeds(c,p);import_registry(c)
   self.assertEqual(c.execute("select count(*) from companies where origin='discovered'").fetchone()[0],1)
 def test_blocked_homepage_does_not_block_careers(self):
  class Fake:
   def get(self,url):
    if url==C['website']:raise CrawlError('HTTP 403')
    return '<a href="https://jobs.lever.co/example">Jobs</a>',url
  self.assertEqual(discover_board(Fake(),C)[:2],('lever','example'))
 def test_workday_partial_detail_and_structured_hybrid(self):
  class Fake:
   deadline=None
   def json(self,url,**kwargs):
    if url.endswith('/jobs'):return {'total':2,'jobPostings':[{'externalPath':'/job/1','title':'Engineer'},{'externalPath':'/job/2','title':'Engineer'}]}
    if url.endswith('/job/2'):raise CrawlError('HTTP 503')
    return {'jobPostingInfo':{'title':'Engineer','jobReqId':'1','jobDescription':'Work with a team','location':'Remote - United States','remoteType':'Hybrid','jobRequisitionLocation':{'country':{'alpha2Code':'US'}},'endDate':'2099-01-01','canApply':True}}
  jobs,complete=workday(Fake(),{**C,'board':'example/wd1/External'})
  self.assertFalse(complete);self.assertEqual(len(jobs),1);self.assertEqual(jobs[0]['remoteType'],'hybrid');self.assertEqual(jobs[0]['validThrough'],'2099-01-01')
 def test_input_reconciliation(self):
  c=sqlite3.connect(':memory:');summary=import_registry(c)
  self.assertEqual(summary['inputRows'],10539);self.assertEqual(summary['uniqueSecurities'],7622);self.assertEqual(summary['etfs'],4456)
  self.assertEqual(c.execute('select count(*) from source_rows').fetchone()[0],10539)
  self.assertEqual(c.execute("select name from securities where symbol='SVIX'").fetchone()[0],'-1x Short VIX Futures ETF')
 def test_remote_is_not_worldwide(self):
  j=normalize(C,'1','Software Engineer','Working remotely from United States only.','Remote - United States','https://example.com/job/1')
  self.assertEqual(j['remoteType'],'remote');self.assertFalse(j['worldwide']);self.assertEqual(j['countries'],['United States'])
 def test_negation_and_boilerplate(self):
  self.assertEqual(work_mode('Engineer','Not remote','Remote teams collaborate')[0],'onsite')
  self.assertEqual(work_mode('Engineer','New York','We work with remote teams.')[0],'unknown')
  self.assertEqual(work_mode('Engineer','Hybrid remote','')[0],'hybrid')
 def test_unknown_salary_currency_and_period(self):
  s=salary_from_text('Salary $90,000 - $120,000','Remote')
  self.assertIsNone(s['currency']);self.assertIsNone(s['interval'])
  s=salary_from_text('Annual salary GBP 90,000 to 120,000','UK')
  self.assertEqual((s['currency'],s['interval'],s['min']),('GBP','year',90000))
  self.assertIsNone(salary_from_text('Work with 100 to 200 employees','US'))
 def test_embedded_greenhouse(self):
  self.assertEqual(detect_ats('https://example.com','<iframe src="https://boards.greenhouse.io/embed/job_app?for=hubspotjobs&token=123"></iframe>')[:2],('greenhouse','hubspotjobs'))
 def test_international_salary_separators(self):
  self.assertEqual(salary_from_text('Annual pay €80.400 - €127.200','Spain')['min'],80400)
  self.assertEqual(salary_from_text('Hourly pay USD 26.50 - 32.75','United States')['min'],26.5)
  self.assertEqual(salary_from_text('Annual pay EUR 47.100 to 64.800','Ireland')['max'],64800)
  self.assertEqual(salary_from_text('Hourly pay EUR 26,50 - 32,75','Germany')['min'],26.5)
 def test_title_level(self):
  self.assertEqual(level('Director of Engineering'),'Senior management');self.assertEqual(level('Engineer II'),'Mid level');self.assertEqual(level('Account Executive'),'Not specified')
 def test_expiration_needs_two_complete_scans(self):
  c=sqlite3.connect(':memory:');c.row_factory=sqlite3.Row;import_registry(c)
  c.execute('INSERT INTO companies(id,name,symbols,kind) VALUES(?,?,?,?)',('company','Example','[]','employer_candidate'))
  j=normalize(C,'1','Remote Engineer','A real description','Remote','https://example.com/job/1'); stamp=dt.datetime.now(dt.timezone.utc).isoformat()
  save_company_jobs(c,C,[j],True,stamp);save_company_jobs(c,C,[],False,stamp)
  self.assertEqual(c.execute('SELECT active FROM jobs').fetchone()[0],1)
  save_company_jobs(c,C,[],True,stamp);self.assertEqual(c.execute('SELECT active FROM jobs').fetchone()[0],1)
  save_company_jobs(c,C,[],True,stamp);self.assertEqual(c.execute('SELECT active FROM jobs').fetchone()[0],0)
  save_company_jobs(c,C,[j],True,stamp);self.assertEqual(c.execute('SELECT active FROM jobs').fetchone()[0],1)
 def test_lever_pagination(self):
  class Fake:
   def __init__(self):self.calls=0
   def json(self,url):
    self.calls+=1
    return [{'id':str(i),'text':'Remote engineer','categories':{'location':'Remote - Canada'},'hostedUrl':'https://jobs.lever.co/example/'+str(i)} for i in range(100)] if self.calls==1 else []
  h=Fake();jobs,complete=lever(h,C);self.assertEqual(len(jobs),100);self.assertTrue(complete);self.assertEqual(h.calls,2)
 def test_no_html_execution(self):
  j=normalize(C,'1','Role','<script>alert(1)</script><p>Actual description</p>','Remote','https://example.com')
  self.assertNotIn('alert',j['description']);self.assertIn('Actual description',j['description'])
 def test_malformed_feed_is_not_empty_success(self):
  class Fake:
   def json(self,url):return {'message':'temporarily unavailable'}
  with self.assertRaises(Exception):greenhouse(Fake(),C)
if __name__=='__main__':unittest.main()
