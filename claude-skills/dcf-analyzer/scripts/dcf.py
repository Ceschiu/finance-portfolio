"""
dcf.py — Discounted Cash Flow valuation engine for the `dcf-analyzer` skill.

Contract (single source of truth):
  INPUT  : a JSON file whose path is passed as argv[1].
  OUTPUT : a single JSON object printed to stdout.

INPUT schema (keys):
  FCFF        list[float]   free cash flow to the firm, one value per year (N = len(FCFF))
  WACC        float | null  if null, it is computed from the components below
  g           float         terminal growth rate (must be < WACC)
  NetDebt     float         net debt, used to bridge Enterprise Value -> Equity Value
  NShares     float         number of shares outstanding
  E_V         float | null  equity weight  E/V   (WACC component)
  Ke          float | null  cost of equity        (WACC component)
  D_V         float | null  debt weight    D/V    (WACC component)
  Kd          float | null  cost of debt          (WACC component)
  t           float | null  tax rate              (WACC component)
  wacc_steps  list[float] | null  absolute deltas applied to WACC for the sensitivity grid
  g_steps     list[float] | null  absolute deltas applied to g    for the sensitivity grid

OUTPUT schema (success):
  {"ok": true, "error": null, "field": null,
   "enterprise_value": float, "equity_value": float, "fair_value_per_share": float,
   "sensitivity": [{"wacc": float, "g": float, "fv_share": float | null}, ...]}

OUTPUT schema (error):
  {"ok": false, "error": "<message>", "field": "<key>"}
"""

import json
import sys

# Default sensitivity steps (absolute deltas):
#   WACC +/- 50 bps, g +/- 25 bps — the way an analyst usually reads a DCF sensitivity table.
WACC_STEPS_DEFAULT = [-0.005, 0.0, 0.005]
G_STEPS_DEFAULT = [-0.0025, 0.0, 0.0025]

# Keys that, together, allow WACC to be reconstructed when WACC is null.
WACC_COMPONENTS = ["E_V", "Ke", "D_V", "Kd", "t"]


def _is_number(x):
    """True for int/float but NOT bool (bool is a subclass of int in Python)."""
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _err(message, field):
    """Build the standard structured-error object."""
    return {"ok": False, "error": message, "field": field}


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
    """Validate presence, types and signs of the inputs.

    Note: this runs BEFORE WACC is resolved, so it does NOT check g < WACC
    (that guard runs in main once WACC is known). It only guarantees that we
    have enough valid data to proceed.
    """
    # --- FCFF: non-empty list of numbers, not all negative ---
    fcff = d.get("FCFF")
    if not isinstance(fcff, list) or len(fcff) == 0:
        return _err("FCFF must be a non-empty list", "FCFF")
    if not all(_is_number(x) for x in fcff):
        return _err("FCFF must contain only numbers", "FCFF")
    if all(x < 0 for x in fcff):
        return _err("all FCFF values are negative: valuation aborted", "FCFF")

    # --- scalar inputs that must always be present and numeric ---
    for key in ["g", "NetDebt", "NShares"]:
        if not _is_number(d.get(key)):
            return _err(f"{key} must be a number", key)
    if d.get("NShares") <= 0:
        return _err("NShares must be > 0", "NShares")

    # --- WACC: either provided as a number, OR all components present & numeric ---
    if d.get("WACC") is None:
        missing = [k for k in WACC_COMPONENTS if not _is_number(d.get(k))]
        if missing:
            return _err(
                "WACC is missing and its components are incomplete: " + ", ".join(missing),
                "WACC",
            )
    elif not _is_number(d.get("WACC")):
        return _err("WACC must be a number or null", "WACC")

    # --- optional sensitivity steps: if present, must be lists of numbers ---
    for key in ["wacc_steps", "g_steps"]:
        steps = d.get(key)
        if steps is not None:
            if not isinstance(steps, list) or not all(_is_number(x) for x in steps):
                return _err(f"{key} must be a list of numbers or null", key)

    return {"ok": True, "error": None, "field": None}


def compute_wacc(d):
    """Reconstruct WACC from its components: WACC = E_V*Ke + D_V*Kd*(1 - t).

    The weights E_V and D_V are already E/V and D/V, so no further normalisation
    is needed.
    """
    return d["E_V"] * d["Ke"] + d["D_V"] * d["Kd"] * (1.0 - d["t"])


def core(d):
    """Run the DCF on a fully-resolved input dict.

    Steps: discount each FCFF, add the discounted Gordon terminal value to get
    the Enterprise Value, bridge to Equity Value via NetDebt, then per share.
    Returns the three headline figures.
    """
    fcff = d["FCFF"]
    wacc = d["WACC"]
    g = d["g"]
    n = len(fcff)

    # Present value of the explicit FCFF stream (year 1 is discounted by ^1).
    pv_fcff = 0.0
    for i in range(1, n + 1):
        pv_fcff += fcff[i - 1] / (1.0 + wacc) ** i

    # Gordon terminal value at year N, then discounted back to today.
    terminal_value = fcff[-1] * (1.0 + g) / (wacc - g)
    pv_terminal = terminal_value / (1.0 + wacc) ** n

    enterprise_value = pv_fcff + pv_terminal
    equity_value = enterprise_value - d["NetDebt"]
    fair_value_per_share = equity_value / d["NShares"]

    return {
        "enterprise_value": round(enterprise_value, 2),
        "equity_value": round(equity_value, 2),
        "fair_value_per_share": round(fair_value_per_share, 4),
    }


def sensitivity(d):
    """Build the WACC x g sensitivity grid as a list of rows.

    Each step is an absolute delta added to the BASE value (no accumulation).
    A combination where g >= WACC is mathematically undefined, so its fv_share
    is reported as null rather than crashing.
    """
    wacc_steps = d.get("wacc_steps") or WACC_STEPS_DEFAULT
    g_steps = d.get("g_steps") or G_STEPS_DEFAULT

    base_wacc = d["WACC"]
    base_g = d["g"]

    rows = []
    for ws in wacc_steps:
        for gs in g_steps:
            w = base_wacc + ws
            gg = base_g + gs
            if w <= gg:
                fv = None  # terminal value undefined when g >= WACC
            else:
                perturbed = dict(d)        # shallow copy is enough: we only swap scalars
                perturbed["WACC"] = w
                perturbed["g"] = gg
                fv = core(perturbed)["fair_value_per_share"]
            rows.append({"wacc": round(w, 6), "g": round(gg, 6), "fv_share": fv})
    return rows


def build_output(base, sens):
    """Assemble the success object and print it as a single JSON line."""
    recap = {"ok": True, "error": None, "field": None}
    recap.update(base)              # enterprise_value, equity_value, fair_value_per_share
    recap["sensitivity"] = sens
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

    # 2. Validate structure / types (before WACC is resolved).
    check = validate(d)
    if not check["ok"]:
        print(json.dumps(check))
        sys.exit(0)

    # 3. Resolve WACC once, only if it was not provided.
    if d.get("WACC") is None:
        d["WACC"] = compute_wacc(d)

    # 4. Now that WACC is known, enforce g < WACC.
    if d["g"] >= d["WACC"]:
        print(json.dumps(_err("g must be < WACC", "g")))
        sys.exit(0)

    # 5. Value + sensitivity, then emit.
    base = core(d)
    sens = sensitivity(d)
    build_output(base, sens)


if __name__ == "__main__":
    main()
