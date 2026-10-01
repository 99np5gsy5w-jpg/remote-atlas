# Remote Atlas operating costs and subscription recommendation

Prepared October 1, 2026. USD. Vendor prices checked on that date; workload and labor estimates are planning assumptions, not quotes or a completed full-universe benchmark.

## Recommendation

Launch at **$14.99 per month or $119 per year**, once the collection coverage and daily freshness are reliable enough to justify charging. Annual billing is $9.92/month equivalent and saves 33.8% relative to 12 monthly payments. Keep a free limited search tier. Include unlimited ordinary searches and local document matching; avoid unlimited expensive AI rewrites in this price.

The current GitHub edition is a free research prototype with no checkout. It must not be represented as a production subscription service. GitHub Pages explicitly disallows using it to run commercial SaaS. Keep GitHub for source, tests and scheduled collection; move the customer-facing paid service to a suitable host when launching subscriptions.

## What the input files actually contain

| Measure | Count |
|---|---:|
| NYSE.csv rows | 2,917 |
| otherExchanges.csv rows | 7,622 |
| Total input rows retained | 10,539 |
| Duplicate symbols across files | 2,917 |
| Unique securities | 7,622 |
| Explicitly marked ETFs | 4,456 |
| Non-ETF securities | 3,166 |
| Conservatively grouped employer candidates | 2,413 |
| Fund/ETF records requiring sponsor mapping | 4,724 |

Every NYSE symbol appears in the other file. The files have no website or industry columns. One ETF, SVIX, has a blank company name; its Security Name supplies the missing label. Employer candidates are a name-based grouping, not a verified count of distinct operating companies. Funds are retained for sponsor resolution, not counted as thousands of separate hiring organizations.

The exchange codes in these files are N, P, Z, A and F. The column named NASDAQ Symbol is not proof of Nasdaq listing: these inputs omit many Nasdaq-listed employers. Expanding coverage to those companies requires another input list. The app does not silently add unrelated employers.

## Scraper design and measured evidence

Collect once for the whole app, then share that job catalog across subscribers. Do not recrawl thousands of websites for each user. Prefer employer-linked public recruiting feeds to browser automation. The implementation has adapters for Greenhouse, Lever, Ashby, SmartRecruiters, Workday and Schema.org JobPosting pages. Coverage remains incomplete; the interface shows healthy, partial, blocked, failed, unresolved and sponsor-needed records.

The first broad discovery pilot processed 12 employers: 250 HTTP requests, 37.3 MB transferred and 249.3 seconds elapsed. It found one complete feed, two blocked sources and nine failures. It is a small, alphabetically selected onboarding sample, **not representative of steady-state costs or total attainable coverage**. Website discovery initially found 1,145 candidates using public Wikidata evidence. A separate measured known-feed run fetched 917 postings from three employers in 3.16 seconds with three requests and 16.99 MB transferred, yielding 70 remote postings. This favorable sample also does not establish full-universe coverage or cost. Current counts and timestamps are in the app’s Company coverage tab.

The crawler measures elapsed seconds, request counts, bytes and cache hits on every run. Public-feed pagination is bounded; an incomplete enumeration cannot retire missing jobs. Two complete successful scans are needed to close a disappeared posting. Failed scans preserve jobs but search hides jobs unverified for more than seven days. HTML traversal is always marked partial because unseen JavaScript or pagination can hide postings. It honors robots.txt for HTML and Workday pages, rate-limits hosts, respects Retry-After, caps responses, checks URLs and never bypasses logins, CAPTCHAs or access restrictions.

## Daily collection model

Plan against 2,413 employer candidates and 30 runs/month. A useful steady-state scenario is eight HTTP requests per employer per day, or **19,304/day and 579,120/month**. This is an assumption: large Workday employers can require far more detail requests; a complete Greenhouse feed often needs one request.

Budget these runner scenarios until a full benchmark replaces them:

| Scenario | Runner minutes/day | Minutes/month | Public standard GitHub runner | Private GitHub Free runner* |
|---|---:|---:|---:|---:|
| Efficient feeds | 30 | 900 | $0 | $0 |
| Base | 90 | 2,700 | $0 | $4.20 |
| Large or slow feeds | 300 | 9,000 | $0 | $42.00 |

*Private cost = max(0, monthly minutes − 2,000) × $0.006 for standard Linux 2-core. The allowance is shared across the account; if other projects consume it, the base crawl costs $16.20/month and the large case $54.00. Public standard runner minutes are free. Larger runners are charged. Store crawler state in a bounded cache and avoid accumulating daily artifacts. GitHub includes 10 GB cache/repository; additional configured cache is $0.07/GB-month and artifact storage beyond the account allowance is $0.25/GB-month. The workflow does not raise paid limits or provision larger runners.

The daily job is scheduled for 07:17 UTC (3:17 a.m. New York during daylight time; 2:17 a.m. in standard time). GitHub schedules can be delayed, and inactive public repositories can have schedules disabled after 60 days. This is suitable for a prototype, not a strict freshness SLA. The job has a 300-minute collection budget and records deferred sources rather than pretending to finish them.

Optional browser fallback is not implemented or enabled in this version. At Cloudflare’s published rate, 25% of 2,413 companies × four pages × 15 browser-seconds × 30 days = 301.6 browser-hours/month; after 10 included hours, browser time is about **$26.25/month**, plus Workers, concurrency, and any external service costs. This does not guarantee access to blocked sites. Apify Starter is an alternative with $19/month prepaid usage and $0.20 per GB-RAM-hour; its credits are consumed, so do not add the $19 minimum twice. Licensed data/enrichment vendors are a separate option requiring a quote or plan, not an assumed free capability.

## Other app costs

For a paid launch with 1,000 monthly active subscribers, plan for two documents per user at 1 MB each, around 2 GB of originals plus extracted text, metadata and backups. Document parsing and vocabulary matching in this prototype run on-device, with **$0 per-match API charges**. There is no third-party model receiving resumes. The paid version needs user authentication, private object storage, per-user access policies, deletion and retention controls, and a secure subscription backend.

| Expense | Base monthly budget | Basis |
|---|---:|---|
| App hosting | $5 | Cloudflare Workers paid baseline; independent account required |
| Database, auth and private file storage | $25 | Supabase Pro starting plan; usage limits and compute apply |
| Email | $20 | Resend Pro: 50,000/month; optional alerts are not implemented |
| Monitoring and backup allowance | $20 | Planning allowance, not a quoted vendor bundle |
| Domain | $2 | $24/year planning allowance; registration/TLD varies |
| Collection contingency | $40 | Planning reserve for retries or approved external services |
| Daily scraper compute | $4.20 | Base private-runner scenario above; public repo is $0 |
| Variable service reserve | $0.10/subscriber | Budget reserve, not incurred by local matching |
| Maintenance | $1,200 | 16 hours/month × $75/hour assumption |

Base fixed infrastructure is **$116.20/month** using the private-runner scenario or **$112/month** with public runners. At 1,000 subscribers, add $100 variable reserve and $1,200 maintenance: **$1,416.20/month before payment fees and acquisition**. At the all-monthly recommended price, payment processing adds $839.64, for a total modeled operating cost of **$2,255.84/month**. Revenue would be $14,990/month and the modeled operating surplus $12,734.16 before omitted business costs. This is arithmetic, not a revenue forecast.

Practical ranges: a free GitHub prototype can have $0 direct hosting/runner charges within platform limits; a lean paid service might need $50–$250/month infrastructure; a broader catalog with licensed data, browsers or heavier AI could need $250–$1,500+ before labor. At 8–40 maintenance hours/month and $75/hour, labor adds $600–$3,000. Add customer support, accounting, privacy/security review, insurance, tax administration, chargebacks and marketing as the business grows. Initial engineering and company-source onboarding are one-time costs: a planning allowance of 120–300 hours at $75/hour is $9,000–$22,500, excluding unusually difficult sites or licensed data. No such amount has been spent by this prototype.

## Unit economics

Assuming U.S. domestic web-card payments through Stripe: payment fee 2.9% + $0.30, plus recurring Billing at 0.7%. International cards, FX, tax tooling, disputes and refunds can add cost. Native app-store sales are excluded; their economics require a separate model.

| Plan | Gross revenue/month equivalent | Payment fee/month equivalent | Variable reserve | Contribution/month |
|---|---:|---:|---:|---:|
| $14.99 monthly | $14.990 | $0.83964 | $0.10 | $14.05036 |
| $119 annual | $9.91667 | $0.38200 | $0.10 | $9.43467 |
| 50% monthly / 50% annual | $12.45333 | $0.61082 | $0.10 | $11.74251 |

Annual fees are charged once on $119: $119 × 3.6% + $0.30 = $4.584/year. Annual revenue is recognized here at 1/12; cash collected up front is not monthly recurring cash flow.

At $1,316.20 fixed operating cost (infrastructure plus maintenance), estimated break-even is **94 monthly subscribers**, **140 annual subscribers**, or **113 subscribers at a 50/50 mix**. This excludes marketing, founder compensation, taxes and one-time engineering. At the 50/50 mix, 100 subscribers produce about −$142/month, 1,000 about $10,426/month, and 10,000 about $116,109/month before scale-driven staffing and infrastructure changes; the last figure is a sensitivity calculation, not a scalable cost promise.

Job-search subscriptions naturally churn when people find work. At $14.05 monthly contribution and an assumed 25% monthly churn, simple contribution LTV is $56.20; a 3:1 LTV/CAC target implies acquisition cost around $18.73 or less before fixed expenses. With 15–35% churn, contribution LTV ranges $93.67–$40.14. Validate with actual cohorts rather than offering lifetime or heavily discounted annual plans prematurely.

FlexJobs currently lists $23.95 every four weeks after its trial, $29.85 quarterly, and $71.40 annually. Every four weeks is not calendar monthly. The $119 annual recommendation is a premium to that annual plan and needs measurable value: fresh employer-direct opportunities, transparent restrictions and useful matching. Test $99 versus $119 annually and $12.99 versus $14.99 monthly after coverage is established. If that value is not demonstrated, use $9.99/month or $79/year for an early paid beta instead of claiming premium value from an incomplete catalog.

## Sources

- GitHub Actions rates and allowances: https://docs.github.com/en/billing/concepts/product-billing/github-actions
- GitHub Pages hosting limits: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- Scheduled workflows: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
- Cloudflare Workers: https://developers.cloudflare.com/workers/platform/pricing/
- Cloudflare Browser Run: https://developers.cloudflare.com/browser-run/pricing/
- D1 and R2: https://developers.cloudflare.com/d1/platform/pricing/ and https://developers.cloudflare.com/r2/pricing/
- Supabase: https://supabase.com/pricing
- Resend: https://resend.com/pricing
- Apify: https://apify.com/pricing
- Stripe Payments and Billing: https://stripe.com/pricing
- FlexJobs: https://www.flexjobs.com/pricing
- Employer feed documentation: https://docs.greenhouse.io/job-board.html and https://github.com/lever/postings-api

Prices are sourced above; workload, labor, conversion, retention, and reserves are explicitly modeled assumptions. The interactive Operating costs screen lets you change subscribers, runner minutes and maintenance hours.
