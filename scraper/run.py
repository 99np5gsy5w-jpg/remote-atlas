#!/usr/bin/env python3
"""Daily, resumable employer crawl. Nothing in the input files is executed."""
import argparse, collections, datetime as dt, fcntl, hashlib, json, re, sys, time, uuid
from pathlib import Path
from registry import ROOT,DEFAULT_FILES,connect,import_registry
from http_client import HTTP,CrawlError,RobotsDenied
from discover import apply_seeds,enrich_wikidata,discover_board
from adapters import ADAPTERS

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()

def save_company_jobs(conn,c,jobs,complete,timestamp):
    seen={j['id'] for j in jobs}
    for j in jobs:
        url=j.get('url','')
        if not url.startswith(('https://','http://')): continue
        old=conn.execute('SELECT first_seen FROM jobs WHERE id=?',(j['id'],)).fetchone()
        j['firstSeen']=old[0] if old else timestamp; j['lastSeen']=timestamp
        expired=False
        if j.get('validThrough'):
            try: expired=dt.datetime.fromisoformat(j['validThrough'].replace('Z','+00:00')).replace(tzinfo=dt.timezone.utc)<dt.datetime.now(dt.timezone.utc)
            except (ValueError,TypeError): pass
        conn.execute('INSERT INTO jobs VALUES(?,?,?,?,?,0,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload,last_seen=excluded.last_seen,missing_scans=0,active=excluded.active',(j['id'],c['id'],json.dumps(j),j['firstSeen'],timestamp,int(not expired)))
    # Only two complete successful enumerations can close a disappeared listing.
    if complete:
        for row in conn.execute('SELECT id,missing_scans FROM jobs WHERE company_id=?',(c['id'],)).fetchall():
            if row['id'] not in seen:
                misses=row['missing_scans']+1
                conn.execute('UPDATE jobs SET missing_scans=?,active=? WHERE id=?',(misses,int(misses<2),row['id']))
    conn.execute('UPDATE companies SET status=?,last_success=?,error=NULL,complete_scans=complete_scans+? WHERE id=?',('healthy' if complete else 'partial',timestamp,int(complete),c['id']))
    conn.commit()

def export(conn):
    inventory=json.loads(conn.execute("SELECT value FROM settings WHERE key='inventory'").fetchone()[0])
    companies=[dict(r) for r in conn.execute('SELECT id,name,symbols,kind,origin,website,careers_url,adapter,industry,evidence_url,status,last_attempt,last_success,error FROM companies ORDER BY name')]
    inventory['csvEmployerCandidates']=inventory['employerCandidates']
    inventory['addedEmployers']=sum(c['kind']=='employer_candidate' and c['origin']=='discovered' for c in companies)
    inventory['employerCandidates']+=inventory['addedEmployers']
    jobs=[]; fingerprints=set(); duplicates=0; cutoff=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(days=7)).isoformat()
    for r in conn.execute('SELECT payload FROM jobs WHERE active=1 AND last_seen>=?',(cutoff,)):
        j=json.loads(r[0])
        if j['remoteType'] in ('remote','hybrid') and j.get('description'):
            fingerprint=hashlib.sha256(json.dumps([j['companyId'],j['title'].casefold(),j['location'].casefold(),re.sub(r'\s+',' ',j['description']).casefold()]).encode()).hexdigest()
            if fingerprint in fingerprints: duplicates+=1; continue
            fingerprints.add(fingerprint); jobs.append(j)
    latest=conn.execute('SELECT * FROM runs ORDER BY started_at DESC LIMIT 1').fetchone()
    stats={**inventory,'statusCounts':dict(collections.Counter(c['status'] for c in companies)),'remoteJobs':sum(j['remoteType']=='remote' for j in jobs),'hybridJobs':sum(j['remoteType']=='hybrid' for j in jobs),'connectedEmployers':sum(bool(c['adapter']) for c in companies),'healthyEmployers':sum(c['status']=='healthy' for c in companies),'lastRun':dict(latest) if latest else None,'generatedAt':now(),'schedule':'Daily workflow prepared; activation requires GitHub repository setup'}
    stats['launchTarget']=1000
    stats['catalogThresholdMet']=stats['remoteJobs']>=1000
    stats['duplicatePostingsHidden']=duplicates
    folder=ROOT/'public/data'; folder.mkdir(parents=True,exist_ok=True)
    for name,data in [('jobs.json',jobs),('coverage.json',companies),('stats.json',stats)]:
        temp=folder/(name+'.tmp'); temp.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))); temp.replace(folder/name)
    return stats

def run(args):
    (ROOT/'var').mkdir(exist_ok=True)
    lock=(ROOT/'var/crawl.lock').open('w')
    try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError: raise SystemExit('Another crawl is running; skipped without changing data.')
    conn=connect(); import_registry(conn,args.files or DEFAULT_FILES); apply_seeds(conn,ROOT/'scraper/seeds.json')
    http=HTTP(conn); start=time.monotonic(); run_id=str(uuid.uuid4()); counts=collections.Counter(); discovered=0
    conn.execute('INSERT INTO runs VALUES(?,?,NULL,NULL)',(run_id,now())); conn.commit()
    if args.discover:
        try: discovered=enrich_wikidata(http,conn); print(f'Discovered {discovered} website candidates',flush=True)
        except Exception as e: print('Website discovery unavailable: '+str(e)[:160],flush=True); counts['discovery_error']+=1
    rows=conn.execute("SELECT * FROM companies WHERE kind='employer_candidate' ORDER BY CASE WHEN adapter IS NOT NULL THEN 0 WHEN website IS NOT NULL THEN 1 ELSE 2 END, COALESCE(last_attempt,''),name").fetchall()
    if args.symbols:
        requested=set(args.symbols.split(',')); rows=[c for c in rows if requested&set(json.loads(c['symbols']))]
    if args.companies:
        requested=set(args.companies); rows=[c for c in rows if c['name'] in requested]
    attempted=0
    for row in rows:
        c=dict(row)
        if not c['website']:
            counts['unresolved']+=1
            conn.execute("UPDATE companies SET status='unresolved',error='Official website not verified' WHERE id=?",(c['id'],)); continue
        if args.limit and attempted>=args.limit: counts['deferred']+=1; continue
        if time.monotonic()-start>args.max_minutes*60: counts['deferred']+=1; continue
        timestamp=now(); attempted+=1
        # Large Workday boards require a detail request per posting.
        http.deadline=min(start+args.max_minutes*60,time.monotonic()+(1800 if c['adapter']=='workday' else 300))
        conn.execute('UPDATE companies SET last_attempt=? WHERE id=?',(timestamp,c['id'])); conn.commit()
        try:
            if not c['adapter']:
                c['adapter'],c['board'],c['careers_url']=discover_board(http,c)
                conn.execute('UPDATE companies SET adapter=?,board=?,careers_url=? WHERE id=?',(c['adapter'],c['board'],c['careers_url'],c['id'])); conn.commit()
            jobs,complete=ADAPTERS[c['adapter']](http,c)
            save_company_jobs(conn,c,jobs,complete,timestamp); counts['healthy' if complete else 'partial']+=1; counts['jobsFetched']+=len(jobs)
            print(f'{c["name"]}: {len(jobs)} postings, {"complete" if complete else "partial"}',flush=True)
        except Exception as e:
            state='blocked' if isinstance(e,RobotsDenied) else 'error'
            conn.execute('UPDATE companies SET status=?,error=? WHERE id=?',(state,str(e)[:350],c['id'])); conn.commit(); counts[state]+=1
            print(f'{c["name"]}: {state}: {str(e)[:130]}',flush=True)
    summary={**dict(counts),'websiteCandidatesAdded':discovered,'httpRequests':http.requests,'downloadBytes':http.bytes,'conditionalCacheHits':http.cached,'seconds':round(time.monotonic()-start,2),'attempted':attempted,'scope':'partial' if args.limit or args.symbols or args.companies or counts['deferred'] else 'all employer candidates'}
    conn.execute('UPDATE runs SET finished_at=?,summary=? WHERE id=?',(now(),json.dumps(summary),run_id))
    conn.execute('DELETE FROM http_cache WHERE fetched_at<?',(time.time()-30*86400,)); conn.commit()
    stats=export(conn); print(json.dumps({'run':summary,'remoteJobs':stats['remoteJobs'],'connectedEmployers':stats['connectedEmployers']},indent=2),flush=True)
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--files',nargs='+',type=Path); p.add_argument('--discover',action='store_true'); p.add_argument('--limit',type=int,default=0); p.add_argument('--symbols'); p.add_argument('--companies',nargs='+'); p.add_argument('--max-minutes',type=float,default=180)
    run(p.parse_args())
