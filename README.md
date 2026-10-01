# Remote Atlas

Worldwide remote-job research app using NYSE.csv and otherExchanges.csv as its starting inventory, expanded with researched employers beyond those files. A free GitHub Pages prototype with a daily GitHub Actions crawler, transparent source coverage and private on-device resume/cover-letter matching.

[Live prototype](https://99np5gsy5w-jpg.github.io/remote-atlas/) · [Cost report](docs/cost-analysis.md)

## What works

- Lossless import of all 10,539 CSV rows; 7,622 unique securities, 4,456 explicit ETFs and 2,413 conservatively grouped employer candidates.
- Verified-source onboarding, public ATS adapters, bounded HTML/Schema.org traversal, per-host throttling, conditional caching, retry/backoff and explicit failure reports.
- Remote and hybrid listings with description, original employer link, location/restriction evidence, inferred title seniority, employer industry when known and salary only when disclosed.
- Search and filters for keyword, location, level, industry, employment, salary/currency/period and first-seen age.
- PDF, DOCX and TXT resume and cover-letter parsing, private browser persistence, deletion and explainable skill-overlap suggestions.
- Interactive operating-cost model and detailed [cost analysis](docs/cost-analysis.md). Recommended paid launch price: $14.99/month or $119.99/year for the planned iOS launch, after at least 1,000 active remote postings and production readiness are sustained.

## Honest limitations

Coverage is incomplete. Every employer candidate and fund appears in the coverage inventory; unresolved websites, blocked sites and incomplete crawls are never counted as fully covered. Name grouping can need manual correction. ETF sponsors require separate mapping. The exchange files omit many Nasdaq-listed employers. Some websites need custom connectors or permission. Browser automation, licensed enrichment, semantic AI matching, subscription checkout and cross-device private accounts are not enabled.

The free prototype stores documents only in the visitor’s browser using IndexedDB. Documents never enter the repository, crawler database, GitHub Actions, or public catalog. Clearing browser data deletes them; shared-device users should remove them after use. Skill overlap is not a hiring probability. The future private-storage deployment path is described in docs/production.md.

GitHub Pages is for this free prototype. GitHub prohibits operating commercial SaaS on Pages, so a subscription launch needs another runtime host while GitHub remains the source and scheduler.

## Run locally

Requires Node.js 22+ and Python 3.12+ (crawler also tested with Python 3.9 on macOS). No paid API key is needed.

```sh
npm ci
python3 scraper/registry.py
python3 scraper/run.py --discover --max-minutes 300
npm run dev:pages
```

Open the Local URL printed by Vite. To build deployable static output: `npm run build:pages`. Outputs are in `pages-dist/`. Input lists are in `inputs/`; registry and cached public responses are in ignored `var/catalog.sqlite3`.

For a quick pilot use `python3 scraper/run.py --symbols NET,HUBS,ESTC --max-minutes 10`. To process every mapped candidate, omit `--symbols` and `--limit`. The bounded run reports deferred companies; it cannot guarantee that every company allows collection. Existing mapped sources are revisited first, while remaining sources are ordered by least-recent attempt. Use a larger runtime budget or sharding before promising complete daily coverage.

## Daily GitHub workflow

`.github/workflows/daily.yml` runs at 07:17 UTC daily and on manual request. Enable repository Settings → Pages → GitHub Actions. Pushes publish the current catalog immediately. Scheduled runs collect first, preserve state in GitHub cache, export the public catalog, build, and deploy. Manual runs offer a collection checkbox. Public standard runners have no minute charge; private repositories have account-wide allowances.

GitHub can delay cron runs, and schedules on inactive public repositories may be disabled after 60 days. Check Actions and each company’s last successful check. The UI export timestamp is not a claim that all companies were freshly scraped. The workflow has a 300-minute collection budget. Cache eviction falls back to the included public bootstrap state; the public catalog hides postings not verified within seven days.

The bootstrap state contains public companies/jobs only, not user documents or secrets. Daily cache can grow; prune expired responses and keep it within GitHub’s included limit. Do not enable paid runner/cache upgrades without an explicit budget.

## Add or repair a source

Add a record to `scraper/seeds.json` with an existing input symbol, official website, careers URL, industry and evidence URL. To add an employer outside the CSVs, include `name` and its official `website`; `symbol` is optional. External employers receive stable domain-based IDs, are preserved on CSV reimport and show “Added research” provenance. For a verified recruiting board, add `adapter` and `board`. Supported boards: Greenhouse token; Lever token with optional `@eu`; Ashby token; SmartRecruiters company identifier; Workday `tenant/wdN/site`. Do not guess or silently substitute another company. Preserve the official careers evidence that establishes ownership.

Wikidata discovery requires exact ticker matching and meaningful name overlap. Treat its website matches as candidates; company career pages establish feed ownership. HTML obeys robots.txt. Documented public ATS feeds use their read-only public endpoints. No application forms are submitted.

## Checks

```sh
python3 -m unittest discover -s scraper/tests -v
node --experimental-strip-types scripts/test-costs.mjs
npx tsc --noEmit
npm run build:pages
```

Tests cover cost scenarios without double-counting Apple and Stripe, external employer retention, partial Workday responses, inventory reconciliation, remote restrictions, title levels, salary uncertainty, feed parsing/pagination, safe description text and retirement only after two complete successful scans. No confidential user documents are used in tests.
