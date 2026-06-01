# Python — Quantitative finance projects

Tre progetti dimostrativi end-to-end di analisi quantitativa di portafoglio, dal data sourcing al reporting visivo.

## Progetti

| # | Cartella | Descrizione | Tecniche |
|---|----------|-------------|----------|
| 1 | [`markowitz/`](./Markowitz) | Mean-Variance Optimization su universo S&P 500. Frontiera efficiente, portafoglio Tangency e GMV. | `numpy`, `scipy.optimize`, `cvxpy`, `yfinance` |
| 2 | [`var-cvar/`](./Var-CVar) | Calcolo Value-at-Risk e Conditional VaR (parametrico, storico, Monte Carlo). Backtesting | `numpy`, `scipy.stats`, `pandas` |
| 3 | [`factor-models/`](./Factor_Models) | Factor regression CAPM e Fama-French 3-factor su universo di fondi. Attribution analysis | `statsmodels`, `pandas`, `yfinance` |

## Stack

- **Core**: `numpy`, `pandas`, `scipy`
- **Visualization**: `matplotlib`, `seaborn`
- **Stats / ML**: `statsmodels`, `scikit-learn`
- **Finance data**: `yfinance`, `pandas_datareader`
- **Notebooks**: Jupyter

## Setup

```bash
pip install -r requirements.txt
```

Apri i notebook `.ipynb` con Jupyter o direttamente in VS Code / Cursor.
