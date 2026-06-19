"""Unit tests for the ratio-analysis skill.

Run from the skill root with:  pytest
"""

import sys
import os

# Make the script in ../scripts importable from here.
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

from ratio import core, validate, safe_div, load_input


def _example(name):
    """Path to a JSON example in this tests/ folder."""
    return os.path.join(HERE, name)


def test_core_full():
    d = load_input(_example("example_full.json"))
    result = core(d)
    assert abs(result["current_ratio"] - 2.0) < 0.01, "current_ratio errato"
    assert abs(result["debt_to_equity"] - 0.62) < 0.01, "debt_to_equity errato"


def test_core_missing_returns_null():
    # Inventory null, InterestExpense 0, TotalEquity null in example_missing.json:
    # the affected ratios must be null, the others still computed.
    d = load_input(_example("example_missing.json"))
    result = core(d)
    assert abs(result["current_ratio"] - 2.0) < 0.01, "current_ratio dovrebbe essere calcolato"
    assert result["quick_ratio"] is None, "quick_ratio dovrebbe essere null (Inventory mancante)"
    assert result["interest_coverage"] is None, "interest_coverage dovrebbe essere null (denominatore 0)"
    assert result["debt_to_equity"] is None, "debt_to_equity dovrebbe essere null (TotalEquity mancante)"


def test_safe_div():
    assert safe_div(10, 0) is None, "denominatore 0 deve dare None"
    assert safe_div(5, None) is None, "denominatore None deve dare None"
    assert safe_div(None, 5) is None, "numeratore None deve dare None"


def test_validate_rejects_negative_revenue():
    d = load_input(_example("example_badsign.json"))
    result = validate(d)
    assert result["ok"] is False and result["field"] == "Revenue", "validate non rifiuta Revenue negativo"
