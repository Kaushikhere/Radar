# Radar — Revised Plan

Revision of the Radar PRD (Nov 7, 2026). This version narrows the scope, fixes the
data model so the backtest can be trusted, and orders the work so there is
something to show after every phase.

## 1. Objective

Radar narrows about 500 NSE stocks to a short research list for a 1–3 year hold.
For each stock it shows why it ranked well, what could go wrong, and how past
shortlists performed against the market.

It is a research filter, not a stock picker. It does not predict prices or give
buy/sell advice.

**What success looks like**

| Goal | Expectation |
|---|---|
| Portfolio project for recruiters | Yes, regardless of stock results |
| Learning backend, data and ML engineering | Yes |
| A useful shortlist of decent companies | Probably |
| Consistently beating the market | Unlikely, and not provable on ~10 years of data |
| ML ranker beating the simple rules | Unlikely; treated as an experiment |

## 2. What changed from the PRD

| Area | PRD | Revised |
|---|---|---|
| Look-ahead | Financials keyed by `period_end` only | `reported_at` on financials and shareholding; scoring uses only rows published before the scoring date |
| Valuation data | No share count or EPS | `shares_outstanding` and `eps` stored per quarter |
| Price adjustment | Not covered | `corporate_actions` table covering splits, bonuses, dividends, rights issues and demergers; raw prices stored, adjusted at query time |
| Universe history | Today's stock list | `index_membership` with date ranges, plus delisted stocks |
| Benchmark | Nifty 50 | Nifty 500 total return (primary), Nifty 50 (secondary) |
| Rebalance | Weekly picks | Quarterly in the backtest, with an annual-rebalance run for comparison; results reported per year |
| Sector rules | One formula for all | Separate factor set for banks/NBFCs; fallback to sector group when a sector has fewer than 10 peers |
| News | FinBERT sentiment | Keyword red flags on exchange announcements; FinBERT deferred |
| Database | DuckDB, then Postgres + TimescaleDB | Postgres from day one, no TimescaleDB |
| Frontend | Streamlit or React (open) | FastAPI + minimal React |
| Scorecard | Live paper portfolio | Backtest scorecard shown now, labelled "backtest"; live portfolio accumulates alongside |

## 3. Scope

**In (v1)**
- Universe and liquidity filter
- Sector-relative scoring with four factors
- Evidence lines on every score
- "What could go wrong" section
- Backtest scorecard and live paper portfolio
- Weekly automated pipeline with run logs
- Keyword red-flag filter
- Telegram alerts and Learn-mode tooltips (cheap extras)
- One ML ranker experiment behind a gate

**Out**
- Company graph and news propagation
- IPO tracker
- FinBERT sentiment (revisit after v1)
- TimescaleDB
- Logins, payments, personalised advice

## 4. Scoring model

Score = 0.40 F + 0.25 V + 0.20 O + 0.15 T, each factor a percentile within the
stock's peer group. Weights are fixed for v1.

| Factor | Signals | Special handling |
|---|---|---|
| Fundamentals (F) | 3–5 year revenue and profit growth, ROE/ROCE, debt-to-equity, operating cash flow | Banks/NBFCs use asset quality (gross and net NPA), capital adequacy and return on assets instead |
| Valuation (V) | P/E and PEG vs peers and vs own 5-year history. P/E is market cap divided by trailing 12-month net profit, so splits and bonuses do not distort it | Loss-making companies get no V score; evidence reads "not meaningful" |
| Ownership (O) | Promoter holding trend, pledging, institutional holding change | — |
| Trend (T) | Long-term price trend on adjusted prices | — |

Rules:
- Every factor function returns `{score, evidence[]}`; the app shows the evidence unchanged.
- Peer group is the sector; if it has fewer than 10 scoreable stocks, use the sector group.
- A missing factor is stored as NULL with an evidence line saying why. The total is
  re-weighted over the factors that exist, and the stock is excluded from the
  shortlist if fewer than three factors are available.
- Balance-sheet and cash-flow fields are filed half-yearly or annually, not every quarter.
  Factors use the latest value published before the scoring date, and the evidence line
  states which period it came from.
- A red flag removes a stock from the shortlist; it does not change the score.
- Every score carries "Based on past data, not a prediction."

## 5. Data model

Twelve tables in Postgres. Everything keys on `stock_id` because symbols get renamed.

```sql
CREATE TABLE stocks (
  stock_id      SERIAL PRIMARY KEY,
  isin          TEXT UNIQUE NOT NULL,
  symbol        TEXT NOT NULL,            -- current symbol
  name          TEXT NOT NULL,
  sector        TEXT,                     -- peer group for ranking
  sector_group  TEXT,                     -- fallback when sector has < 10 peers
  industry      TEXT,
  is_financial  BOOLEAN DEFAULT FALSE,    -- bank/NBFC: uses the bank factor set
  listing_date  DATE,
  delisted_on   DATE,
  is_active     BOOLEAN DEFAULT TRUE
);

CREATE TABLE symbol_history (
  stock_id INT REFERENCES stocks, symbol TEXT,
  valid_from DATE, valid_to DATE,         -- NULL valid_to = current
  PRIMARY KEY (stock_id, valid_from)
);

CREATE TABLE index_membership (
  index_name TEXT, stock_id INT REFERENCES stocks,
  valid_from DATE, valid_to DATE,
  PRIMARY KEY (index_name, stock_id, valid_from)
);

CREATE TABLE prices (                     -- raw prices; adjust at query time
  stock_id INT REFERENCES stocks, date DATE,
  open NUMERIC, high NUMERIC, low NUMERIC, close NUMERIC,
  volume BIGINT, turnover NUMERIC,        -- turnover drives the liquidity filter
  PRIMARY KEY (stock_id, date)
);

CREATE TABLE corporate_actions (
  stock_id INT REFERENCES stocks, ex_date DATE,
  action_type TEXT,                       -- split | bonus | dividend | rights | demerger
  price_factor NUMERIC,                   -- e.g. 0.5 for a 1:1 bonus; for a demerger,
                                          -- the share of value left in the parent
  dividend_per_share NUMERIC,
  PRIMARY KEY (stock_id, ex_date, action_type)
);

CREATE TABLE index_prices (
  index_name TEXT, date DATE,
  close NUMERIC, total_return NUMERIC,    -- benchmark uses total_return
  PRIMARY KEY (index_name, date)
);

CREATE TABLE financials_quarterly (
  stock_id INT REFERENCES stocks,
  period_end DATE, reported_at DATE NOT NULL,   -- when the market could first see it
  is_consolidated BOOLEAN,
  revenue NUMERIC, net_profit NUMERIC,
  operating_profit NUMERIC,               -- with the two below, gives EBIT for ROCE
  finance_costs NUMERIC, tax_expense NUMERIC,
  operating_cf NUMERIC,                   -- often NULL: filed half-yearly or annually
  total_debt NUMERIC, equity NUMERIC,     -- often NULL: filed half-yearly or annually
  shares_outstanding NUMERIC, eps NUMERIC,
  total_assets NUMERIC, gross_npa_pct NUMERIC,  -- banks/NBFCs only
  net_npa_pct NUMERIC, capital_adequacy_pct NUMERIC,
  source_url TEXT,
  PRIMARY KEY (stock_id, period_end, is_consolidated, reported_at)  -- keeps restatements
);

CREATE TABLE shareholding (
  stock_id INT REFERENCES stocks,
  quarter_end DATE, reported_at DATE NOT NULL,
  promoter_pct NUMERIC, pledged_pct NUMERIC, fii_pct NUMERIC, dii_pct NUMERIC,
  PRIMARY KEY (stock_id, quarter_end, reported_at)  -- keeps restatements
);

CREATE TABLE announcements (              -- replaces news for v1
  id BIGSERIAL PRIMARY KEY,
  stock_id INT REFERENCES stocks, published_at TIMESTAMP,
  headline TEXT, category TEXT, source_url TEXT,
  red_flag BOOLEAN DEFAULT FALSE, red_flag_reason TEXT
);

CREATE TABLE scores (
  stock_id INT REFERENCES stocks, as_of DATE,
  factor TEXT,                            -- F | V | O | T | total
  score NUMERIC,                          -- NULL = not meaningful
  evidence JSONB NOT NULL,
  peer_group TEXT, peer_count INT,
  model_version TEXT,
  PRIMARY KEY (stock_id, as_of, factor, model_version)
);

CREATE TABLE picks (
  run_type TEXT,                          -- backtest | live
  as_of DATE, stock_id INT REFERENCES stocks,
  rank INT, score_at_pick NUMERIC, price_at_pick NUMERIC,
  model_version TEXT,
  PRIMARY KEY (run_type, as_of, stock_id, model_version)
);

CREATE TABLE pipeline_runs (
  run_id BIGSERIAL PRIMARY KEY, step TEXT,
  started_at TIMESTAMP, finished_at TIMESTAMP,
  status TEXT, rows_written INT, error TEXT
);
```

`reported_at` is a date, and results are usually published after market close. A row
is therefore usable only from the next day: every query filters on `reported_at < as_of`.

Known simplification: sector is today's classification, not its history. State this in the README.

## 6. Data sources

| Data | Source | Notes |
|---|---|---|
| Prices | NSE bhavcopy archives | Include delisted names; keyed by symbol, so map through `symbol_history` |
| Corporate actions | NSE corporate actions files | Needed before any return calculation; includes rights issues and demergers |
| Index levels | NSE index history (price and total return) | Nifty 500 TRI and Nifty 50 TRI |
| Index membership | NSE index constituent change notices | Rebuild date ranges from the change history; the hardest ingest in the plan, with its own gate in Phase 3 |
| Financials | Exchange result filings (XBRL) | Filing date gives `reported_at` |
| Shareholding | Exchange shareholding pattern filings | Filing date gives `reported_at` |
| Announcements | Exchange corporate announcements | Source for keyword red flags |

Batch and cache every download, and respect each site's terms. Screener.in is for
manual spot-checks only, not ingestion.

Two things are checked in Phase 0, before any ingest code is written:
- How many years of filings exist. The factors need 3–5 years of growth and 5 years of
  valuation history, so the first scoreable date is about 5 years after the earliest filing.
- Whether the scheduled job can download from the exchange at all. Exchange sites may
  block requests from cloud hosts such as GitHub Actions runners.

## 7. Backtest rules

- Universe on each date: stocks in the Nifty 500 on that date that pass the liquidity filter.
- Inputs: only rows with `reported_at < as_of`; prices up to `as_of`.
- Rebalance quarterly, equal weight, top N by total score after the red-flag filter.
- Also run an annual-rebalance variant, since the scores target a 1–3 year hold.
- Returns on adjusted prices including dividends, minus a fixed trading cost per rebalance.
- A stock that delists while held exits at its last traded price.
- Benchmark: Nifty 500 total return; Nifty 50 total return shown as a second line.
- Report excess return and hit rate per calendar year, plus the worst drawdown and portfolio turnover.
- The whole backtest runs from one command and produces the same numbers each time.

## 8. Architecture and stack

- **Language:** Python
- **Database:** Postgres, migrations with Alembic
- **Pipeline:** pandas jobs run weekly by GitHub Actions, each step logged to `pipeline_runs`
- **API:** FastAPI
- **Frontend:** minimal React, three mobile-first screens (Home, Stock detail, Scorecard)
- **ML experiment:** LightGBM + SHAP
- **Packaging:** Docker Compose locally; one free-tier host for the API and database
- **Alerts:** Telegram bot

## 9. Phased build plan

Time estimates assume part-time work and are guesses. Phase 2 is the most likely to overrun.

### Phase 0 — Skeleton and data spike (1 week)
- Repo, Docker Compose with Postgres, Alembic, pytest, linting, GitHub Actions CI
- Data spike on 5 stocks: download results and shareholding filings by hand and record
  the earliest usable `reported_at` for each
- Download test: one scheduled GitHub Actions job fetches a bhavcopy and a filing
- **Gate:** CI is green on an empty app; the earliest filing year and the likely backtest
  window are written down; the scheduled download works, or a fallback (self-hosted
  runner or local cron) is chosen

### Phase 1 — Prices for 50 stocks (2 weeks)
- Bhavcopy ingest, `symbol_history`, corporate actions, adjusted-price view
- Index total-return ingest
- Trend factor returning `{score, evidence[]}`
- First FastAPI endpoint: `/stocks/{symbol}`
- **Gate:** adjusted prices match a reference for 5 stocks, including one with a split or bonus

### Phase 2 — Fundamentals for the same 50 (3–4 weeks)
- Results and shareholding ingest from exchange filings with `reported_at`
- F, V and O factors; total score; missing-value handling
- **Gate:** look-ahead test passes; every score has at least one evidence line

### Phase 3 — Full universe (2–3 weeks)
- Nifty 500 with historical membership and delisted names
- Liquidity filter, bank/NBFC factor set, small-sector fallback
- **Gate (membership):** rebuilt Nifty 500 membership matches a published constituent
  list on 3 past dates, and includes at least one stock that later delisted
- **Gate (coverage):** the usable years estimated in Phase 0 are confirmed on the full
  universe; data coverage is above a threshold you set

### Phase 4 — Backtest (2 weeks)
- Backtest engine following section 7; results written to `picks` with `run_type = 'backtest'`
- Written results, including the bad years
- **Gate:** one command reproduces the full result

**Checkpoint:** after Phase 4 the project is already presentable.

### Phase 5 — Product (3 weeks)
- Remaining API endpoints, three screens, deployment
- Weekly scheduled run with failure alerts
- Keyword red flags, live paper portfolio, Telegram alerts, Learn-mode tooltips
- **Gate:** the weekly run succeeds 4 times in a row with no manual fix

### Phase 6 — ML experiment (2 weeks)
- LightGBM ranker on forward excess return, purged walk-forward validation, SHAP explanations
- **Gate:** beats the rule-based score on unseen years. If not, Radar stays rule-based and the result is published as a negative finding.

## 10. Tests that must exist

| Test | What it proves |
|---|---|
| Look-ahead | No score for date D uses a row with `reported_at` on or after D |
| Adjustment | A split, bonus or demerger does not create a false price jump |
| Survivorship | The backtest universe on a past date includes stocks that later delisted |
| Evidence | Every row in `scores` has at least one evidence line |
| Missing data | A loss-making company and a bank both score without errors |
| Determinism | Two backtest runs give identical results |

## 11. Success metrics

| Metric | Target | Measured by |
|---|---|---|
| Excess return | Positive vs Nifty 500 total return over the backtest | `picks` joined to `index_prices`, per year |
| Hit rate | More than half of picks beat the benchmark | Same period, per pick |
| Backtest honesty | No look-ahead, delisted stocks included | Tests in section 10 |
| Pipeline reliability | Weekly run needs no manual fix | `pipeline_runs` |
| Explainability | 100% of scores have evidence | Automated check |

A negative or flat excess return is an acceptable outcome as long as it is reported honestly.

## 12. Risks

| Risk | Mitigation |
|---|---|
| Users treat scores as advice | "Research shortlist" wording, visible risks, disclaimer on every score |
| Overfitting | Fixed weights for v1; ML only ships if it wins out of sample |
| Too little history to prove an edge | Per-year reporting; no claims of consistent outperformance |
| Filings are hard to parse or incomplete | Start with 50 stocks; measure coverage before widening |
| Data source limits or terms | Batch, cache, official files first |
| Exchange blocks downloads from cloud hosts | Tested in Phase 0; fallback is a self-hosted runner or local cron |
| Regulation (SEBI research analyst rules) | Personal, educational, free, no personalised advice; check the rules before any public launch |
| Scope creep | The "Out" list in section 3 stays out until Phase 5's gate passes |

## 13. Presenting it

Stock projects are common, so lead with the engineering:
- README headline: point-in-time financial data pipeline with a survivorship-free backtest, running weekly
- Top of the README: architecture diagram, the look-ahead test, pipeline run history
- A short write-up of what went wrong: the bugs that inflated early results and how the ML experiment turned out

## 14. Decisions on the PRD's open questions

| Question | Decision |
|---|---|
| Fundamentals source | Exchange filings; Screener.in for spot-checks only |
| Factor weights | Fixed for v1; ML ranker is a challenger |
| Backtest depth | Estimated in the Phase 0 data spike; confirmed after Phase 3 measures real coverage |
| Personal or public | Public read-only demo, no logins |
| Streamlit or FastAPI + React | FastAPI + minimal React |
