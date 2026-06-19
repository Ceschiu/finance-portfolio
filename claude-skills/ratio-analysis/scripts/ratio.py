"""
ratio.py — Financial ratio engine for the `ratio-analysis` skill.

Contract (single source of truth):
  INPUT  : a JSON file whose path is passed as argv[1].
  OUTPUT : a single JSON object printed to stdout.

INPUT schema (keys, all float | null):
  Revenue, NetIncome, EBIT, InterestExpense, TotalAssets, CurrentAssets,
  Inventory, CurrentLiabilities, TotalDebt, TotalEquity

OUTPUT schema (success):
  {"ok": true, "error": null, "field": null,
   "current_ratio": float | null, "quick_ratio": float | null,
   "debt_to_equity": float | null, "interest_coverage": float | null,
   "ROE": float | null, "ROA": float | null,
   "net_margin": float | null, "asset_turnover": float | null}

OUTPUT schema (error):
  {"ok": false, "error": "<message>", "field": "<key>"}

A ratio whose numerator or denominator is missing (null), or whose denominator
is 0, is returned as null; the other ratios are still computed.
"""

import json
import sys

# Inputs that cannot be negative. NetIncome, EBIT and TotalEquity are NOT here:
# losses and negative equity are economically valid.
NON_NEGATIVE = [
    "Revenue", "TotalAssets", "CurrentAssets", "Inventory",
    "CurrentLiabilities", "TotalDebt", "InterestExpense",
]


def _is_number(x):
    """True for int/float but NOT bool (bool is a subclass of int in Python)."""
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _err(message, field):
    """Build the standard structured-error object."""
    return {"ok": False, "error": message, "field": field}


def safe_div(num, den):
    """Divide num/den, returning None if either is missing (None) or den is 0."""
    if num is None or den is None or den == 0:
        return None
    return round(num / den, 2)


def load_input(path):
    """Read and parse the JSON input file.

    Returns the parsed dict on success, or a structured-error dict if the file
    is missing or malformed. The caller must check for the error shape.
    """
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return _err("JSON input file not found", "path")
    except json.JSONDecodeError:
        return _err("JSON input file is malformed", "path")


def validate(d):
    """Validate types and signs. Missing values (null) are allowed: the related
    ratios will simply be null."""
    for key in d:
        value = d.get(key)
        if value is None:
            continue  # missing is allowed
        if not _is_number(value):
            return _err(f"{key} must be a number", key)
        if key in NON_NEGATIVE and value < 0:
            return _err(f"{key} must be non-negative", key)
    return {"ok": True, "error": None, "field": None}


def core(d):
    """Compute the eight ratios. Each is null when its inputs don't allow it."""
    ca = d.get("CurrentAssets")
    inv = d.get("Inventory")
    # Quick-ratio numerator (CurrentAssets - Inventory) needs both operands.
    quick_num = ca - inv if (ca is not None and inv is not None) else None

    return {
        "current_ratio": safe_div(ca, d.get("CurrentLiabilities")),
        "quick_ratio": safe_div(quick_num, d.get("CurrentLiabilities")),
        "debt_to_equity": safe_div(d.get("TotalDebt"), d.get("TotalEquity")),
        "interest_coverage": safe_div(d.get("EBIT"), d.get("InterestExpense")),
        "ROE": safe_div(d.get("NetIncome"), d.get("TotalEquity")),
        "ROA": safe_div(d.get("NetIncome"), d.get("TotalAssets")),
        "net_margin": safe_div(d.get("NetIncome"), d.get("Revenue")),
        "asset_turnover": safe_div(d.get("Revenue"), d.get("TotalAssets")),
    }


def build_output(base):
    """Assemble the success object and print it as a single JSON line."""
    recap = {"ok": True, "error": None, "field": None}
    recap.update(base)
    print(json.dumps(recap))


def main():
    # 1. Read input file.
    if len(sys.argv) < 2:
        print(json.dumps(_err("missing input path argument", "path")))
        sys.exit(0)
    d = load_input(sys.argv[1])
    if d.get("ok") is False:        # load_input returned a structured error
        print(json.dumps(d))
        sys.exit(0)

    # 2. Validate types / signs.
    check = validate(d)
    if not check["ok"]:
        print(json.dumps(check))
        sys.exit(0)

    # 3. Ratios, then emit.
    base = core(d)
    build_output(base)


if __name__ == "__main__":
    main()
