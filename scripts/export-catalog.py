import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scraper'))
from registry import connect,import_registry,ROOT
from run import export
p=argparse.ArgumentParser();p.add_argument('--scheduled',action='store_true');args=p.parse_args()
c=connect();import_registry(c);stats=export(c)
if args.scheduled:
 stats['schedule']='Scheduled daily at 07:17 UTC through GitHub Actions. Runs can be delayed; check the last successful collection for each company.'
 (ROOT/'public/data/stats.json').write_text(json.dumps(stats,separators=(',',':')))
print(json.dumps({k:stats[k] for k in ['inputRows','uniqueSecurities','etfs','employerCandidates','remoteJobs','healthyEmployers']},indent=2))
