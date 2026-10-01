import json,re
from urllib.parse import quote,urljoin,urlsplit
from adapters import Page,detect_ats
from http_client import CrawlError

def enrich_wikidata(http,conn):
    """Official website candidates require exact ticker + US exchange + name overlap."""
    query='''SELECT DISTINCT ?company ?companyLabel ?ticker ?website WHERE {
      ?company p:P414 ?statement . ?statement pq:P249 ?ticker .
      ?company wdt:P856 ?website .
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }'''
    data=http.json('https://query.wikidata.org/sparql?format=json&query='+quote(query))
    mapping={r['symbol']:r['company_id'] for r in conn.execute('SELECT symbol,company_id FROM securities WHERE etf=0')}
    count=0
    for row in data.get('results',{}).get('bindings',[]):
        symbol=row['ticker']['value']; cid=mapping.get(symbol)
        if not cid: continue
        c=conn.execute('SELECT * FROM companies WHERE id=?',(cid,)).fetchone()
        if c['website'] or c['kind']!='employer_candidate': continue
        words=lambda s:set(re.findall(r'[a-z]{3,}',s.lower()))-{'inc','corp','corporation','company','limited','ltd','holdings','group','plc','the'}
        if not words(c['name']) & words(row['companyLabel']['value']): continue
        website=row['website']['value']
        if urlsplit(website).scheme not in ('http','https'): continue
        conn.execute('UPDATE companies SET website=?,evidence_url=?,status=? WHERE id=?',(website,row['company']['value'],'website_found',cid)); count+=1
    conn.commit(); return count

def apply_seeds(conn,path):
    if not path.exists(): return
    for seed in json.loads(path.read_text()):
        row=conn.execute('SELECT company_id FROM securities WHERE symbol=?',(seed['symbol'],)).fetchone()
        if row:
            conn.execute('UPDATE companies SET website=?,careers_url=?,industry=?,evidence_url=?,status=CASE WHEN adapter IS NULL THEN ? ELSE status END WHERE id=?',(seed['website'],seed['careers'],seed['industry'],seed['careers'],'website_found',row[0]))
            if seed.get('adapter') and seed.get('board'):
                conn.execute('UPDATE companies SET adapter=?,board=?,evidence_url=? WHERE id=?',(seed['adapter'],seed['board'],seed.get('evidence',seed['careers']),row[0]))
    conn.commit()

def discover_board(http,c):
    candidates=[c['careers_url']] if c['careers_url'] else []
    if c['website']:
        body,final=http.get(c['website']); found=detect_ats(final,body)
        if found: return found
        links=[urljoin(final,l) for l in Page(body).links if re.search(r'career|jobs|join-us|work-with',l,re.I)]
        candidates.extend(links[:4])
    errors=[]
    for url in dict.fromkeys(candidates):
        try:
            body,final=http.get(url); found=detect_ats(final,body)
            if found: return found
            for link in [l for l in Page(body).links if re.search(r'careers|/jobs|open.positions|opportunities',l,re.I)][:3]:
                if re.search(r'careers|/jobs|open.positions|opportunities',link,re.I):
                    sub=urljoin(final,link)
                    if urlsplit(sub).netloc!=urlsplit(final).netloc or sub!=final:
                        try:
                            nested,fin=http.get(sub); found=detect_ats(fin,nested)
                            if found: return found
                        except CrawlError: pass
            if page_has_jobs(body): return 'jsonld','',final
        except CrawlError as e: errors.append(str(e))
    if c['careers_url']: return 'jsonld','',c['careers_url']
    raise CrawlError('No supported careers feed found'+(': '+errors[0] if errors else ''))

def page_has_jobs(body): return bool(re.search(r'"@type"\s*:\s*"JobPosting"',body))
