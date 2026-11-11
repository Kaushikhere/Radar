# Radar — Phase 0 Data Spike

What the exchange archives actually hold, checked by hand on 11 Nov 2026, and what
that means for the backtest. This closes the "data spike" item in [PHASE.md](PHASE.md).

Stocks checked: `TITAN`, `HDFCBANK`, `RELIANCE`, `ITC`, `ETERNAL` (formerly `ZOMATO`),
plus a yes-or-no check on the delisted HDFC Ltd (`HDFC`).

## Result

| Question | Answer |
|---|---|
| Earliest dated quarterly result | Quarter ended Mar 2007, on NSE |
| First date a score can be computed | About mid-2012 (five years of dated results) |
| First date all four factors are complete | About mid-2018 (balance sheets arrive with XBRL) |
| Likely backtest window | About 2012 to 2026, in two periods (see below) |

| Period | Factors available | Missing |
|---|---|---|
| About 2012 to 2016 | Growth part of F, V, T | Debt, return on equity, cash flow; all of O |
| About 2016 to 2018 | Growth part of F, V, O, T | Debt, return on equity, cash flow |
| About 2018 onward | F, V, O, T in full | — |

These dates come from five large companies. Phase 3's coverage gate confirms them
on the full universe.

## Findings

### Quarterly results (NSE)

| Stock | Earliest quarter listed | Earliest dated quarter | Undated quarters |
|---|---|---|---|
| HDFC Bank | Mar 2005 | Mar 2007 (filed 24 Apr 2007) | 8 |
| ITC | Mar 2005 | Mar 2007 (filed 25 May 2007) | 8 |
| Reliance | Mar 2005 | Mar 2007 (filed 26 Apr 2007) | 8 |
| Titan | Mar 2005 | Mar 2007 (filed 21 Apr 2007) | 8 |
| Eternal | Jun 2021 | Jun 2021 (filed 11 Aug 2021) | 0 |

- The same eight quarters (Mar 2005 to Dec 2006) are undated for every company. This
  is a limit of the archive, not of any one company.
- Eternal listed in July 2021. NSE shows nothing under `ZOMATO`; the archive is keyed
  on the current symbol.

### Formats over time

| Quarters | Format | What it contains |
|---|---|---|
| Mar 2007 to about Dec 2017 | Web page per result | Profit-and-loss lines, segment figures, paid-up equity capital and face value. No balance sheet, no cash flow. |
| Mar 2018 to Dec 2024 | XBRL | Profit and loss every quarter; balance sheet and cash flow in the Sep and Mar filings only |
| Mar 2025 onward | "Integrated Filing (Finance)": XBRL shown as a web page | Same content as XBRL; balance sheet and cash flow in the Sep and Mar filings only |

- The XBRL start (FY2018, filed 18 Jun 2018; every quarter from Sep 2018) was checked
  on Titan only.
- NSE's results feed stops at the Dec 2024 quarter. Later results are under the
  integrated filing, so there is no gap between the two.

### Integrated filing (Titan, BSE)

- **Format:** a web page with the XBRL tags built in, so a program can read it. Not a PDF.
- **Filing date:** shown with a time. The Mar 2025 result was filed on 8 May 2025 at
  10:37 pm, after market close.
- **Balance sheet and cash flow:** both in the Mar 2025 file; neither in the Jun 2025 file.
- **Coverage:** Mar 2025 to Sep 2026.
- **Restatements:** the Mar 2025 result was re-filed twice, the standalone on
  17 Oct 2025 to fix a cash-flow figure and the consolidated on 22 Dec 2025. BSE lists
  the original and each revision as separate rows with their own dates.
- **Units:** amounts are in ₹ crore here, where the older pages use ₹ lakh. Equity
  share capital shows as 89.00 crore.
- Only BSE's page was checked, not NSE's.

### Balance sheets before 2018

Not available in usable form. Checked on Titan:

- The result pages for Sep 2010, Mar 2011, Sep 2015, Mar 2016, Mar 2017 and Sep 2017
  have no balance sheet or cash flow.
- The "Notes to Accounts" attachment for Mar 2011 is a two-page text PDF with results
  and notes, and no balance sheet.
- The attachment for Sep 2015 is a two-page scanned PDF with no text layer, and no
  balance sheet.

### Standalone and consolidated (Titan)

| Type | Starts | Dated from |
|---|---|---|
| Standalone quarterly | Mar 2005 | Mar 2007 |
| Consolidated quarterly | Jun 2017 (filed 9 Aug 2017) | Jun 2017 |
| Consolidated annual | Mar 2005 | Mar 2007 |

A consolidated figure for Jun 2016 exists, but it was first published on 9 Aug 2017
as a comparison figure. Its `reported_at` is therefore 9 Aug 2017.

### Share count

The old result pages show paid-up equity share capital and face value. Titan's
Mar 2005 page shows ₹4,228 lakh at ₹10 face value, which is 4.228 crore shares.
Multiplied by 20 for the 2011 bonus and split, that is about 84.6 crore in today's
terms. The Mar 2025 filing shows share capital of ₹89.00 crore at ₹1 face value, about
89 crore shares, so the count rose by roughly 5% somewhere in between. Share count can
be derived for the whole period.

### Shareholding

| Source | History starts | Dated from |
|---|---|---|
| BSE | Mar 2001 | Mar 2016 (Titan filed 20 Apr 2016; ITC filed 28 Apr 2016) |
| NSE | Sep 2021 | Sep 2021 |

BSE is the source to use. Before Mar 2016 there is no filing date.

### Corporate actions (NSE)

| Stock | Event | Ex-date |
|---|---|---|
| Titan | 1:1 bonus and split from ₹10 to ₹1 face value | 23 Jun 2011 |
| HDFC Bank | Split from ₹2 to ₹1 face value | 19 Sep 2019 |
| Reliance | Rights issue, 1:15 at a ₹1,247 premium | 13 May 2020 |
| Reliance | Demerger (Jio Financial) | 20 Jul 2023 |
| Reliance | Bonus 1:1 | 28 Oct 2024 |
| ITC | Demerger (ITC Hotels) | 6 Jan 2025 |
| HDFC Bank | Bonus 1:1 | 26 Aug 2025 |

- Titan's list covers 2005 to 2026.
- Demerger rows say only "Demerger". They do not name the new company or give a
  ratio, so the price factor for a demerger has to come from somewhere else.

### Delisted companies

HDFC Ltd merged into HDFC Bank in July 2023.

- **NSE:** results are still listed from Mar 2005 to Mar 2023, and the Mar 2023 file opens.
- **BSE:** the page loads with the price frozen at 12 Jul 2023, but the results table is empty.

One case is not proof, but it suggests NSE keeps a delisted company's results.

## What this changes in the plan

| Change | Where |
|---|---|
| Results need three parsers: old web pages, XBRL, integrated filing | Phase 2; estimate raised |
| Results are ingested from the Mar 2007 quarter; the eight undated quarters are skipped | PLAN.md section 6 |
| Shareholding comes from BSE, from Mar 2016 | PLAN.md section 6 |
| Backtest is reported in two periods: reduced fundamentals before 2018, full after | PLAN.md section 7, D-27 |
| Ownership factor is NULL before 2016 | D-26 |
| Consolidated where it exists, standalone otherwise | D-25 |
| Demerger price factor needs its own method | Phase 1 |
| Amounts are converted to one unit on ingest (older pages use ₹ lakh, newer filings ₹ crore) | Phase 2 |
| Each revision of a result is stored as its own row with its own `reported_at` | Already in the schema (D-03); now confirmed as needed |

## Still open

1. **Scheduled download test.** Whether a GitHub Actions job can fetch from NSE and BSE.
2. **XBRL and consolidated start dates beyond Titan.** Checked on one company only.
3. **Demerger price factor.** Where the ratio or the value split comes from.
4. **NSE's integrated filing page.** Only BSE's was checked.
5. **Long-term growth on consolidated figures.** Consolidated annual results are dated
   from Mar 2007, so they could feed the 3–5 year growth measures. To decide in Phase 2.
