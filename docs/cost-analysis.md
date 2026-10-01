# Remote Atlas: daily collection and iOS launch economics

Updated October 1, 2026. USD. Vendor rates were checked on this date. Workload, labor, conversion and retention figures are assumptions unless labeled as measured. No paid services have been purchased.

## Recommendation and launch threshold

Target **$14.99/month or $119.99/year** for the iOS launch, subject to available App Store price points and local pricing. Annual billing is approximately $10/month, a 33.3% discount. This replaces the earlier $119 annual planning figure. Keep a free limited-search tier and validate conversion before committing to the price.

The user’s minimum is **1,000 active remote postings**. Count deduplicated employer postings with a description, direct link and explicit remote evidence; exclude hybrid jobs, expired jobs and listings not verified within seven days. A posting is not a guarantee of a separate headcount. Reaching this threshold is necessary, but daily reliability, useful country-specific results and sustained customer value also matter. Review collection health and sample posting links over a 14-day beta before charging; this observation period has not yet been completed.

The stock-exchange files are a starting inventory. Additional researched private and Nasdaq-listed employers are now included and labeled separately. Current counts are in the app’s Company coverage tab. The initial 70-role catalog was a pilot, not a proposed paid launch catalog.

## What the files contain

| Input measure | Count |
|---|---:|
| NYSE.csv rows | 2,917 |
| otherExchanges.csv rows | 7,622 |
| Rows retained, including duplicates | 10,539 |
| Unique securities | 7,622 |
| Explicit ETFs | 4,456 |
| Non-ETF securities | 3,166 |
| Conservatively grouped employer candidates from the files | 2,413 |
| Fund/ETF records requiring sponsor mapping | 4,724 |

All NYSE symbols also occur in the other file. Neither file contains websites or industries. These are securities lists, so multiple share classes and funds do not each represent a separate hiring company. Every source row remains in the database. CSV-derived candidates and additional researched employers have distinct provenance. Full coverage of every company and fund sponsor remains incomplete.

## Scraper design and measurements

Run one shared collection daily for every app user. The scraper supports Greenhouse, Lever, Ashby, SmartRecruiters, Workday and Schema.org job pages. It records successful, partial, blocked, failed and unresolved sources; it does not bypass logins or access restrictions. HTML and Workday requests observe robots.txt. Hosts are throttled, requests have retry and size limits, and jobs disappear only after two complete successful scans or explicit expiration. Search also hides jobs unverified for seven days.

Measured onboarding runs:

| Sample | HTTP requests | Downloaded data | Elapsed | Result |
|---|---:|---:|---:|---|
| First 12-company discovery pilot | 250 | 37.3 MB | 249.3 s | 1 complete feed, 2 blocked, 9 failures |
| Three known feeds | 3 | 17.0 MB | 3.16 s | 917 postings; 70 remote |
| Expanded 12-employer feed check | 12 | 20.6 MB | 9.22 s | 1,488 postings before remote filtering |

These samples are not representative full-universe benchmarks. The expanded run included companies outside the files. It brought the exported catalog to **1,414 remote postings after suppressing five identical-content duplicates**, across 14 employers with remote results. Counts can rise or fall as jobs open and close. The snapshot is not proof of 14 days of reliability. Known public feeds are inexpensive; discovering and maintaining thousands of company integrations is the expensive work.

Large Workday boards can contain tens of thousands of on-site vacancies. Where available, the crawler uses employer-provided remote-location filters for boards larger than 2,000 jobs, labels coverage partial and preserves partial results when detail requests fail. Structured work-arrangement fields override location wording, so a hybrid job labeled “Work at Home” is not counted as remote. Large feeds have a 30-minute source budget within a 300-minute overall daily budget; other sources have five minutes. Deferred sources remain visible.

## Daily compute and hosting

For planning, 2,413 starting candidates × eight requests × 30 days is **579,120 requests/month**. Additional employers increase this in proportion to their feeds. Reuse cached public responses; subscriber count does not multiply crawl volume.

| Daily runner time | Minutes/month | Public standard GitHub runner | Private GitHub Free runner* |
|---|---:|---:|---:|
| 30 minutes | 900 | $0 | $0 |
| 90 minutes | 2,700 | $0 | $4.20 |
| 300 minutes | 9,000 | $0 | $42.00 |

*Private scenario: max(0, minutes − 2,000) × $0.006, assuming the account’s full included allowance remains available. Without that allowance, the 90-minute case is $16.20/month. Larger runners are extra. GitHub includes 10 GB cache per repository; configured excess cache is $0.07/GB-month, and excess artifact storage is $0.25/GB-month. The workflow uses standard public runners and does not raise paid limits. [GitHub Actions pricing](https://docs.github.com/en/billing/concepts/product-billing/github-actions).

The schedule is 07:17 UTC daily, with deferred sources reported after the time budget. GitHub can delay scheduled runs and disable schedules on public repositories after 60 days without activity. This does not provide a freshness SLA. [Scheduled workflow behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

The **free prototype can cost $0 in direct GitHub hosting and runner charges** within limits. GitHub Pages does not permit commercial SaaS hosting. Keep GitHub for code and collection; a paid iOS product should use a production catalog API and backend on a suitable host. [Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits).

Optional browser fallback is not implemented. As a sensitivity: 25% of 2,413 employers × four pages × 15 seconds × 30 days = 301.6 browser-hours/month. At Cloudflare’s published browser-time rate, after ten included hours, that is about $26.25/month plus Workers and concurrency costs. It does not guarantee access to blocked sources. Apify Starter is another option at $19/month prepaid usage and $0.20/GB-RAM-hour; do not add prepaid credits twice. Licensed data or company enrichment needs a separate quote. [Cloudflare Browser Run](https://developers.cloudflare.com/browser-run/pricing/), [Apify pricing](https://apify.com/pricing).

## Shared backend and iOS operating costs

A paid service needs authentication, private document storage, user-level access controls, retention/deletion, entitlement verification, alerts and monitoring. These are future production requirements, not implemented cloud services in the prototype. The current resume and cover-letter parsing and matching run on the user’s device, so they incur no model API charges. Two 1 MB files for 1,000 users require approximately 2 GB before backups and extracted text.

| Monthly expense | Base allowance | Basis |
|---|---:|---|
| Hosting/API | $5 | Cloudflare Workers paid baseline |
| Database, authentication and private files | $25 | Supabase Pro starting plan; usage/compute limits apply |
| Email | $20 | Resend Pro; 50,000/month |
| Monitoring and backups | $20 | Planning reserve |
| Domain | $2 | $24/year planning reserve |
| Collection contingency | $40 | Planning reserve |
| Public GitHub crawler | $0 | Standard public runners within limits |
| Variable services | $0.10/user | Reserve, not a per-match charge |
| Core maintenance | $1,200 | 16 hours × $75/hour |
| Additional iOS maintenance | $450 | 6 hours × $75/hour |
| Apple Developer Program allocation | $8.25 | $99/year; shared across apps |

Sources: [Workers](https://developers.cloudflare.com/workers/platform/pricing/), [Supabase](https://supabase.com/pricing), [Resend](https://resend.com/pricing), [Apple membership](https://developer.apple.com/programs/whats-included/).

Fixed infrastructure is **$112/month**. Including core maintenance, iOS maintenance and Apple membership gives **$1,770.25/month fixed cost**. At 1,000 subscribers, add $100 variable reserve: **$1,870.25 before storefront/payment fees**. If using private GitHub runners in the base case, add $4.20. An existing Apple membership adds $0 incremental membership cost; $8.25 here is an allocation, not a second account fee.

iOS maintenance covers OS/SDK changes, device testing, accessibility, release preparation, subscription issues and TestFlight/App Store review iterations. A reasonable sensitivity is 4–12 additional hours/month ($300–$900), separate from scraper maintenance. Hardware is not in the recurring base: budget $500–$1,500 one time for test devices if suitable devices are unavailable, plus a compatible Mac if needed. These are planning allowances, not device quotes. Use existing hardware and local Xcode builds first; paid macOS CI and third-party subscription tooling are optional and not included.

## App Store fees and break-even

Model StoreKit in-app subscriptions as the worldwide default. The App Store Small Business Program offers 15% commission to eligible enrolled developers; eligibility considers proceeds across associated accounts, with a $1 million threshold. Do not assume approval or eligibility from this app’s revenue alone. [Apple Small Business Program](https://developer.apple.com/app-store/small-business-program/).

For standard subscriptions, Apple describes 30% commission during the subscriber’s first paid year and 15% after one paid year. Small Business participants receive the 15% rate from the beginning. Taxes and adjustments affect actual proceeds. The model assumes prices before those adjustments. **Do not add Stripe charges to Apple-processed purchases.** [Apple subscription proceeds](https://developer.apple.com/app-store/subscriptions/).

| Channel / plan | Gross/month equivalent | Platform fee/month | Contribution after $0.10 reserve | Subscribers to cover fixed costs |
|---|---:|---:|---:|---:|
| iOS 15%, $14.99 monthly | $14.9900 | $2.2485 | $12.6415 | **141** |
| iOS 15%, $119.99 annual | $9.9992 | $1.4999 | $8.3993 | **211** |
| iOS 30%, $14.99 monthly | $14.9900 | $4.4970 | $10.3930 | **171** |
| iOS 30%, $119.99 annual | $9.9992 | $2.9998 | $6.8994 | **257** |

At a 50/50 monthly/annual mix, break-even is **169 subscribers at 15%** or **205 at 30%**. All scenarios include $1,770.25 fixed operating cost. They exclude acquisition, founder salary, taxes, refunds, initial development and scale-driven staffing.

At **1,000 all-monthly iOS subscribers**:

| Scenario | Gross/month | Modeled costs including commission | Operating surplus before omitted costs |
|---|---:|---:|---:|
| Apple 15% | $14,990 | $4,118.75 | $10,871.25 |
| Apple 30% | $14,990 | $6,367.25 | $8,622.75 |

These are calculations, not revenue forecasts. At 25% assumed monthly churn, contribution LTV is about $50.57 at 15% or $41.57 at 30%; a 3:1 LTV/CAC target implies acquisition costs below approximately $16.86 or $13.86 before fixed costs. Subscription retention is a major risk because successful job seekers often cancel.

For comparison, web purchases modeled with Stripe domestic card fees of 2.9% + $0.30 and Billing at 0.7% produce $14.0504 monthly-plan contribution, or $9.5142 annual-plan monthly-equivalent contribution. International/FX charges, taxes and disputes are extra. A web-only operation removes the iOS labor and Apple membership allocation. [Stripe pricing](https://stripe.com/pricing).

## iOS release work and initial investment

Reuse the catalog, source integrations and matching vocabulary. Build a native iOS experience with document import, saved searches, saved jobs, accessible filters, deep links, account deletion, and StoreKit purchase/restore flows. Validate entitlements on the backend and handle subscription renewal, expiration and refund notifications. Native features and customer utility matter for review; simply packaging the website is not sufficient. Storefront payment-link rules vary, so potential external-payment savings are not in the base model. [App Review Guidelines, sections 3.1 and 4.2](https://developer.apple.com/app-store/review/guidelines/), [Apple in-app purchases](https://developer.apple.com/in-app-purchase/).

One-time planning allowances, not amounts already spent:

- Shared production service and source onboarding: 120–300 hours × $75 = **$9,000–$22,500**.
- Additional native iOS app, StoreKit integration, testing and launch materials: 80–160 hours × $75 = **$6,000–$12,000**.
- Combined engineering: **$15,000–$34,500**, before hardware, licensed datasets, legal/privacy review or marketing. Scope and existing assets can materially change this.

No iOS app has been built or submitted as part of this prototype. No Apple membership or subscription product has been purchased or created. The report now treats iOS as the intended launch channel.

## Pricing validation

Keep the $14.99/$119.99 recommendation for testing after the catalog meets the minimum and sustains quality. FlexJobs advertises $23.95 every four weeks, $29.85 quarterly and $71.40 annually, so our annual proposal requires demonstrable extra value. Every four weeks is not calendar monthly. If users do not value the differentiation, test a lower beta price before raising it; avoid disguising an incomplete catalog with a large raw listing count. [FlexJobs pricing](https://www.flexjobs.com/pricing).

The in-app calculator now defaults to public GitHub runners and iOS at 15%, with selectable 30% and web scenarios, monthly/annual mix, collection time and maintenance hours. The 1,000-posting threshold refers to inventory; 1,000 subscribers is a separate financial scenario.
