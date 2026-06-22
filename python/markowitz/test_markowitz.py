"""Sanity tests for the Markowitz Mean-Variance Optimizer."""

import os
import sys

import numpy as np
import pandas as pd

# Make local modules importable when pytest runs from any cwd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from c_optimizer import (
    compute_stats,
    efficient_frontier,
    max_sharpe,
    min_variance_ptf,
)


# ---------- Helpers: synthetic data ----------

def _fake_returns(seed=42, n_days=252, n_tickers=5):
    """Genera log-returns sintetici deterministici via seed."""
    rng = np.random.default_rng(seed)
    data = rng.normal(loc=0.0005, scale=0.01, size=(n_days, n_tickers))
    return pd.DataFrame(data, columns=[f"T{i}" for i in range(n_tickers)])


# ---------- Tests ----------

def test_stats():
    """mu and Sigma must have shape (n_tickers,) and (n_tickers, n_tickers)."""
    n_days = 252
    n_tickers = 5
    rend = _fake_returns(n_days=n_days, n_tickers=n_tickers)
    mu, Sigma = compute_stats(rend=rend)
    assert (mu.size == n_tickers) and (Sigma.columns.size == n_tickers) and (Sigma.index.size == n_tickers), \
        "mu e Sigma non hanno dimensioni corrette"


def test_mvp_weights_sum_to_one():
    """MVP weights must sum to 1 (fully invested constraint)."""
    rend = _fake_returns()
    mu, Sigma = compute_stats(rend=rend)
    MVP = min_variance_ptf(mu=mu, Sigma=Sigma)
    assert abs(float(np.sum(MVP)) - 1.0) < 1e-6, "I pesi del MVP non sommano a 1"


def test_tgp_weights_sum_to_one():
    """TGP weights must sum to 1 (fully invested constraint)."""
    rend = _fake_returns()
    mu, Sigma = compute_stats(rend=rend)
    TGP = max_sharpe(mu=mu, Sigma=Sigma, rf=0.04)
    assert abs(float(np.sum(TGP)) - 1.0) < 1e-6, "I pesi del TGP non sommano a 1"


def test_mvp_long_only():
    """MVP weights must be non-negative (no short positions)."""
    rend = _fake_returns()
    mu, Sigma = compute_stats(rend=rend)
    MVP = min_variance_ptf(mu=mu, Sigma=Sigma)
    assert all(peso + 1e-6 > 0 for peso in MVP), "I pesi del MVP non sono tutti positivi"


def test_min_variance():
    """MVP must have variance less than or equal to TGP variance."""
    rend = _fake_returns()
    mu, Sigma = compute_stats(rend=rend)
    MVP = min_variance_ptf(mu=mu, Sigma=Sigma)
    TGP = max_sharpe(mu=mu, Sigma=Sigma, rf=0.04)
    Sigma_MVP = MVP @ Sigma @ MVP
    Sigma_TGP = TGP @ Sigma @ TGP
    assert Sigma_MVP < Sigma_TGP + 1e-6, "MVP non è il ptf a varianza minima"


def test_frontier():
    """Efficient frontier must contain exactly n_points portfolios."""
    n_points = 50
    rend = _fake_returns()
    mu, Sigma = compute_stats(rend=rend)
    frontier = efficient_frontier(mu=mu, Sigma=Sigma, n_points=n_points)
    assert len(frontier) == n_points, f"La frontiera non ha {n_points} punti"