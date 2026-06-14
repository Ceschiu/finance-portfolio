# Python — Quantitative finance projects

Three end-to-end portfolio analytics projects, from data sourcing to visual reporting. Each project documents methodology and produces reproducible plots.

---

## Projects

| # | Folder | Description | Stack |
|---|--------|-------------|-------|
| 1 | [`markowitz/`](./markowitz) | Mean-Variance Optimization on a mixed US/EU equity universe. Efficient Frontier, MVP, Tangency Portfolio. | `numpy`, `pandas`, `scipy.optimize`, `yfinance` |
| 2 | [`var-cvar/`](./var-cvar) | Value-at-Risk and Expected Shortfall (parametric, historical, Monte Carlo) on the Tangency Portfolio | `numpy`, `pandas`, `scipy.stats`, `yfinance` |
| 3 | [`factor-models/`](./factor-models) | Factor regression — CAPM, Fama-French 3 and 5-factor — on the Tangency Portfolio with attribution analysis | `numpy`, `pandas`, `statsmodels`, `yfinance` |

The three projects form a **single pipeline**: the Markowitz project produces the Tangency Portfolio weights, which are then consumed as input by VaR&ES and Factor Models.

---

## Stack

- **Core**: `numpy`, `pandas`, `scipy`
- **Statistics & regression**: `statsmodels`
- **Visualization**: `matplotlib`
- **Market data**: `yfinance`
- **Optimization**: `scipy.optimize`

---

## Setup

Each project is self-contained — `cd` into its folder and run the orchestration script (`e_main.py` for Markowitz and Factor Models, `f_main.py` for VaR&ES). Dependencies are listed in each project's README.

---

## Related Modules

- [VBA Toolkit](../vba) — Excel macros and UDFs for analytics
- [SQL Module](../sql) — synthetic SQLite finance DB + buy-side analytics queries