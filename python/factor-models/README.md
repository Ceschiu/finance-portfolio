# Factor Model Regression — CAPM & Fama-French 3/5

This project estimates **CAPM**, **Fama-French 3-factor**, and **Fama-French 5-factor** models on the Tangency Portfolio from the companion Markowitz project. It decomposes portfolio returns into systematic factor exposures and alpha, with full graphical output.

---

## How to Run

```bash
python e_main.py
```

Parameters can be adjusted directly in `a_data.py`:
- `start`, `end` — time window (must be within the FF factors CSV coverage)

To change the portfolio, replace `TgP_weights.csv` with any CSV in the same format (index: tickers, values: weights).

To change which model is shown in the beta and attribution charts, edit `model_selected` in `e_main.py`.

---

## Project Structure

| File | Role |
|------|------|
| `a_data.py` | Loads TgP weights, downloads monthly log-returns, parses FF5 factors from local CSV |
| `b_regression.py` | Runs OLS regression for CAPM, FF3, FF5 — returns full statsmodels result objects |
| `c_attribution.py` | Computes factor attribution: beta, factor mean return, absolute and percentage contribution |
| `d_plotting.py` | Produces a 4-panel chart: R² comparison, betas, return attribution, alpha comparison |
| `e_main.py` | Orchestrates the full pipeline |

---

## Methodology

**Models estimated:**
- **CAPM**: `r_excess = α + β·Mkt-RF`
- **FF3**: `r_excess = α + β₁·Mkt-RF + β₂·SMB + β₃·HML`
- **FF5**: `r_excess = α + β₁·Mkt-RF + β₂·SMB + β₃·HML + β₄·RMW + β₅·CMA`

Where `r_excess = r_portfolio - RF` (portfolio return minus risk-free rate).

**Factor definitions (FF5):**
- `Mkt-RF` — market excess return
- `SMB` — Small Minus Big (size factor)
- `HML` — High Minus Low (value factor)
- `RMW` — Robust Minus Weak (profitability factor)
- `CMA` — Conservative Minus Aggressive (investment factor)

**Attribution:** each factor's contribution to total return = `β × mean factor return`. Contributions sum to the mean portfolio excess return (OLS property). Percentage attribution normalises by total.

**Data alignment:** monthly portfolio returns (`resample("ME")`) and FF factors are aligned to their common date range via inner join before regression.

---

## FF Factors Data

Fama-French 5-factor monthly data (`F-F_Research_Data_5_Factors_2x3.csv`) must be downloaded manually from [Kenneth French's Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) and placed in the project folder. `pandas_datareader` is not used due to incompatibility with pandas 3.x.

---

## Results (Tangency Portfolio, 2016–2026)

- **R²** is approximately 0.58–0.61 across all three models and increases only marginally from CAPM to FF5. The market factor alone explains most of the portfolio's variance — adding size, value, profitability, and investment factors provides little incremental explanatory power.

- **Factor exposures (FF5 betas):** the portfolio loads heavily on `Mkt-RF`, with near-zero exposure to `SMB`, `HML`, and `CMA`. `RMW` shows a small positive loading. This is consistent with a large-cap, growth-oriented portfolio (Tangency Portfolio selected from a mixed US/European equity universe).

- **Return attribution:** the bulk of the portfolio's excess return comes from `Mkt-RF` exposure and from alpha (`const`). The remaining factors contribute negligibly — confirming that the portfolio's performance is driven by broad market beta and manager selection, not factor tilts.

- **Alpha comparison:** alpha is statistically present across all three models and does not shrink materially when moving from CAPM to FF5. This suggests the unexplained excess return is not captured by the standard Fama-French factors.

---

## Why is R² moderate (~0.58–0.61)?

The R² of the three regressions (CAPM, FF3, FF5) sits around 0.58–0.61 on the
Tangency Portfolio, well below the ~0.85+ one would expect from a diversified
US large-cap equity portfolio. This is **not a bug** — it reflects the
cross-asset composition of the TgP that comes out of the Markowitz step.

The Tangency Portfolio is approximately:

| Bucket | Weight | Reason FF factors don't fully explain it |
|--------|--------|------------------------------------------|
| US large-cap equity (AAPL, ABBV, CAT, GS, MSFT) | ~58% | Explained well by `Mkt-RF` (US market factor) |
| Gold ETF (`GLD`) | ~32% | Commodity, structurally decorrelated from equity factors |
| EU equity (`MC.PA`, `SIE.DE`) | ~10% | Fama-French factors are US-only; EU equity carries an idiosyncratic component |

So roughly **42% of the portfolio is not US equity** — and the Fama-French
factors, by construction, regress on the US market. R² 0.58 is exactly what
this asset mix produces.

**To get a higher R²** the regression universe would need a different factor
set: a global / international market factor, or an explicit commodity factor
(e.g. gold spot, oil), or a dedicated EU equity factor. In a follow-up these
could be tested, but the current analysis is intentionally kept on the
canonical FF3/FF5 setup to show how a standard factor model decomposes a
mixed-asset portfolio.

---

## Output

- `Factor_Analysis.png` — 4-panel chart: R² comparison, FF5 betas, return attribution, alpha across models

---

## Dependencies

```
numpy
pandas
scipy
statsmodels
yfinance
matplotlib
requests
zipfile
os
```

---

## Related Projects

- [Markowitz MVO](../markowitz) — generates the input portfolio weights
- [VaR & ES](../var-cvar) — risk estimation on the same portfolio
- [VBA Toolkit](../../vba) — Excel macros and UDFs for analytics
- [SQL Module](../../sql) — synthetic SQLite finance DB + buy-side analytics queries
- [Claude Skills](../../claude-skills) — custom Agent Skills for DCF, ratios, interview prep
