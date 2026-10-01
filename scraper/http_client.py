"""Bounded public HTTP access, robots policy, conditional GET and host throttling."""
import email.utils, ipaddress, json, socket, time, urllib.error, urllib.parse, urllib.request, urllib.robotparser

USER_AGENT='RemoteAtlasBot/0.1 (+remote-job-catalog; public careers pages only)'

class CrawlError(Exception): pass
class RobotsDenied(CrawlError): pass

def public_url(url):
    p=urllib.parse.urlsplit(url)
    if p.scheme not in ('https','http') or not p.hostname or p.username or p.password or p.port not in (None,80,443):
        raise CrawlError('Unsafe or unsupported URL')
    for result in socket.getaddrinfo(p.hostname,p.port or (443 if p.scheme=='https' else 80),type=socket.SOCK_STREAM):
        if not ipaddress.ip_address(result[4][0]).is_global: raise CrawlError('Private address blocked')
    return urllib.parse.urlunsplit((p.scheme,p.netloc.encode('idna').decode(),urllib.parse.quote(p.path,safe='/%:@!$&\'()*+,;=-._~'),urllib.parse.quote(p.query,safe='=&%/:?@!$\'()*+,;~-._'),''))

class CheckedRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self,policy=None): self.policy=policy
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        newurl=public_url(newurl)
        if self.policy: self.policy(newurl)
        # Do not send endpoint-specific headers to another host.
        result=super().redirect_request(req,fp,code,msg,headers,newurl)
        if result and urllib.parse.urlsplit(req.full_url).netloc!=urllib.parse.urlsplit(newurl).netloc:
            for key in ['Authorization','Cookie']: result.remove_header(key)
        return result

class HTTP:
    def __init__(self,conn):
        self.conn=conn; self.robots={}; self.last={}; self.requests=0; self.bytes=0; self.cached=0
        self.deadline=None

    def raw(self,url,data=None,headers=None,limit=12_000_000,attempts=3,delay=1.0,redirect_policy=None):
        if self.deadline and time.monotonic()>self.deadline: raise CrawlError('Company request budget exhausted; resume on next run')
        url=public_url(url); host=urllib.parse.urlsplit(url).netloc
        wait=max(0,delay-(time.monotonic()-self.last.get(host,0)))
        if wait: time.sleep(wait)
        req=urllib.request.Request(url,data=data,headers={'User-Agent':USER_AGENT,'Accept':'application/json,text/html;q=0.9,*/*;q=0.1',**(headers or {})})
        for attempt in range(attempts):
            self.last[host]=time.monotonic(); self.requests+=1
            try:
                opener=urllib.request.build_opener(CheckedRedirect(redirect_policy))
                with opener.open(req,timeout=22) as res:
                    body=res.read(limit+1)
                    if len(body)>limit: raise CrawlError('Response exceeds safe size')
                    self.bytes+=len(body)
                    return body,dict(res.headers),res.geturl()
            except urllib.error.HTTPError as e:
                if e.code==304: raise
                if e.code not in (429,500,502,503,504) or attempt==attempts-1: raise CrawlError(f'HTTP {e.code}') from e
                retry=e.headers.get('Retry-After','')
                if retry.isdigit(): seconds=float(retry)
                else:
                    try: seconds=max(0,email.utils.parsedate_to_datetime(retry).timestamp()-time.time())
                    except Exception: seconds=2**(attempt+1)
                if seconds>60: raise CrawlError('Retry deferred: long server Retry-After')
                time.sleep(seconds)
            except (OSError,TimeoutError) as e:
                if attempt==attempts-1: raise CrawlError(type(e).__name__+': '+str(e)[:140]) from e
                time.sleep(2**attempt)

    def policy(self,url):
        p=urllib.parse.urlsplit(url); origin=f'{p.scheme}://{p.netloc}'
        if origin not in self.robots:
            rp=urllib.robotparser.RobotFileParser()
            try:
                body,_,_=self.raw(origin+'/robots.txt',limit=500_000,attempts=1)
                rp.parse(body.decode('utf-8','replace').splitlines())
            except CrawlError as e:
                if str(e) in ('HTTP 404','HTTP 410'): rp.parse([])
                else: raise RobotsDenied('Robots policy unavailable: '+str(e))
            self.robots[origin]=rp
        rp=self.robots[origin]
        if not rp.can_fetch('RemoteAtlasBot',url): raise RobotsDenied('Disallowed by robots.txt')
        delay=rp.crawl_delay('RemoteAtlasBot') or rp.crawl_delay('*') or 1
        if delay>60: raise RobotsDenied('Crawl delay requires separate scheduling')
        return max(1,delay)

    def get(self,url,public_api=False,data=None):
        # Public ATS GET feeds document unauthenticated syndication. HTML always observes robots.
        delay=1 if public_api else self.policy(url)
        cache=self.conn.execute('SELECT * FROM http_cache WHERE url=?',(url,)).fetchone() if data is None else None
        headers={}
        if cache:
            if cache['etag']: headers['If-None-Match']=cache['etag']
            if cache['modified']: headers['If-Modified-Since']=cache['modified']
        if data is not None: headers['Content-Type']='application/json'
        try: body,h,final=self.raw(url,data=json.dumps(data).encode() if data is not None else None,headers=headers,delay=delay,redirect_policy=None if public_api else self.policy)
        except urllib.error.HTTPError as e:
            if e.code!=304 or not cache: raise
            self.cached+=1; return cache['body'].decode('utf-8','replace'),url
        if data is None:
            self.conn.execute('INSERT OR REPLACE INTO http_cache VALUES(?,?,?,?,?,?)',(url,h.get('ETag'),h.get('Last-Modified'),body,h.get('Content-Type',''),time.time()))
        return body.decode('utf-8','replace'),final

    def json(self,url,public_api=True,data=None):
        body,_=self.get(url,public_api=public_api,data=data)
        try: return json.loads(body)
        except json.JSONDecodeError as e: raise CrawlError('Invalid JSON response') from e
