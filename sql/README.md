# SQL — Portfolio Analytics on a Synthetic Fund Database

SQL queries for buy-side portfolio analytics, built on a synthetic SQLite
database that mimics an asset-management data model (funds, securities, daily
prices, holdings, trades, benchmarks).

The queries progress from basic filtering/joins to advanced window functions
(rolling volatility, ranking, active return), covering the patterns most often
asked in buy-side / risk interviews.

> Internal code comments are in Italian (study notes); this README is in English.

---

## Data model

I added a `securities` dimension table (instrument master) on top of the core
tables, because it is required for clean joins. The schema is essentially a
**star schema**: `securities` and `funds` are dimension tables, while `prices`,
`holdings` and `trades` are fact tables.

```
                          ┌─────────────────┐
                          │     funds       │
                          │  fund_id (PK)   │
                          │  benchmark_id ──┼──► benchmarks ──► securities
                          └────────┬────────┘
                                   │ 1
                    ┌──────────────┼───────────────┐
                    │ N            │ N             │ N
              ┌─────▼─────┐  ┌─────▼─────┐         │
              │ holdings  │  │  trades   │         │
              └─────┬─────┘  └─────┬─────┘         │
                    │ N            │ N             │
                    └──────────────┴───────────────┘
                                   │
                          ┌────────▼────────┐        ┌──────────────┐
                          │   securities    │◄───────│    prices    │
                          │ security_id(PK) │  1   N │ (date, sec)  │
                          │ ticker, sector  │        │ close_price  │
                          │ asset_class ... │        └──────────────┘
                          └─────────────────┘
```

| Table        | Grain                              | Key columns |
|--------------|------------------------------------|-------------|
| `funds`      | one row per fund                   | `fund_id` (PK), `benchmark_id` (FK) |
| `securities` | one row per instrument             | `security_id` (PK), `ticker`, `sector`, `is_benchmark` |
| `benchmarks` | one row per benchmark              | `benchmark_id` (PK), `security_id` (FK) |
| `prices`     | one row per (date, security)       | `price_date`, `security_id`, `close_price` |
| `holdings`   | monthly snapshot (date, fund, sec) | `holding_date`, `fund_id`, `security_id`, `quantity` |
| `trades`     | one row per trade                  | `trade_id` (PK), `fund_id`, `security_id`, `side` |

Dataset: 10 funds, 50 single instruments + 5 benchmark instruments (ETF/index),
~9 months of daily prices, monthly holdings snapshots and random trades.
Reproducible (fixed random seed).

---

## Setup

Generate the synthetic database:
```bash
python setup_finance_db.py        # creates finance.db in this folder
```

Run any of the queries in [`queries/`](queries/) against `finance.db`:
- **Option A (interactive):** open `finance.db` in your preferred SQLite client (e.g. SQLTools extension in VS Code/Cursor) and paste the query.
- **Option B (CLI):** save the query you want to test in a file called `query.sql` in this folder, then run:
```bash
python run_query.py
```
The helper prints results as a formatted pandas DataFrame.

---

## Queries

| # | File | What it answers | SQL concepts |
|---|------|-----------------|--------------|
| 01 | [`queries/01-tech-prices-by-date.sql`](queries/01-tech-prices-by-date.sql) | Tech securities and their close price on a given date | `JOIN`, multi-condition `WHERE`, `ORDER BY` |
| 02 | [`queries/02-cheapest-security-per-sector.sql`](queries/02-cheapest-security-per-sector.sql) | Cheapest security in each sector | argmin per group via **correlated subquery** |
| 03 | [`queries/03-fund-market-value.sql`](queries/03-fund-market-value.sql) | Market value of each fund on a date | multi-table `JOIN` with **date anchoring** + `GROUP BY` |
| 04 | [`queries/04-top-holding-and-weight.sql`](queries/04-top-holding-and-weight.sql) | Largest position per fund and its portfolio weight | argmax + ratio vs aggregate (**derived table**) |
| 05 | [`queries/05-daily-returns-lag.sql`](queries/05-daily-returns-lag.sql) | Daily returns of a security | window function **`LAG`** |
| 06 | [`queries/06-rolling-volatility.sql`](queries/06-rolling-volatility.sql) | 20-day rolling mean and volatility | window **frames** (`ROWS BETWEEN`), manual stddev |
| 07 | [`queries/07-top-holdings-ranking.sql`](queries/07-top-holdings-ranking.sql) | Top 3 holdings of each fund | **`ROW_NUMBER`** top-N per group |
| 08 | [`queries/08-active-return-vs-benchmark.sql`](queries/08-active-return-vs-benchmark.sql) | Daily active return of a security vs its benchmark | `LAG` on multiple series + **self-join** on date |
| 09 | [`queries/09-volatility-screen.sql`](queries/09-volatility-screen.sql) | 5 most volatile securities over the period | `LAG` + per-security aggregation + top-N |

---

## Notes

- **Dialect:** SQLite. Window functions, CTEs and recursive CTEs are
  standard and portable; the few SQLite-specific points are noted inline
  (e.g. standard deviation computed by hand via the variance identity
  `Var = mean(X²) − mean(X)²`, since base SQLite has no `STDDEV`).
- **Date anchoring:** when joining `prices` to `holdings`/`trades`, the join
  is on `security_id` **and** date — otherwise each position is multiplied by
  every price date (a common and silent bug).
- **Ordering:** result order is only guaranteed by an explicit `ORDER BY`;
  window ordering (`OVER (ORDER BY ...)`) is scoped to the function.

---

## Dependencies

- **Python 3.10+** with `pandas`, `numpy` (database setup and query runner)
- **SQLite 3.25+** for window function support (CTEs, `ROW_NUMBER`, `LAG`, frame `ROWS BETWEEN`) — already bundled with Python's `sqlite3` module
- Optional: **SQLTools** extension for VS Code / Cursor for interactive query exploration

---

## Related Projects

- [Markowitz MVO](../python/markowitz) — Mean-Variance portfolio optimization (Python)
- [VaR & ES](../python/var-cvar) — risk estimation on the Tangency Portfolio (Python)
- [Factor Models](../python/factor-models) — CAPM & Fama-French regression (Python)
- [VBA Toolkit](../vba) — Excel macros and UDFs for analytics
- [Claude Skills](../../claude-skills) — custom Agent Skills for DCF, ratios, interview prep