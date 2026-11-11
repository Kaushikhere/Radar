# Radar — Decision Log

Each entry records one decision, why it was made, what it costs, and when to revisit it.
These cover product, data and method. Stack and system-design choices, with the
alternatives rejected, are in [ARCHITECTURE.md](ARCHITECTURE.md).

Add a new entry whenever a decision changes what gets built. Never edit an old entry
to change its meaning: mark it "Superseded by D-xx" and add a new one.

| # | Decision | Area | Status |
|---|---|---|---|
| D-01 | Research filter, not a stock picker | Product | Accepted |
| D-02 | Start with the Nifty 500, not all NSE stocks | Product | Accepted |
| D-03 | Point-in-time data with `reported_at` | Data | Accepted |
| D-04 | Use a row only from the day after it was published | Data | Accepted |
| D-05 | Historical index membership and delisted stocks | Data | Accepted |
| D-06 | Exchange filings as the fundamentals source | Data | Accepted |
| D-07 | Store raw prices, adjust at query time | Data | Accepted |
| D-08 | Key everything on `stock_id` | Data | Accepted |
| D-09 | Fixed factor weights for v1 | Scoring | Accepted |
| D-10 | Sector-relative percentiles with a fallback | Scoring | Accepted |
| D-11 | Separate factor set for banks and NBFCs | Scoring | Accepted |
| D-12 | Missing factors are NULL, never zero | Scoring | Accepted |
| D-13 | P/E from market cap and trailing profit | Scoring | Accepted |
| D-14 | Every factor returns `{score, evidence[]}` | Scoring | Accepted |
| D-15 | Red flags remove a stock, they do not change its score | Scoring | Accepted |
| D-16 | Keyword red flags now, FinBERT later | Scoring | Accepted |
| D-17 | Nifty 500 total return as the primary benchmark | Backtest | Accepted |
| D-18 | Quarterly rebalance, plus an annual run | Backtest | Accepted |
| D-19 | Report results per year | Backtest | Accepted |
| D-20 | Backtest scorecard shown now, live portfolio alongside | Backtest | Accepted |
| D-21 | ML ranker ships only if it wins out of sample | ML | Accepted |
| D-22 | Check data availability in Phase 0 | Process | Accepted |
| D-23 | Build on 50 stocks before 500 | Process | Accepted |
| D-24 | Public read-only demo, no logins | Product | Accepted |

---

## Product

### D-01 — Research filter, not a stock picker
- **Decision:** Radar produces a shortlist to research. It gives no buy/sell advice, target prices or predictions.
- **Why:** Ten years of data cannot prove a ranking beats the market. SEBI also regulates research analysts and investment advice.
- **Cost:** The product is less exciting to describe.
- **Revisit when:** Never for v1. Check SEBI rules before any public launch.

### D-02 — Start with the Nifty 500, not all NSE stocks
- **Decision:** The universe is the Nifty 500 on each date, after a liquidity filter. The PRD's 2,000+ stocks are out of scope for v1.
- **Why:** Small caps have thin or missing filings, and index membership gives a clean, dated definition of the universe.
- **Cost:** Radar will not find small companies outside the index.
- **Revisit when:** Phase 5's gate has passed and coverage on the 500 is high.

### D-24 — Public read-only demo, no logins
- **Decision:** Anyone can view the demo. There are no accounts, payments or personalised output.
- **Why:** Logins add auth, storage of personal data and regulatory exposure, none of which help the portfolio goal.
- **Cost:** No watchlists or per-user alerts.
- **Revisit when:** There is a real user asking for it.

## Data

### D-03 — Point-in-time data with `reported_at`
- **Decision:** Financials and shareholding rows store the date the market could first see them. Restated figures are kept as new rows, not overwritten.
- **Why:** Keying on `period_end` alone lets a backtest use March results on 31 March, weeks before they were published. That inflates returns.
- **Cost:** Every query needs a date filter, and the ingest must capture filing dates.
- **Revisit when:** Never. The backtest is not trustworthy without it.

### D-04 — Use a row only from the day after it was published
- **Decision:** Queries filter on `reported_at < as_of`, not `<=`.
- **Why:** `reported_at` is a date and results are usually published after market close. Using them at that day's closing price would be look-ahead.
- **Cost:** Scores react one trading day late.
- **Revisit when:** Filing timestamps are stored, which would allow an exact rule.

### D-05 — Historical index membership and delisted stocks
- **Decision:** `index_membership` stores date ranges, and delisted stocks stay in `stocks` and `prices`.
- **Why:** Backtesting on today's index members picks only the survivors, which inflates returns.
- **Cost:** Rebuilding membership from change notices is the hardest ingest in the plan.
- **Revisit when:** Phase 3's membership gate fails. The fallback is a shorter backtest window where membership is known.

### D-06 — Exchange filings as the fundamentals source
- **Decision:** Financials and shareholding come from exchange filings. Screener.in is used for manual spot-checks only.
- **Why:** Filings carry the filing date needed for D-03 and are the official source. Scraping an aggregator risks breaking its terms and gives no publication dates.
- **Cost:** Parsing filings is slow work. Phase 2 is the most likely to overrun.
- **Revisit when:** The Phase 0 spike shows filings are unusable or too short. A paid API is the fallback.

### D-07 — Store raw prices, adjust at query time
- **Decision:** `prices` holds prices as traded. Adjustment for splits, bonuses, dividends, rights and demergers is applied from `corporate_actions` when queried.
- **Why:** Adjusted prices change every time a new corporate action happens. Storing them means rewriting history on each one, and a wrong action cannot be fixed without a reload.
- **Cost:** Queries are more complex and slightly slower.
- **Revisit when:** Query time becomes a problem. A materialised view is the first fix.

### D-08 — Key everything on `stock_id`
- **Decision:** All tables reference `stock_id`. Symbols live in `symbol_history` with date ranges.
- **Why:** NSE symbols get renamed. Keying on symbol would split one company's history in two.
- **Cost:** Every ingest has to map symbol and date to `stock_id`.
- **Revisit when:** Never.

## Scoring

### D-09 — Fixed factor weights for v1
- **Decision:** Score = 0.40 F + 0.25 V + 0.20 O + 0.15 T. The weights are not tuned on the backtest.
- **Why:** Tuning weights on the same data used to report results is overfitting. The PRD's "the backtest decides the final values" would do exactly that.
- **Cost:** The weights are a judgement call and may be far from the best.
- **Revisit when:** Phase 6. The ML ranker is the challenger.

### D-10 — Sector-relative percentiles with a fallback
- **Decision:** Each factor is a percentile within the stock's sector. If the sector has fewer than 10 scoreable stocks, the sector group is used.
- **Why:** A P/E of 40 means different things for a software company and a steel maker. Percentiles in a group of 4 are noise.
- **Cost:** The best stock in a weak sector still scores well. Sector is today's classification, not its history.
- **Revisit when:** Backtest results show sector effects dominating the shortlist.

### D-11 — Separate factor set for banks and NBFCs
- **Decision:** Financial companies are scored on asset quality, capital adequacy and return on assets.
- **Why:** Debt-to-equity and operating cash flow do not mean the same thing for a lender. Debt is its raw material.
- **Cost:** A second set of factor code and tests.
- **Revisit when:** Insurers and other financials need their own rules.

### D-12 — Missing factors are NULL, never zero
- **Decision:** A factor that cannot be computed is stored as NULL with an evidence line saying why. The total is re-weighted over the factors that exist. A stock with fewer than three factors is excluded from the shortlist.
- **Why:** Scoring missing data as zero punishes a company for a gap in the data. Guessing a value hides the gap.
- **Cost:** Totals built from three factors are not strictly comparable with totals built from four.
- **Revisit when:** Many shortlisted stocks turn out to have a missing factor.

### D-13 — P/E from market cap and trailing profit
- **Decision:** P/E is market cap divided by trailing 12-month net profit, not price divided by EPS.
- **Why:** Raw EPS and raw prices disagree across a split or bonus. Market cap and total profit are unaffected by share count changes.
- **Cost:** Depends on `shares_outstanding` being correct on each date.
- **Revisit when:** Never, unless share count data proves unreliable.

### D-14 — Every factor returns `{score, evidence[]}`
- **Decision:** Factor functions return the score and the facts behind it together. The app shows the evidence unchanged.
- **Why:** If explanations are written separately from the calculation, they drift apart. This way the reason always matches the number.
- **Cost:** Evidence text is written in the scoring code, not the frontend.
- **Revisit when:** Never. It is a core promise of the product.

### D-15 — Red flags remove a stock, they do not change its score
- **Decision:** A red flag takes a stock off the shortlist. Its score is left as it is.
- **Why:** There is no honest way to convert "auditor resigned" into points. A filter is simple and visible.
- **Cost:** A flag is all-or-nothing, and a false positive removes a good stock.
- **Revisit when:** False positives become common.

### D-16 — Keyword red flags now, FinBERT later
- **Decision:** v1 flags exchange announcements by keyword. FinBERT sentiment on news is deferred.
- **Why:** FinBERT was trained on English financial news, not Indian exchange announcements, and its output is hard to check. Keywords are testable and explainable.
- **Cost:** Keywords miss anything phrased unusually.
- **Revisit when:** v1 is live and keyword misses are documented.

## Backtest

### D-17 — Nifty 500 total return as the primary benchmark
- **Decision:** Results are measured against the Nifty 500 total return index. Nifty 50 total return is shown as a second line.
- **Why:** The picks come from the Nifty 500, so that is the fair comparison. A price-only index ignores dividends and flatters the strategy.
- **Cost:** A harder benchmark to beat than the PRD's Nifty 50 price index.
- **Revisit when:** Never.

### D-18 — Quarterly rebalance, plus an annual run
- **Decision:** The main backtest rebalances quarterly. A second run rebalances annually.
- **Why:** Fundamentals change quarterly, so weekly picks would mostly repeat. The annual run matches the 1–3 year holding horizon and shows how much turnover costs.
- **Cost:** Two sets of results to report and explain.
- **Revisit when:** The two runs tell very different stories.

### D-19 — Report results per year
- **Decision:** Excess return and hit rate are reported for each calendar year, along with the worst drawdown and turnover.
- **Why:** One good year can hide several bad ones in a single headline number.
- **Cost:** The bad years are visible.
- **Revisit when:** Never.

### D-20 — Backtest scorecard shown now, live portfolio alongside
- **Decision:** The scorecard shows backtest results, labelled "backtest". A live paper portfolio accumulates from launch and is shown separately.
- **Why:** A live-only scorecard would be empty for the first year.
- **Cost:** Backtest numbers are weaker evidence than live ones, and readers may not notice the label.
- **Revisit when:** The live portfolio has 12 months of history and can lead the page.

## ML

### D-21 — ML ranker ships only if it wins out of sample
- **Decision:** The LightGBM ranker replaces the rule-based score only if it beats it on years it has not seen. Otherwise the result is published as a negative finding.
- **Why:** With about 500 stocks and a few years of overlapping multi-year returns, there is little independent data. A model can easily fit noise.
- **Cost:** Two weeks of work that will most likely not ship.
- **Revisit when:** More years of data exist.

## Process

### D-22 — Check data availability in Phase 0
- **Decision:** A spike on 5 stocks finds the earliest usable filing, and a test job checks that scheduled downloads work, before any ingest code is written.
- **Why:** The factors need about 5 years of history before the first score. If filings are short or downloads are blocked, the backtest window and the pipeline design both change.
- **Cost:** Phase 0 grows from a few days to a week.
- **Revisit when:** Never.

### D-23 — Build on 50 stocks before 500
- **Decision:** Phases 1 and 2 use 50 stocks. The full universe arrives in Phase 3.
- **Why:** Parsing and adjustment bugs are found faster on a set small enough to check by hand.
- **Cost:** Some problems, such as small sectors and delisted names, only appear at full scale.
- **Revisit when:** Never.

---

## Template

```markdown
### D-xx — Title
- **Decision:** What was decided, in one or two sentences.
- **Why:** The reason, and what would go wrong otherwise.
- **Cost:** What this gives up.
- **Revisit when:** The condition that should reopen it.
```
