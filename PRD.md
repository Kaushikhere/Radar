# Radar — Product Requirements Document

Nov 7, 2026 · @Kaushik

> This is the original PRD. The revised scope, schema and build plan are in [PLAN.md](PLAN.md), which takes precedence where the two differ.

## Overview

Radar is a long-term stock research tool for NSE-listed companies. It ranks stocks within their own sector, shows the evidence behind every score, and publicly tracks whether its past shortlists beat the Nifty 50.

**Problem.** Finding good long-term stocks means reading financials, shareholding and news for thousands of companies. Experienced investors spend hours filtering. Beginners don't know where to start, and many follow tips with no reasons attached.

**Approach.** Radar narrows 2,000+ stocks to a short research list, explains each pick in plain language, and is honest about its own track record. It ranks; the user decides. It does not predict prices or give buy/sell advice.

## Goals and non-goals

**Goals**
- Cover every liquid NSE stock across all sectors, starting with the Nifty 500
- Rank stocks against their own sector for a 1–3 year holding horizon
- Show the evidence behind every score, plus what could go wrong
- Track past shortlists against the Nifty 50, including the misses
- Help beginners learn how to research, not just what to buy

**Non-goals**
- Short-term price prediction or intraday trading signals
- Buy/sell recommendations, target prices or portfolio management
- Placing trades or connecting to broker accounts

## Target users

| Persona | Who they are | What they need from Radar |
|---|---|---|
| Self-directed investor | Already reads annual reports and uses screeners | A fast, sector-fair shortlist with evidence they can verify |
| Beginner | New to investing, doesn't know how to judge a company | Plain-language reasons, term explanations, visible risks |
| Builder (you) | CS student building a portfolio project | An end-to-end system covering data, ML, backend, frontend and MLOps |

## Core features

P0 ships in the first usable version; P1 and P2 follow.

| Feature | What it does | Priority |
|---|---|---|
| Universe & liquidity filter | Tracks all NSE stocks; only liquid ones can be shortlisted | P0 |
| Sector-relative scoring | Scores each stock against peers in its own sector | P0 |
| Evidence lines | Every factor score returns the facts behind it | P0 |
| Risk section | "What could go wrong" shown on every stock | P0 |
| Sector strength view | Heatmap of sectors gaining or losing strength | P1 |
| News red-flag detector | FinBERT flags fraud, governance or auditor issues | P1 |
| Scorecard | Paper portfolio of past shortlists vs Nifty 50 | P1 |
| Company graph | Links companies by sector, supply chain and price correlation; news spreads to neighbours | P2 |
| ML ranker | LightGBM ranks stocks on 1–3 year outperformance, explained with SHAP | P2 |
| IPO tracker | Tracks new listings; ranks them only after 2–3 years of results | P2 |
| Learn mode | Tap any term for a one-line meaning; guided "why A beat B" walkthroughs | P2 |
| Alerts | Telegram message when a score changes after quarterly results | P2 |

## Scoring model

Each stock gets a 0–100 long-term score: a weighted sum of four factor scores, each ranked as a percentile within the stock's sector.

**Score = 0.40 F + 0.25 V + 0.20 O + 0.15 T**

| Factor | Weight | Signals used |
|---|---|---|
| Fundamentals (F) | 40% | 3–5 year revenue and profit growth, ROE/ROCE, debt-to-equity, operating cash flow |
| Valuation (V) | 25% | P/E and PEG vs sector peers and vs the stock's own 5-year history |
| Ownership (O) | 20% | Promoter holding trend, share pledging, institutional holding changes |
| Trend (T) | 15% | Long-term price trend; a timing guard against buying during a crash |

News sentiment does not add points. It acts as a red-flag filter that can push a stock off the shortlist. Weights are a starting point; the backtest decides the final values.

**Explainability rule.** Every factor function returns `{score, evidence[]}`. The app shows the evidence list as-is, so the reasons always match the calculation.

## Architecture and tech stack

The whole stack is Python-first and free to run: pandas, DuckDB, LightGBM, NetworkX, FinBERT, FastAPI, Docker and GitHub Actions. A new model replaces the live one only if it beats it in the backtest.

## Data model

Seven core tables, in DuckDB first and Postgres + TimescaleDB once deployed.

| Table | Key columns | Refreshed |
|---|---|---|
| stocks | symbol, name, sector, industry, listing_date, is_active, delisted_on | Weekly |
| prices | symbol, date, open, high, low, close, volume | Daily |
| financials_quarterly | symbol, period_end, revenue, net_profit, operating_cf, debt, equity | After each result |
| shareholding | symbol, quarter, promoter_pct, pledged_pct, fii_pct, dii_pct | Quarterly |
| news | symbol, published_at, headline, source_url, sentiment, red_flag | Daily |
| scores | symbol, as_of, factor, score, evidence (JSON), model_version | Weekly |
| picks | as_of, symbol, rank, score_at_pick, nifty_at_pick | Weekly |

Keep delisted stocks in `stocks` (`is_active = false`) so backtests aren't run on survivors only.

## Screens

Three mobile-first screens, mocked up in the Radar design canvas.

1. **Home:** sector strength heatmap and the research shortlist, each card with a one-line "Why"
2. **Stock detail:** overall score, rank in sector, the four factor bars with their evidence, and "What could go wrong"
3. **Scorecard:** past shortlists vs Nifty 50, hit rate, and a history of hits and misses

Every score carries the line "Based on past data, not a prediction."

## Success metrics

| Metric | Target | How it's measured |
|---|---|---|
| Shortlist beats Nifty 50 | Positive excess return over 12+ months | Paper portfolio in `picks`, equal-weighted |
| Hit rate | More than half of picks beat Nifty | Share of picks with return above Nifty over the same period |
| Backtest honesty | Includes delisted stocks; no look-ahead | Point-in-time data, checked in tests |
| Pipeline reliability | Weekly run succeeds without manual fixes | Job logs and failure alerts |
| Explainability | Every score shows at least one evidence line | Automated check on `scores.evidence` |

## Roadmap

Each phase ends at a gate. Phase 4's gate matters most: if the ranker can't beat the Nifty 50 on data it hasn't seen, Radar ships with rule-based scores only.

## Risks and limitations

| Risk | Impact | Mitigation |
|---|---|---|
| Users treat scores as buy advice | Real money lost on a ranking | "Research shortlist" wording, visible risks, disclaimer on every score |
| Overfitting the backtest | Good on paper, poor live | Walk-forward testing; only ship models that beat the current one out of sample |
| Survivorship and look-ahead bias | Falsely high results | Keep delisted stocks; use data as it was known on each date |
| Thin or missing fundamentals for small caps | Unfair or broken scores | Liquidity filter; scoring handles missing values explicitly |
| Data source limits or terms | Scrapers blocked or not allowed | Batch, cache, respect site terms; prefer official NSE files and filings |
| Regulation | SEBI rules on research analysts and investment advice | Stay a personal, educational research tool; no paid tips or personalised advice. Check SEBI rules before any public or paid launch. |

## Open questions

- [ ] Which fundamentals source: Screener.in exports, company filings, or a paid API?
- [ ] Final factor weights: fixed rules, or learned by the ML ranker?
- [ ] How far back can point-in-time fundamentals go for the backtest?
- [ ] Personal tool only, or public app with logins?
- [ ] Streamlit for v1, or straight to FastAPI + React?
