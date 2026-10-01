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
| Crawler and backend maintenance | $900 | 12 hours × $75/hour |
| Customer web-app maintenance (web + iOS only) | $300 | 4 hours × $75/hour |
| Additional iOS maintenance | $450 | 6 hours × $75/hour |
| Apple Developer Program allocation | $8.25 | $99/year; shared across apps |

Sources: [Workers](https://developers.cloudflare.com/workers/platform/pricing/), [Supabase](https://supabase.com/pricing), [Resend](https://resend.com/pricing), [Apple membership](https://developer.apple.com/programs/whats-included/).

For the **web + iOS** scenario, fixed infrastructure is **$112/month**. Including crawler/backend maintenance, web-app maintenance, iOS maintenance and Apple membership gives **$1,770.25/month fixed cost**. At 1,000 subscribers, add $100 variable reserve: **$1,870.25 before storefront/payment fees**. If using private GitHub runners in the base case, add $4.20. An existing Apple membership adds $0 incremental membership cost; $8.25 here is an allocation, not a second account fee.

iOS maintenance covers OS/SDK changes, device testing, accessibility, release preparation, subscription issues and TestFlight/App Store review iterations. A reasonable sensitivity is 4–12 additional hours/month ($300–$900), separate from crawler/backend and customer web-app maintenance. Hardware is not in the recurring base: budget $500–$1,500 one time for test devices if suitable devices are unavailable, plus a compatible Mac if needed. These are planning allowances, not device quotes. Use existing hardware and local Xcode builds first; paid macOS CI and third-party subscription tooling are optional and not included.

## iOS app only: separate launch scenario

**An iOS-only paid product is the recommended first production scope.** Keep the existing free prototype for validation; ship the native app with a shared server-side crawler and catalog API. No customer web app or web checkout is needed. A small privacy/support/marketing page remains within the hosting allowance. The scraper cannot run reliably every day on each customer’s iPhone, so removing the web app does not remove collection, database, authentication, entitlement checks or backend costs.

To make the comparison explicit, the original 16-hour core-maintenance allowance is now split into **12 hours for the crawler/backend and four hours for the customer web app**. iOS-only removes those four web hours ($300/month); its six iOS hours remain. This split is a planning assumption, not a measured saving. The underlying infrastructure allowance stays the same because shared data services still exist. Push notifications could later reduce email use, but no speculative email saving is assumed.

| Recurring iOS-only cost | Monthly | Yearly |
|---|---:|---:|
| Infrastructure and reserves, before per-user reserve | $112.00 | $1,344.00 |
| Apple membership allocation | $8.25 | $99.00 |
| Crawler/backend maintenance: 12 h × $75 | $900.00 | $10,800.00 |
| iOS maintenance: 6 h × $75 | $450.00 | $5,400.00 |
| **Fixed budget, before subscribers and Apple commission** | **$1,470.25** | **$17,643.00** |

Add **$0.10 per subscriber per month** and Apple’s commission on sales. Services and reserves excluding labor and commission are $120.25/month with zero subscribers, or **$220.25/month at 1,000 subscribers**. These amounts include contingency reserves, not just vendor invoices. Founder-performed maintenance can reduce cash payments, but its time is still a cost. Existing Apple membership adds no new membership fee; subtract the $8.25 allocation when modeling incremental cash. No separate Stripe or recurring iOS hosting fee is added; backend hosting is already counted.

At **1,000 subscribers, all paying $14.99 monthly**, steady usage for 12 months:

| Product / commission | Total/month including labor and fees | Total/year | Monthly-plan break-even |
|---|---:|---:|---:|
| **iOS only, Apple 15%** | **$3,818.75** | **$45,825.00** | **117 subscribers** |
| iOS only, Apple 30% | $6,067.25 | $72,807.00 | 142 subscribers |
| Web + iOS, all purchases through Apple at 15% | $4,118.75 | $49,425.00 | 141 subscribers |
| Web + iOS, all purchases through Apple at 30% | $6,367.25 | $76,407.00 | 171 subscribers |
| Web only, modeled Stripe fees | $2,251.64 | $27,019.68 | 94 subscribers |

The difference between iOS-only and web + iOS is **$300/month or $3,600/year** under these assumptions. Web-only has different storefront fees, so its lower total is not a pure engineering comparison. The web + iOS scenarios above assume all purchases occur on iOS; a real web/iOS purchase mix would change fees.

If all 1,000 iOS-only subscribers choose **$119.99 annually**, the monthly-equivalent budget is **$3,070.13 at 15%** or **$4,570.00 at 30%**, and break-even is **176 or 214 annual subscribers**, respectively. At a 50/50 monthly/annual mix, iOS-only break-even is **140 at 15%** or **171 at 30%**. Annual-plan costs and revenue are amortized for comparison; subscriptions are paid up front. These are budget scenarios, not subscriber-growth forecasts, and exclude acquisition, tax, refunds and initial development.

## Projected profits

**Profit here means operating revenue minus the modeled recurring costs**, including maintenance labor, reserves, per-user services and storefront/payment fees. It is before tax, refunds, initial engineering and any owner compensation beyond the maintenance allowance. Marketing is **$0 in the base tables**; this is not an assumption that customers can be acquired for free. The calculator has a monthly marketing-budget input that reduces profit and raises break-even. There is no customer-demand evidence yet, so these are conditional projections rather than a forecast of likely sales.

For **iOS only, $14.99/month and Apple at 15%**, holding the subscriber count steady:

| Paying subscribers | Revenue/month | Cost/month | Operating profit/month | Operating profit/year |
|---|---:|---:|---:|---:|
| 100 | $1,499.00 | $1,705.10 | **−$206.10** | **−$2,473.20** |
| 250 | $3,747.50 | $2,057.38 | $1,690.13 | $20,281.50 |
| 500 | $7,495.00 | $2,644.50 | $4,850.50 | $58,206.00 |
| 1,000 | $14,990.00 | $3,818.75 | **$11,171.25** | **$134,055.00** |

Yearly figures use unrounded monthly calculations × 12. They assume that many paying subscribers throughout all 12 months; they are not a first-year growth forecast. The 100-subscriber case loses money after the labor allowance. At 1,000 subscribers the modeled iOS-only margin is 74.5% before omitted costs. If marketing is $500/month, profit falls to **$10,671.25/month or $128,055/year** and monthly-plan break-even rises to 156 subscribers.

Comparison at **1,000 subscribers all paying monthly**, with $0 marketing:

| Product / payment scenario | Operating profit/month | Operating profit/year |
|---|---:|---:|
| **iOS only, Apple 15%** | **$11,171.25** | **$134,055.00** |
| iOS only, Apple 30% | $8,922.75 | $107,073.00 |
| Web + iOS, all sales through Apple at 15% | $10,871.25 | $130,455.00 |
| Web + iOS, all sales through Apple at 30% | $8,622.75 | $103,473.00 |
| Web only, modeled Stripe fees | $12,738.36 | $152,860.32 |

Annual subscriptions generate less monthly-equivalent revenue. With **1,000 iOS-only annual subscribers at $119.99/year**, projected profit is **$6,929.04/month equivalent or $83,148.50/year at 15%**, or **$5,429.17/month equivalent or $65,150.00/year at 30%**. Initial engineering is a separate cash outlay, so launch-year cash remaining will be lower. At scale, adjust support, collection, backend and acquisition budgets rather than assuming profit grows linearly forever. Churn and conversion still need validation.

## Web + iOS: App Store fees and break-even

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

| Remaining engineering work | Hours | Allowance at $75/hour |
|---|---:|---:|
| Shared production backend, crawler hardening and source onboarding | 100–240 | $7,500–$18,000 |
| Customer web app production work, if retained | 20–60 | $1,500–$4,500 |
| Native iOS app, StoreKit, device testing and launch materials | 80–160 | $6,000–$12,000 |
| **iOS only: backend + native app** | **180–400** | **$13,500–$30,000** |
| Web + iOS: all three workstreams | 200–460 | $15,000–$34,500 |
| Web only: backend + customer web app | 120–300 | $9,000–$22,500 |

This refines the earlier shared-service allowance by separating 20–60 hours of customer web-app work. The iOS-only plan avoids an estimated **$1,500–$4,500** of that work. All ranges estimate work remaining after the prototype; they do not value work already completed or represent cash already spent. They exclude hardware, licensed datasets, legal/privacy review and marketing. Scope and existing assets can materially change these estimates. Use the recurring-cost table separately; do not count one-time engineering as a monthly expense.

No iOS app has been built or submitted as part of this prototype. No Apple membership or subscription product has been purchased or created. The report now treats iOS as the intended launch channel.

## Pricing validation

Keep the $14.99/$119.99 recommendation for testing after the catalog meets the minimum and sustains quality. FlexJobs advertises $23.95 every four weeks, $29.85 quarterly and $71.40 annually, so our annual proposal requires demonstrable extra value. Every four weeks is not calendar monthly. If users do not value the differentiation, test a lower beta price before raising it; avoid disguising an incomplete catalog with a large raw listing count. [FlexJobs pricing](https://www.flexjobs.com/pricing).

The in-app calculator now defaults to **iOS app only**, public GitHub runners and Apple at 15%. It also shows web + iOS and web-only comparisons, selectable 30% sensitivity, monthly/annual mix, collection time, separate backend/web/iOS maintenance hours, annualized operating cost, projected profit, and a monthly marketing budget. The 1,000-posting threshold refers to inventory; 1,000 subscribers is a separate financial scenario.
