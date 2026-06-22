---
name: dcf-analyzer
description: Build a DCF valuation of a company (enterprise value, equity value, fair value per share). Use when the user provides FCF and WACC and asks for intrinsic value. Do not use for financial institutions.
license: MIT
allowed-tools: Read, Write, Bash
---

# DCF Analyzer

## Quando usare questa skill

Build a Discounted Cash Flow (DCF) valuation of a company. Use when the user
provides FCF and WACC of the company, asks for the intrinsic value of the
company, or asks for the fair value per share. Do not use if the company is a
financial institution.

## Input

1. FCFF (free cash flow to the firm) for N years (N = len(FCFF))
2. WACC (Weighted Average Cost of Capital) or all its components
   (cost of equity, cost of debt, tax, E/V, D/V)
3. Terminal growth g
4. Company NetDebt
5. Number of shares (NShares)

The user may provide the data in the message or a CSV; the skill assembles them
into input.json following the Contract.

## Procedura

1. Validate the input values, considering their metric, values and sign
   (no negative CF, g < WACC).
2. If all the inputs are correct, convert the ones that need it
   (e.g. convert percentages to decimals: WACC, g, Ke, t...).
3. If the WACC isn't given (but its components are), compute it.
4. Write the inputs to a temp JSON, run `scripts/dcf.py <path>` via Bash,
   parse the JSON from stdout.
5. Build a sensitivity table on WACC and g.

## Output

Return a table with the Enterprise Value, Equity Value and Fair Value per share
of the company, followed by the sensitivity table. Below the tables, return a
brief comment of the results.

## Casi limite

- If g ≥ WACC, return a warning and ask the user for a valid value.
- If a cell of the sensitivity table has g greater than WACC, the relative
  fv_share will be null.
- If the FCF are all negative, return a warning and do not compute.
- If there are missing values, ask the user whether they are missing and what
  values to use instead.
- Any other error during the computation must return a warning explaining the
  problem.

## Contract

The skill writes `input.json`, which is the input for the Python script
`scripts/dcf.py`. Run it via Bash: `python scripts/dcf.py input.json`.

INPUT schema (keys):

```json
{
  "FCFF": [float, ...],
  "WACC": float | null,
  "g": float,
  "NetDebt": float,
  "NShares": float,
  "E_V": float | null,
  "Ke": float | null,
  "D_V": float | null,
  "Kd": float | null,
  "t": float | null,
  "wacc_steps": [float, ...] | null,
  "g_steps": [float, ...] | null
}
```

Use `null` for any missing value. `N` is derived from `len(FCFF)`. If `WACC` is
`null`, its components (`E_V, Ke, D_V, Kd, t`) must all be provided.

The script prints a JSON object to stdout, which the skill parses.

OUTPUT schema (success):

```json
{
  "ok": true, "error": null, "field": null,
  "enterprise_value": float,
  "equity_value": float,
  "fair_value_per_share": float,
  "sensitivity": [{"wacc": float, "g": float, "fv_share": float | null}, ...]
}
```

OUTPUT schema (error):

```json
{"ok": false, "error": "<message>", "field": "<key>"}
```

## Riferimenti

For all the formulas use `references/dcf_methodology.md`.
