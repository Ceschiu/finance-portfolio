"""Sanity tests for the Factor Models module (CAPM, FF3, FF5)."""

import os
import sys

import numpy as np
import pandas as pd

# Make local modules importable when pytest runs from any cwd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from b_regression import CAPM_calc, FF3_calc, FF5_calc
from c_attribution import compute_contribution


# ---------- Helpers: synthetic data ----------

def _fake_ff(seed=42, n_months=120):
    """Fattori FF mensili sintetici (Mkt-RF, SMB, HML, RMW, CMA, RF)."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2016-03-31", periods=n_months, freq="ME")
    return pd.DataFrame({
        "Mkt-RF": rng.normal(0.005, 0.04, n_months),
        "SMB":    rng.normal(0.0,   0.02, n_months),
        "HML":    rng.normal(0.0,   0.02, n_months),
        "RMW":    rng.normal(0.0,   0.015, n_months),
        "CMA":    rng.normal(0.0,   0.015, n_months),
        "RF":     np.full(n_months, 0.002),
    }, index=dates)


def _fake_rend_monthly(seed=43, n_months=120, tickers=("T0", "T1", "T2", "T3", "T4")):
    """Log-returns mensili sintetici (indipendenti dai fattori — per test generici)."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2016-03-31", periods=n_months, freq="ME")
    data = rng.normal(0.005, 0.04, size=(n_months, len(tickers)))
    return pd.DataFrame(data, columns=list(tickers), index=dates)


def _equal_weights(tickers=("T0", "T1", "T2", "T3", "T4")):
    """Pesi 1/n come pd.Series con index = tickers."""
    n = len(tickers)
    return pd.Series([1.0 / n] * n, index=list(tickers))


# ---------- Tests ----------

def test_capm_beta_calibration():
    """If rend_ptf = Mkt + RF + small noise, CAPM must return beta ≈ 1 and alpha ≈ 0."""
    ff = _fake_ff()
    n_months = len(ff)

    rng = np.random.default_rng(99)
    noise = rng.normal(0, 0.001, n_months)
    asset = ff["Mkt-RF"].values + ff["RF"].values + noise   # rend "vero" = mkt + rf + ε

    rend_monthly = pd.DataFrame({"ASSET": asset}, index=ff.index)
    weights = pd.Series([1.0], index=["ASSET"])

    result = CAPM_calc(rend_monthly=rend_monthly, weights=weights, ff=ff)
    beta_mkt = result.params["Mkt-RF"]
    alpha = result.params["const"]

    assert abs(beta_mkt - 1.0) < 0.01, f"beta atteso ~1, ottenuto {beta_mkt:.4f}"
    assert abs(alpha) < 0.01, f"alpha atteso ~0, ottenuto {alpha:.4f}"


def test_rsquared_in_unit_interval():
    """R2 must be in [0, 1] for every model."""
    ff = _fake_ff()
    rend_monthly = _fake_rend_monthly()
    weights = _equal_weights()

    r2_capm = CAPM_calc(rend_monthly=rend_monthly, weights=weights, ff=ff).rsquared
    r2_ff3 = FF3_calc(rend_monthly=rend_monthly, weights=weights, ff=ff).rsquared
    r2_ff5 = FF5_calc(rend_monthly=rend_monthly, weights=weights, ff=ff).rsquared

    assert -1e-9 <= r2_capm <= 1 + 1e-9, "R2_capm fuori da [0,1]"
    assert -1e-9 <= r2_ff3 <= 1 + 1e-9, "R2_ff3 fuori da [0,1]"
    assert -1e-9 <= r2_ff5 <= 1 + 1e-9, "R2_ff5 fuori da [0,1]"


def test_rsquared_monotonic():
    """R2 must grow with the number of regressors (OLS property)."""
    ff = _fake_ff()
    rend_monthly = _fake_rend_monthly()
    weights = _equal_weights()

    r2_capm = CAPM_calc(rend_monthly=rend_monthly, weights=weights, ff=ff).rsquared
    r2_ff3 = FF3_calc(rend_monthly=rend_monthly, weights=weights, ff=ff).rsquared
    r2_ff5 = FF5_calc(rend_monthly=rend_monthly, weights=weights, ff=ff).rsquared

    assert (r2_ff3 + 1e-6 > r2_capm) and (r2_ff5 + 1e-6 > r2_ff3), \
        "R2 non monotoni relativamente al numero di regressori"


def test_contribution_shape():
    """Contribution DataFrame must have shape (n_factors+1, 4) for each model."""
    ff = _fake_ff()
    rend_monthly = _fake_rend_monthly()
    weights = _equal_weights()

    result_capm = CAPM_calc(rend_monthly=rend_monthly, weights=weights, ff=ff)
    result_ff3 = FF3_calc(rend_monthly=rend_monthly, weights=weights, ff=ff)
    result_ff5 = FF5_calc(rend_monthly=rend_monthly, weights=weights, ff=ff)

    df_capm = compute_contribution(result=result_capm, ff=ff)
    assert df_capm.shape == (2, 4), "Shape modello CAPM errata"

    df_ff3 = compute_contribution(result=result_ff3, ff=ff)
    assert df_ff3.shape == (4, 4), "Shape modello FF3 errata"

    df_ff5 = compute_contribution(result=result_ff5, ff=ff)
    assert df_ff5.shape == (6, 4), "Shape modello FF5 errata"


def test_contribution_abs_consistency():
    """For every non-const factor, Abs Contribution must equal Beta * Factor Mean Return."""
    ff = _fake_ff()
    rend_monthly = _fake_rend_monthly()
    weights = _equal_weights()

    result_capm = CAPM_calc(rend_monthly=rend_monthly, weights=weights, ff=ff)
    result_ff3 = FF3_calc(rend_monthly=rend_monthly, weights=weights, ff=ff)
    result_ff5 = FF5_calc(rend_monthly=rend_monthly, weights=weights, ff=ff)

    for result, name in [(result_capm, "capm"), (result_ff3, "ff3"), (result_ff5, "ff5")]:
        df = compute_contribution(result=result, ff=ff)
        for fattore in df.index:
            if fattore == "const":
                continue
            beta = df.loc[fattore, "Beta"]
            fmr = df.loc[fattore, "Factor Mean Return"]
            abs_c = df.loc[fattore, "Abs Contribution"]
            assert abs(abs_c - beta * fmr) < 1e-9, f"Inconsistenza su {fattore} per {name}"