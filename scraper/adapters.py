"""Public recruiting feeds and bounded Schema.org career-page traversal."""
import json, re
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit,quote,parse_qs
from http_client import CrawlError
from normalize import normalize, text

class Page(HTMLParser):
    def __init__(self,body):
        super().__init__(); self.links=[]; self.ld=[]; self.in_ld=False; self.buf=''; self.feed(body)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ('a','iframe') and a.get('href',a.get('src')): self.links.append(a.get('href',a.get('src')))
        if tag=='script' and a.get('type','').lower()=='application/ld+json': self.in_ld=True; self.buf=''
    def handle_data(self,data):
        if self.in_ld: self.buf+=data
    def handle_endtag(self,tag):
        if tag=='script' and self.in_ld:
            self.in_ld=False
            try: self.ld.append(json.loads(self.buf))
            except ValueError: pass

def detect_ats(url,body):
    candidates=[url]+[urljoin(url,l) for l in Page(body).links]+re.findall(r'https?://[^\s"<>\\]+',body)
    for candidate in candidates:
        parsed=urlsplit(candidate)
        if parsed.hostname and parsed.hostname.endswith('greenhouse.io'):
            query=parse_qs(parsed.query)
            token=(query.get('for') or query.get('job_board') or [None])[0]
            if token and re.fullmatch(r'[\w-]+',token): return 'greenhouse',token,candidate
        patterns=[('greenhouse',r'(?:boards|job-boards)\.greenhouse\.io/([\w-]+)'),('greenhouse',r'boards-api\.greenhouse\.io/v1/boards/([\w-]+)'),('lever',r'jobs\.lever\.(co|eu)/([\w-]+)'),('ashby',r'jobs\.ashbyhq\.com/([\w-]+)'),('smartrecruiters',r'(?:careers|jobs)\.smartrecruiters\.com/([\w-]+)'),('workday',r'https://([\w-]+)\.(wd\d+)\.myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?([\w-]+)')]
        for adapter,pat in patterns:
            m=re.search(pat,candidate)
            if m:
                if adapter=='greenhouse' and m[1] in ('embed','users'): continue
                board=('/'.join(m.groups()) if adapter=='workday' else (m[2]+('@eu' if m[1]=='eu' else '')) if adapter=='lever' else m[1])
                return adapter,board,candidate
    return None

def greenhouse(http,c):
    data=http.json(f'https://boards-api.greenhouse.io/v1/boards/{quote(c["board"])}/jobs?content=true')
    if not isinstance(data.get('jobs'),list): raise CrawlError('Greenhouse schema changed')
    out=[]
    for j in data['jobs']:
        if not j.get('title') or not j.get('absolute_url'): raise CrawlError('Greenhouse job missing required fields')
        out.append(normalize(c,j['id'],j['title'],j.get('content',''),j.get('location',{}).get('name'),j['absolute_url'],department=', '.join(x['name'] for x in j.get('departments',[])),posted=j.get('updated_at')))
    return out,True

def lever(http,c):
    board,_,region=c['board'].partition('@'); domain='eu' if region=='eu' else 'co'; out=[]
    for skip in range(0,10000,100):
        rows=http.json(f'https://api.lever.{domain}/v0/postings/{quote(board)}?mode=json&limit=100&skip={skip}')
        if not isinstance(rows,list): raise CrawlError('Lever schema changed')
        for j in rows:
            cat=j.get('categories',{}); sal=j.get('salaryRange')
            if sal: sal={**sal,'interval':{'per-year':'year','per-year-salary':'year','per-hour':'hour','per-hour-wage':'hour','per-month':'month','per-month-salary':'month'}.get(sal.get('interval'),sal.get('interval')),'text':j.get('salaryDescriptionPlain',''),'evidence':'Employer structured salary'}
            desc=j.get('descriptionPlain','')+'\n'+'\n'.join(x.get('text','')+'\n'+text(x.get('content','')) for x in j.get('lists',[]))+'\n'+j.get('additionalPlain','')
            out.append(normalize(c,j['id'],j['text'],desc,cat.get('location'),j['hostedUrl'],explicit=j.get('workplaceType'),salary=sal,department=cat.get('team',''),employment=cat.get('commitment',''),country=j.get('country')))
        if len(rows)<100: return out,True
    return out,False

def ashby(http,c):
    data=http.json(f'https://api.ashbyhq.com/posting-api/job-board/{quote(c["board"])}?includeCompensation=true')
    if not isinstance(data.get('jobs'),list): raise CrawlError('Ashby schema changed')
    out=[]
    for j in data['jobs']:
        tiers=j.get('compensation',{}).get('compensationTierSummary','') if isinstance(j.get('compensation'),dict) else ''
        desc=j.get('descriptionPlain') or j.get('descriptionHtml') or ''
        out.append(normalize(c,j.get('id') or j['jobUrl'],j['title'],desc+'\n'+(tiers or ''),j.get('location'),j['jobUrl'],explicit='remote' if j.get('isRemote') else None,department=j.get('department',''),employment=j.get('employmentType',''),posted=j.get('publishedAt')))
    return out,True

def smartrecruiters(http,c):
    out=[]
    for offset in range(0,10000,100):
        data=http.json(f'https://api.smartrecruiters.com/v1/companies/{quote(c["board"])}/postings?limit=100&offset={offset}')
        if not isinstance(data.get('content'),list): raise CrawlError('SmartRecruiters schema changed')
        for j in data['content']:
            loc=j.get('location',{}); location=', '.join(str(loc[k]) for k in ['city','region','country'] if loc.get(k))
            # Every detail is fetched; a failed detail makes the company incomplete rather than closing unseen jobs.
            detail=http.json(f'https://api.smartrecruiters.com/v1/companies/{quote(c["board"])}/postings/{quote(j["id"])}')
            desc='\n'.join(x.get('text','') for x in detail.get('jobAd',{}).get('sections',{}).values() if isinstance(x,dict))
            out.append(normalize(c,j['id'],j['name'],desc,location,detail.get('postingUrl') or f'https://jobs.smartrecruiters.com/{c["board"]}/{j["id"]}',explicit='remote' if loc.get('remote') else None,department=j.get('department',{}).get('label',''),employment=j.get('typeOfEmployment',{}).get('label',''),posted=j.get('releasedDate'),country=loc.get('country')))
        if offset+len(data['content'])>=data.get('totalFound',0): return out,True
        if not data['content']: return out,False
    return out,False

def workday(http,c):
    tenant,shard,site=c['board'].split('/'); origin=f'https://{tenant}.{shard}.myworkdayjobs.com'; base=f'{origin}/wday/cxs/{tenant}/{site}'
    out=[]; seen=set(); facets={}; partial=False; failed=False
    first=http.json(base+'/jobs',public_api=False,data={'appliedFacets':{},'limit':20,'offset':0,'searchText':''})
    # Large retail boards can contain tens of thousands of on-site jobs. Use the
    # employer's own remote-location facets, and explicitly report partial coverage.
    def remote_locations(nodes):
        for node in nodes:
            if node.get('facetParameter')=='locations':
                for value in node.get('values',[]):
                    if re.search(r'\bremote\b|work (?:from|at) home',value.get('descriptor',''),re.I): yield value['id']
            yield from remote_locations([n for n in node.get('values',[]) if isinstance(n,dict) and n.get('facetParameter')])
    if first.get('total',0)>2000:
        ids=list(remote_locations(first.get('facets',[])))
        if ids: facets={'locations':ids}; partial=True
    for offset in range(0,10000,20):
        try:
            data=first if offset==0 and not facets else http.json(base+'/jobs',public_api=False,data={'appliedFacets':facets,'limit':20,'offset':offset,'searchText':''})
        except CrawlError:
            if out: return out,False
            raise
        if not isinstance(data.get('jobPostings'),list): raise CrawlError('Workday schema changed')
        for j in data['jobPostings']:
            path=j.get('externalPath')
            if not path or path in seen: continue
            seen.add(path)
            try:
                d=http.json(base+path,public_api=False).get('jobPostingInfo',{})
                if not d.get('title') or not d.get('jobDescription'): raise CrawlError('Workday detail missing required fields')
            except CrawlError:
                failed=True
                if http.deadline and __import__('time').monotonic()>http.deadline: return out,False
                continue
            if d.get('canApply') is False: continue
            location=d.get('location',j.get('locationsText',''))
            if d.get('additionalLocations'): location+='; '+'; '.join(d['additionalLocations'])
            mode=str(d.get('remoteType','')).lower()
            country=d.get('jobRequisitionLocation',{}).get('country',{}).get('alpha2Code')
            out.append(normalize(c,d.get('jobReqId',path),d.get('title',j['title']),d.get('jobDescription',''),location,f'{origin}/en-US/{site}{path}',explicit=mode if mode in ('remote','hybrid','on-site','onsite') else None,employment=d.get('timeType',''),posted=d.get('startDate'),country=country,valid_through=d.get('endDate')))
        if offset+len(data['jobPostings'])>=data.get('total',0): return out,not (partial or failed)
        if not data['jobPostings']: return out,False
    return out,False

def walk_json(node):
    if isinstance(node,list):
        for v in node: yield from walk_json(v)
    elif isinstance(node,dict):
        kind=node.get('@type',[])
        if 'JobPosting' in (kind if isinstance(kind,list) else [kind]): yield node
        for v in node.values():
            if isinstance(v,(dict,list)): yield from walk_json(v)

def jsonld(http,c,max_pages=60):
    root=c['careers_url'] or c['website']; queue=[root]; seen=set(); jobs={}
    while queue and len(seen)<max_pages:
        url=queue.pop(0)
        if url in seen: continue
        seen.add(url)
        body,final=http.get(url); page=Page(body)
        for node in page.ld:
            for j in walk_json(node):
                if not j.get('title') or not j.get('description'): continue
                loc=j.get('jobLocation',[]); loc=loc if isinstance(loc,list) else [loc]
                names=[]
                for l in loc:
                    if isinstance(l,dict):
                        address=l.get('address',{})
                        names.append(', '.join(str(address[k]) for k in ['addressLocality','addressRegion','addressCountry'] if address.get(k)) if isinstance(address,dict) else str(address))
                req=j.get('applicantLocationRequirements',[]); req=req if isinstance(req,list) else [req]
                names.extend(x.get('name','') for x in req if isinstance(x,dict))
                pay=j.get('baseSalary'); salary=None
                if isinstance(pay,dict) and isinstance(pay.get('value'),dict):
                    v=pay['value']; salary={'min':v.get('minValue',v.get('value')),'max':v.get('maxValue',v.get('value')),'currency':pay.get('currency'),'interval':str(v.get('unitText','')).lower(),'text':'','evidence':'Employer Schema.org baseSalary'}
                posting=urljoin(final,j.get('url') or final)
                job=normalize(c,posting,j['title'],j['description'],'; '.join(filter(None,names)),posting,explicit='remote' if j.get('jobLocationType')=='TELECOMMUTE' else None,salary=salary,employment=str(j.get('employmentType','')),posted=j.get('datePosted'),valid_through=j.get('validThrough'))
                jobs[job['id']]=job
        for link in page.links:
            absolute=urljoin(final,link).split('#')[0]
            if urlsplit(absolute).netloc==urlsplit(root).netloc and re.search(r'(?:career|/job|vacanc|position|opening)',absolute,re.I) and absolute not in seen and absolute not in queue: queue.append(absolute)
    # HTML link traversal cannot establish that all pagination / JavaScript jobs were enumerated.
    return list(jobs.values()),False

ADAPTERS={'greenhouse':greenhouse,'lever':lever,'ashby':ashby,'smartrecruiters':smartrecruiters,'workday':workday,'jsonld':jsonld}
