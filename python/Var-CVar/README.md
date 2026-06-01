# VaR & ES — Multi-Method Risk Estimation

This project computes **Value at Risk (VaR)** and **Expected Shortfall (ES/CVaR)** for a given portfolio using three methodologies:
- **Parametric** — assumes normally distributed portfolio returns
- **Monte Carlo** — simulates returns for each asset assuming multivariate normality, then aggregates at portfolio level
- **Historical** — uses real historical portfolio returns directly, without distributional assumptions

Input data is taken from the Markowitz companion project (Tangency Portfolio weights), but the project can be adapted to any portfolio by providing a CSV with ticker names and weights, along with the time window of interest.

---

## How to Run

```bash
python f_main.py
```

Parameters can be adjusted directly in `f_main.py`:
- `alpha` — confidence level (default 0.95)
- `n_sim` — number of simulations for Monte Carlo

To change the portfolio or time window, edit `a_data.py`.

---

## Project Structure

| File | Role |
|------|------|
| `a_data.py` | Loads portfolio weights from CSV, defines time window, downloads log-returns |
| `b_parametric.py` | VaR and ES assuming normal portfolio returns (closed-form) |
| `c_historical.py` | VaR and ES using historical portfolio return data |
| `d_montecarlo.py` | VaR and ES via Monte Carlo simulation of asset returns |
| `e_plotting.py` | Plots VaR and ES lines over the historical return distribution |
| `f_main.py` | Orchestrates the full pipeline |

---

## Methodology Notes

- **Parametric**: fast and clean, but underestimates tail risk when returns are not normally distributed
- **Historical**: no distributional assumption, captures fat tails directly from data
- **Monte Carlo**: flexible, but still assumes normality at the asset level

Results from the default Tangency Portfolio show Historical and MC producing more extreme ES values than Parametric — a classic fat tails signal: real returns have heavier tails than the normal distribution predicts.

---

## Input Format

The portfolio CSV must be a `pd.Series` saved with `to_csv()`:
- Index: ticker names
- Values: portfolio weights (non-zero only needed)

---

## Output

- `VaR_ES.png` — histogram of portfolio returns with VaR and ES lines for all three methods

---

## Dependencies

```
pandas
numpy
scipy
yfinance
matplotlib
os
```

---

## Related Projects

- [Markowitz MVO](https://github.com/Ceschiu/markowitz-mvo) — generates the input portfolio weights used in this project
