import hashlib, html, re
from html.parser import HTMLParser

class TextParser(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'): self.skip+=1
        if tag in ('p','div','li','br','h1','h2','h3','h4'): self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
        if tag in ('p','li','div'): self.parts.append('\n')
    def handle_data(self,data):
        if not self.skip: self.parts.append(data)

def text(value):
    p=TextParser(); p.feed(html.unescape(str(value or '')))
    return re.sub(r'\n\s*\n+', '\n\n',''.join(p.parts)).strip()

COUNTRIES={'United States':r'\b(?:United States|USA|U\.S\.|US Remote|Remote,? US|US[- /])\b','United Kingdom':r'\b(?:United Kingdom|UK|London)\b','Canada':r'\b(?:Canada|Toronto|Vancouver)\b','Germany':r'\b(?:Germany|Berlin|Deutschland)\b','France':r'\b(?:France|Paris)\b','India':r'\b(?:India|Bengaluru|Bangalore|Hyderabad)\b','Australia':r'\b(?:Australia|Sydney|Melbourne)\b','Ireland':r'\b(?:Ireland|Dublin)\b','Netherlands':r'\b(?:Netherlands|Amsterdam)\b','Spain':r'\b(?:Spain|Madrid|Barcelona)\b','Poland':r'\b(?:Poland|Warsaw)\b','Portugal':r'\bPortugal\b','Brazil':r'\bBrazil\b','Mexico':r'\bMexico\b','Singapore':r'\bSingapore\b','Japan':r'\bJapan\b','South Africa':r'\bSouth Africa\b','New Zealand':r'\bNew Zealand\b'}
CODE_COUNTRIES={'US':'United States','GB':'United Kingdom','CA':'Canada','DE':'Germany','FR':'France','IN':'India','AU':'Australia','IE':'Ireland','NL':'Netherlands','ES':'Spain','PL':'Poland','BR':'Brazil','MX':'Mexico','SG':'Singapore','JP':'Japan','ZA':'South Africa','NZ':'New Zealand'}

def work_mode(title,location,description,explicit=None):
    if explicit in ('remote','hybrid','on-site','onsite'): return 'onsite' if explicit=='on-site' else explicit,'Employer work arrangement'
    scope=title+' '+location
    if re.search(r'\b(?:not remote|non[- ]remote|on[- ]site only)\b',scope,re.I): return 'onsite',scope
    if re.search(r'\bhybrid\b',scope,re.I): return 'hybrid',scope
    if re.search(r'\b(?:remote|work from home|home[- ]based|telecommut)\w*\b',scope,re.I): return 'remote',scope
    # Avoid generic benefits language and references to working with remote teams.
    for sentence in re.split(r'[\n.!]',description):
        if re.search(r'(?:this (?:role|position|job) is|work location:?)\s+(?:a |fully |100% )?remote\b',sentence,re.I):
            if not re.search(r'\bnot\b|hybrid',sentence,re.I): return 'remote',sentence.strip()[:350]
    return 'unknown','Remote arrangement not explicitly disclosed'

def level(title):
    if re.search(r'\b(mid[- ]level|intermediate|engineer ii|analyst ii|developer ii)\b',title,re.I): return 'Mid level'
    # These common individual-contributor titles do not imply people management.
    if re.search(r'\b(product|program|project|account|customer success|marketing) manager\b',title,re.I):
        return 'Senior' if re.search(r'\b(senior|sr|principal|lead|staff)\b',title,re.I) else 'Not specified'
    for name,pattern in [('Executive',r'\b(chief|CEO|CFO|COO|CTO|CIO|CISO|president)\b'),('Senior management',r'\b(vice president|vp|svp|evp|director|head of)\b'),('Management',r'\b(manager|supervisor)\b'),('Senior',r'\b(senior|sr\.?|staff|principal|lead)\b'),('Entry level',r'\b(junior|jr\.?|entry|graduate|intern|apprentice)\b')]:
        if re.search(pattern,title,re.I): return name
    return 'Not specified'

def salary_from_text(description,location):
    # Only expose a numeric filter when currency AND interval can be established.
    pattern=r'(?P<currency>USD|CAD|AUD|GBP|EUR|PLN|CHF|ILS|INR|NZD|SGD|JPY|BRL|MXN|US\$|CA\$|A\$|\$|£|€)\s*(?P<lo>\d[\d,.]*\d|\d)[ ]*(?P<lk>[kK]?)\s*(?:-|–|—|to)\s*(?:USD|CAD|AUD|GBP|EUR|PLN|CHF|ILS|INR|NZD|SGD|JPY|BRL|MXN|US\$|CA\$|A\$|\$|£|€)?\s*(?P<hi>\d[\d,.]*\d|\d)[ ]*(?P<hk>[kK]?)'
    def amount(raw):
        # 80.400 EUR and 80,400 USD are thousands, while 26.50 is decimal pay.
        if re.fullmatch(r'\d{1,3}(?:[,.]\d{3})+',raw): return float(re.sub(r'[,.]','',raw))
        if ',' in raw and '.' in raw:
            decimal=',' if raw.rfind(',')>raw.rfind('.') else '.'
            return float(raw.replace('.' if decimal==',' else ',','').replace(decimal,'.'))
        if ',' in raw and re.fullmatch(r'\d+,\d{1,2}',raw): return float(raw.replace(',','.'))
        return float(raw.replace(',',''))
    for m in re.finditer(pattern,description):
        try:
            lo=amount(m['lo'])*(1000 if m['lk'] else 1); hi=amount(m['hi'])*(1000 if m['hk'] else 1)
        except ValueError: continue
        if not 0<lo<=hi: continue
        context=description[max(0,m.start()-100):m.end()+100]
        interval='year' if re.search(r'\b(annual|year|yearly|per annum)\b',context,re.I) else 'hour' if re.search(r'\b(hour|hourly)\b',context,re.I) else 'month' if re.search(r'\b(month|monthly)\b',context,re.I) else None
        currency={'US$':'USD','CA$':'CAD','A$':'AUD','£':'GBP','€':'EUR'}.get(m['currency'],m['currency'])
        if currency=='$':
            currency='USD' if re.search(COUNTRIES['United States'],location,re.I) else 'CAD' if re.search(COUNTRIES['Canada'],location,re.I) else 'AUD' if re.search(COUNTRIES['Australia'],location,re.I) else None
        return {'min':lo,'max':hi,'currency':currency,'interval':interval,'text':m[0],'evidence':context.strip()}
    return None

def normalize(company,external_id,title,description,location,url,explicit=None,salary=None,department='',employment='',posted=None,country=None,valid_through=None):
    description=text(description); location=text(location) or 'Location not specified'; title=text(title)
    mode,evidence=work_mode(title,location,description,explicit)
    countries=sorted({name for name,pat in COUNTRIES.items() if re.search(pat,location,re.I)})
    if country: countries=sorted(set(countries+[CODE_COUNTRIES.get(country.upper(),country)]))
    world=bool(re.search(r'\b(worldwide|anywhere in the world|work from anywhere|global remote)\b',location,re.I))
    restrictions=[s.strip() for s in re.split(r'[\n.!]',description) if re.search(r'(?:must (?:be (?:based|located)|reside|live)|eligible (?:countries|locations)|authorized to work|work authorization|time zone|timezone)',s,re.I)][:5]
    return {'id':hashlib.sha256((company['id']+':'+str(external_id)).encode()).hexdigest()[:28],'companyId':company['id'],'company':company['name'],'symbols':__import__('json').loads(company['symbols']),'title':title,'description':description[:70000],'location':location,'countries':countries,'worldwide':world,'restrictions':restrictions,'remoteType':mode,'remoteEvidence':evidence,'level':level(title),'levelSource':'Inferred from title' if level(title)!='Not specified' else 'Not specified','industry':company['industry'] or 'Unclassified','department':department,'employmentType':employment or 'Not specified','salary':salary or salary_from_text(description,location),'url':url,'source':company['adapter'],'postedAt':posted,'validThrough':valid_through}
