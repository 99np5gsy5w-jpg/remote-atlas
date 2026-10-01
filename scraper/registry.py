"""Lossless input inventory and conservative issuer grouping. CSV cells are data only."""
import csv, hashlib, json, re, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILES = [ROOT/'inputs/NYSE.csv', ROOT/'inputs/otherExchanges.csv']

def clean_name(name):
    # Security descriptions are not the employer name. Keep legally distinct issuers separate.
    name = re.split(r'\s+(?:Class [A-Z0-9-]+ (?:Common|Ordinary)|Common Stock|Ordinary Shares|American Deposita(?:ry|ory)|Deposita(?:ry|ory) Shares|Preferred Stock|Preference Shares|Units[, ]|Warrants?\b|\d+(?:\.\d+)?%|Series [A-Z0-9-]+ (?:Preferred|Cumulative))', name, maxsplit=1, flags=re.I)[0]
    return re.sub(r'\s+', ' ', name).strip(' ,.-')

def import_registry(conn, paths=DEFAULT_FILES):
    conn.executescript('''
      CREATE TABLE IF NOT EXISTS securities(symbol TEXT PRIMARY KEY, name TEXT NOT NULL, exchange TEXT, etf INTEGER, test_issue INTEGER, sources TEXT, company_id TEXT);
      CREATE TABLE IF NOT EXISTS companies(id TEXT PRIMARY KEY, name TEXT NOT NULL, symbols TEXT NOT NULL, kind TEXT NOT NULL, website TEXT, careers_url TEXT, adapter TEXT, board TEXT, industry TEXT DEFAULT 'Unclassified', evidence_url TEXT, status TEXT DEFAULT 'unresolved', last_attempt TEXT, last_success TEXT, error TEXT, complete_scans INTEGER DEFAULT 0);
      CREATE TABLE IF NOT EXISTS source_rows(source TEXT NOT NULL, row_number INTEGER NOT NULL, symbol TEXT, payload TEXT, PRIMARY KEY(source,row_number));
      CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, company_id TEXT NOT NULL, payload TEXT NOT NULL, first_seen TEXT NOT NULL, last_seen TEXT NOT NULL, missing_scans INTEGER DEFAULT 0, active INTEGER DEFAULT 1);
      CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, started_at TEXT, finished_at TEXT, summary TEXT);
      CREATE TABLE IF NOT EXISTS http_cache(url TEXT PRIMARY KEY, etag TEXT, modified TEXT, body BLOB, content_type TEXT, fetched_at REAL);
      CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
      CREATE INDEX IF NOT EXISTS jobs_company ON jobs(company_id);
    ''')
    securities={}; counts={}
    for path in paths:
        with path.open(encoding='utf-8-sig',newline='') as source:
            rows=list(csv.DictReader(source))
        counts[path.name]=len(rows)
        for i,r in enumerate(rows,2):
            symbol=(r.get('ACT Symbol') or '').strip(); name=(r.get('Company Name') or r.get('Security Name') or '').strip()
            conn.execute('INSERT OR REPLACE INTO source_rows VALUES(?,?,?,?)',(path.name,i,symbol,json.dumps(r)))
            if not symbol or not name: continue
            prev=securities.get(symbol,{})
            securities[symbol]={'symbol':symbol,'name':name,'exchange':r.get('Exchange') or prev.get('exchange','N'),'etf':int(r.get('ETF', 'N')=='Y') or prev.get('etf',0),'test':int(r.get('Test Issue','N')=='Y'),'sources':sorted(set(prev.get('sources',[])+[path.name]))}
    companies={}
    for s in securities.values():
        kind='test_issue' if s['test'] else 'fund' if s['etf'] or re.search(r'\b(?:ETF|Fund|Trust Units|Trust Shares|Portfolio|ETN)\b',s['name'],re.I) else 'employer_candidate'
        name=clean_name(s['name'])
        # ETFs/funds remain separate inventory records until a sponsor is verified.
        key=kind+':'+(s['symbol'] if kind!='employer_candidate' else re.sub(r'[^a-z0-9]','',name.lower()))
        cid=hashlib.sha256(key.encode()).hexdigest()[:20]
        co=companies.setdefault(cid,{'name':name,'kind':kind,'symbols':[]})
        co['symbols'].append(s['symbol'])
        conn.execute('INSERT OR REPLACE INTO securities VALUES(?,?,?,?,?,?,?)',(s['symbol'],s['name'],s['exchange'],s['etf'],s['test'],json.dumps(s['sources']),cid))
    for cid,c in companies.items():
        conn.execute('INSERT INTO companies(id,name,symbols,kind,status) VALUES(?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,symbols=excluded.symbols,kind=excluded.kind',(cid,c['name'],json.dumps(c['symbols']),c['kind'],'sponsor_needed' if c['kind']=='fund' else 'not_employer' if c['kind']=='test_issue' else 'unresolved'))
    summary={'files':counts,'inputRows':sum(counts.values()),'uniqueSecurities':len(securities),'duplicateRows':sum(counts.values())-len(securities),'etfs':sum(x['etf'] for x in securities.values()),'nonEtfSecurities':sum(not x['etf'] for x in securities.values()),'employerCandidates':sum(x['kind']=='employer_candidate' for x in companies.values()),'fundRecords':sum(x['kind']=='fund' for x in companies.values()),'groupingNote':'Conservative name-based candidates, not a verified employer census. Every source row is retained; fund sponsors require mapping.'}
    conn.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',('inventory',json.dumps(summary)))
    conn.commit()
    return summary

def connect():
    (ROOT/'var').mkdir(exist_ok=True)
    conn=sqlite3.connect(ROOT/'var/catalog.sqlite3',timeout=30)
    conn.row_factory=sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

if __name__=='__main__':
    print(json.dumps(import_registry(connect()),indent=2))
