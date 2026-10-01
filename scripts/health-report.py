import json,os
from pathlib import Path
s=json.loads(Path('public/data/stats.json').read_text())
report=f"""## Collection health

Remote jobs: {s['remoteJobs']}

Complete employer feeds: {s['healthyEmployers']} / {s['employerCandidates']} candidates

Status counts: `{json.dumps(s['statusCounts'])}`

Catalog export: {s['generatedAt']}

An export timestamp is not a successful scrape timestamp. Check individual employers and the latest run summary. Unresolved companies and fund sponsors remain onboarding work.
"""
print(report)
if os.environ.get('GITHUB_STEP_SUMMARY'):
 with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:f.write(report)
