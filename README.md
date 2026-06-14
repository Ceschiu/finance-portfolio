# Finance Portfolio

Technical preparation toolkit for buy-side roles (Portfolio Analyst, ALM Analyst, Fund Selection, Quantitative Risk). Includes Python projects on portfolio analytics and risk, VBA macros for Excel-based finance workflows, ... and a SQL module with a synthetic finance database and analytics queries.

---

## Contents

| Folder | Topic | Status |
|--------|-------|--------|
| [`python/markowitz/`](./python/markowitz) | Mean-Variance Optimization, Tangency & GMV portfolio | ✅ |
| [`python/var-cvar/`](./python/var-cvar) | Value-at-Risk and Expected Shortfall on optimized portfolio | ✅ |
| [`python/factor-models/`](./python/factor-models) | CAPM, Fama-French 3/5-factor regression on Tangency Portfolio | ✅ |
| [`vba/`](./vba) | 5 macros + bond pricing UDFs + range-to-array optimization | ✅ |
| [`sql/`](./sql) | Synthetic SQLite finance DB + 9 buy-side analytics queries (JOIN, CTE, window functions) | ✅ |

Each subfolder contains a dedicated README with full project documentation.

---

## Background

MSc in Mathematical Engineering — Quantitative Finance track (Politecnico di Milano). Two years at KPMG on credit risk modelling and validation (Basel IRB, IFRS 9, Solvency II, stress testing). Currently consolidating the buy-side toolkit ahead of interviews for Portfolio Analyst, ALM Analyst, and Fund Selection roles.

---

## Stack

- **Python** — `numpy`, `pandas`, `scipy`, `statsmodels`, `scikit-learn`, `yfinance`, Jupyter
- **VBA** — native objects, `Scripting.Dictionary`, range-to-array pattern, UDFs
- **SQL** — SQLite, window functions (`LAG`, `ROW_NUMBER`, frame `ROWS BETWEEN`), CTEs, correlated subqueries, multi-table joins with date anchoring
- **Excel** — Microsoft 365 with VBA enabled
