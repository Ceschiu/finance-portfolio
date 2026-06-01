# Markowitz Mean-Variance Optimizer

Starting from market data for a given time window and an initial universe of assets, this project screens the best **n** assets and constructs the **Efficient Frontier**, the **Minimum Variance Portfolio (MVP)** and the **Tangency Portfolio (TGP)**, with full graphical output.

---

## How to Run

```bash
python e_main.py
```

No modifications needed. Parameters can be adjusted directly in `e_main.py`:
- `n` — number of assets to select after screening
- `rf` — risk-free rate used for Sharpe ratio
- `NaN_treshold`, `vol_treshold`, `drawdown_treshold` — screening thresholds

To change the asset universe or time window, edit `a_data.py`.

---

## Project Structure

| File | Role |
|------|------|
| `a_data.py` | Defines ticker universe, sectors, time window; downloads raw prices (`get_prices`) and clean log-returns (`get_returns`) |
| `b_screening.py` | Screens assets by data quality, volatility, max drawdown, and composite Sharpe/correlation score; returns selected ticker list |
| `c_optimizer.py` | Computes MVP, Tangency Portfolio, and Efficient Frontier using `scipy.optimize` |
| `d_plotting.py` | Plots the Efficient Frontier with MVP and TGP annotated; prints portfolio weights |
| `e_main.py` | Orchestrates the full pipeline |

---

## Screening Logic

The pipeline separates screening from optimization deliberately:

1. **Screening** operates on prices with `ffill` for missing days (market holidays from mixed US/European universe). Assets are eliminated in order:
   - **Missing data** — NaN check on prices; removed if NaN rate exceeds threshold
   - **Volatility, Max Drawdown, Composite score** — computed on log-returns from ffilled prices; removed if vol > threshold or drawdown < threshold; top `n` selected by Sharpe + inverse correlation score

2. **Optimization** re-downloads clean log-returns for the selected tickers only (no ffill, `dropna` on the first row), ensuring portfolio weights are computed on real observed returns with no synthetic data.

---

## Output

- `Frontiera.png` — Efficient Frontier with MVP (red) and TGP (blue) highlighted
- `Scatter_Single_Name.png` — Risk/return scatter of individual assets
- Console output with portfolio weights for MVP and TGP
- `TgP_weights.csv` — Tangency Portfolio weights, used as input by the VaR & ES and Factor Models sibling projects in this repository
---

## Dependencies

```
numpy
pandas
yfinance
scipy
matplotlib
```

## Related Projects

- [VaR & ES](../Var-CVar) — risk estimation on the Tangency Portfolio
- [Factor Models](../Factor_Models) — CAPM & Fama-French regression on the Tangency Portfolio
- [VBA Toolkit](../../vba) — Excel macros and UDFs for analytics
