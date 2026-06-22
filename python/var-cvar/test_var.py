"""Sanity tests for the VaR / ES module."""

import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import norm

# Make local modules importable when pytest runs from any cwd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from b_parametric import VaR_parametric
from c_historical import VaR_Historical
from d_montecarlo import VaR_MonteCarlo


# ---------- Helpers: synthetic data ----------

def _fake_returns(seed=42, n_days=1000, n_tickers=5):
    """Genera log-returns sintetici i.i.d. ~ N(mu=0.0005, sigma=0.01)."""
    rng = np.random.default_rng(seed)
    data = rng.normal(loc=0.0005, scale=0.01, size=(n_days, n_tickers))
    return pd.DataFrame(data, columns=[f"T{i}" for i in range(n_tickers)])


def _equal_weights(n_tickers=5):
    """Pesi equally-weighted (1/n) come np.ndarray."""
    return np.ones(n_tickers) / n_tickers


# ---------- Tests ----------

def test_parametric_var_closed_form():
    """Parametric VaR must coincide with -mu_p + sigma_p * z(alpha)."""
    w = _equal_weights()
    rend = _fake_returns()
    alpha = 0.95

    var_calc, _ = VaR_parametric(w=w, rend=rend, alpha=alpha)

    mu_p = w @ rend.mean()
    sigma_p = np.sqrt(w @ rend.cov() @ w)
    var_expected = -mu_p + sigma_p * norm.ppf(alpha)

    assert abs(var_calc - var_expected) < 1e-9, "VaR parametrico non coincide con la formula chiusa"


def test_montecarlo_var_reproducible():
    """MonteCarlo VaR must match exactly when called twice with the same seed."""
    w = _equal_weights()
    rend = _fake_returns()
    alpha = 0.95
    n_sim = 10000
    seed = 42

    var_mc1, _ = VaR_MonteCarlo(w=w, rend=rend, alpha=alpha, n_sim=n_sim, seed=seed)
    var_mc2, _ = VaR_MonteCarlo(w=w, rend=rend, alpha=alpha, n_sim=n_sim, seed=seed)
    assert abs(var_mc1 - var_mc2) < 1e-9, "VaR MonteCarlo non coincide a parita di seed"


def test_es_ge_var():
    """ES must be greater than or equal to VaR for every methodology."""
    w = _equal_weights()
    rend = _fake_returns()
    alpha = 0.95
    n_sim = 10000
    seed = 42

    var_mc, es_mc = VaR_MonteCarlo(w=w, rend=rend, alpha=alpha, n_sim=n_sim, seed=seed)
    var_h, es_h = VaR_Historical(w=w, rend=rend, alpha=alpha)
    var_p, es_p = VaR_parametric(w=w, rend=rend, alpha=alpha)

    assert (es_mc > var_mc + 1e-9) and (es_h > var_h + 1e-9) and (es_p > var_p + 1e-9), \
        "VaR maggiore di ES"


def test_var_increases_with_alpha():
    """VaR must be non-decreasing in alpha."""
    w = _equal_weights()
    rend = _fake_returns()
    n_sim = 10000
    seed = 42

    var_mc95, _ = VaR_MonteCarlo(w=w, rend=rend, alpha=0.95, n_sim=n_sim, seed=seed)
    var_h95, _ = VaR_Historical(w=w, rend=rend, alpha=0.95)
    var_p95, _ = VaR_parametric(w=w, rend=rend, alpha=0.95)
    var_mc99, _ = VaR_MonteCarlo(w=w, rend=rend, alpha=0.99, n_sim=n_sim, seed=seed)
    var_h99, _ = VaR_Historical(w=w, rend=rend, alpha=0.99)
    var_p99, _ = VaR_parametric(w=w, rend=rend, alpha=0.99)

    assert (var_mc99 > var_mc95 + 1e-9) and (var_h99 > var_h95 + 1e-9) and (var_p99 > var_p95 + 1e-9), \
        "VaR decrescente al crescere di alpha"


def test_historical_var_is_quantile():
    """Historical VaR must coincide with -quantile(rend_ptf, 1-alpha)."""
    w = _equal_weights()
    rend = _fake_returns()
    alpha = 0.95

    var_h, _ = VaR_Historical(w=w, rend=rend, alpha=alpha)
    rend_ptf = rend @ w
    var_expected = -rend_ptf.quantile(1 - alpha)

    assert abs(var_h - var_expected) < 1e-9, "Historical VaR non coincide col quantile empirico"