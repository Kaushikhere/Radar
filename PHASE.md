# Radar — Phase Tracker

What is being pushed in each phase, and why. [PLAN.md](PLAN.md) holds the full plan;
this file tracks progress against it. Update it in the same commit as the work it describes.

Related: [DECISIONS.md](DECISIONS.md) for why each choice was made,
[ARCHITECTURE.md](ARCHITECTURE.md) for the system design and the alternatives rejected.

## Status

| Phase | What it delivers | Estimate | Status |
|---|---|---|---|
| Docs | PRD, plan, decisions, architecture | — | Done |
| 0 | Skeleton and data spike | 1 week | Not started |
| 1 | Prices for 50 stocks | 2 weeks | Not started |
| 2 | Fundamentals for the same 50 | 3–4 weeks | Not started |
| 3 | Full universe | 2–3 weeks | Not started |
| 4 | Backtest | 2 weeks | Not started |
| 5 | Product | 3 weeks | Not started |
| 6 | ML experiment | 2 weeks | Not started |

**Current phase:** 0 (next up)

## How to use this file

- A phase is done only when its gate passes. Tick the gate last.
- Do not start a phase before the previous gate passes. The order exists so that
  each phase's data can be trusted by the next.
- Every push gets one line in the push log at the bottom: what changed and why.

---

## Phase 0 — Skeleton and data spike

**Why this phase exists.** Two unknowns can change the whole plan: how many years of
filings exist, and whether a scheduled job can download from the exchange. Both are
cheap to check now and expensive to discover in Phase 3.

**What gets pushed**
- [ ] Repo layout, `docker-compose.yml` with Postgres
- [ ] Alembic set up with an empty first migration
- [ ] pytest and linting configured
- [ ] GitHub Actions CI workflow
- [ ] Data spike notes: earliest usable `reported_at` for 5 stocks
- [ ] Scheduled workflow that fetches one bhavcopy and one filing

**Gate**
- [ ] CI is green on an empty app
- [ ] Earliest filing year and likely backtest window are written down
- [ ] Scheduled download works, or a fallback (self-hosted runner or local cron) is chosen

## Phase 1 — Prices for 50 stocks

**Why this phase exists.** Every return, trend score and backtest number depends on
correct adjusted prices. Getting this right on 50 stocks is far easier than debugging
it on 500.

**What gets pushed**
- [ ] Migrations for `stocks`, `symbol_history`, `prices`, `corporate_actions`, `index_prices`
- [ ] Bhavcopy ingest, mapped through `symbol_history`
- [ ] Corporate actions ingest
- [ ] Adjusted-price view
- [ ] Index total-return ingest
- [ ] Trend factor returning `{score, evidence[]}`
- [ ] `/stocks/{symbol}` endpoint
- [ ] Adjustment test

**Gate**
- [ ] Adjusted prices match a reference for 5 stocks, including one with a split or bonus

## Phase 2 — Fundamentals for the same 50

**Why this phase exists.** Fundamentals carry 85% of the score (F, V and O). This is
also where look-ahead bias enters, so the point-in-time rule is built and tested here.

**What gets pushed**
- [ ] Migrations for `financials_quarterly`, `shareholding`, `scores`
- [ ] Results ingest from exchange filings, with `reported_at`
- [ ] Shareholding ingest, with `reported_at`
- [ ] F, V and O factors, each returning `{score, evidence[]}`
- [ ] Total score with re-weighting for missing factors
- [ ] Look-ahead test, evidence test, missing-data test

**Gate**
- [ ] Look-ahead test passes
- [ ] Every score has at least one evidence line

## Phase 3 — Full universe

**Why this phase exists.** A backtest on today's 50 survivors proves nothing. This
phase adds the stocks that were in the index on each past date, including the ones
that later delisted.

**What gets pushed**
- [ ] Migration for `index_membership`
- [ ] Nifty 500 membership rebuilt from change notices
- [ ] Delisted stocks added to `stocks` and `prices`
- [ ] Liquidity filter
- [ ] Bank/NBFC factor set
- [ ] Small-sector fallback to sector group
- [ ] Survivorship test
- [ ] Coverage report

**Gate (membership)**
- [ ] Rebuilt membership matches a published constituent list on 3 past dates
- [ ] It includes at least one stock that later delisted

**Gate (coverage)**
- [ ] Usable years from Phase 0 are confirmed on the full universe
- [ ] Data coverage is above the threshold set for it

## Phase 4 — Backtest

**Why this phase exists.** This is the evidence for whether the scoring works. It is
also the first point where the project is presentable.

**What gets pushed**
- [ ] Migration for `picks`
- [ ] Backtest engine following PLAN.md section 7
- [ ] Quarterly run and annual-rebalance run
- [ ] Results per calendar year: excess return, hit rate, drawdown, turnover
- [ ] Written results, including the bad years
- [ ] Determinism test

**Gate**
- [ ] One command reproduces the full result

**Checkpoint:** the project is presentable from here.

## Phase 5 — Product

**Why this phase exists.** Turns the data and backtest into something a person can
open and use, and proves the pipeline runs unattended.

**What gets pushed**
- [ ] Migrations for `announcements`, `pipeline_runs`
- [ ] Remaining API endpoints
- [ ] Three screens: Home, Stock detail, Scorecard
- [ ] Deployment
- [ ] Weekly scheduled run with failure alerts
- [ ] Keyword red flags
- [ ] Live paper portfolio
- [ ] Telegram alerts
- [ ] Learn-mode tooltips

**Gate**
- [ ] The weekly run succeeds 4 times in a row with no manual fix

## Phase 6 — ML experiment

**Why this phase exists.** Tests whether a learned ranker beats the fixed weights. A
negative result is expected and is still worth publishing.

**What gets pushed**
- [ ] LightGBM ranker on forward excess return
- [ ] Purged walk-forward validation
- [ ] SHAP explanations
- [ ] Write-up of the result, positive or negative

**Gate**
- [ ] Beats the rule-based score on unseen years. If not, Radar stays rule-based.

---

## Push log

One line per push, newest first.

| Date | Phase | What was pushed | Why |
|---|---|---|---|
| 2026-11-11 | Docs | `PHASE.md`, `DECISIONS.md`, `ARCHITECTURE.md` | Record what each phase delivers, why each decision was made, and which alternatives were rejected |
| 2026-11-11 | Docs | Revised `PLAN.md`; one-line fix in `PRD.md` | Move the data check to Phase 0, fix schema gaps (ROCE inputs, restatements, same-day look-ahead, demergers), add an annual-rebalance run |
| 2026-11-11 | Docs | `PRD.md`, `PLAN.md` | Put the original PRD and the revised plan under version control |
