"""Unit + end-to-end tests for the dcf-analyzer skill.

Run from the skill root with:  pytest
"""

import sys
import os
import json
import subprocess

# Make the script in ../scripts importable from here.
HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

from dcf import (
    core,
    compute_wacc,
    validate,
    load_input,
    sensitivity,
    WACC_STEPS_DEFAULT,
    G_STEPS_DEFAULT,
)


def _example(name):
    """Path to a JSON example in this tests/ folder."""
    return os.path.join(HERE, name)


def test_core_enterprise_value():
    d = load_input(_example("example_wacc.json"))
    result = core(d)
    assert abs(result["enterprise_value"] - 1681.19) < 0.01, "EV non corrisponde"


def test_compute_wacc():
    # compute_wacc returns a float, not a dict.
    d = load_input(_example("example_components.json"))
    wacc = compute_wacc(d)
    assert abs(wacc - 0.0752) < 0.0001, "WACC non corrisponde"


def test_validate_rejects_negative_fcff():
    # validate() catches structural problems; here: all FCFF negative.
    d = {
        "FCFF": [-10, -20], "WACC": 0.09, "g": 0.02,
        "NetDebt": 0, "NShares": 10,
        "E_V": None, "Ke": None, "D_V": None, "Kd": None, "t": None,
        "wacc_steps": None, "g_steps": None,
    }
    result = validate(d)
    assert result["ok"] is False and result["field"] == "FCFF", "validate non rifiuta FCFF negativi"


def test_main_rejects_g_ge_wacc():
    # g >= WACC is enforced in main(), so we test the whole script end-to-end.
    script = os.path.join(HERE, "..", "scripts", "dcf.py")
    proc = subprocess.run(
        [sys.executable, script, _example("example_badg.json")],
        capture_output=True, text=True,
    )
    out = json.loads(proc.stdout)
    assert out["ok"] is False and out["field"] == "g", "main non rifiuta g >= WACC"


def test_sensitivity_grid():
    d = load_input(_example("example_wacc.json"))
    base = core(d)["fair_value_per_share"]
    grid = sensitivity(d)
    # 3 x 3 grid by default.
    assert len(grid) == len(WACC_STEPS_DEFAULT) * len(G_STEPS_DEFAULT), "dimensione griglia errata"
    # Central cell (ws=0, gs=0) must match the base fair value. Index 4 of a 3x3 grid.
    center = grid[4]
    assert abs(center["fv_share"] - base) < 0.01, "cella centrale != fair value base"
